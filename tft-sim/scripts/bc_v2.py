"""Huan luyen clone v2 (uni2, 179 chieu) tren du lieu teacher v3. 40 epoch, 3 seed torch (0,1,2).
Bao do khop theo loai tren test (chi dong >=2 hop le), seed 0 luu checkpoint de choi."""
import json, sys
from pathlib import Path
import numpy as np
import torch
from tft_sim.bc_train import train, val_agreement
from tft_sim.tftgoat import action_type

D = Path(sys.argv[1]); R = Path("results/fixed/real"); R.mkdir(parents=True, exist_ok=True)
tr = np.load(D / "train.npz"); te = np.load(D / "test.npz")
Xtr, Mtr, ytr = tr["uni2"], tr["mask"], tr["action"]
Xte, Mte, yte = te["uni2"], te["mask"].astype(bool), te["action"]
names = np.array([action_type(int(a)) for a in yte])
ge = Mte.sum(1) >= 2
out = {"train_rows": int(len(ytr)), "test_rows": int(len(yte)), "epochs": 40, "seeds": {}}
for seed in range(3):
    m = train(Xtr, Mtr, ytr, epochs=40, seed=seed)
    overall = val_agreement(m, Xte, Mte, yte)
    per = {}
    mu, sd = m.norm
    with torch.no_grad():
        p = torch.argmax(m(torch.from_numpy(((Xte - mu) / sd).astype(np.float32)), torch.from_numpy(Mte)), 1).numpy()
    for t in np.unique(names[ge]):
        s = ge & (names == t)
        per[str(t)] = round(float((p == yte)[s].mean()), 4)
    out["seeds"][seed] = {"overall": round(overall, 4), "per_type": per}
    print("seed", seed, "overall", round(overall, 4), per, flush=True)
    if seed == 0:
        torch.save({"state": m.state_dict(), "mu": mu, "sd": sd, "in_dim": Xtr.shape[1]}, D / "clone_v2_seed0.pt")
(R / "bc_v2.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("BCDONE", flush=True)
