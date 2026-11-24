"""Co che: voi luat cua ghe A (vd valuemax) va ghe B (default), dem moi lan gan item:
ty le gan cho unit DA co item, gia tri unit dich, so item trung binh tren moi ghe cuoi game.
Args: RULE_A RULE_B lo hi. Ghi results/fixed/real/mech_<A>_vs_<B>_<lo>.json."""
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
from tft_goat.engine.resolver import EngineResolver
from tft_goat.env import actions as ACT
from tft_goat.env.tft_env import TftEnv
from tft_sim.params import make_aug_rule
from tft_sim.real_content import build_real
from tft_sim.tftgoat import play, seat_groups
import item_target_probe_rules as R  # noqa: E402

RA, RB, lo, hi = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
stats = {"A": defaultdict(list), "B": defaultdict(list)}
GROUP_A: set[str] = set()
_orig = ACT._equip

def _watch(state, player):
    grp = "A" if player.agent_id in GROUP_A else "B"
    rule = RA if grp == "A" else RB
    before = len(player.components)
    cands = [u for u in player.board if u.items < ACT.ITEMS_MAX]
    if before >= ACT.COMPONENTS_PER_ITEM and cands and rule != "none":
        holders_before = {id(u) for u in player.board if u.items > 0}
        _alt(state, player, rule)
        # unit da duoc gan (so items tang)
        for u in player.board:
            if u.items > 0 and id(u) not in holders_before:
                stats[grp]["target_already_had_item"].append(0)
                stats[grp]["target_value"].append(R.value(state, u))
                break
        else:
            stats[grp]["target_already_had_item"].append(1)
        stats[grp]["events"].append(1)
    else:
        _alt(state, player, rule)

def _alt(state, player, rule):
    if rule == "default":
        return _orig(state, player)
    if rule == "none" or len(player.components) < ACT.COMPONENTS_PER_ITEM:
        return
    cands = [u for u in player.board if u.items < ACT.ITEMS_MAX]
    if not cands:
        return
    item_api = ACT.combine_components(player.components[0], player.components[1], state.set_content)
    if item_api is None:
        return
    target = R.pick(rule, state, player, cands)
    target.item_apis = tuple(target.item_apis) + (item_api,)
    target.items += 1
    del player.components[0:ACT.COMPONENTS_PER_ITEM]

ACT._equip = _watch
env = TftEnv(set_content=build_real("TFTSet17"), resolver=EngineResolver())
v4 = make_aug_rule()
for s in range(lo, hi):
    GROUP_A.clear(); GROUP_A.update(k for k, g in seat_groups(s).items() if g == "A")
    play(env, s, v4, v4)
out = {}
for g in "AB":
    out[g] = {k: (float(np.mean(v)) if v else None, len(v)) for k, v in stats[g].items()}
Path("results/fixed/real").mkdir(parents=True, exist_ok=True)
Path(f"results/fixed/real/mech_{RA}_vs_{RB}_{lo}.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print(json.dumps(out), flush=True)
