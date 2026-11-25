"""Nghien cuu combat Set 17 v2 (docs/research/combat-public-data.md). Mo ta, khong nguong.
  collect LO HI OUT.jsonl : choi lobby v4 (seed LO..HI-1). Ghi moi cap ban cung vong (same) va xuyen vong (cross).
                            Augment lay tu chosen_augments. Kiem items == len(item_apis) tren moi unit.
  analyze IN.jsonl OUT.json: lay mau 400 same + 400 cross, chia lobby theo id%10 (3 phan 10 giu lai lam test).
Ledger: 288000-288099 (dung de lay cap, khong phai danh gia chinh sach)."""
import json, random, sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import fight as F  # noqa: E402
from tft_goat.engine.resolver import EngineResolver  # noqa: E402
from tft_goat.env.tft_env import TftEnv  # noqa: E402
from tft_sim.params import make_aug_rule  # noqa: E402
from tft_sim.real_content import build_real  # noqa: E402

CONTENT = build_real("TFTSet17")
F.set_content(17, CONTENT)
_ITEM_MISMATCH = [0, 0]  # [kiem, lech]


def _units(board):
    out = []
    for u in board:
        apis = list(getattr(u, "item_apis", ()) or ())
        _ITEM_MISMATCH[0] += 1
        if int(u.items) != len(apis):
            _ITEM_MISMATCH[1] += 1
        out.append({"api": u.champion_api, "star": int(u.star), "items": apis, "pos": None})
    return out


def _side(p):
    return {"level": int(p.level), "augments": list(p.chosen_augments), "units": _units(p.board)}


def collect(lo, hi, out):
    env = TftEnv(set_content=CONTENT, resolver=EngineResolver())
    v4 = make_aug_rule()
    n_same = n_cross = 0
    with open(out, "w", encoding="utf-8") as f:
        for seed in range(lo, hi):
            obs, infos = env.reset(seed=seed)
            rngs = {a: random.Random(seed * 100 + i) for i, a in enumerate(sorted(env.agents))}
            snaps = {}  # round -> {agent: side}
            last = None
            step = 0
            while env.agents and step < 20000:
                st = env._state
                r = st.round_index
                if r != last and r >= 2:
                    last = r
                    snaps[r] = {a: _side(st.players[a]) for a in env.agents if st.players[a].board}
                actions = {a: v4(env, a, obs[a], infos[a]["action_mask"], rngs[a]) for a in list(env.agents)}
                obs, _, _, _, infos = env.step(actions)
                step += 1
            # cap cung vong
            for rr, sides in snaps.items():
                keys = sorted(sides)
                for i in range(len(keys)):
                    for j in range(i + 1, len(keys)):
                        rec = {"schema": "fight-v1", "set": 17, "label": "sim", "source": f"same {seed} {rr}",
                               "a": sides[keys[i]], "b": sides[keys[j]], "result": {"winner": None}}
                        f.write(json.dumps(rec, ensure_ascii=False) + "\n"); n_same += 1
            # cap xuyen vong: 40 cap moi lobby, luong RNG co dinh theo seed
            rr_rng = random.Random(seed)
            rounds = sorted(snaps)
            if len(rounds) >= 2:
                for _ in range(40):
                    r1, r2 = rr_rng.sample(rounds, 2)
                    pa = [a for a in snaps[r1]]; pb = [a for a in snaps[r2]]
                    if not pa or not pb:
                        continue
                    ia = rr_rng.choice(pa); ib = rr_rng.choice(pb)
                    rec = {"schema": "fight-v1", "set": 17, "label": "sim", "source": f"cross {seed} {r1} {r2}",
                           "a": snaps[r1][ia], "b": snaps[r2][ib], "result": {"winner": None}}
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n"); n_cross += 1
    print("COLLECTED same", n_same, "cross", n_cross, "items_checked", _ITEM_MISMATCH[0],
          "items_mismatch", _ITEM_MISMATCH[1], flush=True)


def strength(side):
    tot = 0.0; items = 0; traits = set()
    for u in side["units"]:
        ch = CONTENT.champions.get(u["api"])
        cost = float(ch.cost) if ch else 1.0
        tot += cost * 3 ** (u["star"] - 1)
        items += len(u["items"])
        if ch:
            traits |= set(ch.traits)
    return np.array([tot, items, side["level"], len(traits)], float)


