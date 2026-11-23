"""Phat trien quy tac (wrapper) tren seed 20000-21999 (seed da dung cho tuning). Mot bien the moi lan.
  python scripts/rules_dev.py <ten> <sell 0|1> <floor>
Ghi results/fixed/real/rule_dev_<ten>.json (tom tat + hieu hang tung lobby A-B; A = quy tac, B = scripted)."""
import json, sys
from pathlib import Path
import numpy as np
from tft_sim.real_content import build_real
from tft_sim.rules import make_rule
from tft_sim.tftgoat import make_env, play, scripted_policy, summarize

name, sell, floor = sys.argv[1], bool(int(sys.argv[2])), int(sys.argv[3])
R = Path("results/fixed/real")
env = make_env(build_real("TFTSet17"))
pol = make_rule(sell=sell, floor=floor)
lobs = [play(env, s, pol, scripted_policy) for s in range(20000, 22000)]
s = summarize(lobs)
out = {"variant": name, "sell": sell, "floor": floor, "seeds": "20000-21999 (tuning)", "summary": s,
       "per_lobby_diff_A_minus_B": [float(np.mean(l.placements_a) - np.mean(l.placements_b)) for l in lobs]}
(R / f"rule_dev_{name}.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("RESULT", name, round(s["diff_A_minus_B"], 4), s["ci95_diff"], "illegal", s["illegal_A"], flush=True)
