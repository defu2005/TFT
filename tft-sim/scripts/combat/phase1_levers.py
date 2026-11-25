"""Phase 1 (sim Set 17): xep hang don bay bang ti le dao chieu so voi 'hand' tren cap quyet dinh cua hand.
Quy tac (khoa truoc khi chay, xem docs/model-plan.md muc 11): quyet dinh = p_hand >= 0.9 hoac <= 0.1;
dao chieu = (p_cfg > 0.5) != (p_hand > 0.5); CI 95% bootstrap theo lobby, 2000 lan.
Usage: python phase1_levers.py pairs17_v2.jsonl out_dir
"""
import csv, gzip, json, sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import fight as F  # noqa: E402
from tft_sim.real_content import build_real  # noqa: E402

F.set_content(17, build_real("TFTSet17"))
N = 20
CONFIGS = {
    "hand": dict(ability="hand", items=True, augments=True, traits=True, novars=False),
    "hand_noaug": dict(ability="hand", items=True, augments=False, traits=True, novars=False),
    "hand_noitems": dict(ability="hand", items=False, augments=True, traits=True, novars=False),
    "hand_notraits": dict(ability="hand", items=True, augments=True, traits=False, novars=False),
    "generic": dict(ability="generic", items=True, augments=True, traits=True, novars=False),
    "generic_novars": dict(ability="generic", items=True, augments=True, traits=True, novars=True),
    "none": dict(ability="none", items=True, augments=True, traits=True, novars=False),
}


def lobby_of(rec):
    return int(rec["source"].split()[1])


def _eval(rec):
    return {k: F.predict_win(rec, N, seed0=0, **kw)["p_a"] for k, kw in CONFIGS.items()}


def main(inp, outdir):
    recs = [r for r in F.load_jsonl(inp) if r["source"].startswith("same")]
    rng = np.random.default_rng(0)
    pick = sorted(rng.choice(len(recs), size=min(2000, len(recs)), replace=False))
    sample = [recs[i] for i in pick]
    with Pool(4) as pool:
        res = pool.map(_eval, sample, chunksize=8)
    out = Path(outdir); out.mkdir(parents=True, exist_ok=True)
    with gzip.open(out / "phase1_pairs.csv.gz", "wt", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["lobby", "source"] + list(CONFIGS))
        for r, pv in zip(sample, res):
            w.writerow([lobby_of(r), r["source"]] + [round(pv[k], 4) for k in CONFIGS])
    ph = np.array([pv["hand"] for pv in res])
    dec = (ph >= 0.9) | (ph <= 0.1)
    lob = np.array([lobby_of(r) for r in sample])
    L = np.unique(lob[dec])
    m = {"n_pairs": len(sample), "n_decisive": int(dec.sum()), "rule": "dao chieu so voi hand tren cap quyet dinh cua hand; bootstrap theo lobby 2000",
         "configs": {}}
    for name in CONFIGS:
        if name == "hand":
            continue
        pv = np.array([x[name] for x in res])
        flip = (pv > 0.5) != (ph > 0.5)
        d = flip[dec].astype(float)
        byl = {l: flip[dec & (lob == l)].astype(float) for l in L}
        reps = [np.concatenate([byl[l] for l in rng.choice(L, len(L), replace=True)]).mean() for _ in range(2000)]
        changed_any = int((np.abs(pv - ph) > 1e-9).sum())
        m["configs"][name] = {"flip_rate_decisive": round(float(d.mean()), 4),
                              "ci95": [round(float(np.percentile(reps, 2.5)), 4), round(float(np.percentile(reps, 97.5)), 4)],
                              "pairs_changed_any": changed_any,
                              "mean_abs_gap_vs_hand": round(float(np.abs(pv - ph).mean()), 4)}
    (out / "phase1_levers.json").write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(m, ensure_ascii=False, indent=1), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
