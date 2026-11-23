"""Chan doan (buoc 2 cua advisor), 200 lobby tinh chinh seed 20000-20199, quy tac sell (ban unit re nhat).
- Theo tung buoc, cho moi seat: so unit tren board, so unit 2 sao tro len (ca board va banc).
- Trong cac lan ban: ti le ban unit 2 sao+, ti le ban unit co ban sao khac cua cung tuong trong board/banc, ti le ban unit co trait chung voi board.
Ghi results/fixed/real/diag_sell2.json."""
import json
from collections import Counter
from pathlib import Path
import numpy as np
from tft_sim.real_content import build_real
from tft_sim.rules import make_rule
from tft_sim.tftgoat import make_env, scripted_policy, seat_groups, action_type
from tft_goat.env.actions import SELL_BENCH_START

env = make_env(build_real("TFTSet17"))
rule = make_rule(sell=True, floor=54)
board_n = {"A": [], "B": []}; star2 = {"A": [], "B": []}
sell = Counter()
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
            if step % 10 == 0:
                board_n[g].append(len(pl.board))
                star2[g].append(sum(1 for u in list(pl.board) + list(pl.bench) if u.star >= 2))
            pol = rule if g == "A" else scripted_policy
            act = int(pol(env, a, obs[a], mask, rngs[a]))
            if g == "A" and SELL_BENCH_START <= act < SELL_BENCH_START + 9 and act - SELL_BENCH_START < len(pl.bench):
                u = pl.bench[act - SELL_BENCH_START]
                others = [v for v in list(pl.board) + [x for j, x in enumerate(pl.bench) if j != act - SELL_BENCH_START]]
                sell["sells"] += 1
                sell["star2plus"] += int(u.star >= 2)
                sell["same_champ_owned"] += int(any(v.champion_api == u.champion_api for v in others))
                cost = env._state.set_content.champions[u.champion_api].traits
                ctr = set(t for v in pl.board for t in env._state.set_content.champions[v.champion_api].traits)
                sell["shares_trait_with_board"] += int(bool(set(cost) & ctr))
            acts[a] = act
        obs, r, t, tr, infos = env.step(acts)
        step += 1
out = {"seeds": "20000-20199 (tuning)",
       "board_size_mean": {g: round(float(np.mean(board_n[g])), 2) for g in "AB"},
       "star2plus_units_mean": {g: round(float(np.mean(star2[g])), 3) for g in "AB"},
       "sell_events": sell["sells"],
       "share_sold_star2plus": round(sell["star2plus"] / max(1, sell["sells"]), 4),
       "share_sold_same_champ_owned": round(sell["same_champ_owned"] / max(1, sell["sells"]), 4),
       "share_sold_shares_trait_with_board": round(sell["shares_trait_with_board"] / max(1, sell["sells"]), 4)}
Path("results/fixed/real/diag_sell2.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(out, ensure_ascii=False, indent=2))
