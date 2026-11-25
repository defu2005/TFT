from tft_sim.real_content import load_raw_snapshot
"""Chan doan EQUIP tren noi dung that (CDragon latest 18.7, nhan Set 17), it van: 3 van."""
import json, collections
from pathlib import Path
from tft_goat.agent.scripted import scripted_action
from tft_goat.data.content import build_set_content
from tft_goat.env.actions import EQUIP
from tft_goat.env.tft_env import TftEnv
raw = load_raw_snapshot()
content = build_set_content(raw, "latest-2026-11-23-set17block")
print("champions", len(content.champions), "items", len(content.items))
env = TftEnv(set_content=content)
hist = collections.Counter(); noop = 0; total = 0
for seed in range(3):
    env.reset(seed=seed); n = 0
    while env.agents and n < 20000:
        before = {a: len(env._state.players[a].components) for a in env.agents}
        acts = {a: int(scripted_action(env._state, env._state.players[a])) for a in env.agents}
        for a, act in acts.items():
            hist[act] += 1
            if act == EQUIP:
                total += 1
                if a in env._state.players and len(env._state.players[a].components) == before[a]:
                    noop += 1
        env.step(acts); n += 1
    print("seed", seed, "steps", n, "completed", not env.agents)
print({"equip_total": total, "equip_noop": noop, "top_actions": hist.most_common(6)})
