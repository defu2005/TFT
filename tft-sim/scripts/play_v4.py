import torch; torch.set_num_threads(1)
"""Choi tren EngineResolver, seed 160000-160999 (chua dung). Mode:
  v4null   : v4 vs v4 (null)
  clone_v4 : clone v4 vs teacher v4
  clone_v3 : clone v4 vs teacher v3
  clone_scr: clone v4 vs scripted goc
Hieu A-B; so am = tot hon. Ghi results/fixed/real/play_v4_<mode>.json."""
import json, sys
from pathlib import Path
import numpy as np
import torch
from tft_goat.engine.resolver import EngineResolver
from tft_goat.env.tft_env import TftEnv
from tft_sim.bc_train import MaskedMLP
from tft_sim.features_v4 import universal_features_v4
from tft_sim.params import make_aug_rule
from tft_sim.real_content import build_real
from tft_sim.rules import make_swap_rule
from tft_sim.tftgoat import play, scripted_policy, summarize

mode = sys.argv[1]; CK = Path(sys.argv[2])
ck = torch.load(CK, weights_only=False)
model = MaskedMLP(ck["in_dim"]); model.load_state_dict(ck["state"]); model.eval()
mu, sd = ck["mu"], ck["sd"]
v3 = make_swap_rule(key="value"); v4 = make_aug_rule()

@torch.no_grad()
def clone(env_, agent, obs, mask, rng):
    x = universal_features_v4(obs, env_, agent)
    xt = torch.from_numpy(((x - mu) / sd).astype(np.float32))[None]
    m = torch.from_numpy(np.asarray(mask, dtype=bool))[None]
    return int(torch.argmax(model(xt, m), dim=1).item())

env = TftEnv(set_content=build_real("TFTSet17"), resolver=EngineResolver())
A, B = {"v4null": (v4, v4), "clone_v4": (clone, v4), "clone_v3": (clone, v3), "clone_scr": (clone, scripted_policy)}[mode]
lobs = [play(env, s, A, B) for s in range(160000, 161000)]
s = summarize(lobs)
out = {"mode": mode, "seeds": "160000-160999 (held-out, engine)", "summary": s,
       "per_lobby_diff_A_minus_B": [float(np.mean(l.placements_a) - np.mean(l.placements_b)) for l in lobs]}
Path("results/fixed/real").mkdir(parents=True, exist_ok=True)
Path(f"results/fixed/real/play_v4_{mode}.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("RESULT", mode, round(s["diff_A_minus_B"], 4), s["ci95_diff"], "illegal", s["illegal_A"], flush=True)
