"""Dem augment va god trong AUGMENT_REGISTRY duoc chao nhung khong duoc chon (v3 tu dau, engine resolver, 200 lobby, seed 100000-100199).
Ghi results/fixed/real/diag_aug.json."""
import json
from pathlib import Path
from tft_goat.env.combat import AUGMENT_REGISTRY as _CA
from tft_goat.engine.augments_set17 import AUGMENT_REGISTRY as REG
from tft_goat.engine.resolver import EngineResolver
from tft_goat.env.actions import PICK_AUGMENT_START, PICK_GOD_START
from tft_goat.env.tft_env import TftEnv
import numpy as np
from tft_sim.real_content import build_real
from tft_sim.rules import make_swap_rule
env = TftEnv(set_content=build_real("TFTSet17"), resolver=EngineResolver())
v3 = make_swap_rule(key="value")
c = dict(aug_decisions=0, offers_with_registry=0, registry_offered_not_picked=0, registry_picked=0,
         god_decisions=0, god_offers_with_registry=0, god_registry_not_picked=0)
for seed in range(100000, 100200):
    obs, infos = env.reset(seed=seed)
    rngs = {a: np.random.default_rng(seed * 100 + i) for i, a in enumerate(env.agents)}
    step = 0
    while env.agents and step < 20000:
        acts = {}
        for a in list(env.agents):
            mask = infos[a]["action_mask"]; p = env._state.players[a]
            act = int(v3(env, a, obs[a], mask, rngs[a]))
            if mask[PICK_AUGMENT_START:PICK_AUGMENT_START + 3].any():
                c["aug_decisions"] += 1
                offer = list(p.augment_offer)[:3]
                reg = [o in REG for o in offer]
                if any(reg):
                    c["offers_with_registry"] += 1
                    i = act - PICK_AUGMENT_START
                    if 0 <= i < len(offer):
                        if offer[i] in REG:
                            c["registry_picked"] += 1
                        else:
                            c["registry_offered_not_picked"] += 1
            if any(mask[PICK_GOD_START:PICK_GOD_START + 3]):
                c["god_decisions"] += 1
                gods = [p.god_offer[i] if hasattr(p, "god_offer") and i < len(p.god_offer) else None for i in range(3)]
                if any(g in REG for g in gods if g):
                    c["god_offers_with_registry"] += 1
                    i = act - PICK_GOD_START
                    if 0 <= i < 3 and gods[i] not in REG:
                        c["god_registry_not_picked"] += 1
            acts[a] = act
        obs, r, t, tr, infos = env.step(acts)
        step += 1
Path("results/fixed/real/diag_aug.json").write_text(json.dumps(c, indent=2), encoding="utf-8")
print(c, flush=True)
