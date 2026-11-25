"""Driver cho mixed_lobby. Args: selftest | league LO HI TAG.
Pool: scripted, v3, v4, mask_full, mask_c, v4_null (v4 lai duoi nhan khac: null tich hop)."""
import sys
from pathlib import Path
import numpy as np
import torch
sys.path.insert(0, str(Path(__file__).parent))
from mask_exp import apply_fmask
from mixed_lobby import league, selftest
from tft_goat.engine.resolver import EngineResolver
from tft_goat.env.tft_env import TftEnv
from tft_sim.bc_train import MaskedMLP
from tft_sim.features_v4 import universal_features_v4
from tft_sim.params import make_aug_rule, make_swap_rule
from tft_sim.real_content import build_real
from tft_sim.tftgoat import scripted_policy

torch.set_num_threads(1)


def clone_policy(ckpt):
    ck = torch.load(ckpt, weights_only=False)
    model = MaskedMLP(ck["in_dim"]); model.load_state_dict(ck["state"]); model.eval()
    mu, sd, fm = ck["mu"], ck["sd"], ck["fmask"]

    @torch.no_grad()
    def pol(env_, agent, obs, mask, rng):
        x = apply_fmask(universal_features_v4(obs, env_, agent), fm)
        xt = torch.from_numpy(((x - mu) / sd).astype(np.float32))[None]
        return int(torch.argmax(model(xt, torch.from_numpy(np.asarray(mask, dtype=bool))[None]), dim=1).item())
    return pol


env = TftEnv(set_content=build_real("TFTSet17"), resolver=EngineResolver())
v4 = make_aug_rule()
mode = sys.argv[1]
if mode == "selftest":
    selftest(env, range(150000, 150005), scripted_policy, v4)
else:
    lo, hi, tag = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    pool = {
        "scripted": scripted_policy,
        "v3": make_swap_rule(key="value"),
        "v4": v4,
        "mask_full": clone_policy("results/checkpoints/mask_full.pt"),
        "mask_c": clone_policy("results/checkpoints/mask_c.pt"),
        "v4_null": v4,
    }
    league(env, lo, hi, pool, tag)
