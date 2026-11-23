#!/usr/bin/env python3
"""
TFT RAM Probe & Memory Scanner
Đọc trực tiếp bộ nhớ của tiến trình TFTClient-Win64-Shipping.exe.

Chức năng:
1. scan: Tìm kiếm và lọc vùng nhớ theo giá trị (Gold, HP, Level, Stage).
2. inspect: Xem nội dung bộ nhớ tại một địa chỉ cụ thể.
3. live: Xuất trạng thái thời gian thực ra JSONL (cho tft-coach ingest).
"""

import os
import sys
import json
import time
import struct
import argparse
import ctypes
from ctypes import wintypes
import psutil

kernel32 = ctypes.windll.kernel32

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", wintypes.DWORD),
        ("Alignment1", wintypes.DWORD),
        ("RegionSize", ctypes.c_size_t),
        ("State", wintypes.DWORD),
        ("Protect", wintypes.DWORD),
        ("Type", wintypes.DWORD),
        ("Alignment2", wintypes.DWORD),
    ]

MEM_COMMIT = 0x1000
PAGE_READWRITE = 0x04
PAGE_READONLY = 0x02
PAGE_EXECUTE_READ = 0x20
PAGE_EXECUTE_READWRITE = 0x40

def get_tft_pid():
    for p in psutil.process_iter(['pid', 'name']):
        name = (p.info['name'] or '').lower()
        if 'tftclient-win64-shipping' in name:
            return p.info['pid']
    return None

def open_process(pid):
    handle = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
    if not handle:
        err = kernel32.GetLastError()
        raise PermissionError(f"Không thể mở tiến trình PID {pid}. Mã lỗi: {err}")
    return handle

def read_memory_bytes(handle, address, size):
    buf = (ctypes.c_char * size)()
    bytes_read = ctypes.c_size_t()
    res = kernel32.ReadProcessMemory(handle, ctypes.c_void_p(address), buf, size, ctypes.byref(bytes_read))
    if not res:
        return None
    return bytes(buf[:bytes_read.value])

def scan_value_int32(handle, target_val, candidate_addrs=None):
    """
    Quét tìm số nguyên int32 (4 bytes).
    Nếu candidate_addrs có dữ liệu, chỉ kiểm tra lại các địa chỉ đó (Differential scan).
    """
    target_bytes = struct.pack('<i', int(target_val))

    if candidate_addrs:
        matches = []
        for addr in candidate_addrs:
            data = read_memory_bytes(handle, addr, 4)
            if data == target_bytes:
                matches.append(addr)
        return matches

    matches = []
    mbi = MEMORY_BASIC_INFORMATION()
    address = 0
    chunk_size = 256 * 1024
    buf = (ctypes.c_char * chunk_size)()
    bytes_read = ctypes.c_size_t()

    while kernel32.VirtualQueryEx(handle, ctypes.c_void_p(address), ctypes.byref(mbi), ctypes.sizeof(mbi)):
        if mbi.State == MEM_COMMIT and mbi.Protect in (PAGE_READWRITE, PAGE_EXECUTE_READWRITE):
            region_size = mbi.RegionSize
            curr = mbi.BaseAddress or 0
            remaining = region_size

            while remaining >= 4:
                to_read = min(remaining, chunk_size)
                if kernel32.ReadProcessMemory(handle, ctypes.c_void_p(curr), buf, to_read, ctypes.byref(bytes_read)):
                    data = bytes(buf[:bytes_read.value])
                    idx = 0
                    while True:
                        idx = data.find(target_bytes, idx)
                        if idx == -1:
                            break
                        # Chỉ lấy các địa chỉ căn 4-byte (4-byte alignment)
                        if (idx % 4) == 0:
                            matches.append(curr + idx)
                        idx += 4
                curr += to_read
                remaining -= to_read

        address = (mbi.BaseAddress or 0) + mbi.RegionSize
        if address >= 0x7FFFFFFFFFFF:
            break

    return matches

def interactive_scan():
    pid = get_tft_pid()
    if not pid:
        print("[RAM Probe] TFTClient-Win64-Shipping.exe chưa khởi chạy.")
        print("Vui lòng mở game TFT và vào một trận đấu trước khi quét.")
        return

    print(f"[RAM Probe] Đã phát hiện TFT Client đang chạy tại PID: {pid}")
    try:
        handle = open_process(pid)
    except Exception as e:
        print(f"[RAM Probe] Lỗi: {e}")
        return

    candidates = None
    try:
        while True:
            prompt = "\nNhập giá trị cần tìm (vd: số Vàng hiện tại, hoặc 'q' để thoát): "
            user_input = input(prompt).strip()
            if user_input.lower() == 'q':
                break

            try:
                val = int(user_input)
            except ValueError:
                print("Vui lòng nhập một số nguyên hợp lệ.")
                continue

            t0 = time.time()
            if candidates is None:
                print(f"Bắt đầu quét toàn bộ bộ nhớ Committed RW cho giá trị = {val}...")
                candidates = scan_value_int32(handle, val)
                dt = time.time() - t0
                print(f"Lần 1 hoàn tất sau {dt:.2f}s: tìm thấy {len(candidates)} kết quả.")
            else:
                print(f"Lọc lại {len(candidates)} địa chỉ cho giá trị mới = {val}...")
                candidates = scan_value_int32(handle, val, candidate_addrs=candidates)
                dt = time.time() - t0
                print(f"Lọc hoàn tất sau {dt:.3f}s: còn lại {len(candidates)} địa chỉ ứng viên.")

            if len(candidates) <= 20:
                print("\nDanh sách địa chỉ tiềm năng:")
                for addr in candidates:
                    print(f"  -> {hex(addr)}")

            if len(candidates) == 0:
                print("Không còn địa chỉ nào khớp! Bạn có muốn bắt đầu quét mới không? (y/n)")
                ans = input().strip().lower()
                if ans == 'y':
                    candidates = None
    finally:
        kernel32.CloseHandle(handle)

