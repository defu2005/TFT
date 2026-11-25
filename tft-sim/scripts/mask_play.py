"""Choi clone mask (vai A) vs teacher v4 (vai B) tren EngineResolver, seed LO..HI-1 (ledger: 260000-260999).
Args: mode(clone|null) ckpt LO HI TAG. null = v4 vs v4 (ckpt bo qua). Ghi results/fixed/real/play_<TAG>.json."""
import json, sys
from pathlib import Path
import numpy as np
import torch
sys.path.insert(0, str(Path(__file__).parent))
from mask_exp import apply_fmask
from tft_goat.engine.resolver import EngineResolver
from tft_goat.env.tft_env import TftEnv
from tft_sim.bc_train import MaskedMLP
from tft_sim.features_v4 import universal_features_v4
from tft_sim.params import make_aug_rule
from tft_sim.real_content import build_real
from tft_sim.tftgoat import play, summarize

torch.set_num_threads(1)
mode, CK, LO, HI, TAG = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
v4 = make_aug_rule()
if mode == "clone":
    ck = torch.load(CK, weights_only=False)
    model = MaskedMLP(ck["in_dim"]); model.load_state_dict(ck["state"]); model.eval()
    mu, sd, fm = ck["mu"], ck["sd"], ck["fmask"]

    @torch.no_grad()
    def policy(env_, agent, obs, mask, rng):
        x = apply_fmask(universal_features_v4(obs, env_, agent), fm)
        xt = torch.from_numpy(((x - mu) / sd).astype(np.float32))[None]
        return int(torch.argmax(model(xt, torch.from_numpy(np.asarray(mask, dtype=bool))[None]), dim=1).item())
    A, B = policy, v4
else:
    A, B = v4, v4
env = TftEnv(set_content=build_real("TFTSet17"), resolver=EngineResolver())
lobs = [play(env, s, A, B) for s in range(LO, HI)]
s = summarize(lobs)
out = {"mode": mode, "tag": TAG, "ckpt": CK if mode == "clone" else None, "resolver": "EngineResolver",
       "content": "TFTSet17 (real_content)", "teacher_B": "make_aug_rule (v4)", "seeds": [LO, HI - 1],
       "summary": s,
       "per_lobby_diff_A_minus_B": [float(np.mean(l.placements_a) - np.mean(l.placements_b)) for l in lobs]}
Path("results/fixed/real").mkdir(parents=True, exist_ok=True)
Path(f"results/fixed/real/play_{TAG}.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("RESULT", TAG, round(s["diff_A_minus_B"], 4), s["ci95_diff"], "illegal", s["illegal_A"], flush=True)
