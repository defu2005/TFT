"""Chan doan quy tac sell tren 200 lobby tinh chinh (seed 20000-20199): mua, ban, bang, vang, cap do theo seat."""
import json
from collections import Counter
from pathlib import Path
import numpy as np
from tft_sim.real_content import build_real
from tft_sim.rules import make_rule
from tft_sim.tftgoat import make_env, scripted_policy, seat_groups, action_type

env = make_env(build_real("TFTSet17"))
rule = make_rule(sell=True, floor=54)
agg = {g: Counter() for g in "AB"}
end = {g: {"board": [], "bench": [], "gold": [], "level": [], "hp": []} for g in "AB"}
for seed in range(20000, 20200):
    groups = seat_groups(seed)
    rngs = {a: np.random.default_rng(seed * 100 + i) for i, a in enumerate(groups)}
    obs, infos = env.reset(seed=seed)
    step = 0
    while env.agents and step < 20000:
        acts = {}
        for a in list(env.agents):
            g = groups[a]
            mask = infos[a]["action_mask"]
            pol = rule if g == "A" else scripted_policy
            act = int(pol(env, a, obs[a], mask, rngs[a]))
            agg[g][action_type(act)] += 1
            acts[a] = act
        obs, r, t, tr, infos = env.step(acts)
        step += 1
    for a, g in groups.items():
        pl = env._state.players[a]
        end[g]["board"].append(len(pl.board)); end[g]["bench"].append(len(pl.bench))
        end[g]["gold"].append(pl.gold); end[g]["level"].append(pl.level); end[g]["hp"].append(pl.hp)
out = {"seeds": "20000-20199 (tuning seeds)"}
for g, name in (("A", "rule"), ("B", "scripted")):
    n = 200 * 4
    out[name] = {"actions_per_seat_lobby": {k: round(v / n, 2) for k, v in agg[g].items()},
                 **{f"end_{k}_mean": round(float(np.mean(v)), 2) for k, v in end[g].items()}}
Path("results/fixed/real/diag_rule.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(out, ensure_ascii=False, indent=2))
