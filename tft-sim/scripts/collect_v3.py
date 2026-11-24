"""Thu du lieu clone v2 bang teacher v3 (doi unit, value) tren ca 8 ghe. Dac trung: uni2 (179 chieu), mask, action,
seat, seed, step. Khoi: train 80000-80399, val 80400-80499, test 81000-81199 (so ghi tai README)."""
import sys
from pathlib import Path
import numpy as np
from tft_sim.real_content import build_real
from tft_sim.rules import make_swap_rule
from tft_sim.tftgoat import make_env, seat_groups, universal_features_v2

lo, hi, out = int(sys.argv[1]), int(sys.argv[2]), Path(sys.argv[3])
env = make_env(build_real("TFTSet17"))
v3 = make_swap_rule(key="value")
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
            act = int(v3(env, a, obs[a], mask, rngs[a]))
            if int(mask.sum()) >= 2:
                U.append(universal_features_v2(obs[a], env, a)); M.append(mask.copy()); Y.append(act)
                SEED.append(seed); SEAT.append(int(a.split("_")[1])); STEP.append(step)
            acts[a] = act
        obs, r, t, tr, infos = env.step(acts)
        step += 1
    if (seed - lo) % 50 == 49:
        print("seed", seed, "rows", len(Y), flush=True)
np.savez_compressed(out, uni2=np.asarray(U, np.float32), mask=np.asarray(M, bool), action=np.asarray(Y, np.int64),
                    seed=np.asarray(SEED, np.int64), seat=np.asarray(SEAT, np.int64), step=np.asarray(STEP, np.int64))
print("DONE rows", len(Y), flush=True)
