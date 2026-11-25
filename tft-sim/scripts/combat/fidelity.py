"""Doi chieu do trung thuc: xac suat engine du doan vs ket qua that (muc 11.7).
Args: records.jsonl [ability=hand|generic|none] [items=1|0] [n=40] [emblems=0|1]
Quy tac:
  - Chi cham ban ghi label 'real' co result.winner khac null. Ban ghi sim bi tu choi ca file.
  - Ban ghi hong (sai schema, tuong la, winner la) bi BO QUA va dem theo ly do; khong dung ca file.
  - Ban ghi source 'dryrun-*' la du lieu thu nghiem, luon bi bo qua (khong phai ket qua that).
  - Ten item khong co trong noi dung duoc dem trong 'unknown_items' (ban ghi van cham, engine bo qua item do).
Tra ve dict co n, accuracy, brier, skipped{ly do: so}, unknown_items{ten: so}."""
import json, sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import fight as F  # noqa: E402
from fight import predict_win, set_content, check_record  # noqa: E402
from tft_sim.item_alias import build_set18_records  # noqa: E402
from tft_sim.real_content import build_real  # noqa: E402
set_content(17, build_real('TFTSet17'))
_C18 = build_set18_records()[0]
set_content(18, _C18)  # Set 18 dung noi dung da alias (xem combat-public-data.md 8b)


def read_real(path, allow_dryrun=False):
    """Doc tung dong, tra ve (ban ghi cham duoc, Counter ly do bo qua, Counter item la)."""
    good, skipped, unk = [], Counter(), Counter()
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            skipped["json_hong"] += 1
            continue
        try:
            check_record(r)
        except (ValueError, KeyError, TypeError) as e:
            skipped[f"schema:{e}"] += 1
            continue
        if r.get("label") != "real":
            raise SystemExit(f"tu choi: co ban ghi label={r.get('label')} trong file do luong")
        if str(r.get("source", "")).startswith("dryrun-") and not allow_dryrun:
            skipped["dryrun"] += 1
            continue
        if r.get("result", {}).get("winner") is None:
            skipped["winner_null"] += 1
            continue
        bad = None
        content = F._CONTENT[r["set"]]
        for side in ("a", "b"):
            for u in r[side]["units"]:
                if u["api"] not in content.champions:
                    bad = f"tuong_la:{u['api']}"
                for it in u.get("items", []):
                    if it not in content.items:
                        unk[it] += 1
        if bad:
            skipped[bad] += 1
            continue
        good.append(r)
    return good, skipped, unk


def score(path, ability=None, items=True, n=40, emblems=False, allow_dryrun=False):
    good, skipped, unk = read_real(path, allow_dryrun)
    if not good:
        return {"n": 0, "note": "chua co ban ghi real co ket qua", "skipped": dict(skipped), "unknown_items": dict(unk)}
    def mode(r):
        return ability or ("hand" if r["set"] == 17 else "generic")
    p, y, kept = [], [], 0
    for r in good:
        try:
            p.append(predict_win(r, n, mode(r), items, emblems=emblems and r["set"] == 18)["p_a"])
        except ValueError as e:
            skipped[f"predict:{str(e)[:60]}"] += 1
            continue
        y.append(1.0 if r["result"]["winner"] == 0 else 0.0)
        kept += 1
    if not kept:
        return {"n": 0, "note": "moi ban ghi real deu bi bo", "skipped": dict(skipped), "unknown_items": dict(unk)}
    p, y = np.array(p), np.array(y)
    return {"n": kept, "ability": ability or "auto(hand Set17, generic Set18)", "items": items, "emblems": emblems,
            "accuracy": round(float(np.mean((p > 0.5) == (y > 0.5))), 4),
            "brier": round(float(np.mean((p - y) ** 2)), 4),
            "skipped": dict(skipped), "unknown_items": dict(unk)}


if __name__ == "__main__":
    ab = sys.argv[2] if len(sys.argv) > 2 else None
    it = (sys.argv[3] if len(sys.argv) > 3 else "1") == "1"
    nn = int(sys.argv[4]) if len(sys.argv) > 4 else 40
    em = (sys.argv[5] if len(sys.argv) > 5 else "0") == "1"
    print(json.dumps(score(sys.argv[1], ab, it, nn, em), ensure_ascii=False, indent=1))
