"""Quy tac augment (registry truoc, roi tier) tren v3, duoi EngineResolver, seed dev 100000-100399. Ghi results/fixed/real/aug_engine_dev.json."""
import json
from pathlib import Path
import numpy as np
from tft_goat.engine.resolver import EngineResolver
from tft_goat.env.tft_env import TftEnv
from tft_sim.params import make_aug_rule
from tft_sim.real_content import build_real
from tft_sim.rules import make_swap_rule
from tft_sim.tftgoat import play, summarize
env = TftEnv(set_content=build_real("TFTSet17"), resolver=EngineResolver())
v3 = make_swap_rule(key="value")
lobs = [play(env, s, make_aug_rule(), v3) for s in range(100000, 100400)]
s = summarize(lobs)
out = {"rule": "augment registry-first then tier", "seeds": "100000-100399 (dev, engine)", "summary": s,
       "per_lobby_diff_A_minus_B": [float(np.mean(l.placements_a) - np.mean(l.placements_b)) for l in lobs]}
Path("results/fixed/real").mkdir(parents=True, exist_ok=True)
Path("results/fixed/real/aug_engine_dev.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("RESULT", round(s["diff_A_minus_B"], 4), s["ci95_diff"], "illegal", s["illegal_A"], flush=True)
