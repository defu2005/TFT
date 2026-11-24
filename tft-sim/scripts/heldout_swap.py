"""Kiem dinh giu-lai quy tac doi unit (key=value, dong bang tren seed tinh chinh) tren seed 60000-61999 (chua dung).
  python scripts/heldout_swap.py <17|18> <vs_scripted|vs_hybrid|null_scripted|null_hybrid>
Ghi results/fixed/real/heldout_swap_<set>_<exp>.json."""
import json, sys
from pathlib import Path
import numpy as np
from tft_sim.real_content import build_real, build_real_set18_clean
from tft_sim.rules import make_rule, make_swap_rule
from tft_sim.tftgoat import make_env, play, scripted_policy, summarize

which, exp = sys.argv[1], sys.argv[2]
content = build_real("TFTSet17") if which == "17" else build_real_set18_clean()
env = make_env(content)
hybrid = make_rule(sell=True, floor=54, pick="hybrid")
swap = make_swap_rule(key="value")
A, B = {"vs_scripted": (swap, scripted_policy), "vs_hybrid": (swap, hybrid),
        "null_scripted": (scripted_policy, scripted_policy), "null_hybrid": (hybrid, hybrid)}[exp]
lobs = [play(env, s, A, B) for s in range(60000, 62000)]
s = summarize(lobs)
out = {"set": which, "exp": exp, "seeds": "60000-61999 (held-out)", "rule": "swap key=value over hybrid",
       "summary": s, "per_lobby_diff_A_minus_B": [float(np.mean(l.placements_a) - np.mean(l.placements_b)) for l in lobs]}
Path("results/fixed/real").mkdir(parents=True, exist_ok=True)
Path(f"results/fixed/real/heldout_swap_{which}_{exp}.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("RESULT", which, exp, round(s["diff_A_minus_B"], 4), s["ci95_diff"], "illegal", s["illegal_A"], flush=True)
