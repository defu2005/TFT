"""Lobby hon hop: moi ghe mot policy (seat -> policy). Khong sua play() (tftgoat.py).
Dung: python scripts/mixed_lobby.py selftest            -> kiem tra 4/4 khop play() tren 5 seed
      python scripts/mixed_lobby.py league LO HI TAG    -> giai dau: moi lobby chon 8 policy tu pool (co seed), in bang hang.
"""
import json, random, sys
from pathlib import Path
import numpy as np
import torch
sys.path.insert(0, str(Path(__file__).parent))
from tft_sim.tftgoat import Lobby, play, seat_groups, bootstrap_ci

torch.set_num_threads(1)


def play_mixed(env, seed: int, policy_of_seat: dict) -> dict:
    """policy_of_seat: {agent_id: policy}. Tra ve placement theo agent_id. Cung cach goi rng nhu play()."""
    agents = list(policy_of_seat)
    rngs = {a: random.Random(seed * 100 + i) for i, a in enumerate(agents)}
    obs, infos = env.reset(seed=seed)
    step, illegal = 0, 0
    while env.agents and step < 20000:
        actions = {}
        for a in list(env.agents):
            mask = infos[a]["action_mask"]
            act = policy_of_seat[a](env, a, obs[a], mask, rngs[a])
            illegal += int(not mask[act])
            actions[a] = act
        obs, _, _, _, infos = env.step(actions)
        step += 1
    return {"placements": {a: env._state.players[a].placement for a in agents}, "completed": not env.agents,
            "illegal": illegal, "steps": step}


def selftest(env, seeds, scripted, v4):
    ok = True
    for s in seeds:
        groups = seat_groups(s)
        ref = play(env, s, scripted, v4)
        m = {a: (scripted if g == "A" else v4) for a, g in groups.items()}
        got = play_mixed(env, s, m)["placements"]
        pa = [got[a] for a, g in groups.items() if g == "A"]
        pb = [got[a] for a, g in groups.items() if g == "B"]
        same = pa == ref.placements_a and pb == ref.placements_b
        ok &= same
        print("seed", s, "match", same, flush=True)
    print("SELFTEST", "PASS" if ok else "FAIL", flush=True)
    return ok


def league(env, lo, hi, pool: dict, tag: str):
    names = list(pool)
    rows = []  # (policy name, placement, lobby index)
    lobby_ids = []
    for li, s in enumerate(range(lo, hi)):
        rng = np.random.default_rng(s)
        agents = [f"player_{i}" for i in range(8)]
        pick = rng.choice(len(names), size=8, replace=True)  # 8 ghe, co the trung policy
        policy_of_seat = {a: pool[names[k]] for a, k in zip(agents, pick)}
        res = play_mixed(env, s, policy_of_seat)
        for a, k in zip(agents, pick):
            rows.append((names[k], res["placements"][a], li))
        lobby_ids.append(li)
    table = {}
    for n in names:
        vals = [(p, li) for nm, p, li in rows if nm == n]
        if not vals:
            continue
        mean = float(np.mean([p for p, _ in vals]))
        # bootstrap theo lobby: moi lobby cho trung binh cua n trong lobby do
        per_lobby = {}
        for p, li in vals:
            per_lobby.setdefault(li, []).append(p)
        means = np.array([np.mean(v) for v in per_lobby.values()])
        lo_ci, hi_ci = bootstrap_ci(means)
        table[n] = {"mean_placement": round(mean, 3), "ci95_by_lobby": [round(lo_ci, 3), round(hi_ci, 3)], "n_seats": len(vals)}
    out = {"tag": tag, "seeds": [lo, hi - 1], "pool": names, "table": table}
    Path("results/fixed/real").mkdir(parents=True, exist_ok=True)
    Path(f"results/fixed/real/league_{tag}.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    for n in sorted(table, key=lambda x: table[x]["mean_placement"]):
        print(n, table[n], flush=True)
    return out
