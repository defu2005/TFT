"""Kiem tra n=400 tren ban CO item (dang ky o plan 11.27; khong dung VOD).

Tap cap: 1000 cap gan nhau (Random(7)); A co 0-2 item (Random(13)) tu item Set 18 co noi dung,
khong tinh emblem va mocs alias twin; B la ban sao cua A voi mot unit doi tuong hoac sao.
Chon: p(n=20, seed0=0) trong [0,1; 0,9]. Do: p(n=400) voi seed0=0 va 1000. Nguong 5%.
Dung:  PYTHONPATH=<goat>/src:<sim>/src python3 scripts/combat/check_adaptive_n_items.py [--workers 3]
"""
import argparse
import json
import random
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "src"))

import check_symmetry_seed as C  # noqa: E402
import fidelity as Fd  # noqa: E402
import fight as F  # noqa: E402
from tft_sim import names18 as N  # noqa: E402

N_BASE, SEED_A, SEED_B, THRESH = 20, 0, 1000, 0.05
N_FULL = 400  # ghi de bang --n-full
OUT = ROOT / "results/fixed/combat/adaptive_n_items_check.json"


def _pool(c):
    data = json.loads(N.NAMES.read_text(encoding="utf-8"))
    twin = {r["twin_tft_item"] for r in data["items"] if r.get("twin_tft_item")}
    apis = sorted({r["api"] for r in data["items"] if r["api"] not in twin
                   and r["api"] in c.items and not r["api"].startswith("DA_18_Emblem")})
    return apis


def _pairs(c, champs):
    rng, rng2 = random.Random(7), random.Random(13)
    pool = _pool(c)
    eligible = [a for a, v in champs.items() if getattr(v, "cost", None) and getattr(v, "traits", None)]
    out = []
    for _ in range(1000):
        la = rng.randint(6, 8)
        units = []
        for _ in range(la):
            units.append({"api": rng.choice(eligible), "star": rng.choice([1, 1, 1, 2]),
                          "items": rng2.sample(pool, rng2.randint(0, 2)), "pos": None})
        A = {"level": la, "augments": [], "units": units}
        i = rng.randrange(la)
        Bu = [dict(u) for u in units]
        if rng.random() < 0.5:
            Bu[i]["api"] = rng.choice([x for x in eligible if x != Bu[i]["api"]])
        else:
            Bu[i]["star"] = 2 if Bu[i]["star"] == 1 else 1
        B = {"level": la, "augments": [], "units": Bu}
        out.append((A, B))
    return out


def _init():
    F.set_content(18, Fd._C18)


def _work(args):
    idx, A, B = args
    return idx, C._p(C._rec(A, B), SEED_A, N_FULL), C._p(C._rec(A, B), SEED_B, N_FULL)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--n-full", type=int, default=400)
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()
    global N_FULL
    N_FULL = args.n_full
    out = Path(args.out)
    F.set_content(18, Fd._C18)
    c = F._CONTENT[18]
    pairs = _pairs(c, c.champions)
    mid = [i for i, (A, B) in enumerate(pairs)
           if 0.1 <= C._p(C._rec(A, B), SEED_A, N_BASE) <= 0.9]
    print("cap giu lai:", len(mid), flush=True)
    if args.n_full == 800:
        assert len(mid) == 398, len(mid)
    jobs = [(i, pairs[i][0], pairs[i][1]) for i in mid]
    res = []
    with ProcessPoolExecutor(max_workers=args.workers, initializer=_init) as ex:
        for k, r in enumerate(ex.map(_work, jobs, chunksize=4), 1):
            res.append(r)
            if k % 50 == 0:
                print(f"  {k}/{len(jobs)}", flush=True)
    flips, exact, rows, x_mid = 0, 0, [], 0
    for idx, p0, p1 in res:
        if p0 == 0.5 or p1 == 0.5:
            exact += 1
            continue
        if 0.1 <= p0 <= 0.9:
            x_mid += 1
        if (p0 > 0.5) != (p1 > 0.5):
            flips += 1
        rows.append({"pair": idx, "p_s0_n400": p0, "p_s1_n400": p1})
    rate = flips / len(mid)
    rep = {"pairs_total": 1000, "mid_at_n20_with_items": len(mid), "n_base": N_BASE, "n_full": N_FULL,
           "seeds": [SEED_A, SEED_B], "flip_count": flips, "exact_half_excluded": exact,
           "flip_rate_over_mid": round(rate, 4), "threshold": THRESH, "passed": rate <= THRESH,
           "alt_denominator_mid_at_n400": x_mid,
           "flip_rate_over_alt": round(flips / x_mid, 4) if x_mid else None, "rows": rows}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print({k: v for k, v in rep.items() if k != "rows"}, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
