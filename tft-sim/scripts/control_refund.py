"""Doi chung: quy tac sell voi hoan gia ban binh thuong va voi hoan gia = 0 (200 lobby tinh chinh, seed 20000-20199).
Neu hieu hang mat di khi hoan gia = 0 thi loi the den tu vong mua-ban (gia tri hoan), khong phai tu chinh sach."""
import json, sys
from pathlib import Path
import numpy as np
import tft_goat.env.actions as acts
from tft_sim.real_content import build_real
from tft_sim.rules import make_rule
from tft_sim.tftgoat import make_env, play, scripted_policy, summarize

mode = sys.argv[1]  # normal | zero
if mode == "zero":
    acts.sell_value = lambda cost, star: 0
env = make_env(build_real("TFTSet17"))
lobs = [play(env, s, make_rule(sell=True, floor=54), scripted_policy) for s in range(20000, 20200)]
s = summarize(lobs)
out = {"refund": mode, "summary": s}
Path("results/fixed/real").mkdir(parents=True, exist_ok=True)
Path(f"results/fixed/real/control_refund_{mode}.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("RESULT", mode, round(s["diff_A_minus_B"], 4), s["ci95_diff"], flush=True)
