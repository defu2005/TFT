"""Choi tren seed 90000-91999 (chua dung). Mode:
  v3null      : v3 vs v3 (null)
  clone_v3    : clone v2 vs v3 (Set 17)
  clone_scr   : clone v2 vs scripted goc (Set 17)
  clone18_v3  : clone v2 (huan luyen Set 17) vs v3 tren Set 18 DA-only
Hieu A-B; so am = tot hon. Ghi results/fixed/real/play_v2_<mode>.json."""
import json, sys
from pathlib import Path
import numpy as np
import torch
from tft_sim.bc_train import MaskedMLP
from tft_sim.real_content import build_real, build_real_set18_clean
from tft_sim.rules import make_swap_rule
from tft_sim.tftgoat import make_env, play, scripted_policy, summarize, universal_features_v2

mode = sys.argv[1]; CK = Path(sys.argv[2])
ck = torch.load(CK, weights_only=False)
model = MaskedMLP(ck["in_dim"]); model.load_state_dict(ck["state"]); model.eval()
mu, sd = ck["mu"], ck["sd"]
v3 = make_swap_rule(key="value")

@torch.no_grad()
def clone(env_, agent, obs, mask, rng):
    x = universal_features_v2(obs, env_, agent)
    xt = torch.from_numpy(((x - mu) / sd).astype(np.float32))[None]
    m = torch.from_numpy(np.asarray(mask, dtype=bool))[None]
    return int(torch.argmax(model(xt, m), dim=1).item())

content = build_real_set18_clean() if mode == "clone18_v3" else build_real("TFTSet17")
env = make_env(content)
A, B = {"v3null": (v3, v3), "clone_v3": (clone, v3), "clone_scr": (clone, scripted_policy),
        "clone18_v3": (clone, v3)}[mode]
lobs = [play(env, s, A, B) for s in range(90000, 92000)]
s = summarize(lobs)
out = {"mode": mode, "seeds": "90000-91999 (fresh)", "summary": s,
       "per_lobby_diff_A_minus_B": [float(np.mean(l.placements_a) - np.mean(l.placements_b)) for l in lobs]}
Path("results/fixed/real").mkdir(parents=True, exist_ok=True)
Path(f"results/fixed/real/play_v2_{mode}.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("RESULT", mode, round(s["diff_A_minus_B"], 4), s["ci95_diff"], "illegal", s["illegal_A"], flush=True)
