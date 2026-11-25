"""Phan tich combat Set 17 v3 (docs/research/combat-public-data.md muc 7). Mo ta, khong nguong.

  score IN.jsonl OUT.csv : moi cap (mau co dinh) -> xac suat cho cac cau hinh, luu tung dong. Song song 4 tien trinh.
  report OUT.csv RESULT.json : A, B, C tach theo cung vong / xuyen vong; khoang tin cay bootstrap theo lobby.

Mau: test = 300 cung vong + 300 xuyen vong tu lobby id%10<3; train = 300 + 300 tu lobby id%10>=3 (chi cau hinh hand).
Cau hinh:
  hand          : ability viet tay, trang bi bat, augment bat (engine day du)
  hand_noaug    : nhu hand, bo augment
  hand_seed2    : nhu hand, seed0 = 1000 (tran nhieu: do dong thuan voi chinh no)
  generic       : moi tuong dung default_ability, trang bi bat
  none          : khong ability, trang bi bat
  hand_noitems  : ability viet tay, khong trang bi
  public        : khong ability, khong trang bi (tuong duong 'public' v1)
"""
import csv, json, sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import fight as F  # noqa: E402
from tft_sim.real_content import build_real  # noqa: E402

CONTENT = build_real("TFTSet17")
F.set_content(17, CONTENT)

CONFIGS = {
    "hand": dict(ability="hand", items=True, augments=True, seed0=0),
    "hand_noaug": dict(ability="hand", items=True, augments=False, seed0=0),
    "hand_seed2": dict(ability="hand", items=True, augments=True, seed0=1000),
    "generic": dict(ability="generic", items=True, augments=True, seed0=0),
    "none": dict(ability="none", items=True, augments=True, seed0=0),
    "hand_noitems": dict(ability="hand", items=False, augments=True, seed0=0),
    "public": dict(ability="none", items=False, augments=True, seed0=0),
}
N = 20


def strength_vec(side):
    tot = 0.0; items = 0; traits = set()
    for u in side["units"]:
        ch = CONTENT.champions.get(u["api"])
        cost = float(ch.cost) if ch else 1.0
        tot += cost * 3 ** (u["star"] - 1)
        items += len(u["items"])
        if ch:
            traits |= set(ch.traits)
    return [tot, items, side["level"], len(traits)]


def _eval(rec):
    out = {}
    for name, c in CONFIGS.items():
        out[name] = F.predict_win(rec, N, c["ability"], c["items"], c["seed0"], c["augments"])["p_a"]
    return out


def lobby_of(rec):
    return int(rec["source"].split()[1])


def sample(recs, rng):
    same = [r for r in recs if r["source"].startswith("same")]
    cross = [r for r in recs if r["source"].startswith("cross")]
    def pick(L, k):
        return [L[i] for i in sorted(rng.choice(len(L), size=min(k, len(L)), replace=False))]
    test = [x for x in pick([r for r in same if lobby_of(r) % 10 < 3], 300)] + \
           [x for x in pick([r for r in cross if lobby_of(r) % 10 < 3], 300)]
    train = [x for x in pick([r for r in same if lobby_of(r) % 10 >= 3], 300)] + \
            [x for x in pick([r for r in cross if lobby_of(r) % 10 >= 3], 300)]
    return test, train


def score(inp, out_csv):
    recs = F.load_jsonl(inp)
    test, train = sample(recs, np.random.default_rng(0))
    rows = [("test", i, r) for i, r in enumerate(test)] + [("train", i, r) for i, r in enumerate(train)]
    with Pool(4) as pool:
        res = pool.map(_eval_split, rows)
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["split", "idx", "kind", "lobby", "sa", "sb"] + list(CONFIGS))
        for (split, i, r), pv in zip(rows, res):
            sa = strength_vec(r["a"]); sb = strength_vec(r["b"])
            w.writerow([split, i, r["source"].split()[0], lobby_of(r),
                        " ".join(f"{x:g}" for x in sa), " ".join(f"{x:g}" for x in sb)]
                       + [round(pv[k], 4) if k in pv else "" for k in CONFIGS])
    print("WROTE", out_csv, len(rows), flush=True)


def _eval_split(row):
    split, i, r = row
    if split == "train":
        c = CONFIGS["hand"]
        return {"hand": F.predict_win(r, N, c["ability"], c["items"], c["seed0"], c["augments"])["p_a"]}
    return _eval(r)


