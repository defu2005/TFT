"""Quet 252 augment DA_* cua Set 18 tren cung mot ban, PRIMARY, cung seed. Khong dung du lieu VOD.

Voi moi augment: dat augment do cho ben a, so p_a voi augment va khong augment (cung ban, cung seed, n = 100).
Augment lam doi ket qua neu p_a khac nhau. Phan loai mo ta la heuristic theo tu khoa, chi de doc.
Dung:  PYTHONPATH=<goat>/src:<sim>/src python3 scripts/combat/check_augment_sweep.py [--n 100]
"""
import argparse
import gzip
import json
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "src"))

import fidelity as Fd  # noqa: E402
import fight as F  # noqa: E402

OUT = ROOT / "results/fixed/combat/augment_sweep.json"
COND = re.compile(r"\b(if|when|whenever|after|each|every|per|once|first|lowest|highest|in combat|Round)\b", re.I)
ECON = re.compile(r"\b(gold|xp|shop|reroll|income|interest|loot|orb|item component|component|pick)\b", re.I)
COMBAT = re.compile(r"\b(combat start|attack|damage|health|armor|magic resist|ability power|attack speed|durability|shield|heal)\b", re.I)


def _descs(content):
    """Mo ta lay tu noi dung engine (real_content), khong tu snapshot."""
    return {k: re.sub(r"<[^>]+>", " ", (a.desc or "")) for k, a in content.augments.items()}


def _category(desc: str) -> str:
    if COND.search(desc):
        return "co_dieu_kien"
    if ECON.search(desc) and not COMBAT.search(desc):
        return "kinh_te"
    if COMBAT.search(desc):
        return "chi_so_bat_dau_combat"
    return "khac"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=100)
    args = ap.parse_args()
    F.set_content(18, Fd._C18)
    c = F._CONTENT[18]
    champs = [a for a, v in c.champions.items() if v.stats and v.traits]
    rng = random.Random(3)
    base = None
    for attempt in range(40):  # chon ban can bang: p ban dau trong [0,3; 0,7], neu khong augment khong the doi ket qua
        side_a = {"level": 7, "augments": [], "units": [{"api": rng.choice(champs), "star": 1, "items": [], "pos": None} for _ in range(7)]}
        side_b = {"level": 7, "augments": [], "units": [{"api": rng.choice(champs), "star": 1, "items": [], "pos": None} for _ in range(7)]}
        cand = {"schema": "fight-v1", "set": 18, "label": "real", "source": "g-1:3-2", "fight_key": "g|3-2|x|y",
                "a": side_a, "b": side_b, "result": {"winner": 0}}
        pc = Fd._cfg_p(cand, Fd.PRIMARY, args.n, 0)
        if 0.3 <= pc <= 0.7:
            base, p0 = cand, pc
            break
    if base is None:
        raise SystemExit("khong tim duoc ban can bang trong 40 lan thu")
    descs = _descs(c)
    augs = sorted(k for k in c.augments if k.startswith("DA_"))
    rows = []
    for k in augs:
        rec = json.loads(json.dumps(base))
        rec["a"]["augments"] = [k]
        p = Fd._cfg_p(rec, Fd.PRIMARY, args.n, 0)
        desc = descs.get(k, "")
        rows.append({"augment": k, "p_a": p, "delta": round(p - p0, 4), "changed": p != p0,
                     "category_heuristic": _category(desc), "desc": desc[:160]})
    changed = [r for r in rows if r["changed"]]
    rep = {"n": args.n, "board_seed_rng": 3, "attempts": attempt + 1, "p_a_no_augment": p0, "augments": len(rows),
           "changed_count": len(changed), "changed": [r["augment"] for r in changed],
           "rows": rows}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print({k: v for k, v in rep.items() if k not in ("rows", "changed")})
    print("augment lam doi p_a:", rep["changed"][:20])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