def lobby_of(rec):
    return int(rec["source"].split()[1])


def analyze(inp, out):
    recs = F.load_jsonl(inp)
    rng = np.random.default_rng(0)
    same = [r for r in recs if r["source"].startswith("same")]
    cross = [r for r in recs if r["source"].startswith("cross")]
    test_same = [r for r in same if lobby_of(r) % 10 < 3]
    test_cross = [r for r in cross if lobby_of(r) % 10 < 3]
    train_same = [r for r in same if lobby_of(r) % 10 >= 3]
    train_cross = [r for r in cross if lobby_of(r) % 10 >= 3]
    pick = lambda L, k: [L[i] for i in sorted(rng.choice(len(L), size=min(k, len(L)), replace=False))]  # noqa: E731
    test = pick(test_same, 300) + pick(test_cross, 300)
    train = pick(train_same, 300) + pick(train_cross, 300)
    swap = pick(test, 100)

    def p(rec, ability, items=True):
        return np.array(F.predict_win(rec, 20, ability, items)["p_a"])

    ph = np.array([p(r, "hand") for r in test])
    configs = {"generic": [p(r, "generic") for r in test],
               "none": [p(r, "none") for r in test],
               "hand_noitems": [p(r, "hand", False) for r in test]}
    kind = np.array([r["source"].split()[0] for r in test])
    decisive = (ph >= 0.9) | (ph <= 0.1)
    A = {"n_test": len(test), "decisive_frac": round(float(decisive.mean()), 4),
         "decisive_won_by_A_share": round(float((ph[decisive] >= 0.5).mean()), 4),
         "same_decisive": round(float(decisive[kind == "same"].mean()), 4),
         "cross_decisive": round(float(decisive[kind == "cross"].mean()), 4)}
    dev = [abs(p(r, "hand") + p(_swap(r), "hand") - 1.0) for r in swap]
    A["swap_check_mean_abs_dev"] = round(float(np.mean(dev)), 4)
    C = {}
    for name, vals in configs.items():
        v = np.array(vals)
        C[name] = {"agree_with_hand_on_decisive": round(float(((v > 0.5) == (ph > 0.5))[decisive].mean()), 4),
                   "mean_abs_gap_all": round(float(np.abs(v - ph).mean()), 4)}
    # B: logistic (soft label p_hand) fit tren lobby train, test tren lobby held-out
    ptr = np.array([p(r, "hand") for r in train])
    Xtr = np.array([strength(r["a"]) - strength(r["b"]) for r in train])
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-9
    Xtr = (Xtr - mu) / sd
    Xte = (np.array([strength(r["a"]) - strength(r["b"]) for r in test]) - mu) / sd
    w = np.zeros(Xtr.shape[1]); b0 = 0.0
    for _ in range(3000):
        pr = 1 / (1 + np.exp(-(Xtr @ w + b0)))
        g = pr - ptr
        w -= 0.05 * (Xtr.T @ g) / len(ptr); b0 -= 0.05 * g.mean()
    pred = 1 / (1 + np.exp(-(Xte @ w + b0)))
    gap = np.abs(Xte.sum(1))
    B = {"features": ["sum_cost_star", "items", "level", "traits"], "weights_std": [round(float(x), 4) for x in w],
         "acc_decisive_test": round(float(((pred > 0.5) == (ph > 0.5))[decisive].mean()), 4),
         "baseline_always_A_on_decisive": round(float((ph[decisive] >= 0.5).mean()), 4)}
    bins = {}
    if decisive.any():
        qs = np.quantile(gap[decisive], [0, 1 / 3, 2 / 3, 1])
        for k in range(3):
            m = decisive & (gap >= qs[k]) & (gap <= qs[k + 1])
            if m.any():
                bins[f"gap_tercile_{k+1}"] = {"n": int(m.sum()),
                                              "acc": round(float(((pred > 0.5) == (ph > 0.5))[m].mean()), 4)}
    B["by_gap_tercile"] = bins
    res = {"label": "sim (engine Set 17, khong phai tran that)", "A": A, "C": C, "B": B,
           "items_mismatch": _ITEM_MISMATCH}
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=2), flush=True)


def _swap(r):
    return {**r, "a": r["b"], "b": r["a"], "result": {"winner": None}}


if __name__ == "__main__":
    if sys.argv[1] == "collect":
        collect(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    else:
        analyze(sys.argv[2], sys.argv[3])
