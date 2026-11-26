"""Sản lượng dùng được để chấm điểm, theo từng slot (chỉ đọc).

Một fight được tính là DÙNG ĐƯỢC khi đủ cả bốn điều kiện:
  1. winner đã biết (0 hoặc 1);
  2. cả hai bên có ít nhất một unit với api đã phân giải được trong nội dung Set 18;
  3. cả hai tên người chơi trong fight_key là tên thật (không unk_/unknown_);
  4. mọi khung hình được tham chiếu đều tồn tại trong thư mục VOD.
Một ván (game) dùng được khi có ít nhất một fight dùng được.

Đầu ra: bảng theo slot + JSON. So sánh với mục tiêu 137 ván (±0,10) và 545 ván (±0,05).

Dùng:  PYTHONPATH=<goat>/src:<sim>/src python3 scripts/combat/scoreable_yield.py
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT_ROOT = ROOT / "data/vod_out/20261125"
OUT = ROOT / "results/fixed/combat/scoreable_yield.json"
PH = re.compile(r"(unknown_|unk_)", re.I)
TARGET_GAMES = {"h010": 137, "h005": 545}


def _jsonl(p: Path):
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def main() -> int:
    sys.path.insert(0, str(HERE))
    sys.path.insert(0, str(ROOT / "src"))
    import fight as F
    from tft_sim.real_content import build_real
    F.set_content(18, build_real("TFTSet18"))
    champs = F._CONTENT[18].champions

    per = defaultdict(Counter)
    usable_games = defaultdict(set)
    reasons = defaultdict(Counter)
    for slot_dir in sorted(p for p in OUT_ROOT.iterdir() if p.is_dir() and p.name != "none"):
        slot = slot_dir.name
        C = per[slot]
        for vdir in sorted(p for p in slot_dir.iterdir() if p.is_dir()):
            vod = vdir.name
            games = {g["game_id"] for g in _jsonl(vdir / "games.jsonl")}
            C["games"] += len(games)
            for f in _jsonl(vdir / "fights.jsonl"):
                C["fights"] += 1
                gid = str(f.get("source", "")).split(":")[0]
                why = None
                w = (f.get("result") or {}).get("winner")
                pair = str(f.get("fight_key", "")).split("|")[-2:]
                if w not in (0, 1):
                    why = "winner_null"
                elif PH.search("|".join(pair)):
                    why = "nombre_placeholder"
                else:
                    for side in ("a", "b"):
                        units = (f.get(side) or {}).get("units", [])
                        if not any(u.get("api") in champs for u in units):
                            why = f"board_{side}_khong_phan_giai"
                            break
                if why is None:
                    for side in ("a", "b"):
                        for u in (f.get(side) or {}).get("units", []):
                            for fr in u.get("frames", []) or []:
                                if not (vdir / fr).exists():
                                    why = "frame_thieu"
                if why is None:
                    C["usable_fights"] += 1
                    usable_games[slot].add((vod, gid))
                else:
                    reasons[slot][why] += 1
            C["_games_seen"] = C.get("_games_seen", 0)
        C["usable_games"] = len(usable_games[slot])
    report = {}
    for slot, C in sorted(per.items()):
        d = {k: v for k, v in C.items() if not k.startswith("_")}
        d["reject_reasons"] = dict(reasons[slot])
        report[slot] = d
    total_usable = sum(d.get("usable_games", 0) for d in report.values())
    summary = {"usable_games_total": total_usable,
               "targets": {"h010_games": TARGET_GAMES["h010"], "h005_games": TARGET_GAMES["h005"]},
               "slots": report}
    print(f"{'slot':<5} {'ván':>5} {'fight':>6} {'dùng được':>9} {'ván dùng được':>13}")
    for slot, d in report.items():
        print(f"{slot:<5} {d['games']:>5} {d['fights']:>6} {d.get('usable_fights',0):>9} {d.get('usable_games',0):>13}")
    print(f"tổng ván dùng được: {total_usable} / mục tiêu 137 (±0,10) và 545 (±0,05)")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"ghi {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
