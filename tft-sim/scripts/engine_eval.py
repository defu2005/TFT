"""v3 duoi EngineResolver (combat tick-by-tick). Seed dev 100000-100399 (400 lobby). Mode: null | vs_hybrid.
Ghi results/fixed/real/engine_eval_<mode>.json (co hieu tung lobby)."""
import json, sys
from pathlib import Path
import numpy as np
from tft_goat.engine.resolver import EngineResolver
from tft_goat.env.tft_env import TftEnv
from tft_sim.real_content import build_real
from tft_sim.rules import make_rule, make_swap_rule
from tft_sim.tftgoat import play, summarize
mode = sys.argv[1]
env = TftEnv(set_content=build_real("TFTSet17"), resolver=EngineResolver())
v3 = make_swap_rule(key="value"); hybrid = make_rule(sell=True, floor=54, pick="hybrid")
B = v3 if mode == "null" else hybrid
lobs = [play(env, s, v3, B) for s in range(100000, 100400)]
s = summarize(lobs)
out = {"mode": mode, "resolver": "EngineResolver", "seeds": "100000-100399 (dev)", "summary": s,
       "per_lobby_diff_A_minus_B": [float(np.mean(l.placements_a) - np.mean(l.placements_b)) for l in lobs]}
Path("results/fixed/real").mkdir(parents=True, exist_ok=True)
Path(f"results/fixed/real/engine_eval_{mode}.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("RESULT", mode, round(s["diff_A_minus_B"], 4), s["ci95_diff"], flush=True)
