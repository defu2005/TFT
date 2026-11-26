"""Test guong: A dau voi chinh A (cung doi, dat o ca hai ben), PRIMARY, n = 400. Khong dung du lieu VOD.

Dang ky truoc: |p_a - 0,5| > 0,01 la co thien vi. Nhung p_a = thang_a / n (hoa khong tinh cho ben nao),
nen hoa keo p_a xuong duoi 0,5 ngay ca khi hai ben doi xung. Vi vay bao ca:
  - thien vi ben: (thang_a - thang_b) / n, trung binh tren cac ban;
  - ti le hoa, va p_a neu hoa tinh 0,5 diem (quy uoc cua fidelity.credit).
Dung:  PYTHONPATH=<goat>/src:<sim>/src python3 scripts/combat/check_mirror.py
"""
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "src"))

import check_symmetry_seed as C  # noqa: E402
import fidelity as Fd  # noqa: E402
import fight as F  # noqa: E402

N, BOARDS, OUT = 400, 50, ROOT / "results/fixed/combat/mirror_check.json"


def main() -> int:
    F.set_content(18, Fd._C18)
    champs = F._CONTENT[18].champions
    rng = random.Random(11)
    eligible = [a for a, c in champs.items() if getattr(c, "cost", None) and getattr(c, "traits", None)]
    rows = []
    for _ in range(BOARDS):
        A = C._board(rng, eligible, rng.randint(6, 8))
        rec = C._rec(A, {"level": A["level"], "augments": [], "units": [dict(u) for u in A["units"]]})
        r = F.predict_win(rec, N, "generic", True, 0, True, True, False, False, False, False)
        a, b, d = r["a"], r["b"], r["draw"]
        rows.append({"a": a, "b": b, "draw": d, "p_a": r["p_a"]})
    m = lambda k: sum(x[k] for x in rows) / len(rows)
    bias = [(x["a"] - x["b"]) / N for x in rows]
    p_half = [(x["a"] + x["draw"] / 2) / N for x in rows]
    rep = {"n": N, "boards": BOARDS,
           "side_bias_mean": round(sum(bias) / len(bias), 5),
           "side_bias_se": round((sum((v - sum(bias) / len(bias)) ** 2 for v in bias) / (len(bias) - 1)) ** 0.5 / len(bias) ** 0.5, 5),
           "p_a_mean": round(m("p_a") if False else sum(x["a"] / N for x in rows) / len(rows), 5),
           "draw_rate_mean": round(sum(x["draw"] for x in rows) / (N * len(rows)), 5),
           "p_a_with_draw_half_mean": round(sum(p_half) / len(p_half), 5),
           "threshold_registered": 0.01,
           "flag_side_bias": abs(sum(bias) / len(bias)) > 0.01,
           "rows": rows}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print({k: v for k, v in rep.items() if k != "rows"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
