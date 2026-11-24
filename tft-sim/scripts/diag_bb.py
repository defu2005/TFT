"""Chan doan (buoc 2 advisor): nhieu BENCH_BOARD (board -> banc) tren hybrid, seed 20000-20199 (dev).
Voi moi lan chuyen ngau nhien: unit ra (cost, sao), va su kien tiep theo cua seat do:
  same = unit do duoc FIELD lai; other = FIELD unit khac; sold = ban; none = khong co FIELD/ban trong 3 buoc.
Ghi tong hop va gia/sao cua unit ra va unit vao. Ghi results/fixed/real/diag_bb.json."""
import json
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from tft_sim.real_content import build_real
from tft_sim.rules import make_rule
from tft_sim.tftgoat import action_type, make_env, scripted_policy, seat_groups
from tft_goat.env.actions import FIELD_BENCH_START, SELL_BENCH_START, BENCH_BOARD_START

env = make_env(build_real("TFTSet17"))
hybrid = make_rule(sell=True, floor=54, pick="hybrid")
champs = None
outcome = Counter(); pairs = []
for seed in range(20000, 20200):
    groups = seat_groups(seed)
    rngs = {a: np.random.default_rng(seed * 100 + i) for i, a in enumerate(groups)}
    obs, infos = env.reset(seed=seed)
    champs = env._state.set_content.champions
    pending = defaultdict(list)  # agent -> [(out_api, out_cost, out_star, steps_left)]
    step = 0
    while env.agents and step < 20000:
        acts = {}
        for a in list(env.agents):
            mask = infos[a]["action_mask"]
            pl = env._state.players[a]
            act = int(hybrid(env, a, obs[a], mask, rngs[a]))
            # 1) resolve pending records with this step's chosen action (before applying)
            still = []
            for rec in pending[a]:
                out_api, oc, os_, left = rec
                if act == FIELD_BENCH_START or FIELD_BENCH_START <= act < FIELD_BENCH_START + 9:
                    idx = act - FIELD_BENCH_START
                    if idx < len(pl.bench):
                        u = pl.bench[idx]
                        k = "same" if u.champion_api == out_api else "other"
                        outcome[k] += 1
                        pairs.append((oc, os_, champs[u.champion_api].cost, u.star))
                    continue
                if SELL_BENCH_START <= act < SELL_BENCH_START + 9:
                    outcome["sold"] += 1
                    continue
                if left <= 1:
                    outcome["none"] += 1
                    continue
                still.append((out_api, oc, os_, left - 1))
            pending[a] = still
            # 2) decide this step's action and record a new BENCH_BOARD if it is noise
            if rngs[a].random() < 0.1 and mask[BENCH_BOARD_START:BENCH_BOARD_START + 9].any():
                legal = [i for i in range(9) if mask[BENCH_BOARD_START + i]]
                j = int(rngs[a].choice(legal))
                if j < len(pl.board):
                    b = pl.board[j]
                    pending[a].append((b.champion_api, champs[b.champion_api].cost, b.star, 3))
                    act = BENCH_BOARD_START + j
            acts[a] = act
        obs, r, t, tr, infos = env.step(acts)
        step += 1
pairs = np.array(pairs) if pairs else np.zeros((0, 4))
out = {"seeds": "20000-20199 (dev)", "outcomes": dict(outcome), "n_pairs_same_or_other": len(pairs),
       "mean_cost_out_vs_in_when_other": None if len(pairs) == 0 else
       {"cost_out": round(float(pairs[:, 0].mean()), 3), "cost_in": round(float(pairs[:, 2].mean()), 3),
        "star_out": round(float(pairs[:, 1].mean()), 3), "star_in": round(float(pairs[:, 3].mean()), 3)}}
Path("results/fixed/real/diag_bb.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(out, ensure_ascii=False, indent=2))
