"""Giu-lai quy tac augment (registry truoc, roi tier) duoi EngineResolver, seed 110000-111999 (chua dung).
Mode: aug (aug vs v3) | null (v3 vs v3). Ghi results/fixed/real/heldout_aug_engine_<mode>.json."""
import json, sys
from pathlib import Path
import numpy as np
from tft_goat.engine.resolver import EngineResolver
from tft_goat.env.tft_env import TftEnv
from tft_sim.params import make_aug_rule
from tft_sim.real_content import build_real
from tft_sim.rules import make_swap_rule
from tft_sim.tftgoat import play, summarize
mode = sys.argv[1]
env = TftEnv(set_content=build_real("TFTSet17"), resolver=EngineResolver())
v3 = make_swap_rule(key="value")
A = make_aug_rule() if mode == "aug" else v3
lobs = [play(env, s, A, v3) for s in range(110000, 112000)]
s = summarize(lobs)
out = {"mode": mode, "seeds": "110000-111999 (held-out, engine)", "summary": s,
       "per_lobby_diff_A_minus_B": [float(np.mean(l.placements_a) - np.mean(l.placements_b)) for l in lobs]}
Path("results/fixed/real").mkdir(parents=True, exist_ok=True)
Path(f"results/fixed/real/heldout_aug_engine_{mode}.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("RESULT", mode, round(s["diff_A_minus_B"], 4), s["ci95_diff"], "illegal", s["illegal_A"], flush=True)
