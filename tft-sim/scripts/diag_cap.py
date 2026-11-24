"""Ti le pha lap ke hoach ket thuc do tran 50 (thay vi moi nguoi PASS) voi v3, 100 lobby, seed 100000-100099 (dev moi).
Ghi results/fixed/real/diag_cap.json."""
import json
from collections import Counter
from pathlib import Path
import numpy as np
from tft_sim.real_content import build_real
from tft_sim.rules import make_swap_rule
from tft_sim.tftgoat import make_env, scripted_policy, seat_groups
from tft_goat.env.tft_env import MAX_PLANNING_STEPS
env = make_env(build_real("TFTSet17"))
v3 = make_swap_rule(key="value")
phases = Counter(); lengths = []
for seed in range(100000, 100100):
    groups = seat_groups(seed)
    rngs = {a: np.random.default_rng(seed * 100 + i) for i, a in enumerate(groups)}
    obs, infos = env.reset(seed=seed)
    step = 0; prev_ps = 0
    while env.agents and step < 20000:
        acts = {a: int(v3(env, a, obs[a], infos[a]["action_mask"], rngs[a])) for a in list(env.agents)}
        before_round = env._state.round if hasattr(env._state, "round") else None
        obs, r, t, tr, infos = env.step(acts)
        ps = getattr(env, "_phase_steps", 0)
        if ps == 0 and prev_ps > 0:
            phases["cap" if prev_ps >= MAX_PLANNING_STEPS else "all_passed"] += 1
            lengths.append(prev_ps)
        prev_ps = ps
        step += 1
out = {"lobbies": 100, "phases": dict(phases), "cap_share": round(phases["cap"] / max(1, sum(phases.values())), 4),
       "phase_len_mean": round(float(np.mean(lengths)), 2) if lengths else None}
Path("results/fixed/real/diag_cap.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print(out)
