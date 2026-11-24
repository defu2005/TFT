import collections
import tft_goat.env.actions as A
from tft_goat.agent.scripted import scripted_action
from tft_goat.data.sample import build_sample_content
from tft_goat.env.tft_env import TftEnv
stats = collections.Counter()
orig = A.combine_components
def spy(c1, c2, content):
    r = orig(c1, c2, content)
    stats["combine_none" if r is None else "combine_ok"] += 1
    return r
A.combine_components = spy
env = TftEnv(set_content=build_sample_content())
for seed in range(5):
    env.reset(seed=seed)
    n = 0
    while env.agents and n < 20000:
        acts = {a: int(scripted_action(env._state, env._state.players[a])) for a in env.agents}
        env.step(acts); n += 1
print(dict(stats))
