#!/usr/bin/env python3
"""
TFT Network Probe
Theo dõi và phân tích lưu lượng mạng của TFT Client (TFTClient-Win64-Shipping.exe)
và Riot Client Services.

Tầng mạng của TFT Standalone (Unreal Engine):
1. Game Server Socket: UDP thông qua Unreal Engine Iris Replication (GameNetDriver / RGINetDriver).
2. Chat / XMPP: TCP port 5223 (TLS) tới sa3.chat.si.riotgames.com.
3. Riot Client Services API: Localhost HTTPS với xác thực Basic auth từ lockfile.
"""

import os
import sys
import time
import json
import psutil
import socket
from datetime import datetime, timezone

def get_riot_lockfile():
    localappdata = os.environ.get("LOCALAPPDATA", "")
    lockfile_path = os.path.join(localappdata, "Riot Games", "Riot Client", "Config", "lockfile")
    if os.path.exists(lockfile_path):
        try:
            with open(lockfile_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                parts = content.split(":")
                if len(parts) >= 5:
                    return {
                        "name": parts[0],
                        "pid": int(parts[1]),
                        "port": int(parts[2]),
                        "token": parts[3],
                        "protocol": parts[4]
                    }
        except Exception as e:
            print(f"[Network Probe] Không đọc được lockfile: {e}", file=sys.stderr)
    return None

def find_tft_processes():
    tft_procs = []
    for p in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
        try:
            name = (p.info['name'] or '').lower()
            if 'tft' in name or 'riotclient' in name:
                tft_procs.append(p)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return tft_procs

def probe_connections():
    procs = find_tft_processes()
    if not procs:
        print("[Network Probe] Không tìm thấy tiến trình TFT hoặc Riot Client đang chạy.")
        return []

    conn_records = []
    now = datetime.now(timezone.utc).isoformat()

    for p in procs:
        try:
            conns = p.net_connections(kind='all')
            for c in conns:
                rec = {
                    "ts": now,
                    "pid": p.pid,
                    "process": p.name(),
                    "type": "TCP" if c.type == socket.SOCK_STREAM else "UDP",
                    "status": c.status,
                    "local": f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else None,
                    "remote": f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else None,
                }
                # Phân loại luồng kết nối
                if rec["type"] == "UDP":
                    rec["role"] = "Game Iris NetDriver (Unreal Engine Replication UDP)"
                elif rec["remote"] and ":5223" in rec["remote"]:
                    rec["role"] = "Riot Chat / XMPP Gateway (TLS)"
                elif rec["remote"] and ":443" in rec["remote"]:
                    rec["role"] = "Riot Web / Telemetry / Store API (HTTPS)"
                elif rec["local"] and ("127.0.0.1" in rec["local"] or "0.0.0.0" in rec["local"]):
                    rec["role"] = "Local Client RPC / Listener"
                else:
                    rec["role"] = "Khác"
                conn_records.append(rec)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return conn_records

def main():
    print("=" * 60)
    print("TFT COACH - NETWORK PROBE & ANALYZER")
    print("=" * 60)

    lockfile = get_riot_lockfile()
    if lockfile:
        print(f"[Riot Client API] Port: {lockfile['port']} | PID: {lockfile['pid']} | Protocol: {lockfile['protocol']}")
    else:
        print("[Riot Client API] Lockfile chưa sẵn sàng hoặc client tắt.")

    print("\n[Đang quét kết nối mạng hiện tại...]")
    records = probe_connections()
    if not records:
        print("Chưa có kết nối nào được tạo.")
        return

    print(f"\nTìm thấy {len(records)} socket đang hoạt động:")
    print(f"{'PID':<8} {'Tiến trình':<28} {'Giao thức':<6} {'Remote Address':<24} {'Vai trò'}")
    print("-" * 90)
    for r in records:
        remote_str = r['remote'] or "(listening)"
        print(f"{r['pid']:<8} {r['process']:<28} {r['type']:<6} {remote_str:<24} {r['role']}")

if __name__ == "__main__":
    main()