def live_reader(offsets_path, output_path, interval_ms=250):
    if not os.path.exists(offsets_path):
        print(f"[RAM Live] Không tìm thấy file cấu hình offset: {offsets_path}", file=sys.stderr)
        print("Vui lòng chạy 'python scripts/probe-ram.py --interactive' để xác định offset trước.", file=sys.stderr)
        return

    with open(offsets_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print(f"[RAM Live] Bắt đầu đọc RAM chu kỳ {interval_ms}ms, ghi vào {output_path}...")

    handle = None
    last_pid = None

    try:
        while True:
            pid = get_tft_pid()
            if not pid:
                if handle:
                    kernel32.CloseHandle(handle)
                    handle = None
                    last_pid = None
                time.sleep(1)
                continue

            if pid != last_pid or not handle:
                try:
                    handle = open_process(pid)
                    last_pid = pid
                    print(f"[RAM Live] Đã gắn vào tiến trình PID {pid}")
                except Exception as e:
                    print(f"[RAM Live] Lỗi mở tiến trình: {e}", file=sys.stderr)
                    time.sleep(1)
                    continue

            # Đọc các trường theo offset/địa chỉ đã cấu hình
            state = {
                "ts": time.time(),
                "pid": pid,
                "gold": 0,
                "hp": 100,
                "level": 1,
                "stage": 1,
                "shop": [None, None, None, None, None]
            }

            if "gold_addr" in config:
                val = read_memory_bytes(handle, int(config["gold_addr"], 16), 4)
                if val: state["gold"] = struct.unpack('<i', val)[0]

            if "hp_addr" in config:
                val = read_memory_bytes(handle, int(config["hp_addr"], 16), 4)
                if val: state["hp"] = struct.unpack('<i', val)[0]

            if "level_addr" in config:
                val = read_memory_bytes(handle, int(config["level_addr"], 16), 4)
                if val: state["level"] = struct.unpack('<i', val)[0]

            if "stage_addr" in config:
                val = read_memory_bytes(handle, int(config["stage_addr"], 16), 4)
                if val: state["stage"] = struct.unpack('<i', val)[0]

            # Ghi atomic tạm qua file .tmp rồi rename
            tmp_path = output_path + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(state, f)
            os.replace(tmp_path, output_path)

            time.sleep(interval_ms / 1000.0)
    finally:
        if handle:
            kernel32.CloseHandle(handle)

def main():
    parser = argparse.ArgumentParser(description="TFT RAM Probe & Scanner")
    parser.add_argument("--interactive", action="store_true", help="Chạy quét tương tác để xác định offset")
    parser.add_argument("--check", action="store_true", help="Kiểm tra trạng thái tiến trình và quyền đọc bộ nhớ")
    parser.add_argument("--live", action="store_true", help="Chạy service đọc RAM theo thời gian thực")
    parser.add_argument("--offsets", default="captures/ram-offsets.json", help="Đường dẫn file cấu hình offset")
    parser.add_argument("--output", default="captures/ram-state.json", help="Đường dẫn file output cho live mode")
    parser.add_argument("--interval", type=int, default=250, help="Chu kỳ đọc (ms)")
    args = parser.parse_args()

    if args.live:
        live_reader(args.offsets, args.output, args.interval)
    elif args.interactive:
        interactive_scan()
    else:
        pid = get_tft_pid()
        if not pid:
            print("[RAM Probe] TFTClient-Win64-Shipping.exe chưa chạy.")
            print("Gợi ý: Mở game qua Riot Client và vào trận để kiểm tra.")
        else:
            print(f"[RAM Probe] Tìm thấy TFT Client (PID {pid}).")
            try:
                h = open_process(pid)
                print(f"[RAM Probe] Handle bộ nhớ: {hex(h)} -> Quyền đọc PROCESS_VM_READ thành công!")
                kernel32.CloseHandle(h)
            except Exception as e:
                print(f"[RAM Probe] Thất bại khi mở quyền đọc: {e}")
    else:
        interactive_scan()

if __name__ == "__main__":
    main()
