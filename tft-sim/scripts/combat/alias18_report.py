"""Bao cao anh huong alias: p_off vs p_on tren cap sim Set 18 (generic). Decisive = p_off >=0.9 hoac <=0.1.
Bootstrap theo lobby, 2000 lan. Usage: python alias18_report.py p_off.json p_on.json out.json"""
import json, sys
import numpy as np
off = json.load(open(sys.argv[1])); on = json.load(open(sys.argv[2]))
assert [r["source"] for r in off] == [r["source"] for r in on]
po = np.array([r["p"] for r in off]); pn = np.array([r["p"] for r in on])
lob = np.array([int(r["source"].split()[1]) for r in off])
dec = (po >= 0.9) | (po <= 0.1)
flip = ((po > 0.5) != (pn > 0.5))
rng = np.random.default_rng(0)
L = np.unique(lob[dec]); byl = {l: flip[dec & (lob == l)] for l in L}
pt = float(flip[dec].mean()) if dec.any() else None
reps = [np.concatenate([byl[l] for l in rng.choice(L, len(L), replace=True)]).mean() for _ in range(2000)] if dec.any() else []
out = {"label": "sim (engine Set 18, alias on/off; khong phai tran that)", "n_pairs": len(po),
       "n_lobbies": int(len(np.unique(lob))), "decisive_n": int(dec.sum()),
       "flip_rate_decisive": round(pt, 4) if pt is not None else None,
       "flip_ci95": [round(float(np.percentile(reps, 2.5)), 4), round(float(np.percentile(reps, 97.5)), 4)] if reps else None,
       "mean_abs_dp_all": round(float(np.abs(po - pn).mean()), 4)}
json.dump(out, open(sys.argv[3], "w"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
