#!/usr/bin/env python3
"""Read the TFT HUD from the Windows client, an image, or a paced video replay."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import ctypes
from ctypes import wintypes
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

from PIL import Image, ImageGrab

from hud_ocr import HudReader


def find_tft_hwnd(win32gui):
    hwnd = win32gui.FindWindow(None, "TFT  ")
    if hwnd and win32gui.IsWindowVisible(hwnd):
        return hwnd

    candidates = []

    def inspect_window(handle, _):
        if win32gui.IsWindowVisible(handle) and "tft" in win32gui.GetWindowText(handle).lower():
            candidates.append(handle)

    win32gui.EnumWindows(inspect_window, None)
    return candidates[0] if candidates else None


class WindowCapture:
    def __init__(self, backend):
        if os.name != "nt":
            raise ValueError("live window capture requires Windows; use --image or --video here")
        import win32gui
        import win32ui
        import pywintypes

        self.gui = win32gui
        self.ui = win32ui
        self.error = pywintypes.error
        self.backend = backend
        # Use physical client pixels on monitors with different DPI settings.
        user32 = ctypes.windll.user32
        user32.SetThreadDpiAwarenessContext(ctypes.c_void_p(-4))
        self.print_window = user32.PrintWindow
        self.print_window.argtypes = (wintypes.HWND, wintypes.HDC, wintypes.UINT)
        self.print_window.restype = wintypes.BOOL

    def read(self):
        try:
            return self.capture_client()
        except self.error as exc:
            raise OSError(f"TFT client capture failed: {exc}") from exc

    def capture_client(self):
        hwnd = find_tft_hwnd(self.gui)
        if not hwnd or self.gui.IsIconic(hwnd):
            return None
        left, top, width, height = self.gui.GetClientRect(hwnd)
        if width <= 0 or height <= 0:
            return None
        if self.backend == "screen":
            if hwnd != self.gui.GetForegroundWindow():
                return None
            origin = self.gui.ClientToScreen(hwnd, (left, top))
            extent = self.gui.ClientToScreen(hwnd, (width, height))
            frame = ImageGrab.grab(bbox=(*origin, *extent), all_screens=True)
            return frame if hwnd == self.gui.GetForegroundWindow() else None

        window_dc = self.gui.GetDC(hwnd)
        source = target = bitmap = previous = None
        try:
            source = self.ui.CreateDCFromHandle(window_dc)
            target = source.CreateCompatibleDC()
            bitmap = self.ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(source, width, height)
            previous = target.SelectObject(bitmap)
            # PW_CLIENTONLY | PW_RENDERFULLCONTENT
            if not self.print_window(hwnd, target.GetSafeHdc(), 3):
                return None
            return Image.frombytes("RGB", (width, height), bitmap.GetBitmapBits(True), "raw", "BGRX", 0, 1)
        finally:
            if previous is not None:
                target.SelectObject(previous)
            if target is not None:
                target.DeleteDC()
            if bitmap is not None:
                self.gui.DeleteObject(bitmap.GetHandle())
            # The source HDC belongs to the window and must be released with ReleaseDC.
            if source is not None:
                source.Detach()
            self.gui.ReleaseDC(hwnd, window_dc)


def publish(path, record):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as tmp:
        staged = Path(tmp.name)
        try:
            json.dump(record, tmp, ensure_ascii=False, allow_nan=False)
            tmp.close()
            os.replace(staged, path)
        finally:
            staged.unlink(missing_ok=True)


def sample(recognize, capture, source, index, scheduled, interval, dropped, *, source_size=None):
    start = time.perf_counter()
    captured_at = time.time_ns() // 1_000_000
    error = None
    try:
        image = capture()
    except OSError as exc:
        if source != "window":
            raise
        image = None
        error = str(exc)
    captured = time.perf_counter()
    data = {"hudDetected": False, "gold": None, "level": None, "shop": None,
            "shopSlots": [None] * 5}
    if image is not None:
        try:
            data = recognize(image)
        except (subprocess.SubprocessError, OSError) as exc:
            error = f"OCR failed: {exc}"
    elif source == "window" and error is None:
        error = "TFT client frame unavailable"
    finished = time.perf_counter()
    latency = lambda seconds: round(seconds * 1000, 2)
    return {
        "hudSchema": 2, "set": 18, "source": source, "frame": index,
        "capturedAtMs": captured_at,
        "mediaTimeMs": latency(index * interval) if source == "video" else None,
        "resolution": list(source_size or image.size) if image is not None else None,
        "captureLatencyMs": latency(captured - start),
        "recognitionLatencyMs": latency(finished - captured),
        "processingLatencyMs": latency(finished - start),
        "scheduleLagMs": latency(start - scheduled),
        "endToEndLatencyMs": latency(finished - scheduled),
        "deadlineMissed": finished - scheduled > interval,
        "droppedFrames": dropped,
        "error": error,
        **data,
    }


def window_records(reader, interval, backend):
    window = WindowCapture(backend)
    scheduled = time.perf_counter()
    index = dropped = 0
    while True:
        time.sleep(max(0, scheduled - time.perf_counter()))
        record = sample(reader.read, window.read, "window", index, scheduled, interval, dropped)
        yield {**record, "captureBackend": backend}
        scheduled += interval
        index += 1
        # Accept a late sample instead of bursting through obsolete deadlines.
        skipped = max(0, math.floor((time.perf_counter() - scheduled) / interval))
        scheduled += skipped * interval
        index += skipped
        dropped += skipped


def video_records(reader, filename, interval):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
         "-of", "json", filename], capture_output=True, check=True,
    )
    streams = json.loads(result.stdout)["streams"]
    if not streams:
        raise ValueError("input has no video stream")
    stream = streams[0]
    size = stream["width"], stream["height"]
    (left, top, right, bottom), boxes = reader.video_crops(size)
    hud_size = right - left, bottom - top
    frame_bytes = hud_size[0] * hud_size[1] * 3
    # Crop only after converting to RGB so subsampled chroma yields the same
    # boundary pixels as decoding the full frame to RGB before cropping.
    filters = f"fps={1 / interval:.9f}:start_time=0,format=rgb24,crop={hud_size[0]}:{hud_size[1]}:{left}:{top}:exact=1"

    def recognize(image):
        return reader.read_crops(image, boxes)

    command = ["ffmpeg", "-nostdin", "-v", "error", "-threads", "2", "-noautorotate", "-i", filename,
               "-map", "0:v:0", "-vf", filters, "-threads", "2",
               "-pix_fmt", "rgb24", "-f", "rawvideo", "pipe:1"]
    with subprocess.Popen(command, stdout=subprocess.PIPE) as decoder, ThreadPoolExecutor(max_workers=1) as prefetch:
        def read_frame():
            data = decoder.stdout.read(frame_bytes)
            if data and len(data) != frame_bytes:
                raise ValueError("video decoder returned an incomplete frame")
            return data

        pending = prefetch.submit(read_frame)

        def take_frame():
            nonlocal pending
            data = pending.result()
            if data:
                # Keep just the next frame moving through the pipe during OCR.
                pending = prefetch.submit(read_frame)
            return data

        def capture():
            data = take_frame()
            return Image.frombytes("RGB", hud_size, data) if data else None

        try:
            first = sample(recognize, capture, "video", 0, time.perf_counter(), interval, 0, source_size=size)
            if first["resolution"] is None:
                if decoder.wait():
                    raise ValueError("ffmpeg could not decode the video")
                return
            # Record cold-start latency on sample zero. Pace the rest once
            # the first result is available so decoder startup cannot skip it.
            started = time.perf_counter()
            yield first
            index, dropped = 1, 0
            while True:
                skipped = max(0, math.floor((time.perf_counter() - started) / interval) - index)
                if skipped:
                    for _ in range(min(skipped, 8)):
                        if not take_frame():
                            if decoder.wait():
                                raise ValueError("ffmpeg could not decode the video")
                            return
                        index += 1
                        dropped += 1
                    continue
                scheduled = started + index * interval
                time.sleep(max(0, scheduled - time.perf_counter()))
                record = sample(recognize, capture, "video", index, scheduled, interval, dropped, source_size=size)
                if record["resolution"] is None:
                    break
                yield record
                index += 1
            if decoder.wait():
                raise ValueError("ffmpeg could not decode the video")
        finally:
            if decoder.poll() is None:
                decoder.terminate()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    media = parser.add_mutually_exclusive_group()
    media.add_argument("--image", type=Path)
    media.add_argument("--video")
    parser.add_argument("--profile", type=Path)
    parser.add_argument("--language", default="eng", help="installed Tesseract language")
    parser.add_argument("--tesseract", default="tesseract", help="path to the Tesseract executable")
    parser.add_argument("--capture", choices=("window", "screen"), default="window",
                        help="Windows capture backend; screen requires TFT in foreground")
    parser.add_argument("--interval", type=float, default=0.25, help="seconds between samples")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--output", type=Path, help="write the latest HUD atomically")
    args = parser.parse_args()
    if not math.isfinite(args.interval) or args.interval <= 0:
        parser.error("--interval must be positive and finite")
    if shutil.which(args.tesseract) is None:
        parser.error("Tesseract is required; install it or pass --tesseract")
    if args.video and any(shutil.which(command) is None for command in ("ffmpeg", "ffprobe")):
        parser.error("--video requires ffmpeg and ffprobe")
    if (args.video or args.image) and args.capture != "window":
        parser.error("--capture screen is only for a live window")
    reader = None
    try:
        reader = HudReader(args.profile, args.language, args.tesseract)
        if args.image:
            with Image.open(args.image) as image:
                records = [sample(reader.read, image.copy, "image", 0, time.perf_counter(), args.interval, 0)]
        elif args.video:
            records = video_records(reader, args.video, args.interval)
        else:
            args.output = args.output or Path("captures/hud-live.json")
            records = window_records(reader, args.interval, args.capture)

        try:
            for record in records:
                if args.output:
                    started = time.perf_counter()
                    publish(args.output, record)
                    # Report publication timing on stdout, after replacing the file.
                    record["publishLatencyMs"] = round((time.perf_counter() - started) * 1000, 2)
                print(json.dumps(record, ensure_ascii=True), flush=True)
                if args.once:
                    break
        finally:
            if hasattr(records, "close"):
                records.close()
    except KeyboardInterrupt:
        return
    except (ValueError, OSError, ImportError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"HUD reader: {exc}\n")
    finally:
        if reader is not None:
            reader.close()


if __name__ == "__main__":
    main()
