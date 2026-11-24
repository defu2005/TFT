"""(Phien ban 2: A/B la hai nhom ghe trong cung lobby; ghi hieu A-B.)
Do do quyet dinh trang bi (EQUIP) co la don bay trong engine khong.
env automatically gives the finished item to the highest-cost unit (mac dinh). Thay luat chon dich
bang 'cheapest' (unit re nhat) hoac 'random' (ngau nhien). Cung chinh sach v4 tren cung seed; ghi
diem placement trung binh moi lobby (8 ghe). So sanh voi mac dinh bang script compare.
Args: MODE(default|cheapest|random) lo hi."""
import json, random, sys
from pathlib import Path
import numpy as np
from tft_goat.engine.resolver import EngineResolver
from tft_goat.env import actions as ACT
from tft_goat.env.tft_env import TftEnv


from tft_sim.params import make_aug_rule
from tft_sim.real_content import build_real
from tft_sim.tftgoat import play

from tft_sim.tftgoat import seat_groups
mode, lo, hi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
GROUP_A: set[str] = set()  # ghe nhom A dung luat thay the; nhom B giu mac dinh (cung lobby)
_orig = ACT._equip
ITEMS_MAX = ACT.ITEMS_MAX
COMPONENTS_PER_ITEM = ACT.COMPONENTS_PER_ITEM

def _alt(state, player):
    if mode == "default" or player.agent_id not in GROUP_A:
        return _orig(state, player)
    if len(player.components) < COMPONENTS_PER_ITEM:
        return
    cands = [u for u in player.board if u.items < ITEMS_MAX]
    if not cands:
        return
    item_api = ACT.combine_components(player.components[0], player.components[1], state.set_content)
    if item_api is None:
        return
    if mode == "cheapest":
        target = min(cands, key=lambda u: ACT._champ_cost(state, u.champion_api))
    else:
        target = random.Random(state.round_index * 131 + len(player.board)).choice(cands)
    target.item_apis = tuple(target.item_apis) + (item_api,)
    target.items += 1
    del player.components[0:COMPONENTS_PER_ITEM]

ACT._equip = _alt
env = TftEnv(set_content=build_real("TFTSet17"), resolver=EngineResolver())
v4 = make_aug_rule()
per = []
for s in range(lo, hi):
    GROUP_A.clear(); GROUP_A.update(k for k, g in seat_groups(s).items() if g == "A")
    l = play(env, s, v4, v4)
    per.append(float(np.mean(l.placements_a) - np.mean(l.placements_b)))
Path("results/fixed/real").mkdir(parents=True, exist_ok=True)
Path(f"results/fixed/real/item_probe_{mode}_{lo}.json").write_text(json.dumps({"mode": mode, "seeds": f"{lo}-{hi-1}", "per_lobby_diff_A_minus_B": per}), encoding="utf-8")
print("DONE", mode, round(float(np.mean(per)), 4), flush=True)
