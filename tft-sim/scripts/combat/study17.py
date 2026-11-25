"""Nghien cuu combat Set 17 (model-plan / docs/research/combat-public-data.md). Mo ta, khong nguong.
  collect LO HI OUT.jsonl : choi lobby v4 (seed LO..HI-1), lay cap ban (cung vong, cung lobby) lam fight-v1 nhan 'sim'.
  analyze IN.jsonl OUT.json: (A) tran nhieu; (B) hoi quy logistic tren dac trung suc manh; (C) doi chieu public vs full.
Ledger: 288000-288099."""
import json, random, sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))
import fight as F  # noqa: E402
from tft_goat.engine.resolver import EngineResolver  # noqa: E402
from tft_goat.env.tft_env import TftEnv  # noqa: E402
from tft_sim.params import make_aug_rule  # noqa: E402
from tft_sim.real_content import build_real  # noqa: E402

CONTENT = build_real("TFTSet17")
F.set_content(17, CONTENT)


def _units(board):
    out = []
    for u in board:
        items = list(getattr(u, "item_apis", ()) or ())
        out.append({"api": u.champion_api, "star": int(u.star), "items": items, "pos": None})
    return out


def collect(lo, hi, out):
    env = TftEnv(set_content=CONTENT, resolver=EngineResolver())
    v4 = make_aug_rule()
    n = 0
    with open(out, "w", encoding="utf-8") as f:
        for seed in range(lo, hi):
            obs, infos = env.reset(seed=seed)
            rngs = {a: random.Random(seed * 100 + i) for i, a in enumerate(sorted(env.agents))}
            last_round = None
            step = 0
            while env.agents and step < 20000:
                st = env._state
                if st.round_index != last_round and st.round_index >= 2:
                    last_round = st.round_index
                    snap = {}
                    for a in env.agents:
                        p = st.players[a]
                        if p.board:
                            snap[a] = {"level": int(p.level), "augments": [],
                                       "units": _units(p.board)}
                    keys = sorted(snap)
                    for i in range(len(keys)):
                        for j in range(i + 1, len(keys)):
                            rec = {"schema": "fight-v1", "set": 17, "label": "sim",
                                   "source": f"v4 lobby seed {seed} round {last_round}",
                                   "a": snap[keys[i]], "b": snap[keys[j]], "result": {"winner": None}}
                            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                            n += 1
                actions = {}
                for a in list(env.agents):
                    actions[a] = v4(env, a, obs[a], infos[a]["action_mask"], rngs[a])
                obs, _, _, _, infos = env.step(actions)
                step += 1
    print("COLLECTED", n, flush=True)


def strength(side):
    """Dac trung suc manh khong phu thuoc set: tong cost*3^(sao-1), so trang bi, cap, so trait."""
    tot = 0.0
    items = 0
    traits = set()
    for u in side["units"]:
        ch = CONTENT.champions.get(u["api"])
        cost = float(ch.cost) if ch else 1.0
        tot += cost * 3 ** (u["star"] - 1)
        items += len(u["items"])
        if ch:
            traits |= set(ch.traits)
    return np.array([tot, items, side["level"], len(traits)], float)


def analyze(inp, out):
    recs = F.load_jsonl(inp)
    pick = np.random.default_rng(0).choice(len(recs), size=min(500, len(recs)), replace=False)
    recs = [recs[i] for i in sorted(pick)]
    rows = []
    for r in recs:
        full = F.predict_win(r, 20, "full")
        pub = F.predict_win(r, 20, "public")
        rows.append((r, full["p_a"], pub["p_a"]))
    p = np.array([x[1] for x in rows]); q = np.array([x[2] for x in rows])
    decisive = (p >= 0.9) | (p <= 0.1)
    coin = (p >= 0.4) & (p <= 0.6)
    A = {"n": len(rows), "decisive_frac": round(float(decisive.mean()), 4),
         "coinflip_frac": round(float(coin.mean()), 4)}
    # (C) public vs full: dau cung phia tren cac tran quyet dinh
    sign_agree = float(((q > 0.5) == (p > 0.5))[decisive].mean()) if decisive.any() else None
    C = {"agree_on_decisive": None if sign_agree is None else round(sign_agree, 4),
         "n_decisive": int(decisive.sum()), "mean_abs_gap": round(float(np.abs(p - q).mean()), 4)}
    # (B) logistic tren chenh lech dac trung (a-b), nhan mem = p_full (huan luyen tren ca hai nhom)
    X = np.array([strength(r["a"]) - strength(r["b"]) for r, _, _ in rows])
    X = (X - X.mean(0)) / (X.std(0) + 1e-9)
    w = np.zeros(X.shape[1]); bias = 0.0
    for _ in range(3000):
        z = X @ w + bias
        pr = 1 / (1 + np.exp(-z))
        g = pr - p
        w -= 0.05 * (X.T @ g) / len(p); bias -= 0.05 * g.mean()
    pred = 1 / (1 + np.exp(-(X @ w + bias)))
    acc_dec = float(((pred > 0.5) == (p > 0.5))[decisive].mean()) if decisive.any() else None
    B = {"features": ["sum_cost_star", "items", "level", "traits"], "weights_std": [round(float(x), 4) for x in w],
         "acc_on_decisive": None if acc_dec is None else round(acc_dec, 4),
         "ceiling_note": "tran quyet dinh co nhan dang tin cay; tran tung dong xu khong dung de cham"}
    res = {"label": "sim (engine Set 17, khong phai tran that)", "A": A, "B": B, "C": C}
    Path(out).write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "collect":
        collect(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    else:
        analyze(sys.argv[2], sys.argv[3])
