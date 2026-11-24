import collections
import tft_goat.env.actions as A
from tft_goat.agent.scripted import scripted_action
from tft_goat.env.items import components_and_recipes
from tft_goat.env.tft_env import TftEnv
from tft_sim.content import build_full_recipe_content
content = build_full_recipe_content()
comps, rec = components_and_recipes(content)
print("components:", comps, "recipes:", len(rec))
seen = collections.Counter()
orig = A.combine_components
def spy(c1, c2, c):
    r = orig(c1, c2, c)
    seen[(c1, c2, r is None)] += 1
    return r
A.combine_components = spy
env = TftEnv(set_content=content)
env.reset(seed=0)
n = 0
while env.agents and n < 3000:
    acts = {a: int(scripted_action(env._state, env._state.players[a])) for a in env.agents}
    env.step(acts); n += 1
print(list(seen.items())[:8])
print("components held sample:", [ (a, env._state.players[a].components[:3]) for a in list(env.agents)[:2]])
