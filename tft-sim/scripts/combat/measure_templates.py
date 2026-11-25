"""Do template (Set 17) theo advisor: ~2000 cap cung vong tu CA 100 lobby, khong chia train/test.
Cau hinh: hand (engine viet tay), template (mo ta+bien, fallback default_ability), generic, none.
Chi so: dong thuan voi hand tren cap quyet dinh; |p - p_hand| trung binh; hieu theo cap voi none
(bootstrap theo lobby, 2000 lan). Luu bang tung cap (.csv.gz) de co the tinh lai.

Usage: python measure_templates.py pairs17_v2.jsonl out_dir
"""
import csv, gzip, json, sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import fight as F  # noqa: E402
from tft_sim.real_content import build_real  # noqa: E402

F.set_content(17, build_real("TFTSet17"))

CONFIGS = {"hand": ("hand", True), "template": ("template", True), "generic": ("generic", True), "none": ("none", True)}
N = 20


def lobby_of(rec):
    return int(rec["source"].split()[1])


def _eval(rec):
    return {k: F.predict_win(rec, N, ab, it, 0)["p_a"] for k, (ab, it) in CONFIGS.items()}


def main(inp, outdir):
    recs = [r for r in F.load_jsonl(inp) if r["source"].startswith("same")]
    rng = np.random.default_rng(0)
    pick = sorted(rng.choice(len(recs), size=min(2000, len(recs)), replace=False))
    sample = [recs[i] for i in pick]
    with Pool(4) as pool:
        res = pool.map(_eval, sample, chunksize=8)
    out = Path(outdir); out.mkdir(parents=True, exist_ok=True)
    with gzip.open(out / "template_pairs_288000.csv.gz", "wt", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["lobby", "source"] + list(CONFIGS))
        for r, pv in zip(sample, res):
            w.writerow([lobby_of(r), r["source"]] + [round(pv[k], 4) for k in CONFIGS])
    # metrics
    ph = np.array([pv["hand"] for pv in res]); dec = (ph >= 0.9) | (ph <= 0.1)
    lob = np.array([lobby_of(r) for r in sample])
    m = {"n_pairs": len(sample), "decisive_frac": round(float(dec.mean()), 4), "n_decisive": int(dec.sum())}
    def agree(name):
        v = np.array([pv[name] for pv in res])
        return (v > 0.5) == (ph > 0.5), v
    def boot_diff(a, b):
        ag_a, _ = agree(a); ag_b, _ = agree(b)
        d = (ag_a.astype(float) - ag_b.astype(float))
        pts = d[dec].mean()
        L = np.unique(lob[dec]); byl = {l: d[dec & (lob == l)] for l in L}
        reps = []
        for _ in range(2000):
            pick_l = rng.choice(L, size=len(L), replace=True)
            reps.append(np.concatenate([byl[l] for l in pick_l]).mean())
        return round(float(pts), 4), [round(float(np.percentile(reps, 2.5)), 4), round(float(np.percentile(reps, 97.5)), 4)]
    for name in ("template", "generic", "none"):
        ag, v = agree(name)
        m[name] = {"agree_on_decisive": round(float(ag[dec].mean()), 4),
                   "mean_abs_gap_vs_hand": round(float(np.abs(v - ph).mean()), 4)}
    m["template_minus_none"] = boot_diff("template", "none")
    m["template_minus_generic"] = boot_diff("template", "generic")
    m["generic_minus_none"] = boot_diff("generic", "none")
    Path(out / "template_metrics_288000.json").write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(m, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
