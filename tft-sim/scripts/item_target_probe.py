"""Do luat chon dich trang bi (EQUIP) tren EngineResolver. Hai nhom ghe trong cung lobby, moi nhom mot luat:
  default  : unit cost cao nhat (env goc)
  cheapest : unit cost thap nhat
  random   : ngau nhien (deterministic theo round)
  spread   : unit it item nhat; hoa thi gia tri cao nhat (gia tri = cost*3^(sao-1))
  valuemax : unit gia tri cao nhat (cost*3^(sao-1))
  none     : khong ghep item (doi chung sign)
Chinh sach: v4. Ghi hieu A-B (am = nhom A thu hang tot hon) vao results/fixed/real/item_<A>_vs_<B>_<lo>.json.
Args: RULE_A RULE_B lo hi."""
import json, random, sys
from pathlib import Path
import numpy as np
from tft_goat.engine.resolver import EngineResolver
from tft_goat.env import actions as ACT
from tft_goat.env.tft_env import TftEnv
from tft_sim.params import make_aug_rule
from tft_sim.real_content import build_real
from tft_sim.tftgoat import play, seat_groups

RA, RB, lo, hi = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
ITEMS_MAX, COMPONENTS_PER_ITEM = ACT.ITEMS_MAX, ACT.COMPONENTS_PER_ITEM
GROUP_A: set[str] = set()
_orig = ACT._equip

def _value(state, u):
    return ACT._champ_cost(state, u.champion_api) * 3 ** (int(getattr(u, "star", 1)) - 1)

def _pick(rule, state, player, cands):
    if rule == "cheapest":
        return min(cands, key=lambda u: ACT._champ_cost(state, u.champion_api))
    if rule == "random":
        return random.Random(state.round_index * 131 + len(player.board)).choice(cands)
    if rule == "spread":
        return min(cands, key=lambda u: (u.items, -_value(state, u)))
    if rule == "valuemax":
        return max(cands, key=lambda u: _value(state, u))
    return max(cands, key=lambda u: ACT._champ_cost(state, u.champion_api))  # default

def _alt(state, player):
    rule = RA if player.agent_id in GROUP_A else RB
    if rule == "default":
        return _orig(state, player)
    if rule == "none":
        return
    if len(player.components) < COMPONENTS_PER_ITEM:
        return
    cands = [u for u in player.board if u.items < ITEMS_MAX]
    if not cands:
        return
    item_api = ACT.combine_components(player.components[0], player.components[1], state.set_content)
    if item_api is None:
        return
    target = _pick(rule, state, player, cands)
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
Path(f"results/fixed/real/item_{RA}_vs_{RB}_{lo}.json").write_text(json.dumps({"A": RA, "B": RB, "seeds": f"{lo}-{hi-1}", "per_lobby_diff_A_minus_B": per}), encoding="utf-8")
print("DONE", RA, RB, round(float(np.mean(per)), 4), flush=True)
