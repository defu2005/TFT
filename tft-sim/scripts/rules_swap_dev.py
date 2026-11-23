"""Tinh chinh lop doi (swap) tren hybrid, seed 20000-21999 (dev). Argv: ten, key (star_cost|cost|value).
Ghi results/fixed/real/swap_dev_<ten>.json."""
import json, sys
from pathlib import Path
import numpy as np
from tft_sim.real_content import build_real
from tft_sim.rules import make_swap_rule
from tft_sim.tftgoat import make_env, play, scripted_policy, summarize

name, key = sys.argv[1], sys.argv[2]
env = make_env(build_real("TFTSet17"))
pol = make_swap_rule(key=key)
lobs = [play(env, s, pol, scripted_policy) for s in range(20000, 22000)]
s = summarize(lobs)
out = {"variant": name, "key": key, "seeds": "20000-21999 (dev)", "summary": s,
       "per_lobby_diff_A_minus_B": [float(np.mean(l.placements_a) - np.mean(l.placements_b)) for l in lobs]}
Path("results/fixed/real").mkdir(parents=True, exist_ok=True)
Path(f"results/fixed/real/swap_dev_{name}.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("RESULT", name, round(s["diff_A_minus_B"], 4), s["ci95_diff"], "illegal", s["illegal_A"], "completed", s["completed"], flush=True)
