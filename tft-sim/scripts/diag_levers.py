"""Chan doan (advisor buoc 2 va 4), v3 tu dau, seed 100000-100199 (dev).
(a) Tuong quan (Spearman, tu xep hang numpy) cua trung binh theo vong PvP cua tung seat voi placement cuoi.
(b) Nut theta: BUY_XP, REROLL, cap, vang cho theta (7,54,5,1) va (54,54,0,0)."""
import json
from pathlib import Path
import numpy as np
from tft_goat.env.combat import board_strength
from tft_goat.env.rounds import is_pvp
from tft_goat.env.actions import BUY_XP, REROLL
from tft_sim.params import Theta, make_param_policy
from tft_sim.real_content import build_real
from tft_sim.rules import make_swap_rule
from tft_sim.tftgoat import make_env, action_type

def rank(x):
    o = np.argsort(x, kind="mergesort"); r = np.empty(len(x)); r[o] = np.arange(len(x))
    return r

def spearman(a, b):
    ra, rb = rank(np.asarray(a, float)), rank(np.asarray(b, float))
    return float(np.corrcoef(ra, rb)[0, 1])

env = make_env(build_real("TFTSet17"))
v3 = make_swap_rule(key="value")
FEAT = ["gold", "level", "board_strength", "n_2star_plus", "hp"]
seats_feat, seats_pl = [], []
for seed in range(100000, 100200):
    obs, infos = env.reset(seed=seed)
    rngs = {a: np.random.default_rng(seed * 100 + i) for i, a in enumerate(env.agents)}
    acc = {a: [] for a in env.agents}
    step = 0
    while env.agents and step < 20000:
        acts = {a: int(v3(env, a, obs[a], infos[a]["action_mask"], rngs[a])) for a in list(env.agents)}
        obs, r, t, tr, infos = env.step(acts)
        step += 1
        if env._phase_steps == 0 and is_pvp(env._state.round_index):
            for a in list(env._state.players):
                p = env._state.players[a]
                if p.hp <= 0:
                    continue
                n2 = sum(1 for u in list(p.board) + list(p.bench) if u.star >= 2)
                acc[a].append([p.gold, p.level, board_strength(p.board, env._state.set_content), n2, p.hp])
    for a in list(env._state.players):
        p = env._state.players[a]
        if acc.get(a):
            seats_feat.append(np.mean(acc[a], axis=0)); seats_pl.append(p.placement)
F = np.array(seats_feat); P = -np.array(seats_pl, float)  # cao hon = tot hon
out = {"n_seat_games": len(P), "spearman_with_goodness": {}}
for i, n in enumerate(FEAT):
    out["spearman_with_goodness"][n] = round(spearman(F[:, i], P), 3)
Path("results/fixed/real/diag_levers.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print(out, flush=True)
# (b) nut theta
for th in [Theta(7, 54, 5, 1), Theta(54, 54, 0, 0), Theta()]:
    pol = make_param_policy(th)
    n_xp = n_rr = 0; lv = []; gold = []; steps = 0
    for s in range(100000, 100050):
        obs, infos = env.reset(seed=s)
        rngs = {a: np.random.default_rng(s * 100 + i) for i, a in enumerate(env.agents)}
        st = 0
        while env.agents and st < 20000:
            acts = {}
            for a in list(env.agents):
                m = infos[a]["action_mask"]
                x = pol(env, a, obs[a], m, rngs[a]); acts[a] = int(x)
                n_xp += int(x == BUY_XP); n_rr += int(x == REROLL)
            obs, r, t, tr, infos = env.step(acts); st += 1
            steps += 1
        for a in list(env._state.players):
            lv.append(env._state.players[a].level); gold.append(env._state.players[a].gold)
    print("theta", th, "BUY_XP", n_xp, "REROLL", n_rr, "level_mean", round(float(np.mean(lv)), 2), "gold_end_mean", round(float(np.mean(gold)), 2), flush=True)
