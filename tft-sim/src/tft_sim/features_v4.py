"""uni3 = uni2 (179) + 3 co registry cho 3 augment dang duoc chao (0/1 moi slot) + 3 co 'slot co augment' -> 185 chieu.
Dung cho clone v4 de hoc lua chon augment theo registry (quy tac make_aug_rule)."""
import numpy as np
from tft_goat.engine.augments_set17 import AUGMENT_REGISTRY as REG
from tft_sim.tftgoat import universal_features_v2


def universal_features_v4(obs: dict, env, agent) -> np.ndarray:
    base = universal_features_v2(obs, env, agent)
    p = env._state.players[agent]
    offer = list(p.augment_offer)[:3]
    has = np.zeros(3, np.float32)
    inreg = np.zeros(3, np.float32)
    for i, name in enumerate(offer):
        has[i] = 1.0
        inreg[i] = 1.0 if name in REG else 0.0
    return np.concatenate([base, has, inreg]).astype(np.float32)
