#!/usr/bin/env python3
"""
TFT Watch & Capture Monitor
Tự động giám sát liên tục:
1. Trạng thái Log: Matchmaking -> Game Found -> Loading -> In Match (Round/Phase).
2. Tầng Network: Quét socket UDP Iris NetDriver kết nối tới Game Server.
3. Tầng RAM: Mở handle bộ nhớ của tiến trình TFTClient-Win64-Shipping.exe ngay khi vào trận.
"""

import os
import sys
import time
import json
import socket
import psutil
import struct
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone

kernel32 = ctypes.windll.kernel32
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010

LOG_PATH = os.path.expandvars(r'%LOCALAPPDATA%\TFT\Saved\Logs\TFT.log')
EVENTS_OUT = r'captures\live-captured-events.jsonl'
os.makedirs('captures', exist_ok=True)

def find_tft_proc():
    for p in psutil.process_iter(['pid', 'name']):
        if 'tftclient-win64-shipping' in (p.info['name'] or '').lower():
            return p
    return None

def check_udp_connection(proc):
    try:
        conns = proc.net_connections(kind='udp')
        for c in conns:
            if c.raddr:
                return f"{c.raddr.ip}:{c.raddr.port}"
            elif c.laddr and c.laddr.port != 0:
                return f"Bound UDP port {c.laddr.port}"
    except Exception:
        pass
    return None

def main():
    print("=" * 65)
    print("TFT AUTO WATCH & CAPTURE - MONITORING STARTED")
    print(f"Target log: {LOG_PATH}")
    print(f"Events out: {EVENTS_OUT}")
    print("=" * 65)

    last_size = 0
    if os.path.exists(LOG_PATH):
        last_size = os.path.getsize(LOG_PATH)
        # Bắt đầu đọc từ 100KB trước đuôi file để không lỡ các sự kiện vừa diễn ra
        last_size = max(0, last_size - 100 * 1024)

    tft_proc = None
    last_phase = None
    connected_server = None
    match_active = False

    while True:
        # 1. Kiểm tra tiến trình TFT
        if not tft_proc or not tft_proc.is_running():
            tft_proc = find_tft_proc()
            if tft_proc:
                print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] Phát hiện TFT Client PID {tft_proc.pid}")

        # 2. Đọc log mới
        if os.path.exists(LOG_PATH):
            curr_size = os.path.getsize(LOG_PATH)
            if curr_size > last_size:
                with open(LOG_PATH, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(last_size)
                    new_text = f.read()
                    last_size = curr_size

                for line in new_text.splitlines():
                    # Matchmaking & Game Flow
                    if "Entered matchmaking" in line:
                        print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] [LOBBY] Đang tìm trận...")
                    elif "MatchmakerMatchFound" in line or "MatchFound" in line:
                        print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] [MATCH] >>> TÌM THẤY TRẬN ĐẤU! <<<")
                    elif "Browse: " in line and "/Mode_Bootstrap" in line:
                        print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] [NETWORK] Kết nối Game Server: {line.strip()}")
                        with open(EVENTS_OUT, 'a', encoding='utf-8') as ef:
                            ef.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), "kind": "network_connect", "raw": line.strip()}) + "\n")
                    elif "Welcomed by server" in line:
                        print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] [NETWORK] Handshake Game Server thành công!")
                        match_active = True
                    elif "ETFTPhaseType::" in line:
                        phase = line.split("ETFTPhaseType::")[1].split()[0]
                        if phase != last_phase:
                            last_phase = phase
                            print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] [PHASE] Chuyển Phase: {phase}")
                            with open(EVENTS_OUT, 'a', encoding='utf-8') as ef:
                                ef.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), "kind": "phase", "phase": phase}) + "\n")
                    elif "Trigger[Audio.Event.VO.Unit.Purchase" in line:
                        print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] [GAMEPLAY] Mua tướng: {line.strip()[-50:]}")
                    elif "TFTRoundSubsystem:" in line:
                        print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] [ROUND] {line.strip()}")
                    elif "Augment choice lifecycle" in line:
                        print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] [AUGMENT] Sự kiện Lõi Nâng Cấp")

        # 3. Kiểm tra tầng Network UDP nếu có tiến trình
        if tft_proc and not connected_server:
            udp_addr = check_udp_connection(tft_proc)
            if udp_addr:
                connected_server = udp_addr
                print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] [UDP SOCKET] Server Endpoint: {udp_addr}")

        # In nhịp quan sát mỗi 5 giây nếu đang tìm trận
        time.sleep(1)

if __name__ == "__main__":
    main()
