"""Kiem tra n thich ung tren 1000 cap gan nhau (chi chay MOT lan, dang ky truoc). Khong dung du lieu VOD.

Quy tac dang ky truoc (khong doi sau khi chay):
  1. Tap cap: 1000 cap cua check_symmetry_seed.py --mode close --seed 7 (tai tao, kiem tra khop voi file n=20).
  2. Buoc 20 luot: giu cap co 0,1 <= p <= 0,9 (seed0 = 0). Mau so = so cap nay (319).
  3. Buoc 400 luot: voi moi cap giu lai, p_s0 = P(seed0=0, n=400), p_s1 = P(seed0=1000, n=400).
     Dem dao chieu: p_s0 va p_s1 khac phia 0,5, ca hai khac 0,5 chinh xac.
  4. Qua neu ti le dao <= 5%. Khong qua thi bao con so va dung, khong do them.

Dung:  PYTHONPATH=<goat>/src:<sim>/src python3 scripts/combat/check_adaptive_n.py [--workers 3]
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

N_BASE, N_FULL, SEED_A, SEED_B = 20, 400, 0, 1000
THRESH = 0.05
PAIRS_FILE = ROOT / "results/fixed/combat/symmetry_seed_close_n20.json"
OUT = ROOT / "results/fixed/combat/adaptive_n_check.json"


def _pairs():
    F.set_content(18, Fd._C18)
    champs = F._CONTENT[18].champions
    rng = random.Random(7)
    eligible = [a for a, c in champs.items() if getattr(c, "cost", None) and getattr(c, "traits", None)]
    return [C._close_pair(rng, eligible) for _ in range(1000)]


def _work(args):
    idx, A, B = args
    p_s0 = C._p(C._rec(A, B), SEED_A, N_FULL)
    p_s1 = C._p(C._rec(A, B), SEED_B, N_FULL)
    return idx, p_s0, p_s1


def _init():
    F.set_content(18, Fd._C18)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args()
    stored = json.loads(PAIRS_FILE.read_text(encoding="utf-8"))["rows"]
    pairs = _pairs()
    # Kiem tra tai tao: p o n=20 phai khop file da luu (cap dau).
    mism = 0
    mid_idx = []
    for i, (A, B) in enumerate(pairs):
        p20 = C._p(C._rec(A, B), SEED_A, N_BASE) if i < 5 else stored[i]["p_ab"]
        if abs(p20 - stored[i]["p_ab"]) > 1e-9:
            mism += 1
        if 0.1 <= stored[i]["p_ab"] <= 0.9:
            mid_idx.append(i)
    if mism:
        raise SystemExit(f"tai tao cap khong khop: {mism}")
    print("cap giu lai (0,1 <= p20 <= 0,9):", len(mid_idx), flush=True)
    jobs = [(i, pairs[i][0], pairs[i][1]) for i in mid_idx]
    res = []
    with ProcessPoolExecutor(max_workers=args.workers, initializer=_init) as ex:
        for k, r in enumerate(ex.map(_work, jobs, chunksize=4), 1):
            res.append(r)
            if k % 50 == 0:
                print(f"  {k}/{len(jobs)}", flush=True)
    flips, exact = 0, 0
    rows = []
    for idx, p0, p1 in res:
        if p0 == 0.5 or p1 == 0.5:
            exact += 1
            continue
        if (p0 > 0.5) != (p1 > 0.5):
            flips += 1
        rows.append({"pair": idx, "p_s0_n400": p0, "p_s1_n400": p1})
    denom = len(mid_idx)
    rate = flips / denom
    passed = rate <= THRESH
    rep = {"pairs_total": 1000, "mid_at_n20": denom, "n_base": N_BASE, "n_full": N_FULL,
           "seeds": [SEED_A, SEED_B], "flip_count": flips, "exact_half_excluded": exact,
           "flip_rate_over_mid": round(rate, 4), "threshold": THRESH, "passed": passed,
           "rows": rows}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print({k: v for k, v in rep.items() if k != "rows"}, flush=True)
    print("ghi", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
