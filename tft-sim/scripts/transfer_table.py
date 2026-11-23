"""Bang tu transfer_seeds.json: mean va range qua 5 seed, cho moi (bien the, epoch)."""
import json, sys
from collections import defaultdict
import numpy as np
from pathlib import Path
rows = json.load(open(sys.argv[1]))
g = defaultdict(list)
for r in rows: g[(r["variant"], r["epochs"])].append(r)
lines = []
hdr = "| bien the | epoch | BUY_SHOP A->B | BUY_SHOP B->B | penalty BUY_SHOP | penalty BUY_XP | penalty REROLL | penalty overall | BUY_SHOP A->A (val) |"
lines.append(hdr); lines.append("|" + "---|" * 9)
def ms(xs):
    xs = np.array(xs) * 100
    return f"{xs.mean():.1f} [{xs.min():.1f}, {xs.max():.1f}]"
def pen(r, k):
    if k == "overall":
        return (r["B_to_B_test"]["overall"] - r["A_to_B_test"]["overall"]) * 100
    return (r["B_to_B_test"][k] - r["A_to_B_test"][k]) * 100
for (v, ep), rs in sorted(g.items(), key=lambda kv: (["flat", "flat+slot", "universal"].index(kv[0][0]), kv[0][1])):
    lines.append(f"| {v} | {ep} | {ms([r['A_to_B_test']['BUY_SHOP'] for r in rs])} | {ms([r['B_to_B_test']['BUY_SHOP'] for r in rs])} | "
                 f"{ms([pen(r,'BUY_SHOP')/100 for r in rs])} | {ms([pen(r,'BUY_XP')/100 for r in rs])} | "
                 f"{ms([pen(r,'REROLL')/100 for r in rs])} | {ms([pen(r,'overall')/100 for r in rs])} | {ms([r['A_to_A_val']['BUY_SHOP'] for r in rs])} |")
txt = "\n".join(lines); print(txt)
Path(sys.argv[2]).write_text(txt + "\n", encoding="utf-8")
