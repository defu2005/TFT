"""Buoc 3 closed loop: universal + tier augment (40 epoch, A), 2000 lobby (seed 20000-21999), noi dung A.
Dung augment_tiers(env, agent) trong policy (thong tin ma nguoi choi that nhin thay)."""
import json, sys
from pathlib import Path
import numpy as np
import torch
from tft_sim.bc_train import train
from tft_sim.tftgoat import default_content, make_env, play, scripted_policy, slot_features, augment_tiers, summarize

S = Path(sys.argv[1]); R = Path(sys.argv[2]); R.mkdir(parents=True, exist_ok=True)
tr = np.load(S / "train.npz")
f = tr["flat"]
Xtr = np.concatenate([f[:, 0:10], f[:, 74:95], f[:, 95:126], tr["aux"], tr["tiers"]], 1)
model = train(Xtr, tr["mask"], tr["action"], epochs=40, seed=0); mu, sd = model.norm

@torch.no_grad()
def pol(env, agent, obs, mask, rng):
    x = np.concatenate([np.asarray(obs["scalars"], np.float32).ravel(),
                        np.asarray(obs["opponents"], np.float32).ravel(),
                        np.asarray(obs["gods"], np.float32).ravel(), slot_features(env, agent),
                        augment_tiers(env, agent)])
    xt = torch.from_numpy(((x - mu) / sd).astype(np.float32))[None]
    m = torch.from_numpy(np.asarray(mask, dtype=bool))[None]
    return int(torch.argmax(model(xt, m), dim=1).item())

env = make_env(default_content())
ev = [play(env, s, pol, scripted_policy, check_teacher=True) for s in range(20000, 22000)]
s_ = summarize(ev)
tot, hit = {}, {}
for e in ev:
    for k, v in e.type_total.items(): tot[k] = tot.get(k, 0) + v
    for k, v in e.type_hits.items(): hit[k] = hit.get(k, 0) + v
out = {"placement": s_, "illegal_A": int(sum(e.illegal["A"] for e in ev)),
       "agree_clone_states": {k: {"n": tot[k], "agree": round(hit.get(k, 0) / tot[k], 4)} for k in tot}}
(R / "big_eval_tiers.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("diff", round(s_["diff_A_minus_B"], 4), s_["ci95_diff"], "illegal", out["illegal_A"], flush=True)
for k, v in sorted(out["agree_clone_states"].items(), key=lambda kv: -kv[1]["n"]): print(" ", k, v, flush=True)
print("done", flush=True)
