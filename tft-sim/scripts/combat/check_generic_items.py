"""Do anh huong cua phan cong generic item (_GENERIC_ITEM) trong boards_of len p_a cua PRIMARY. Khong dung du lieu VOD.

Loi da xac nhan: fight.boards_of dat items=len(item_apis) trong BoardUnit, nen tft_goat.build_unit cong
_GENERIC_ITEM (+150 HP, +15 AP, +15 giap, +15 KP, ...) MOI item, cong them vao item that.
Script so sanh p_a voi boards_of hien tai (items=len) va boards_of voi items=0 (chi item that).
Dung:  PYTHONPATH=<goat>/src:<sim>/src python3 scripts/combat/check_generic_items.py [--boards 40] [--n 100]
"""
import argparse
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "src"))

import fidelity as Fd  # noqa: E402
import fight as F  # noqa: E402
from tft_goat.env.state import BoardUnit  # noqa: E402

OUT = ROOT / "results/fixed/combat/generic_items_effect.json"


def _boards_items0(record, items=True, item_alias=None):
    sides, pos, augs = [], [], []
    for k in ("a", "b"):
        units, plist = [], []
        for u in record[k]["units"]:
            its = list(u.get("items", [])) if items else []
            units.append(BoardUnit(u["api"], int(u["star"]), on_board=True, items=0, item_apis=tuple(its)))
            plist.append(u.get("pos"))
        sides.append(units)
        pos.append(plist if any(p is not None for p in plist) else None)
        augs.append(tuple(record[k].get("augments", [])))
    return sides[0], sides[1], tuple(pos), augs[0], augs[1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--boards", type=int, default=40)
    ap.add_argument("--n", type=int, default=100)
    args = ap.parse_args()
    F.set_content(18, Fd._C18)
    c = F._CONTENT[18]
    champs = [a for a, v in c.champions.items() if v.stats and v.traits]
    real_items = [a for a, v in c.items.items() if v.effects and a.startswith("TFT_Item_")]
    rng = random.Random(5)

    def side():
        return {"level": 7, "augments": [], "units": [
            {"api": rng.choice(champs), "star": 1, "items": rng.sample(real_items, rng.randint(0, 2)), "pos": None}
            for _ in range(7)]}
    deltas, cur_list = [], []
    orig = F.boards_of
    for _ in range(args.boards):
        rec = {"schema": "fight-v1", "set": 18, "label": "real", "source": "g-1:3-2", "fight_key": "g|3-2|x|y",
               "a": side(), "b": side(), "result": {"winner": 0}}
        F.boards_of = orig
        p_cur = Fd._cfg_p(rec, Fd.PRIMARY, args.n, 0)
        F.boards_of = _boards_items0
        p_0 = Fd._cfg_p(rec, Fd.PRIMARY, args.n, 0)
        F.boards_of = orig
        deltas.append(p_cur - p_0)
    mean = sum(deltas) / len(deltas)
    rep = {"boards": args.boards, "n": args.n, "mean_delta_p_current_minus_items0": round(mean, 4),
           "max_abs_delta": round(max(abs(x) for x in deltas), 4),
           "boards_changed_by_0.1_or_more": sum(abs(x) >= 0.1 for x in deltas),
           "deltas": [round(x, 4) for x in deltas]}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print({k: v for k, v in rep.items() if k != "deltas"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
