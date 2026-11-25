"""Muc 11.5: do do nhay emblem tren pairs18_sample.jsonl (generic, items, N=20), off so voi on.
Usage: python emblem_sensitivity.py pairs18_sample.jsonl out.json"""
import json, sys
from multiprocessing import Pool
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
import fight as F  # noqa: E402
from tft_sim.item_alias import build_set18_records  # noqa: E402
from tft_goat.env.traits import trait_counts  # noqa: E402

C, _ = build_set18_records()
F.set_content(18, C)
N = 20


def tiers(units, with_emblem: bool):
    held = [{t for api in u.item_apis if (t := F.emblem_trait_of(api, C))} if with_emblem else set() for u in units]
    cnt = dict(trait_counts([u.champion_api for u in units], C))
    for u, hs in zip(units, held):
        own = C.champions[u.champion_api].traits if u.champion_api in C.champions else ()
        for t in hs:
            if t not in own:
                cnt[t] = cnt.get(t, 0) + 1
    by = {t.name: t for t in C.traits.values()}
    out = {}
    for name, c in cnt.items():
        tr = by.get(name)
        if tr is None:
            continue
        tier = sum(1 for bp in tr.breakpoints if c >= bp)
        if tier:
            out[name] = tier
    return out


def _eval(rec):
    ba, bb, _, _, _ = F.boards_of(rec, True)
    tier_change = any(tiers(b, True) != tiers(b, False) for b in (ba, bb))
    has_emblem = any(api.startswith("DA_18_Emblem") for s in ("a", "b") for u in rec[s]["units"]
                     for api in u.get("items", []))
    off = F.predict_win(rec, N, "generic", True, 0, emblems=False)["p_a"]
    on = F.predict_win(rec, N, "generic", True, 0, emblems=True)["p_a"]
    return off, on, has_emblem, tier_change


def main(inp, out):
    recs = F.load_jsonl(inp)
    with Pool(4) as pool:
        res = pool.map(_eval, recs, chunksize=8)
    off = np.array([r[0] for r in res]); on = np.array([r[1] for r in res])
    he = np.array([r[2] for r in res]); tc = np.array([r[3] for r in res])
    dec = (off >= 0.9) | (off <= 0.1)
    flip = ((on > 0.5) != (off > 0.5)).astype(float)
    d = np.abs(on - off)
    rng = np.random.default_rng(0)
    reps = [flip[rng.choice(len(recs), len(recs))].mean() for _ in range(2000)]
    m = {"n_pairs": len(recs), "pairs_with_emblem_item": int(he.sum()),
         "pairs_with_tier_change": int(tc.sum()), "share_tier_change": round(float(tc.mean()), 4),
         "pairs_p_change_gt_0.05": int((d > 0.05).sum()),
         "flip_rate_all": round(float(flip.mean()), 4),
         "flip_all_ci95": [round(float(np.percentile(reps, 2.5)), 4), round(float(np.percentile(reps, 97.5)), 4)],
         "flip_rate_decisive_off": round(float(flip[dec].mean()), 4) if dec.any() else None,
         "n_decisive_off": int(dec.sum()), "mean_abs_gap": round(float(d.mean()), 4)}
    Path(out).write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(m, ensure_ascii=False, indent=1), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
