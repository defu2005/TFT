"""Giai doan 3: CEM tren tham so theta cua v3 (xem tft_sim/params.py). Moi ung vien so voi v3 tren cung seed.
Seed dev moi 100000-100399 (ghep cap). Ghi results/fixed/real/cem_stage3.json."""
import json, sys
from pathlib import Path
import numpy as np
from tft_sim.params import Theta, make_param_policy
from tft_sim.real_content import build_real
from tft_sim.rules import make_swap_rule
from tft_sim.tftgoat import make_env, play

N_LOBBY = int(sys.argv[1]) if len(sys.argv) > 1 else 400
GENS = int(sys.argv[2]) if len(sys.argv) > 2 else 4
POP = int(sys.argv[3]) if len(sys.argv) > 3 else 12
import multiprocessing as mp
SEEDS = range(100000, 100000 + N_LOBBY)
_env = None; _v3 = None


def _init():
    global _env, _v3
    _env = make_env(build_real("TFTSet17")); _v3 = make_swap_rule(key="value")


def _eval(vec):
    th = Theta.from_vec(np.clip(vec, [0, 0, 0, 0], [120, 120, 15, 5]))
    pol = make_param_policy(th)
    diffs = []
    for s in SEEDS:
        lob = play(_env, s, pol, _v3)
        diffs.append(np.mean(lob.placements_a) - np.mean(lob.placements_b))
    return float(np.mean(diffs)), tuple(th.__dict__.values()), np.array(diffs)
def main():
    rng = np.random.default_rng(0)
    mu = np.array([54, 54, 5, 1], float); sig = np.array([20, 20, 3, 1.5])
    hist = []
    best = None
    for g in range(GENS):
        cands = [mu + sig * rng.standard_normal(4) for _ in range(POP)]
        cands[0] = mu.copy()  # giu v3 lam moc
        with mp.Pool(4, initializer=_init) as pool:
            res = pool.map(_eval, cands)
        res.sort(key=lambda r: r[0])
        elite = [np.array(r[1], float) for r in res[: max(2, POP // 4)]]
        mu = np.mean(elite, axis=0); sig = np.std(elite, axis=0) + 1e-3
        best = res[0]
        hist.append({"gen": g, "best_theta": best[1], "best_diff": best[0], "mean_diff_pop": float(np.mean([r[0] for r in res]))})
        print("gen", g, "best", best[1], round(best[0], 4), flush=True)
    out = {"seeds": f"100000-{100000 + N_LOBBY - 1} (dev)", "history": hist, "best_theta": best[1], "best_diff": best[0]}
    Path("results/fixed/real/cem_stage3.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("CEMDONE", flush=True)


if __name__ == "__main__":
    main()
