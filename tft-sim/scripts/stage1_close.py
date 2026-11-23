"""Dong giai doan 1 (buoc 7 advisor): nhieu eps=0,1 DEU tren teacher v3 (doi unit, value) vs teacher v3, seed 70000-71999 (moi).
Ghi phan du, dong giai doan 1 du ket qua the nao. Ghi results/fixed/real/stage1_close_eps01.json."""
import json
from pathlib import Path
import numpy as np
from tft_sim.real_content import build_real
from tft_sim.rules import make_swap_rule
from tft_sim.tftgoat import make_env, play, summarize

env = make_env(build_real("TFTSet17"))
v3 = make_swap_rule(key="value")

def eps_v3(env_, agent, obs, mask, rng):
    if rng.random() < 0.1:
        return int(rng.choice(list(np.flatnonzero(mask))))
    return v3(env_, agent, obs, mask, rng)

lobs = [play(env, s, eps_v3, v3) for s in range(70000, 72000)]
s = summarize(lobs)
out = {"seeds": "70000-71999 (fresh)", "A": "teacher v3 + eps=0.1 uniform", "B": "teacher v3", "summary": s,
       "per_lobby_diff_A_minus_B": [float(np.mean(l.placements_a) - np.mean(l.placements_b)) for l in lobs]}
Path("results/fixed/real/stage1_close_eps01.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("RESULT", round(s["diff_A_minus_B"], 4), s["ci95_diff"], flush=True)
