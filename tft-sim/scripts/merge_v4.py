"""Gop cac shard collect_v4 thanh train/val/test theo seed (chia co dinh, khong ngau nhien).
Args: out_dir shard1.npz [shard2.npz ...]
train: seed 300000-301499 | val: 301500-301599 | test: 301600-301999 (dai seed dat truoc, xem cloud-agents.md muc 2).
Kiem tra shape, action trong [0,42], mask hop le, seed trong dai. Loai shard loi, in ra."""
import sys
from pathlib import Path
import numpy as np

SPLITS = {"train": (300000, 301500), "val": (301500, 301600), "test": (301600, 302000)}
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
parts = {k: {"uni3": [], "mask": [], "action": [], "seed": []} for k in SPLITS}
for f in sys.argv[2:]:
    try:
        d = np.load(f)
        assert d["uni3"].shape[1] == 185 and d["mask"].shape[1] == 43, "shape"
        a = d["action"]; assert a.min() >= 0 and a.max() <= 42, "action range"
        assert d["mask"][np.arange(len(a)), a].all(), "action khong hop le"
        assert np.isfinite(d["uni3"]).all(), "NaN/inf"
    except (AssertionError, KeyError, ValueError) as e:
        print("LOAI", f, e, flush=True); continue
    for k, (lo, hi) in SPLITS.items():
        m = (d["seed"] >= lo) & (d["seed"] < hi)
        for key in parts[k]:
            parts[k][key].append(d[key][m])
for k in SPLITS:
    arrs = {key: np.concatenate(v) if v else np.zeros(0) for key, v in parts[k].items()}
    np.savez_compressed(out / f"{k}.npz", **arrs)
    print(k, len(arrs["action"]), "dong", flush=True)
