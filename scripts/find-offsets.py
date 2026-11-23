#!/usr/bin/env python3
"""
TFT Offset Finder (CLI / Non-interactive)
Thu hẹp địa chỉ biến số (gold, hp, level, stage) trong RAM một cách nhanh chóng.

Cách dùng:
Lần 1: python scripts/find-offsets.py --gold 2 --hp 100 --level 2
Lần 2 (khi vàng đổi): python scripts/find-offsets.py --gold 4
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
PAGE_EXECUTE_READWRITE = 0x40

CANDIDATES_FILE = "captures/ram-candidates.json"
OFFSETS_FILE = "captures/ram-offsets.json"

def get_tft_pid():
    for p in psutil.process_iter(['pid', 'name']):
        name = (p.info['name'] or '').lower()
        if 'tftclient-win64-shipping' in name:
            return p.info['pid']
    return None

def open_process(pid):
    handle = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
    if not handle:
        raise PermissionError(f"Không thể mở tiến trình PID {pid}. Lỗi: {kernel32.GetLastError()}")
    return handle

def read_bytes(handle, address, size):
    buf = (ctypes.c_char * size)()
    bytes_read = ctypes.c_size_t()
    res = kernel32.ReadProcessMemory(handle, ctypes.c_void_p(address), buf, size, ctypes.byref(bytes_read))
    if not res:
        return None
    return bytes(buf[:bytes_read.value])

def scan_all_int32(handle, target_val):
    target_bytes = struct.pack('<i', int(target_val))
    matches = []
    mbi = MEMORY_BASIC_INFORMATION()
    address = 0
    chunk_size = 256 * 1024
    buf = (ctypes.c_char * chunk_size)()
    bytes_read = ctypes.c_size_t()

    PAGE_NOACCESS = 0x01
    PAGE_GUARD = 0x100

    while kernel32.VirtualQueryEx(handle, ctypes.c_void_p(address), ctypes.byref(mbi), ctypes.sizeof(mbi)):
        if mbi.State == MEM_COMMIT and not (mbi.Protect & (PAGE_GUARD | PAGE_NOACCESS)) and (mbi.Protect & (PAGE_READWRITE | PAGE_EXECUTE_READWRITE)):
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
                        if (idx % 4) == 0:
                            matches.append(curr + idx)
                        idx += 4
                curr += to_read
                remaining -= to_read

        address = (mbi.BaseAddress or 0) + mbi.RegionSize
        if address >= 0x7FFFFFFFFFFF:
            break

    return matches

def filter_candidates(handle, addrs, target_val):
    target_bytes = struct.pack('<i', int(target_val))
    matches = []
    for addr in addrs:
        b = read_bytes(handle, addr, 4)
        if b == target_bytes:
            matches.append(addr)
    return matches

def main():
    parser = argparse.ArgumentParser(description="TFT Fast RAM Offset Finder")
    parser.add_argument("--gold", type=int, help="Giá trị vàng hiện tại")
    parser.add_argument("--hp", type=int, help="Giá trị máu hiện tại")
    parser.add_argument("--level", type=int, help="Level hiện tại")
    parser.add_argument("--stage", type=int, help="Stage hiện tại")
    parser.add_argument("--reset", action="store_true", help="Xóa bộ đệm ứng viên và bắt đầu lại")
    args = parser.parse_args()

    if args.reset and os.path.exists(CANDIDATES_FILE):
        os.remove(CANDIDATES_FILE)
        print("[Offset Finder] Đã reset bộ đệm ứng viên.")
        return

    pid = get_tft_pid()
    if not pid:
        print("[Offset Finder] TFTClient-Win64-Shipping.exe chưa chạy.")
        return

    h = open_process(pid)
    os.makedirs("captures", exist_ok=True)

    candidates = {}
    if os.path.exists(CANDIDATES_FILE):
        try:
            with open(CANDIDATES_FILE, "r", encoding="utf-8") as f:
                candidates = json.load(f)
        except Exception:
            candidates = {}

    offsets = {}
    if os.path.exists(OFFSETS_FILE):
        try:
            with open(OFFSETS_FILE, "r", encoding="utf-8") as f:
                offsets = json.load(f)
        except Exception:
            offsets = {}

    fields = [("gold", args.gold), ("hp", args.hp), ("level", args.level), ("stage", args.stage)]
    updated = False

    try:
        for field, val in fields:
            if val is None:
                continue

            prev = candidates.get(field, [])
            t0 = time.time()

            if not prev:
                print(f"[{field}] Quét lần 1 cho giá trị = {val}...")
                found = scan_all_int32(h, val)
                dt = time.time() - t0
                print(f"[{field}] Hoàn tất ({dt:.2f}s): tìm thấy {len(found)} địa chỉ.")
                candidates[field] = found
                updated = True
            else:
                print(f"[{field}] Lọc {len(prev)} địa chỉ cho giá trị mới = {val}...")
                found = filter_candidates(h, prev, val)
                dt = time.time() - t0
                print(f"[{field}] Hoàn tất ({dt:.3f}s): còn lại {len(found)} địa chỉ.")
                candidates[field] = found
                updated = True

            if len(candidates[field]) == 1:
                addr_hex = hex(candidates[field][0])
                offsets[f"{field}_addr"] = addr_hex
                print(f"[THÀNH CÔNG] Xác định được địa chỉ chính xác của {field}: {addr_hex}")
            elif 1 < len(candidates[field]) <= 10:
                print(f"[{field}] Các ứng viên còn lại: {[hex(a) for a in candidates[field]]}")
                offsets[f"{field}_addr"] = hex(candidates[field][0])
            elif len(candidates[field]) == 0:
                print(f"[{field}] Không còn địa chỉ nào khớp! Vui lòng kiểm tra lại giá trị hoặc dùng --reset.")

        if updated:
            with open(CANDIDATES_FILE, "w", encoding="utf-8") as f:
                json.dump(candidates, f)
            with open(OFFSETS_FILE, "w", encoding="utf-8") as f:
                json.dump(offsets, f, indent=2)
            print(f"[Offset Finder] Đã cập nhật {OFFSETS_FILE}")

    finally:
        kernel32.CloseHandle(h)

if __name__ == "__main__":
    main()
