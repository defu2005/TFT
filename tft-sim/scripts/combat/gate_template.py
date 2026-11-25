"""Cong template (muc 11.2): template vs generic_novars tren cung 2000 cap same cua phase1_levers.
Usage: python gate_template.py pairs17_v2.jsonl out_dir"""
import csv, gzip, json, sys
from multiprocessing import Pool
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
import fight as F  # noqa: E402
from tft_sim.real_content import build_real  # noqa: E402
F.set_content(17, build_real("TFTSet17"))
N = 20
CONFIGS = {"hand": ("hand", True, False), "template": ("template", True, False), "generic_novars": ("generic", True, True)}


def lobby_of(rec):
    return int(rec["source"].split()[1])


def _eval(rec):
    return {k: F.predict_win(rec, N, ab, it, 0, novars=nv)["p_a"] for k, (ab, it, nv) in CONFIGS.items()}


def main(inp, outdir):
    recs = [r for r in F.load_jsonl(inp) if r["source"].startswith("same")]
    rng = np.random.default_rng(0)
    pick = sorted(rng.choice(len(recs), size=min(2000, len(recs)), replace=False))
    sample = [recs[i] for i in pick]
    with Pool(4) as pool:
        res = pool.map(_eval, sample, chunksize=8)
    out = Path(outdir); out.mkdir(parents=True, exist_ok=True)
    with gzip.open(out / "gate_template_pairs.csv.gz", "wt", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["lobby", "source"] + list(CONFIGS))
        for r, pv in zip(sample, res):
            w.writerow([lobby_of(r), r["source"]] + [round(pv[k], 4) for k in CONFIGS])
    ph = np.array([pv["hand"] for pv in res]); dec = (ph >= 0.9) | (ph <= 0.1)
    lob = np.array([lobby_of(r) for r in sample]); H = ph > 0.5
    fl = {k: ((np.array([pv[k] for pv in res]) > 0.5) != H).astype(float) for k in ("template", "generic_novars")}
    d = fl["template"] - fl["generic_novars"]
    L = np.unique(lob[dec]); idx = {l: np.where(dec & (lob == l))[0] for l in L}
    reps = []
    for _ in range(2000):
        s = rng.choice(L, len(L), replace=True)
        reps.append(d[np.concatenate([idx[l] for l in s])].mean())
    lo, hi = np.percentile(reps, [2.5, 97.5])
    m = {"n_pairs": len(sample), "n_decisive": int(dec.sum()),
         "flip_template": round(float(fl["template"][dec].mean()), 4),
         "flip_generic_novars": round(float(fl["generic_novars"][dec].mean()), 4),
         "diff_template_minus_novars": round(float(d[dec].mean()), 4), "ci95": [round(float(lo), 4), round(float(hi), 4)],
         "verdict": "PASS" if hi < 0 else "FAIL"}
    (out / "gate_template.json").write_text(json.dumps(m, indent=1), encoding="utf-8")
    print(json.dumps(m, indent=1), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
