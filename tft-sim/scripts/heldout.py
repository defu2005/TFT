"""Kiem dinh giu-lai (held-out) quy tac DA CHON: sell=1, floor=54, pick=useless. Seed 30000-31999 (chua dung).
  python scripts/heldout.py <17|18> <rule|null>
rule = quy tac vs scripted; null = scripted vs scripted (cung seed). Ghi results/fixed/real/heldout_<set>_<exp>.json."""
import json, sys
from pathlib import Path
import numpy as np
from tft_sim.real_content import build_real, build_real_set18_clean
from tft_sim.rules import make_rule
from tft_sim.tftgoat import make_env, play, scripted_policy, summarize

which, exp = sys.argv[1], sys.argv[2]
content = build_real("TFTSet17") if which == "17" else build_real_set18_clean()
env = make_env(content)
pol_a = make_rule(sell=True, floor=54, pick="useless") if exp == "rule" else scripted_policy
lobs = [play(env, s, pol_a, scripted_policy) for s in range(30000, 32000)]
s = summarize(lobs)
out = {"set": which, "exp": exp, "seeds": "30000-31999 (held-out)", "rule": "sell=1 floor=54 pick=useless",
       "summary": s, "per_lobby_diff_A_minus_B": [float(np.mean(l.placements_a) - np.mean(l.placements_b)) for l in lobs]}
Path("results/fixed/real").mkdir(parents=True, exist_ok=True)
Path(f"results/fixed/real/heldout_{which}_{exp}.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("RESULT", which, exp, round(s["diff_A_minus_B"], 4), s["ci95_diff"], "illegal", s["illegal_A"], flush=True)
