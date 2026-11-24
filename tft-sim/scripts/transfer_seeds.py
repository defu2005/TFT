"""Lap lai transfer A->B voi 5 seed torch (0-4) va epoch 10/20/40, 3 bien the.
Bao cao: BUY_SHOP, BUY_XP, REROLL, overall: A->A (val), A->B (test), B->B (test), penalty = B->B - A->B.
train() co tham so seed (mac dinh 0, tu dat torch.manual_seed ben trong): phai truyen seed= de cac lan lap khac nhau."""
import json, sys
from pathlib import Path
import numpy as np
import torch
from tft_sim.bc_train import train
from tft_sim.tftgoat import action_type

SA = Path(sys.argv[1]); SB = Path(sys.argv[2]); R = Path(sys.argv[3]); R.mkdir(parents=True, exist_ok=True)
SCAL = slice(0, 10); OPP = slice(74, 95); GODS = slice(95, 126)
def feats(z, v):
    f = z["flat"]
    if v == "flat": return f
    if v == "flat+slot": return np.concatenate([f, z["aux"]], 1)
    return np.concatenate([f[:, SCAL], f[:, OPP], f[:, GODS], z["aux"]], 1)

trA = np.load(SA / "train.npz"); vaA = np.load(SA / "val.npz")
trB = np.load(SB / "B_train.npz"); teB = np.load(SB / "B_test.npz")

def acc(model, z, v, types=("BUY_SHOP", "BUY_XP", "REROLL")):
    X = feats(z, v); mu, sd = model.norm
    M = z["mask"].astype(bool); y = z["action"]
    with torch.no_grad():
        p = torch.argmax(model(torch.from_numpy(((X - mu) / sd).astype(np.float32)),
                               torch.from_numpy(M)), 1).numpy()
    ge = M.sum(1) >= 2
    names = np.array([action_type(int(a)) for a in y])
    out = {"overall": float((p == y)[ge].mean())}
    for t in types:
        s = ge & (names == t)
        out[t] = float((p == y)[s].mean())
    return out

rows = []
for v in ["flat", "flat+slot", "universal"]:
    for ep in [10, 20, 40]:
        for seed in range(5):
            mA = train(feats(trA, v), trA["mask"], trA["action"], epochs=ep, seed=seed)
            mB = train(feats(trB, v), trB["mask"], trB["action"], epochs=ep, seed=seed)
            aa = acc(mA, vaA, v); ab = acc(mA, teB, v); bb = acc(mB, teB, v)
            rows.append({"variant": v, "epochs": ep, "seed": seed, "A_to_A_val": aa, "A_to_B_test": ab, "B_to_B_test": bb})
            print(v, ep, seed, "BUY_SHOP A->B", round(ab["BUY_SHOP"], 4), "B->B", round(bb["BUY_SHOP"], 4), flush=True)
(R / "transfer_seeds.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
print("done", flush=True)
