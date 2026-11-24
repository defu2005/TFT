"""Buoc 3: universal + tier augment (3 cot), huan luyen tren A (tiers/train), danh gia tren A val (tiers/val).
Bao cao PICK_AUGMENT, REROLL_AUGMENT, BUY_SHOP (hang >=2 hop le). Dem so dong REROLL_AUGMENT."""
import json, sys
from pathlib import Path
import numpy as np
import torch
from tft_sim.bc_train import train
from tft_sim.tftgoat import action_type

S = Path(sys.argv[1]); R = Path(sys.argv[2]); R.mkdir(parents=True, exist_ok=True)
SCAL = slice(0, 10); OPP = slice(74, 95); GODS = slice(95, 126)
def feats(z):
    f = z["flat"]
    return np.concatenate([f[:, SCAL], f[:, OPP], f[:, GODS], z["aux"], z["tiers"]], 1)

tr = np.load(S / "train.npz"); va = np.load(S / "val.npz")
out = {"rows_train_REROLL_AUGMENT": int((tr["action"] == 42).sum()),
       "rows_train_PICK_AUGMENT": int(((tr["action"] >= 36) & (tr["action"] <= 38)).sum()), "runs": {}}
Xtr, Xva = feats(tr), feats(va)
M = np.asarray(va["mask"]).astype(bool); y = va["action"]; ge = M.sum(1) >= 2
names = np.array([action_type(int(a)) for a in y])
for ep in [10, 40]:
    m = train(Xtr, tr["mask"], tr["action"], epochs=ep, seed=0); mu, sd = m.norm
    with torch.no_grad():
        p = torch.argmax(m(torch.from_numpy(((Xva - mu) / sd).astype(np.float32)), torch.from_numpy(M)), 1).numpy()
    row = {}
    for t in ["BUY_SHOP", "PICK_AUGMENT", "REROLL_AUGMENT"]:
        sel = ge & (names == t)
        row[t] = {"n": int(sel.sum()), "agree": round(float((p == y)[sel].mean()), 4) if sel.sum() else None}
    out["runs"][f"ep{ep}"] = row
    print(ep, row, flush=True)
(R / "aug_train.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print("done", flush=True)
