"""Huan luyen 2 bien the BC, do dong y tren val, roi danh gia tren seed test 1000-1199."""
import json, sys, time
import numpy as np
import torch
from pathlib import Path
from tft_sim.tftgoat import default_content
from tft_sim.bc_train import features, policy_from, train, val_agreement
from tft_sim.tftgoat import make_env, play, random_policy, scripted_policy, summarize

S = Path(sys.argv[1]); R = Path(sys.argv[2]); R.mkdir(parents=True, exist_ok=True)
tr = np.load(S / "train.npz"); va = np.load(S / "val.npz")
res = {"content": "synthetic (full-recipe content, tft_sim.content)", "train_rows": int(len(tr["action"])),
       "val_rows": int(len(va["action"])), "variants": {}}
env = make_env(default_content())
for variant in ["flat", "flat+slot"]:
    t0 = time.time()
    Xtr, Xva = features(tr, variant), features(va, variant)
    model = train(Xtr, tr["mask"], tr["action"], epochs=3)
    acc = val_agreement(model, Xva, va["mask"], va["action"])
    torch.save({"state": model.state_dict(), "norm": model.norm, "variant": variant}, R / f"bc_{variant}.pt")
    pol = policy_from(model, variant)
    ev_rand, ev_scr = [], []
    agree = {}; tot = {}
    from tft_sim.tftgoat import action_type
    for s in range(1000, 1200):
        lr_ = play(env, s, pol, random_policy, check_teacher=True)
        ev_rand.append(lr_)
        for k, v in lr_.type_total.items(): tot[k] = tot.get(k, 0) + v
        for k, v in lr_.type_hits.items(): agree[k] = agree.get(k, 0) + v
    for s in range(1000, 1200):
        ev_scr.append(play(env, s, pol, scripted_policy))
    res["variants"][variant] = {
        "val_teacher_agreement": round(acc, 4),
        "vs_random": summarize(ev_rand),
        "vs_scripted": summarize(ev_scr),
        "per_type_agreement_on_clone_states": {k: {"n": tot[k], "agree": round(agree.get(k, 0) / tot[k], 4)} for k in tot},
        "elapsed_s": round(time.time() - t0, 1),
    }
    print(variant, json.dumps(res["variants"][variant], ensure_ascii=False)[:600], flush=True)
(R / "bc_results.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
print("done")
