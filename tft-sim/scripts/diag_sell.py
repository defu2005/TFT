"""Chan doan co che cho SELL_BENCH tren Set 17 (200 lobby, seed 20000-20199; seed nay da dung cho tuning, chi de chan doan).
Do: (1) ty le buoc co bench day (9/9) va vang trung binh, cho seat scripted (B) va seat co nhieu SELL (A, eps SELL=0.1);
(2) o seat B: khi bench day va vang >= 2 (co the mua), teacher chon hanh dong gi;
(3) o seat A: so lan ban, gia tri ban, bench truoc khi ban.
Ghi results/fixed/real/diag_sell.json."""
import json
from collections import Counter
from pathlib import Path
import numpy as np
from tft_sim.real_content import build_real
from tft_sim.tftgoat import action_type, make_env, scripted_policy, seat_groups
from tft_goat.env.economy import sell_value
from tft_goat.env.actions import SELL_BENCH_START

env = make_env(build_real("TFTSet17"))
R = Path("results/fixed/real"); R.mkdir(parents=True, exist_ok=True)

stats = {"B": Counter(), "A": Counter()}
gold = {"B": [], "A": []}
teacher_when_blocked = Counter()
sells = []

for seed in range(20000, 20200):
    groups = seat_groups(seed)
    rngs = {a: np.random.default_rng(seed * 100 + i) for i, a in enumerate(groups)}
    obs, infos = env.reset(seed=seed)
    step = 0
    while env.agents and step < 20000:
        acts = {}
        for a in list(env.agents):
            g = groups[a]
            mask = infos[a]["action_mask"]
            pl = env._state.players[a]
            full = len(pl.bench) >= 9
            stats[g]["steps"] += 1
            stats[g]["bench_full"] += int(full)
            gold[g].append(pl.gold)
            t = scripted_policy(env, a, obs[a], mask, rngs[a])
            if g == "A" and rngs[a].random() < 0.1:
                legal = [int(i) for i in np.flatnonzero(mask) if action_type(int(i)) == "SELL_BENCH"]
                if legal:
                    act = int(rngs[a].choice(legal))
                    idx = act - SELL_BENCH_START
                    unit = pl.bench[idx]
                    sells.append({"bench_before": len(pl.bench), "gold_before": pl.gold,
                                  "sell_gold": int(sell_value(env._state.set_content.champions[unit.champion_api].cost, unit.star))})
                    stats["A"]["sells"] += 1
                else:
                    act = t
            else:
                act = t
            if g == "B" and full and pl.gold >= 2:
                teacher_when_blocked[action_type(t)] += 1
            acts[a] = act
        obs, r, term, trunc, infos = env.step(acts)
        step += 1

out = {"seeds": "20000-20199 (tuning seeds, diagnostics only)"}
for g in ("B", "A"):
    s = stats[g]
    out[f"seat_{g}"] = {"steps": s["steps"], "bench_full_share": s["bench_full"] / max(1, s["steps"]),
                        "gold_mean": float(np.mean(gold[g])) if gold[g] else None}
out["seat_A_sells"] = stats["A"]["sells"]
out["sell_bench_before_mean"] = float(np.mean([x["bench_before"] for x in sells])) if sells else None
out["sell_gold_mean"] = float(np.mean([x["sell_gold"] for x in sells])) if sells else None
out["teacher_action_when_bench_full_and_gold_ge2"] = dict(teacher_when_blocked)
(R / "diag_sell.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(out, ensure_ascii=False, indent=2))
