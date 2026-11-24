"""Chuyen giao tren noi dung that (CDragon latest 18.7). Dac trung: uni (universal + tier, 85 chieu).
Ba phep so, moi phep 5 seed torch (0-4), epoch 40, bao cao theo loai hanh dong (exact, >=2 hop le):
 (1) Set 17: model huan luyen tren SYNTHETIC (uni/train) -> test Set 17 ; model huan luyen tren Set 17 -> test Set 17
 (2) Set 18 roster duoi quy tac Set 17: model tren Set 17 -> test Set 18 ; model tren Set 18 -> test Set 18
Kiem tra: chieu uni giong nhau tren moi noi dung."""
import json, sys
from pathlib import Path
import numpy as np
import torch
from tft_sim.bc_train import train
from tft_sim.tftgoat import action_type

R = Path(sys.argv[1]); R.mkdir(parents=True, exist_ok=True)
REAL = Path(sys.argv[2]); SYN = Path(sys.argv[3])
L = lambda p: np.load(p)
syn_tr = L(SYN / "train.npz"); s17_tr = L(REAL / "s17_train.npz"); s17_te = L(REAL / "s17_test.npz")
s18_tr = L(REAL / "s18_train.npz"); s18_te = L(REAL / "s18_test.npz")
for nm, z in [("syn_tr", syn_tr), ("s17_tr", s17_tr), ("s17_te", s17_te), ("s18_tr", s18_tr), ("s18_te", s18_te)]:
    assert z["uni"].shape[1] == 85, (nm, z["uni"].shape)
print("uni width 85 on all sets", flush=True)

def ev(model, z):
    X = z["uni"]; mu, sd = model.norm
    M = z["mask"].astype(bool); y = z["action"]; ge = M.sum(1) >= 2
    with torch.no_grad():
        p = torch.argmax(model(torch.from_numpy(((X - mu) / sd).astype(np.float32)), torch.from_numpy(M)), 1).numpy()
    names = np.array([action_type(int(a)) for a in y])
    res = {"overall": float((p == y)[ge].mean())}
    for t in np.unique(names[ge]):
        s = ge & (names == t)
        res[t] = float((p == y)[s].mean())
    return res

def run(train_z, test_z, name):
    out = []
    for seed in range(5):
        m = train(train_z["uni"], train_z["mask"], train_z["action"], epochs=40, seed=seed)
        out.append(ev(m, test_z))
    keys = sorted({k for o in out for k in o})
    agg = {k: {"mean": round(float(np.mean([o[k] for o in out if k in o])), 4),
               "min": round(float(np.min([o[k] for o in out if k in o])), 4),
               "max": round(float(np.max([o[k] for o in out if k in o])), 4)} for k in keys}
    print(name, {k: v["mean"] for k, v in agg.items() if k in ("overall", "BUY_SHOP", "BUY_XP", "PASS", "REROLL", "PICK_AUGMENT", "REROLL_AUGMENT")}, flush=True)
    return agg

res = {"label": "CDragon latest (18.7). Set 17 block: TFTSet17; Set 18 roster: TFTSet18",
       "S17_syn_to_S17": run(syn_tr, s17_te, "syn->S17"),
       "S17_S17_to_S17": run(s17_tr, s17_te, "S17->S17"),
       "S18_S17_to_S18": run(s17_tr, s18_te, "S17 rules->S18"),
       "S18_S18_to_S18": run(s18_tr, s18_te, "S18->S18")}
(R / "transfer_real.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
print("done", flush=True)
