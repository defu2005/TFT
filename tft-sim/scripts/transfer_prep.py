"""Buoc 2 (kiem tra void): huan luyen lau hon, va mo hinh khong noi dung (universal-only:
scalars + opponents + gods + aux slot) tren A, do dong y BUY_SHOP tren val (hang >= 2 hop le).
Flat layout: scalars 0:10, shop 10:15, bench 15:42, board 42:72, traits 72:74, opponents 74:95, gods 95:126."""
import json, sys, time
from pathlib import Path
import numpy as np
import torch
from tft_sim.bc_train import MaskedMLP, train
from tft_sim.tftgoat import action_type

S = Path(sys.argv[1]); R = Path(sys.argv[2]); R.mkdir(parents=True, exist_ok=True)
tr = np.load(S / "train.npz"); va = np.load(S / "val.npz")
SCAL = slice(0, 10); OPP = slice(74, 95); GODS = slice(95, 126)

def feats(npz, variant):
    f = npz["flat"]
    if variant == "flat": return f
    if variant == "flat+slot": return np.concatenate([f, npz["aux"]], 1)
    if variant == "universal": return np.concatenate([f[:, SCAL], f[:, OPP], f[:, GODS], npz["aux"]], 1)
    raise ValueError(variant)

Mv = np.asarray(va["mask"]).astype(bool); yv = va["action"]; multi = Mv.sum(1) >= 2
names = np.array([action_type(int(a)) for a in yv])
bs = multi & (names == "BUY_SHOP")
res = {"rows_val_ge2": int(multi.sum()), "rows_val_buyshop_ge2": int(bs.sum()), "runs": {}}
for variant in ["flat", "flat+slot", "universal"]:
    Xtr, Xva = feats(tr, variant), feats(va, variant)
    for ep in [3, 10]:
        t0 = time.time()
        m = train(Xtr, tr["mask"], tr["action"], epochs=ep)
        mu, sd = m.norm
        with torch.no_grad():
            pred = torch.argmax(m(torch.from_numpy(((Xva - mu) / sd).astype(np.float32)),
                                  torch.from_numpy(Mv)), 1).numpy()
        key = f"{variant}|ep{ep}"
        res["runs"][key] = {
            "val_ge2": round(float((pred[multi] == yv[multi]).mean()), 4),
            "buyshop_ge2": round(float((pred[bs] == yv[bs]).mean()), 4),
            "elapsed_s": round(time.time() - t0, 1)}
        print(key, res["runs"][key], flush=True)
        torch.save({"state": m.state_dict(), "norm": m.norm, "variant": variant, "epochs": ep},
                   R / f"A_{variant}_ep{ep}.pt")
(R / "transfer_prep_check.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
print("done", flush=True)
