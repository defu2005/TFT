import os
"""Sân chính = EngineResolver (combat tick-by-tick). Mode:
  replay  : 20 seed dau 120000-120019, chay v3 vs v3 hai lan, kiem tra placement khop
  null    : v3 vs v3, 120000-120999
  scr     : v3 vs scripted goc, 120000-120999
  clone   : clone v2 (uni2) vs v3, 120000-120999 (clone huan luyen tren teacher v3, khong dung engine khi huan luyen)
Ghi results/fixed/real/engine_arena_<mode>.json."""
import json, sys
from pathlib import Path
import numpy as np
import torch
from tft_goat.engine.resolver import EngineResolver
from tft_goat.env.tft_env import TftEnv
from tft_sim.bc_train import MaskedMLP
from tft_sim.real_content import build_real
from tft_sim.rules import make_swap_rule
from tft_sim.tftgoat import play, scripted_policy, summarize, universal_features_v2
mode = sys.argv[1]
env = TftEnv(set_content=build_real("TFTSet17"), resolver=EngineResolver())
v3 = make_swap_rule(key="value")
R = Path("results/fixed/real"); R.mkdir(parents=True, exist_ok=True)
if mode == "replay":
    same = 0
    for s in range(120000, 120020):
        a = play(env, s, v3, v3); b = play(env, s, v3, v3)
        same += int(a.placements_a == b.placements_a and a.placements_b == b.placements_b)
    out = {"mode": "replay", "identical_lobbies": same, "of": 20}
    (R / "engine_arena_replay.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("RESULT replay", same, "of 20", flush=True); sys.exit(0)
seeds = range(120000, 121000)
if mode == "null":
    A, B = v3, v3
elif mode == "scr":
    A, B = v3, scripted_policy
elif mode == "clone":
    ck = torch.load(os.environ.get("CLONE_CKPT", "results/checkpoints/clone_v2_seed0.pt"), weights_only=False)
    m = MaskedMLP(ck["in_dim"]); m.load_state_dict(ck["state"]); m.eval(); mu, sd = ck["mu"], ck["sd"]
    @torch.no_grad()
    def clone(env_, agent, obs, mask, rng):
        x = universal_features_v2(obs, env_, agent)
        xt = torch.from_numpy(((x - mu) / sd).astype(np.float32))[None]
        return int(torch.argmax(m(xt, torch.from_numpy(np.asarray(mask, dtype=bool))[None]), dim=1).item())
    A, B = clone, v3
lobs = [play(env, s, A, B) for s in seeds]
s = summarize(lobs)
out = {"mode": mode, "seeds": "120000-120999 (engine arena, held-out for this stage)", "summary": s,
       "per_lobby_diff_A_minus_B": [float(np.mean(l.placements_a) - np.mean(l.placements_b)) for l in lobs]}
(R / f"engine_arena_{mode}.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("RESULT", mode, round(s["diff_A_minus_B"], 4), s["ci95_diff"], "illegal", s["illegal_A"], flush=True)
