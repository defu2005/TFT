"""Phan tich giai dau pool drop (model-plan 10.10). Args: out.json [out2.json ...] (cac shard league2 run ... drop).
Moi lobby co dung mot ghe cho moi slot, nen chenh theo cap = placement(X) - placement(Y) trong cung lobby.
CI95 bootstrap theo lobby (2000 lan, seed 0). Tieu chi dang ky:
  1. v4 - v4_null: CI95 chua 0.
  2. drop@X - mask_X, X in {full, c, a}: CI95 nam hoan toan trong [-0.2, +0.2].
Ghi results/fixed/real/dropout_league.json."""
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np

rows = []
for f in sys.argv[1:]:
    rows += json.loads(Path(f).read_text(encoding="utf-8"))

by_lobby = defaultdict(dict)
for r in rows:
    by_lobby[r["seed"]][r["policy"]] = r["placement"]
complete = all(r["completed"] for r in rows)
illegal = sum(r["illegal"] for r in rows)
lobbies = sorted(s for s, d in by_lobby.items() if len(d) == 8)
print("lobbies", len(lobbies), "rows", len(rows), "completed_all", complete, "illegal", illegal)

rng = np.random.default_rng(0)


def paired(a, b):
    d = np.array([by_lobby[s][a] - by_lobby[s][b] for s in lobbies], float)
    idx = rng.integers(0, len(d), size=(2000, len(d)))
    boot = d[idx].mean(1)
    return {"mean": round(float(d.mean()), 4),
            "ci95": [round(float(np.percentile(boot, 2.5)), 4), round(float(np.percentile(boot, 97.5)), 4)]}


res = {"lobbies": len(lobbies), "rows": len(rows), "completed_all": complete, "illegal": illegal, "pairs": {}}
res["pairs"]["v4 - v4_null"] = paired("v4", "v4_null")
for x in ["full", "c", "a"]:
    res["pairs"][f"drop@{x} - mask_{x}"] = paired(f"drop@{x}", f"mask_{x}")
for k, v in res["pairs"].items():
    print(k, v)

c1 = res["pairs"]["v4 - v4_null"]["ci95"]
res["criterion_1_pass"] = c1[0] <= 0 <= c1[1]
res["criterion_2_pass"] = {}
for x in ["full", "c", "a"]:
    lo, hi = res["pairs"][f"drop@{x} - mask_{x}"]["ci95"]
    res["criterion_2_pass"][x] = bool(-0.2 <= lo and hi <= 0.2)
print("CRIT1", res["criterion_1_pass"], "CRIT2", res["criterion_2_pass"])

# Dem ghe theo slot (kiem tra can bang)
seats = defaultdict(int)
for r in rows:
    seats[r["policy"]] += 1
res["seats_per_slot"] = dict(seats)
Path("results/fixed/real").mkdir(parents=True, exist_ok=True)
Path("results/fixed/real/dropout_league.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
