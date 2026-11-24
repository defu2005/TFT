"""Quet nguong HP cho quy tac 'tieu vang khi may' (v3 + endgame). Seed dev 100000-100399. Ghi results/fixed/real/endgame_dev.json."""
import json, sys
from pathlib import Path
import numpy as np
from tft_sim.params import make_endgame
from tft_sim.real_content import build_real
from tft_sim.rules import make_swap_rule
from tft_sim.tftgoat import make_env, play, summarize
H = int(sys.argv[1])
env = make_env(build_real("TFTSet17"))
v3 = make_swap_rule(key="value")
lobs = [play(env, s, make_endgame(H), v3) for s in range(100000, 100400)]
s = summarize(lobs)
out = {"hp_threshold": H, "seeds": "100000-100399 (dev)", "summary": s,
       "per_lobby_diff_A_minus_B": [float(np.mean(l.placements_a) - np.mean(l.placements_b)) for l in lobs]}
Path("results/fixed/real").mkdir(parents=True, exist_ok=True)
Path(f"results/fixed/real/endgame_dev_H{H}.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("RESULT", H, round(s["diff_A_minus_B"], 4), s["ci95_diff"], "illegal", s["illegal_A"], flush=True)
