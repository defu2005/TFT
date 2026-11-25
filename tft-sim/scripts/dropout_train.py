"""Huan luyen MOT mo hinh group-dropout (model-plan 10.10). Args: data_dir.
data_dir chua train.npz, test.npz (uni3, mask, action) - cung du lieu voi mask_train.py.
40 epoch, seed 0 (bc_train.train, khong sua). Kiem tra truoc khi choi:
  (1) do chinh xac tren test tung dieu kien co dinh, so voi mo hinh mask_<X> rieng (mask_<X>_bc.json);
  (2) leak test: doi cac cot bi an cua dieu kien X thi logit khong doi.
Luu results/checkpoints/drop.pt, results/fixed/real/drop_bc.json."""
import json, sys
from pathlib import Path
import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).parent))
from dropout_exp import CONDS, N_IN, row_conditions, dropout_input  # noqa: E402
from mask_exp import CONDITIONS  # noqa: E402
from tft_sim.bc_train import train, val_agreement, MaskedMLP  # noqa: E402

D = Path(sys.argv[1])
tr = np.load(D / "train.npz"); te = np.load(D / "test.npz")
Xtr_raw, Mtr, ytr = tr["uni3"], tr["mask"], tr["action"]
Xte_raw, Mte, yte = te["uni3"], te["mask"].astype(bool), te["action"]
ctr = row_conditions(len(ytr), seed=0)
Xtr = dropout_input(Xtr_raw, ctr)
print("train rows per cond", {c: int((ctr == c).sum()) for c in CONDS}, flush=True)

m = train(Xtr, Mtr, ytr, epochs=40, seed=0)
mu, sd = m.norm

# (1) do chinh xac tung dieu kien co dinh, so voi mo hinh rieng
ref = {c: json.loads(Path(f"results/fixed/real/mask_{c}_bc.json").read_text(encoding="utf-8"))["overall_test"]
       for c in CONDS}
fixed = {}
for c in CONDS:
    acc = val_agreement(m, dropout_input(Xte_raw, c), Mte, yte)
    fixed[c] = {"drop": round(acc, 4), "dedicated_mask": ref[c], "gap": round(acc - ref[c], 4)}
    print("TEST", c, fixed[c], flush=True)
mixed_te = row_conditions(len(yte), seed=1)
fixed["mixed_test"] = round(val_agreement(m, dropout_input(Xte_raw, mixed_te), Mte, yte), 4)

# (2) leak test: doi cot bi an cua X thi logit khong doi
rng = np.random.default_rng(123)
sub = slice(0, 20000)
X0 = Xte_raw[sub].astype(np.float32); M0 = Mte[sub]
leak = {}
with torch.no_grad():
    for c in CONDS:
        hidden = sorted(set(range(185)) - set(CONDITIONS[c]))
        X1 = X0.copy()
        X1[:, hidden] = rng.normal(0, 1, size=(len(X0), len(hidden))).astype(np.float32) * 10
        def logits(X):
            xt = torch.from_numpy(((dropout_input(X, c) - mu) / sd).astype(np.float32))
            return m(xt, torch.from_numpy(M0)).numpy()
        l0, l1 = logits(X0), logits(X1)
        fin = np.isfinite(l0) & np.isfinite(l1)
        diff = float(np.max(np.abs(np.where(fin, l0 - l1, 0.0))))
        leak[c] = {"hidden_dims": len(hidden), "max_abs_logit_change": diff}
        print("LEAK", c, leak[c], flush=True)

Path("results/checkpoints").mkdir(parents=True, exist_ok=True)
torch.save({"state": m.state_dict(), "mu": mu, "sd": sd, "in_dim": N_IN, "kind": "dropout",
            "presence": {"a": [1, 0, 0, 0], "c": [1, 1, 1, 0], "full": [1, 1, 1, 1]}},
           "results/checkpoints/drop.pt")
Path("results/fixed/real").mkdir(parents=True, exist_ok=True)
Path("results/fixed/real/drop_bc.json").write_text(json.dumps(
    {"model": "drop", "in_dim": N_IN, "train_rows": int(len(ytr)), "test_rows": int(len(yte)),
     "train_cond_counts": {c: int((ctr == c).sum()) for c in CONDS},
     "test_fixed": fixed, "leak": leak}, ensure_ascii=False, indent=2), encoding="utf-8")
print("DROPDONE", flush=True)
