"""Kiem thu ingest_vod.py tren fixture: hai VOD cung mot lobby + mot lobby khac.

Ky vong:
  - 3 fight vao (lobby1: 3-2 AB trung o hai VOD, 2-1 CD; lobby2: 1-1 GH) -> 3 fight ra, 1 fight_extra.
  - 3 cum game raw (moi game_id mot cum) -> 2 cum sau khi khu trung theo lobby_id.
  - Ket qua qua validate_vod.py (thoat 0).
  - Ca gop co loi (dup_source) -> ingest tu choi.
Chay:  python3 scripts/combat/selftest_ingest_vod.py   (can tft_goat va tft_sim trong PYTHONPATH)
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ingest_vod  # noqa: E402

L1 = [f"Player{i}" for i in range(1, 9)]
L2 = [f"Other{i}" for i in range(1, 9)]


def _w(p: Path, rows) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")


def _game(gid, lobby):
    return {"type": "game", "game_id": gid, "lobby_names": lobby}


def _fight(gid, stage, a, b):
    unit = [{"api": "DA_Krug18", "star": 1, "items": [], "pos": None}]
    return {"schema": "fight-v1", "set": 18, "label": "real", "source": f"{gid}:{stage}",
            "fight_key": f"{gid}|{stage}|{a}|{b}",
            "a": {"level": 6, "augments": [], "units": unit}, "b": {"level": 6, "augments": [], "units": unit},
            "result": {"winner": 0}}


def _handoff(vid, slot, ranges):
    return {"schema": "vod-handoff-v1", "vod_id": vid, "slot": slot, "role": "primary", "status": "done",
            "covered_ranges_s": ranges, "remaining_ranges_s": [], "game_ids": [], "counts": {},
            "validator": None, "needs_review": 0, "commit": None, "remaining": ""}


def build(root: Path, dup_source=False, short=False) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    out = root / "out"
    rows = [{"vod_id": "twitch-1", "slot": "P1", "role": "primary", "streamer": "twitch-1", "url": "x"},
            {"vod_id": "twitch-22", "slot": "P2", "role": "primary", "streamer": "twitch-22", "url": "x"},
            {"vod_id": "twitch-2", "slot": "P3", "role": "primary", "streamer": "twitch-2", "url": "x"}]
    man = root / "manifest.json"
    man.write_text(json.dumps({"schema": "vod-manifest-v1",
                               "slots": {"P1": {}, "P2": {}, "P3": {}, "V1": {}, "none": {}}, "vods": rows}),
                   encoding="utf-8")
    d1 = out / "P1" / "twitch-1"
    f1 = [_fight("twitch-1-g0", "3-2", "A", "B"), _fight("twitch-1-g0", "2-1", "C", "D")]
    if dup_source:
        f1.append(_fight("twitch-1-g0", "3-2", "A", "B"))
    _w(d1 / "games.jsonl", [_game("twitch-1-g0", L1)])
    _w(d1 / "fights.jsonl", f1)
    (d1 / "handoff.json").write_text(json.dumps(_handoff("twitch-1", "P1", [[0, 900]])), encoding="utf-8")
    d2 = out / "P2" / "twitch-22"
    _w(d2 / "games.jsonl", [_game("twitch-22-g0", ["  PLAYER1 "] + L1[1:])])  # ten lobby khac hoa/thuong, khoang trang
    _w(d2 / "fights.jsonl", [_fight("twitch-22-g0", "3-2", "A", "B")])
    (d2 / "handoff.json").write_text(json.dumps(_handoff("twitch-22", "P2", [[0, 900]])), encoding="utf-8")
    d3 = out / "P3" / "twitch-2"
    _w(d3 / "games.jsonl", [_game("twitch-2-g0", L2[:7] if short else L2)])
    _w(d3 / "fights.jsonl", [_fight("twitch-2-g0", "1-1", "G", "H")])
    (d3 / "handoff.json").write_text(json.dumps(_handoff("twitch-2", "P3", [[0, 900]])), encoding="utf-8")
    return root


def main() -> int:
    ok = True
    base = Path(tempfile.mkdtemp(prefix="ingest_vod_"))
    try:
        root = build(base / "ok")
        dest = base / "ok_dest"
        rep = ingest_vod.ingest(root / "manifest.json", root / "out", dest)
        fights = [json.loads(l) for l in (dest / "fights.jsonl").read_text(encoding="utf-8").splitlines()]
        extra = [json.loads(l) for l in (dest / "fight_extra.jsonl").read_text(encoding="utf-8").splitlines() if l]
        clusters = {f["source"].split(":")[0] for f in fights}
        raw_clusters = {"twitch-1-g0", "twitch-22-g0", "twitch-2-g0"}
        c1 = len(fights) == 3 and len(extra) == 1 and len(clusters) == 2
        print(f"{'PASS' if c1 else 'FAIL'} khu trung: fight={len(fights)} (3), extra={len(extra)} (1), "
              f"cum={len(clusters)} (2); cum raw={len(raw_clusters)} (3)")
        ok &= c1
        v = subprocess.run([sys.executable, str(HERE / "validate_vod.py"), str(dest / "fights.jsonl")],
                           capture_output=True, text=True)
        c2 = v.returncode == 0
        print(f"{'PASS' if c2 else 'FAIL'} validate_vod tren dau ra: thoat={v.returncode}")
        if not c2:
            print(v.stdout + v.stderr)
        ok &= c2
        sh = build(base / "short", short=True)
        rs = ingest_vod.ingest(sh / "manifest.json", sh / "out", base / "short_dest")
        c4 = rs["held_incomplete"] == 1 and rs["fights_out"] == 2
        print(f"{'PASS' if c4 else 'FAIL'} lobby 7 ten: giu lai 1 fight, dau ra 2 (held={rs['held_incomplete']}, out={rs['fights_out']})")
        ok &= c4
        bad = build(base / "bad", dup_source=True)
        try:
            ingest_vod.ingest(bad / "manifest.json", bad / "out", base / "bad_dest")
            c3 = False
        except SystemExit as e:
            c3 = "tu choi" in str(e)
        print(f"{'PASS' if c3 else 'FAIL'} ca gop co loi bi tu choi")
        ok &= c3
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print("SELFTEST INGEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
