"""Kiem tra do doi xung ben va do on dinh theo seed cua PRIMARY tren BAN TONG HOP (khong co du lieu that).

Muc dich: biet nhieu nen cua mo phong bao nhieu truoc khi cham diem. Day la chan doan nhieu mo phong,
KHONG phai do do chinh xac du doan.

1. Doi xung ben: voi moi cap bàn (A, B), so p_ab = P(A thang | A ben a) va p_ba = P(B thang | B ben a).
   Neu engine khong thien vi ben, p_ab + p_ba = 1. Do lech trung binh (bias) = mean(p_ab + p_ba - 1).
2. On dinh theo seed: p voi seed0=0 va seed0=1000 (cung n). Dem so lan dau cua (p - 0,5) bi doi,
   so lan p == 0,5 dung, va do lech |p_s0 - p_s1| trung binh.

Quy tac DANG KY TRUOC khi chay: neu ti le doi dau du doan (seed) > 5% o n=20 thi tang n va ghi vao
model-plan nhu thay doi cau hinh dong bang. Khong dieu chinh theo ket qua khac.

Ban tong hop: doi bang nhau tu noi dung Set 18, level 6-8, so unit = level, khong item, khong augment.
Dung:  PYTHONPATH=<goat>/src:<sim>/src python3 scripts/combat/check_symmetry_seed.py [--boards 40] [--seed 7]
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

OUT = ROOT / "results/fixed/combat/symmetry_seed_check.json"
N = 20


def _board(rng, champs, level):
    apis = list(champs)
    units = []
    for _ in range(level):
        units.append({"api": rng.choice(apis), "star": rng.choice([1, 1, 1, 2]), "items": [], "pos": None})
    return {"level": level, "augments": [], "units": units}


def _rec(a, b):
    return {"schema": "fight-v1", "set": 18, "label": "real", "source": "syn-1:3-2", "fight_key": "syn|3-2|A|B",
            "a": a, "b": b, "result": {"winner": 0}}


def _p(rec, seed0, n=None):
    return Fd._cfg_p(rec, Fd.PRIMARY, n or N, seed0)


def _close_pair(rng, eligible):
    """Cap sat nhau: B la ban sao cua A, doi mot unit sang tuong khac hoac doi sao (1 <-> 2)."""
    la = rng.randint(6, 8)
    A = _board(rng, eligible, la)
    B = {"level": A["level"], "augments": [], "units": [dict(u) for u in A["units"]]}
    i = rng.randrange(len(B["units"]))
    u = B["units"][i]
    if rng.random() < 0.5:
        u["api"] = rng.choice([x for x in eligible if x != u["api"]])
    else:
        u["star"] = 2 if u["star"] == 1 else 1
    return A, B


def close_mode(args, champs) -> dict:
    rng = random.Random(args.seed)
    eligible = [a for a, c in champs.items() if getattr(c, "cost", None) and getattr(c, "traits", None)]
    rows, flips, mid = [], 0, 0
    for _ in range(args.pairs):
        A, B = _close_pair(rng, eligible)
        p0 = _p(_rec(A, B), 0, args.n)
        p1 = _p(_rec(A, B), 1000, args.n)
        rows.append({"p_ab": p0, "p_ab_seed1000": p1})
        if 0.1 <= p0 <= 0.9:
            mid += 1
            if p0 != 0.5 and p1 != 0.5 and (p0 > 0.5) != (p1 > 0.5):
                flips += 1
    rate = flips / mid if mid else float("nan")
    return {"mode": "close", "n": args.n, "pairs": len(rows), "non_saturated": mid,
            "flip_count_non_saturated": flips, "flip_rate_non_saturated": round(rate, 4) if mid else None,
            "rule_preregistered": "flip_rate tren tap khong bao hoa > 0.05 o n=20 thi tang n va ghi vao model-plan",
            "rule_triggered": bool(mid) and rate > 0.05, "rows": rows}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["random", "close"], default="random")
    ap.add_argument("--pairs", type=int, default=1000, help="so cap sat nhau (mode close)")
    ap.add_argument("--n", type=int, default=N, help="so luot mo phong moi p (mode close)")
    ap.add_argument("--boards", type=int, default=40)
    ap.add_argument("--seed", type=int, default=7, help="seed cua generator ban, khong phai seed mo phong")
    args = ap.parse_args()
    F.set_content(18, Fd._C18)
    champs = F._CONTENT[18].champions
    if args.mode == "close":
        rep = close_mode(args, champs)
        out = ROOT / f"results/fixed/combat/symmetry_seed_close_n{args.n}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
        print({k: v for k, v in rep.items() if k != "rows"})
        print("ghi", out)
        return 0
    rng = random.Random(args.seed)

    pairs = []
    for _ in range(args.boards):
        la, lb = rng.randint(6, 8), rng.randint(6, 8)
        A, B = _board(rng, champs, la), _board(rng, champs, lb)
        pairs.append((A, B))

    sym_sum, flips, exact_half, seed_gap = [], 0, 0, []
    rows = []
    for A, B in pairs:
        p_ab = _p(_rec(A, B), 0)
        p_ba = _p(_rec(B, A), 0)
        sym_sum.append(p_ab + p_ba - 1.0)
        p_s0 = p_ab
        p_s1 = _p(_rec(A, B), 1000)
        if (p_s0 > 0.5) != (p_s1 > 0.5) and p_s0 != 0.5 and p_s1 != 0.5:
            flips += 1
        if p_s0 == 0.5 or p_s1 == 0.5:
            exact_half += 1
        seed_gap.append(abs(p_s0 - p_s1))
        rows.append({"p_ab": p_ab, "p_ba": p_ba, "p_ab_seed1000": p_s1})

    m = lambda xs: sum(xs) / len(xs) if xs else float("nan")
    rep = {
        "n": N, "boards": len(pairs), "seed0": [0, 1000],
        "symmetry_bias_mean": round(m(sym_sum), 4),
        "symmetry_abs_max": round(max(abs(x) for x in sym_sum), 4),
        "flip_count": flips, "flip_rate": round(flips / len(pairs), 4),
        "exact_half_count": exact_half,
        "seed_gap_mean": round(m(seed_gap), 4),
        "seed_gap_max": round(max(seed_gap), 4),
        "rule_preregistered": "flip_rate > 0.05 o n=20 thi tang n va ghi vao model-plan",
        "rule_triggered": flips / len(pairs) > 0.05,
        "rows": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print({k: v for k, v in rep.items() if k != "rows"})
    print("ghi", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
