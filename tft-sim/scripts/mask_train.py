"""Huan luyen clone v4 voi mask nhom (mask_exp.py). Args: cond data_dir.
data_dir chua train.npz va test.npz (uni3, mask, action). 40 epoch, seed 0 (mac dinh cua bc_v4).
Luu checkpoint results/checkpoints/mask_<cond>.pt (co fmask), ket qua results/fixed/real/mask_<cond>_bc.json."""
import json, sys
from pathlib import Path
import numpy as np
import torch
sys.path.insert(0, str(Path(__file__).parent))
from mask_exp import fmask_for, apply_fmask
from tft_sim.bc_train import train, val_agreement
from tft_sim.tftgoat import action_type

cond, D = sys.argv[1], Path(sys.argv[2])
fm = fmask_for(cond)
tr = np.load(D / "train.npz"); te = np.load(D / "test.npz")
Xtr = apply_fmask(tr["uni3"], fm); Mtr, ytr = tr["mask"], tr["action"]
Xte = apply_fmask(te["uni3"], fm); Mte = te["mask"].astype(bool); yte = te["action"]
names = np.array([action_type(int(a)) for a in yte])
ge = Mte.sum(1) >= 2
m = train(Xtr, Mtr, ytr, epochs=40, seed=0)
overall = val_agreement(m, Xte, Mte, yte)
mu, sd = m.norm
with torch.no_grad():
    p = torch.argmax(m(torch.from_numpy(((Xte - mu) / sd).astype(np.float32)), torch.from_numpy(Mte)), 1).numpy()
per = {str(t): round(float((p == yte)[ge & (names == t)].mean()), 4) for t in np.unique(names[ge])}
Path("results/checkpoints").mkdir(parents=True, exist_ok=True)
torch.save({"state": m.state_dict(), "mu": mu, "sd": sd, "in_dim": 185, "fmask": fm, "cond": cond},
           f"results/checkpoints/mask_{cond}.pt")
Path("results/fixed/real").mkdir(parents=True, exist_ok=True)
Path(f"results/fixed/real/mask_{cond}_bc.json").write_text(json.dumps(
    {"cond": cond, "dims": int(fm.sum()), "train_rows": int(len(ytr)), "test_rows": int(len(yte)),
     "overall_test": round(overall, 4), "per_type_ge2": per}, ensure_ascii=False, indent=2), encoding="utf-8")
print("BCDONE", cond, round(overall, 4), per, flush=True)
