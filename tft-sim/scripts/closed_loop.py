"""Closed loop: mo hinh universal (huan luyen tren A, 40 epoch, seed 0) choi voi scripted tren seed moi 10000-10199.
Hai noi dung: A (default) va B (hoan vi). Bao cao: illegal, diff hang +- CI, dong y theo loai tren trang thai clone (>=2 hop le)."""
import json, sys
from pathlib import Path
import numpy as np
import torch
from tft_sim.bc_train import train
from tft_sim.tftgoat import (default_content, make_env, play, scripted_policy, slot_features, summarize)
from tft_sim.content_b import build_shuffled_content

SA = Path(sys.argv[1]); R = Path(sys.argv[2]); R.mkdir(parents=True, exist_ok=True)
SEEDS = range(10000, 10200)
SCAL = slice(0, 10)

tr = np.load(SA / "train.npz")
# Feature cho tung quan sat theo KEY (khong cat theo offset): scalars, opponents, gods, slot.
def uni_obs(env, agent, obs):
    return np.concatenate([np.asarray(obs["scalars"], np.float32).ravel(),
                           np.asarray(obs["opponents"], np.float32).ravel(),
                           np.asarray(obs["gods"], np.float32).ravel(),
                           slot_features(env, agent)])

# Huan luyen: lay feature universal tu train.npz bang offset da kiem tra (flat 0:10, 74:95, 95:126)
Xtr = np.concatenate([tr["flat"][:, 0:10], tr["flat"][:, 74:95], tr["flat"][:, 95:126], tr["aux"]], 1)
model = train(Xtr, tr["mask"], tr["action"], epochs=40, seed=0)
mu, sd = model.norm
# Kiem tra: feature theo key tren mot quan sat phai co cung so chieu voi Xtr
env_a = make_env(default_content())
obs, infos = env_a.reset(seed=1)
ag = env_a.agents[0]
assert uni_obs(env_a, ag, obs[ag]).shape[0] == Xtr.shape[1], "universal width mismatch"

@torch.no_grad()
def pol(env, agent, obs, mask, rng):
    x = uni_obs(env, agent, obs)  # play() truyen obs[agent] (dict cua mot quan sat)
    xt = torch.from_numpy(((x - mu) / sd).astype(np.float32))[None]
    m = torch.from_numpy(np.asarray(mask, dtype=bool))[None]
    return int(torch.argmax(model(xt, m), dim=1).item())

out = {"epochs": 40, "seeds": "10000-10199"}
for name, content in [("A", default_content()), ("B", build_shuffled_content())]:
    env = make_env(content)
    ev = [play(env, s, pol, scripted_policy, check_teacher=True) for s in SEEDS]
    s_ = summarize(ev)
    tot = {}; hit = {}
    for e in ev:
        for k, v in e.type_total.items(): tot[k] = tot.get(k, 0) + v
        for k, v in e.type_hits.items(): hit[k] = hit.get(k, 0) + v
    out[name] = {"placement": s_, "illegal_A": sum(e.illegal["A"] for e in ev),
                 "agree_clone_states": {k: {"n": tot[k], "agree": round(hit.get(k, 0) / tot[k], 4)} for k in tot}}
    print(name, out[name]["placement"].get("diff_A_minus_B"), out[name]["placement"].get("ci95_diff"),
          "illegal", out[name]["illegal_A"], flush=True)
(R / "closed_loop.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("done", flush=True)
