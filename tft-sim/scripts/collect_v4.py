"""Thu du lieu clone v4 bang teacher v4 (= make_aug_rule) tren EngineResolver, ca 8 ghe.
Dac trung uni3 (185 chieu). Args: lo hi out.npz. Dung seed moi 150000+ (chua dung trong README)."""
import sys
from pathlib import Path
import numpy as np
from tft_goat.engine.resolver import EngineResolver
from tft_goat.env.tft_env import TftEnv
from tft_sim.features_v4 import universal_features_v4
from tft_sim.params import make_aug_rule
from tft_sim.real_content import build_real
from tft_sim.tftgoat import seat_groups

lo, hi, out = int(sys.argv[1]), int(sys.argv[2]), Path(sys.argv[3])
env = TftEnv(set_content=build_real("TFTSet17"), resolver=EngineResolver())
v4 = make_aug_rule()
U, M, Y, SEED, SEAT, STEP = [], [], [], [], [], []
for seed in range(lo, hi):
    groups = seat_groups(seed)
    rngs = {a: np.random.default_rng(seed * 100 + i) for i, a in enumerate(groups)}
    obs, infos = env.reset(seed=seed)
    step = 0
    while env.agents and step < 20000:
        acts = {}
        for a in list(env.agents):
            mask = infos[a]["action_mask"]
            act = int(v4(env, a, obs[a], mask, rngs[a]))
            if int(mask.sum()) >= 2:
                U.append(universal_features_v4(obs[a], env, a)); M.append(mask.copy()); Y.append(act)
                SEED.append(seed); SEAT.append(int(a.split("_")[1])); STEP.append(step)
            acts[a] = act
        obs, r, t, tr, infos = env.step(acts)
        step += 1
    if (seed - lo) % 25 == 24:
        print("seed", seed, "rows", len(Y), flush=True)
np.savez_compressed(out, uni3=np.asarray(U, np.float32), mask=np.asarray(M, bool), action=np.asarray(Y, np.int64),
                    seed=np.asarray(SEED, np.int64), seat=np.asarray(SEAT, np.int64), step=np.asarray(STEP, np.int64))
print("DONE rows", len(Y), flush=True)
