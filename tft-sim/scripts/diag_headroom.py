"""Do du dia (advisor buoc 1-3), v3 tu dau, HeuristicResolver, 200 lobby (seed 100000-100199, dev).
(1) Vang tai thoi diem ghe bi loai (theo placement): vang cuoi cung truoc khi chet.
(2) Board headroom: board_strength thuc / board_strength tot nhat chon tu board+bench (tham lam theo contrib).
(3) Augment: so lan chon augment co tier thap hon tier cao nhat dang duoc chao.
Ghi results/fixed/real/diag_headroom.json."""
import json
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from tft_goat.env.combat import board_strength, STAR_MULT, AUGMENT_REGISTRY
from tft_goat.env.rounds import is_pvp
from tft_goat.env.actions import PICK_AUGMENT_START
from tft_sim.real_content import build_real
from tft_sim.rules import make_swap_rule
from tft_sim.tftgoat import make_env, seat_groups

env = make_env(build_real("TFTSet17"))
v3 = make_swap_rule(key="value")
gold_at_death = []; ratios = []; aug_total = 0; aug_suboptimal = 0; aug_registry_offer = 0; aug_registry_pick = 0
RANK = {"silver": 1, "gold": 2, "prismatic": 3, "god": 4}
for seed in range(100000, 100200):
    obs, infos = env.reset(seed=seed)
    rngs = {a: np.random.default_rng(seed * 100 + i) for i, a in enumerate(env.agents)}
    last_gold = {}
    step = 0
    while env.agents and step < 20000:
        acts = {}
        for a in list(env.agents):
            mask = infos[a]["action_mask"]
            p = env._state.players[a]
            if mask[PICK_AUGMENT_START:PICK_AUGMENT_START + 3].any():
                offer = list(p.augment_offer)[:3]
                tiers = [RANK.get(env._state.set_content.augments[o].tier, 0) for o in offer if o in env._state.set_content.augments]
                legal = [i for i in range(3) if mask[PICK_AUGMENT_START + i]]
                aug_total += 1
                if tiers and legal:
                    chosen = int(v3(env, a, obs[a], mask, rngs[a])) - PICK_AUGMENT_START
                    if 0 <= chosen < len(offer) and offer[chosen] in env._state.set_content.augments:
                        ch = RANK.get(env._state.set_content.augments[offer[chosen]].tier, 0)
                        if ch < max(tiers):
                            aug_suboptimal += 1
                        if offer[chosen] in AUGMENT_REGISTRY:
                            aug_registry_pick += 1
                        aug_registry_offer += sum(1 for o in offer if o in AUGMENT_REGISTRY) > 0
            acts[a] = int(v3(env, a, obs[a], mask, rngs[a]))
            if env._phase_steps == 0 and is_pvp(env._state.round_index) and p.hp > 0:
                last_gold[a] = p.gold
                units = list(p.board) + list(p.bench)
                cur = board_strength(p.board, env._state.set_content)
                # tham lam toi uu: chon cap cost*star tot nhat cho board_cap unit
                vals = sorted(units, key=lambda u: -env._state.set_content.champions[u.champion_api].cost * STAR_MULT.get(u.star, 1))
                best = board_strength(vals[:max(1, p.board_cap)], env._state.set_content)
                if best > 0:
                    ratios.append(cur / best)
        obs, r, t, tr, infos = env.step(acts)
        step += 1
    for a in list(env._state.players):
        p = env._state.players[a]
        if a in last_gold:
            gold_at_death.append((p.placement, last_gold[a]))
gd = np.array(gold_at_death, float)
out = {"gold_at_last_pvp_by_placement": {
           "top4_mean": round(float(gd[gd[:, 0] <= 4, 1].mean()), 2),
           "bottom4_mean": round(float(gd[gd[:, 0] > 4, 1].mean()), 2)},
       "board_headroom_mean_ratio": round(float(np.mean(ratios)), 3),
       "augment_decisions": aug_total, "augment_suboptimal_tier_picks": aug_suboptimal,
       "augment_registry_picks": aug_registry_pick}
Path("results/fixed/real/diag_headroom.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print(out, flush=True)
