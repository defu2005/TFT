"""Kiem thu merge_check_vod.py tren fixture hai agent.

Ca sach phai qua (thoat 0). Ca loi: moi kieu duoc cai dung mot lan tren ban sao rieng.
Ca tai phan cong: thu muc da go khoi slot cu va chuyen sang slot moi -> thoat 0.
Chay:  python3 scripts/combat/selftest_merge_vod.py
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
MERGE = HERE / "merge_check_vod.py"
LOBBY1 = [f"Player{i}" for i in range(1, 9)]
LOBBY2 = [f"Other{i}" for i in range(1, 9)]


def _w(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _jl(rows) -> str:
    return "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n"


def _game(gid, lobby):
    return {"type": "game", "game_id": gid, "lobby_names": lobby}


def _fight(gid, stage, a, b):
    return {"schema": "fight-v1", "set": 18, "label": "real", "source": f"{gid}:{stage}",
            "fight_key": f"{gid}|{stage}|{a}|{b}",
            "a": {"level": 6, "augments": [], "units": [{"api": "DA_Krug18", "star": 1, "items": [], "pos": None}]},
            "b": {"level": 6, "augments": [], "units": [{"api": "DA_Krug18", "star": 1, "items": [], "pos": None}]},
            "result": {"winner": 0}}


def _handoff(vid, slot, ranges, status="done"):
    return {"schema": "vod-handoff-v1", "vod_id": vid, "slot": slot, "role": "primary", "status": status,
            "covered_ranges_s": ranges, "game_ids": [], "counts": {}, "validator": None,
            "needs_review": 0, "commit": None, "remaining": ""}


def _manifest(rows):
    return {"schema": "vod-manifest-v1", "slots": {"P1": {}, "P2": {}, "P3": {}, "V1": {}, "none": {}}, "vods": rows}


def _row(vid, slot, role):
    return {"vod_id": vid, "slot": slot, "role": role, "url": "REPLACE", "streamer": vid}


def build(root: Path, plant: str | None) -> Path:
    out = root / "out"
    p2_slot = "P3" if plant == "reassign" else "P2"  # twitch-2 sau khi tai phan cong nam o P3
    rows = [_row("twitch-1", "P1", "primary"), _row("twitch-2", p2_slot, "primary"),
            _row("twitch-1", "V1", "second_label"), _row("twitch-3", "none", "hud_processed")]
    if plant == "vod_dup":
        rows.append(_row("twitch-1", "P2", "primary"))
    if plant == "partition":
        rows.append(_row("twitch-22", "P3", "primary"))  # streamer twitch-22 ... dat rieng o P3 de sinh loi
        rows[-1]["streamer"] = "twitch-2"               # cung streamer voi twitch-2 o slot khac
    if plant == "bad_id":
        rows.append(_row("twitch-9:x", "P2", "primary"))

    d1 = out / "P1" / "twitch-1"
    fights1 = [_fight("twitch-1-g0", "3-2", "A", "B")]
    if plant == "dup_source":
        fights1.append(_fight("twitch-1-g0", "3-2", "A", "B"))
    h1 = _handoff("twitch-1", "P1", [[0, 100], [100, 200]])
    if plant == "bad_status":
        h1["status"] = "ok"  # trang thai ngoai bo tu spec
    if plant == "handoff_mismatch":
        h1["vod_id"] = "twitch-2"
    if plant == "remaining_overlap":
        h1["remaining_ranges_s"] = [[150, 300]]  # chong covered [100,200]
    if plant == "bad_range":
        h1["covered_ranges_s"] = [[200, 100]]
    _w(d1 / "handoff.json", json.dumps(h1))
    g1 = _game("twitch-1-g0", LOBBY1)
    if plant == "bad_source_url":
        g1["vod_url"] = "https://kick.com/videos/1"
    if plant == "short_lobby":
        g1["lobby_names"] = LOBBY1[:7]
    if plant == "lobby_over8":
        g1["lobby_names"] = LOBBY1 + ["Extra9"]
    if plant == "placeholder":
        g1["lobby_names"] = ["unknown_1_0"] + LOBBY1[1:]
    if plant == "bad_game_id":
        g1["game_id"] = "twitch-9-g0"  # sai vod_id
        fights1 = [_fight("twitch-1-g0", "3-2", "A", "B")]
    _w(d1 / "games.jsonl", _jl([g1]))
    _w(d1 / "fights.jsonl", _jl(fights1))

    d2 = out / p2_slot / "twitch-2"
    _w(d2 / "handoff.json", json.dumps(_handoff("twitch-2", p2_slot, [[0, 300]])))
    games2 = [_game("twitch-2-g0", LOBBY2)]
    if plant == "no_fights":
        games2.append(_game("twitch-2-g9", LOBBY2))  # khong co fight nao
    _w(d2 / "games.jsonl", _jl(games2))
    _w(d2 / "fights.jsonl", _jl([_fight("twitch-2-g0", "1-1", "C", "D")]))

    if plant in ("dup_fight_key", "lobby_case", "lobby_partial"):
        if plant == "lobby_case":
            lob = [LOBBY1[0].upper() + " "] + LOBBY1[1:]     # khac hoa/thuong va khoang trang
        elif plant == "lobby_partial":
            lob = LOBBY1[:6] + LOBBY2[:2]                    # chung 6 ten
        else:
            lob = LOBBY1
        dd = out / "P2" / "twitch-22"
        rows.append(_row("twitch-22", "P2", "primary"))
        _w(dd / "handoff.json", json.dumps(_handoff("twitch-22", "P2", [[0, 50]])))
        _w(dd / "games.jsonl", _jl([_game("twitch-22-g0", lob)]))
        _w(dd / "fights.jsonl", _jl([_fight("twitch-22-g0", "3-2", "A", "B")]))
    if plant == "overlap":
        # thu muc cu cua twitch-1 chua duoc go khoi P2, khoang chong voi P1
        ds = out / "P2" / "twitch-1"
        _w(ds / "handoff.json", json.dumps(_handoff("twitch-1", "P2", [[50, 150]], status="stale")))
    (root / "manifest.json").write_text(json.dumps(_manifest(rows)), encoding="utf-8")
    return root


def run(root: Path) -> tuple[int, str]:
    p = subprocess.run([sys.executable, str(MERGE), str(root / "manifest.json"), str(root / "out")],
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


# (ten, kieu loi cai vao, ma phai xuat hien, thoat mong doi: 0 hoac 1)
CASES = [
    ("sach", None, None, 0),
    ("tai_phan_cong", "reassign", None, 0),
    ("vod_dup", "vod_dup", "vod_primary_duplicate", 1),
    ("streamer_nhieu_slot", "partition", "streamer_multi_slot", 1),
    ("overlap", "overlap", "overlap_across_slots", 1),
    ("dup_source", "dup_source", "duplicate_source", 1),
    ("lobby_ban_trung", "dup_fight_key", "shared_lobby_needs_ingest", 0),
    ("lobby_hoa_thuong", "lobby_case", "shared_lobby_needs_ingest", 0),
    ("lobby_chung_6", "lobby_partial", "lobby_partial_overlap", 0),
    ("game_id_sai_vod", "bad_game_id", "bad_game_id", 1),
    ("handoff_lech_vod", "handoff_mismatch", "handoff_mismatch", 1),
    ("khoang_sai", "bad_range", "bad_range", 1),
    ("bad_id", "bad_id", "bad_id", 1),
    ("nguon_khac", "bad_source_url", "bad_source_url", 1),
    ("lobby_thieu_7_ten", "short_lobby", "incomplete_lobby", 0),
    ("lobby_qua_8_ten", "lobby_over8", "bad_lobby", 1),
    ("placeholder_ten", "placeholder", "placeholder_name", 1),
    ("game_khong_fight", "no_fights", "game_without_fights", 1),
    ("remaining_chong_covered", "remaining_overlap", "covered_remaining_overlap", 1),
    ("trang_thai_ngoai_spec", "bad_status", "bad_status", 1),
]


def main() -> int:
    ok = True
    base = Path(tempfile.mkdtemp(prefix="merge_vod_"))
    try:
        for name, plant, want, want_code in CASES:
            root = base / name
            build(root, plant)
            code, text = run(root)
            passed = code == want_code and (want is None or want in text)
            ok &= passed
            print(f"{'PASS' if passed else 'FAIL'} {name}: thoat={code} (mong doi {want_code}), "
                  f"ma={want or 'khong loi'}")
            if not passed:
                print(text)
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print("SELFTEST MERGE", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
