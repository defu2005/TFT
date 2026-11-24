"""Kiem tra EngineResolver (combat tick-by-tick, abilities/items/augments Set 17) voi v3 tren 30 lobby (seed 100000-100029).
Do: co chay duoc khong, toc do, va hieu v3 vs v3 (null) va v3 vs hybrid. Ghi results/fixed/real/engine_check.json."""
import json, time
from pathlib import Path
import numpy as np
from tft_goat.engine.resolver import EngineResolver
from tft_sim.real_content import build_real
from tft_sim.rules import make_rule, make_swap_rule
from tft_sim.tftgoat import make_env, play, scripted_policy, summarize
from tft_goat.env.tft_env import TftEnv
env = TftEnv(set_content=build_real("TFTSet17"), resolver=EngineResolver())
v3 = make_swap_rule(key="value"); hybrid = make_rule(sell=True, floor=54, pick="hybrid")
t0 = time.time()
lob_null = [play(env, s, v3, v3) for s in range(100000, 100030)]
t1 = time.time()
lob_h = [play(env, s, v3, hybrid) for s in range(100000, 100030)]
out = {"n": 30, "seconds_null": round(t1 - t0, 1), "seconds_vs_hybrid": round(time.time() - t1, 1),
       "null_v3_vs_v3": summarize(lob_null), "v3_vs_hybrid": summarize(lob_h)}
Path("results/fixed/real/engine_check.json").write_text(json.dumps(out, ensure_ascii=False, indent=2, default=float), encoding="utf-8")
print(out["seconds_null"], out["seconds_vs_hybrid"], out["null_v3_vs_v3"].get("diff_A_minus_B"), out["v3_vs_hybrid"].get("diff_A_minus_B"), flush=True)
