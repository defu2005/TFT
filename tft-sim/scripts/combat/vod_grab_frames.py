#!/usr/bin/env python3
"""Lay khung hinh tu Twitch VOD qua HLS (khong tai full file).

Dung:
  python3 scripts/combat/vod_grab_frames.py \\
    --url https://www.twitch.tv/videos/2927534195 \\
    --seconds 60,180,300,420 --out /tmp/frames --height 480

Can: yt-dlp, ffmpeg tren PATH.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def hls_url(page: str, height: int) -> str:
    fmt = f"{height}p/best[height<={height}]/best"
    r = subprocess.run(
        ["yt-dlp", "-f", fmt, "-g", page],
        check=True,
        capture_output=True,
        text=True,
    )
    lines = [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]
    if not lines:
        raise SystemExit("yt-dlp khong tra HLS URL")
    return lines[0]


def grab(hls: str, second: int, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-ss",
            str(second),
            "-i",
            hls,
            "-frames:v",
            "1",
            "-q:v",
            "3",
            str(dest),
        ],
        check=True,
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--seconds", required=True, help="vd 60,180,300 hoac 60:20:60 (start:stop:step)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--height", type=int, default=480)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    if ":" in args.seconds and "," not in args.seconds:
        a, b, step = [int(x) for x in args.seconds.split(":")]
        secs = list(range(a, b + 1, step))
    else:
        secs = [int(x) for x in args.seconds.split(",") if x.strip()]

    hls = hls_url(args.url, args.height)
    for s in secs:
        dest = out / f"t{s:05d}.jpg"
        try:
            grab(hls, s, dest)
            print("ok", dest)
        except subprocess.CalledProcessError as e:
            print("fail", s, e, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
