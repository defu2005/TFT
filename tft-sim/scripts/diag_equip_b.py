"""Chan doan vong lap EQUIP: dem cac lan EQUIP khong lam thay doi components (khong tieu thu)."""
import collections
from tft_goat.agent.scripted import scripted_action
from tft_goat.data.sample import build_sample_content
from tft_sim.content_b import build_shuffled_content as build_full_recipe_content
from tft_goat.env.actions import EQUIP
from tft_goat.env.tft_env import TftEnv

env = TftEnv(set_content=build_full_recipe_content())
noop = collections.Counter(); total = collections.Counter()
for seed in range(9000, 9020):
    obs, infos = env.reset(seed=seed)
    steps = 0
    while env.agents and steps < 20000:
        acts = {}
        before = {a: len(env._state.players[a].components) for a in env.agents}
        for a in env.agents:
            acts[a] = int(scripted_action(env._state, env._state.players[a]))
        obs, r, t, tr, infos = env.step(acts)
        for a, act in acts.items():
            if act == EQUIP:
                total["equip"] += 1
                p = env._state.players.get(a)
                if p is not None and len(p.components) == before[a]:
                    noop["equip_no_consume"] += 1
        steps += 1
    total["games"] += 1
print({"games": total["games"], "equip_actions": total["equip"], "equip_without_consuming_components": noop["equip_no_consume"]})
