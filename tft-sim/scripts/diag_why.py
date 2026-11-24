"""(a) Replicate eps ladder on fresh seeds 3000-3199 (eps 0.05, 0.1, 0.2).
(b) Mechanism: for eps=0.1 (A) vs scripted (B), mean level, gold, hp, board size by round,
and action-type counts, including XP/REROLL with gold < 54 (the teacher never does these)."""
import json, random, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from tft_sim.tftgoat import (default_content, make_env, seat_groups, scripted_policy, action_type,
                             play, summarize, MAX_STEPS)

R = Path(sys.argv[1]); R.mkdir(parents=True, exist_ok=True)
SEEDS = range(3000, 3200)

def eps_policy(eps):
    def pol(env, agent, obs, mask, rng):
        if rng.random() < eps:
            return int(rng.choice(list(np.flatnonzero(mask))))
        return scripted_policy(env, agent, obs, mask, rng)
    return pol

env = make_env(default_content())
out = {"seeds": "3000-3199", "replication": {}, "mechanism": {}}
for eps in [0.05, 0.1, 0.2]:
    ev = [play(env, s, eps_policy(eps), scripted_policy) for s in SEEDS]
    out["replication"][str(eps)] = summarize(ev)
    print("eps", eps, out["replication"][str(eps)]["diff_A_minus_B"], out["replication"][str(eps)]["ci95_diff"], flush=True)

pol_a = eps_policy(0.1)
stats = {"A": defaultdict(list), "B": defaultdict(list)}
acts = {"A": Counter(), "B": Counter()}
lowecon = {"A": Counter(), "B": Counter()}
for seed in SEEDS:
    groups = seat_groups(seed)
    rngs = {a: random.Random(seed * 100 + i) for i, a in enumerate(groups)}
    obs, infos = env.reset(seed=seed); step = 0
    last = {}
    while env.agents and step < MAX_STEPS:
        acts_now = {}
        for a in list(env.agents):
            g = groups[a]; mask = infos[a]["action_mask"]
            pol = pol_a if g == "A" else scripted_policy
            act = pol(env, a, obs[a], mask, rngs[a])
            name = action_type(act); acts[g][name] += 1
            p = env._state.players[a]
            if name in ("BUY_XP", "REROLL") and p.gold < 54: lowecon[g][name] += 1
            acts_now[a] = act
        obs, r, t, tr, infos = env.step(acts_now); step += 1
        rnd = env._state.round_index
        for a in list(env.agents) + [x for x in groups if x not in env.agents]:
            p = env._state.players.get(a)
            if p is None: continue
            last[(groups[a], rnd, a)] = (p.level, p.gold, p.hp, len(p.board))
    for (g, rnd, a), v in last.items():
        for name, x in zip(["level", "gold", "hp", "board"], v):
            stats[g][(rnd, name)].append(x)
mech = {}
for g in "AB":
    mech[g] = {}
    for rnd in range(0, 12):
        row = {}
        for name in ["level", "gold", "hp", "board"]:
            vals = stats[g].get((rnd, name))
            if vals: row[name] = round(float(np.mean(vals)), 2)
        if row: mech[g][rnd] = row
out["mechanism"] = {
    "by_round": mech,
    "action_counts_A_eps0.1": dict(acts["A"].most_common()),
    "action_counts_B_scripted": dict(acts["B"].most_common()),
    "xp_or_reroll_below_54_gold_A": dict(lowecon["A"]),
    "xp_or_reroll_below_54_gold_B": dict(lowecon["B"]),
}
(R / "diag_why.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("done", flush=True)
