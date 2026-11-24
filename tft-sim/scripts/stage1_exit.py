"""Thoat giai doan 1: nhieu eps=0.1 tren teacher moi (hybrid) vs teacher moi. Seed 40000-41999 (chua dung).
A = hybrid voi 10% hanh dong ngau nhien (hop le); B = hybrid. Am = nhieu tot hon. Ghi results/fixed/real/stage1_exit_eps01.json."""
import json
from pathlib import Path
import numpy as np
from tft_sim.real_content import build_real
from tft_sim.rules import make_rule
from tft_sim.tftgoat import make_env, play, summarize

env = make_env(build_real("TFTSet17"))
hybrid = make_rule(sell=True, floor=54, pick="hybrid")

def eps_hybrid(env_, agent, obs, mask, rng):
    if rng.random() < 0.1:
        return int(rng.choice(list(np.flatnonzero(mask))))
    return hybrid(env_, agent, obs, mask, rng)

lobs = [play(env, s, eps_hybrid, hybrid) for s in range(40000, 42000)]
s = summarize(lobs)
out = {"seeds": "40000-41999 (fresh)", "A": "hybrid + eps=0.1 uniform", "B": "hybrid", "summary": s,
       "per_lobby_diff_A_minus_B": [float(np.mean(l.placements_a) - np.mean(l.placements_b)) for l in lobs]}
Path("results/fixed/real/stage1_exit_eps01.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("RESULT", round(s["diff_A_minus_B"], 4), s["ci95_diff"], flush=True)
