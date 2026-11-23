"""Chan doan EQUIP tren noi dung that: bo bao _equip de ghi nhanh thoat som va so thanh phan."""
import json, collections
from pathlib import Path
import tft_goat.env.actions as acts
from tft_goat.data.content import build_set_content
from tft_goat.agent.scripted import scripted_action
from tft_goat.env.tft_env import TftEnv
from tft_goat.env.actions import EQUIP
from tft_goat.env.items import combine

RAW = Path("/home/user/mielpopsssssss/tft_goat/data/cdragon/cdragon_latest_fetched-2026-11-23.json")
content = build_set_content(json.loads(RAW.read_text(encoding="utf-8")), "latest-2026-11-23-set17block")
reasons = collections.Counter()
orig = acts._equip
def wrapped(state, player):
    n = len(player.components)
    if n < 2:
        reasons["fewer_than_2_components"] += 1
    elif not [u for u in player.board if u.items < acts.ITEMS_MAX]:
        reasons["no_unit_with_room"] += 1
    else:
        pair = (player.components[0], player.components[1])
        if combine(pair[0], pair[1], state.set_content) is None:
            reasons["no_recipe"] += 1
        else:
            reasons["would_consume"] += 1
    before = len(player.components)
    orig(state, player)
    after = len(player.components)
    reasons["consumed_2" if before - after == 2 else f"consumed_{before-after}"] += 1
acts._equip = wrapped
env = TftEnv(set_content=content)
total = 0
for seed in range(3):
    env.reset(seed=seed); n = 0
    while env.agents and n < 20000:
        a_ = {a: int(scripted_action(env._state, env._state.players[a])) for a in env.agents}
        total += sum(1 for v in a_.values() if v == EQUIP)
        env.step(a_); n += 1
print({"equip_actions": total, "equip_branch_reasons": dict(reasons)})
