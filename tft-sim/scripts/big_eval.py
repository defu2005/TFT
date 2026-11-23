"""Do do phan giai placement voi 2000 lobby (seed 20000-21999, moi). So sanh:
- closed-loop universal (A) vs scripted, noi dung A
- scripted co eps=0.1 va eps=0.3 ngau nhien (A) vs scripted, noi dung A (de biet co phan giai duoc muc nho khong)
Ghi CI95 cua hieu hang trung binh theo lobby."""
import json, sys, random
from pathlib import Path
import numpy as np
import torch
from tft_sim.bc_train import train
from tft_sim.tftgoat import default_content, make_env, play, scripted_policy, slot_features, summarize

SA = Path(sys.argv[1]); R = Path(sys.argv[2]); R.mkdir(parents=True, exist_ok=True)
SEEDS = range(20000, 22000)
tr = np.load(SA / "train.npz")
Xtr = np.concatenate([tr["flat"][:, 0:10], tr["flat"][:, 74:95], tr["flat"][:, 95:126], tr["aux"]], 1)
model = train(Xtr, tr["mask"], tr["action"], epochs=40, seed=0); mu, sd = model.norm

@torch.no_grad()
def pol_uni(env, agent, obs, mask, rng):
    x = np.concatenate([np.asarray(obs["scalars"], np.float32).ravel(),
                        np.asarray(obs["opponents"], np.float32).ravel(),
                        np.asarray(obs["gods"], np.float32).ravel(), slot_features(env, agent)])
    xt = torch.from_numpy(((x - mu) / sd).astype(np.float32))[None]
    m = torch.from_numpy(np.asarray(mask, dtype=bool))[None]
    return int(torch.argmax(model(xt, m), dim=1).item())

def eps_policy(eps):
    def pol(env, agent, obs, mask, rng):
        if rng.random() < eps:
            return int(rng.choice(list(np.flatnonzero(mask))))
        return scripted_policy(env, agent, obs, mask, rng)
    return pol

env = make_env(default_content())
out = {"seeds": "20000-21999", "lobbies": len(SEEDS), "results": {}}
for name, pol in [("universal_ep40_vs_scripted", pol_uni), ("eps0.1_vs_scripted", eps_policy(0.1)),
                  ("eps0.3_vs_scripted", eps_policy(0.3))]:
    ev = [play(env, s, pol, scripted_policy) for s in SEEDS]
    s_ = summarize(ev)
    out["results"][name] = {**s_, "illegal_A": int(sum(e.illegal["A"] for e in ev))}
    print(name, round(s_["diff_A_minus_B"], 4), s_["ci95_diff"], "illegal", out["results"][name]["illegal_A"], flush=True)
    (R / "big_eval.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("done", flush=True)
