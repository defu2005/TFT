"""Sang nhieu theo loai tren teacher v4, EngineResolver. Voi xac suat 0.1, chon deu mot hanh dong hop le
loai do (neu co), nguoc lai v4. A = v4 + nhieu loai T, B = v4. Am = nhieu tot hon.
Args: TYPE|null lo hi. Ghi results/fixed/real/sieve_v4_<TYPE>_<lo>.json."""
import json, sys
from pathlib import Path
import numpy as np
from tft_goat.engine.resolver import EngineResolver
from tft_goat.env.tft_env import TftEnv
from tft_sim.params import make_aug_rule
from tft_sim.real_content import build_real
from tft_sim.tftgoat import action_type, play, summarize

t, lo, hi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
env = TftEnv(set_content=build_real("TFTSet17"), resolver=EngineResolver())
v4 = make_aug_rule()

def pol(env_, agent, obs, mask, rng):
    if t != "null" and rng.random() < 0.1:
        legal = [int(i) for i in np.flatnonzero(mask) if action_type(int(i)) == t]
        if legal:
            return int(rng.choice(legal))
    return v4(env_, agent, obs, mask, rng)

lobs = [play(env, s, pol, v4) for s in range(lo, hi)]
s = summarize(lobs)
out = {"type": t, "seeds": f"{lo}-{hi-1}", "A": f"v4 + eps=0.1 type {t}" if t != "null" else "v4 vs v4",
       "B": "v4", "summary": s, "per_lobby_diff_A_minus_B": [float(np.mean(l.placements_a) - np.mean(l.placements_b)) for l in lobs]}
Path("results/fixed/real").mkdir(parents=True, exist_ok=True)
Path(f"results/fixed/real/sieve_v4_{t}_{lo}.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("RESULT", t, round(s["diff_A_minus_B"], 4), s["ci95_diff"], "illegal", s["illegal_A"], flush=True)