def _logit_fit(X, p, steps=3000, lr=0.05):
    w = np.zeros(X.shape[1]); b = 0.0
    for _ in range(steps):
        z = 1 / (1 + np.exp(-(X @ w + b)))
        g = z - p
        w -= lr * (X.T @ g) / len(p); b -= lr * g.mean()
    return w, b


def report(csv_path, out_json):
    rows = list(csv.DictReader(open(csv_path, encoding="utf-8")))
    test = [r for r in rows if r["split"] == "test"]
    train = [r for r in rows if r["split"] == "train"]
    rng = np.random.default_rng(1)

    def vec(r):
        sa = np.array([float(x) for x in r["sa"].split()]); sb = np.array([float(x) for x in r["sb"].split()])
        return sa - sb

    def stats(sub, label):
        ph = np.array([float(r["hand"]) for r in sub])
        dec = (ph >= 0.9) | (ph <= 0.1)
        out = {"n": len(sub), "decisive_frac": round(float(dec.mean()), 4),
               "decisive_won_by_A_share": round(float((ph[dec] >= 0.5).mean()), 4) if dec.any() else None}
        # C: dong thuan dau voi hand tren cap quyet dinh, CI bootstrap theo lobby
        lobbies = sorted(set(int(r["lobby"]) for r in sub))
        byl = defaultdict(list)
        for r in sub:
            byl[int(r["lobby"])].append(r)
        C = {}
        for name in CONFIGS:
            if name == "hand":
                continue
            v = np.array([float(r[name]) for r in sub])
            agree = ((v > 0.5) == (ph > 0.5))[dec]
            reps = []
            for _ in range(2000):
                pick_l = rng.choice(lobbies, size=len(lobbies), replace=True)
                sel = [r for l in pick_l for r in byl[l]]
                pv = np.array([float(r[name]) for r in sel]); ppv = np.array([float(r["hand"]) for r in sel])
                dm = (ppv >= 0.9) | (ppv <= 0.1)
                if dm.any():
                    reps.append(float((((pv > 0.5) == (ppv > 0.5))[dm]).mean()))
            lo, hi = (np.percentile(reps, [2.5, 97.5]) if reps else (None, None))
            C[name] = {"agree_on_decisive": round(float(agree.mean()), 4) if agree.size else None,
                       "ci95": [round(float(lo), 4), round(float(hi), 4)] if reps else None,
                       "mean_abs_gap_all": round(float(np.abs(v - ph).mean()), 4)}
        return out, C

    res = {"label": "sim (engine Set 17, khong phai tran that)"}
    for kind in ("same", "cross", "all"):
        sub = [r for r in test if kind == "all" or r["kind"] == kind]
        A, C = stats(sub, kind)
        res[kind] = {"A": A, "C": C}

    # B: logistic tren hieu dac trung, nhan mem = p hand; huan luyen tren train, do tren test
    Xtr = np.array([vec(r) for r in train]); ptr = np.array([float(r["hand"]) for r in train])
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-9
    w, b = _logit_fit((Xtr - mu) / sd, ptr)
    B = {}
    for kind in ("same", "cross", "all"):
        sub = [r for r in test if kind == "all" or r["kind"] == kind]
        X = (np.array([vec(r) for r in sub]) - mu) / sd
        ph = np.array([float(r["hand"]) for r in sub])
        dec = (ph >= 0.9) | (ph <= 0.1)
        z = X @ w + b
        pred = 1 / (1 + np.exp(-z))
        corr = (pred > 0.5) == (ph > 0.5)
        absz = np.abs(z)
        t = {"acc_decisive": round(float(corr[dec].mean()), 4) if dec.any() else None,
             "baseline_always_A": round(float((ph[dec] >= 0.5).mean()), 4) if dec.any() else None}
        if dec.any():
            q = np.quantile(absz[dec], [0, 1 / 3, 2 / 3, 1])
            terc = {}
            for k in range(3):
                m = dec & (absz >= q[k]) & (absz <= q[k + 1])
                if m.any():
                    terc[f"tercile_{k+1}"] = {"n": int(m.sum()), "acc": round(float(corr[m].mean()), 4)}
            t["by_model_score_tercile"] = terc
        B[kind] = t
    res["B"] = {"features": ["sum_cost_star", "items", "level", "traits"], "weights_std": [round(float(x), 4) for x in w],
                "by_split": B}
    Path(out_json).parent.mkdir(parents=True, exist_ok=True)
    Path(out_json).write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "score":
        score(sys.argv[2], sys.argv[3])
    else:
        report(sys.argv[2], sys.argv[3])
