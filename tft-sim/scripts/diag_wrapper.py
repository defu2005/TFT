"""Ung vien teacher moi (mot wrapper quanh scripted): khi scripted chon PASS, gold >= 40 va BUY_XP hop le
thi mua XP. Do tren seed moi 4000-4199, A = wrapper, B = scripted goc, so cap doi."""
import json, sys
from pathlib import Path
import numpy as np
from tft_sim.tftgoat import default_content, make_env, scripted_policy, play, summarize

R = Path(sys.argv[1]); R.mkdir(parents=True, exist_ok=True)
PASS, REROLL, BUY_XP = 0, 1, 2
FLOOR = 40

def wrapper(env, agent, obs, mask, rng):
    act = scripted_policy(env, agent, obs, mask, rng)
    if act == PASS and mask[BUY_XP] and env._state.players[agent].gold >= FLOOR:
        return BUY_XP
    return act

env = make_env(default_content())
seeds = range(4000, 4200)
ev = [play(env, s, wrapper, scripted_policy) for s in seeds]
res = {"candidate": f"scripted; PASS -> BUY_XP when gold>={FLOOR} and BUY_XP legal",
       "seeds": "4000-4199", "vs_scripted": summarize(ev)}
(R / "wrapper_candidate.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
v = res["vs_scripted"]
print(v["diff_A_minus_B"], v["ci95_diff"], v["completed"], v["mean_placement_A"], v["mean_placement_B"], flush=True)
