"""Gate 0: 4 scripted vs 4 random tren TFT_GOAT, noi dung TONG HOP (build_sample_content).

Khong tai mang. Xoay seat theo lobby. Kiem tra replay cung seed. Bootstrap CI theo lobby.
Chay: PYTHONPATH=<tft_goat>/src:<tft-sim>/src python scripts/gate0_tftgoat.py --lobbies N
"""

from __future__ import annotations

import argparse
import json
import time

import numpy as np

from tft_goat.agent.scripted import scripted_action
from tft_goat.data.sample import build_sample_content
from tft_goat.env.tft_env import TftEnv
from tft_sim.harness import assign_groups

MAX_STEPS = 20000


def play(seed: int, env: TftEnv) -> dict:
    groups = assign_groups(seed, 8)
    names = [f"player_{i}" for i in range(8)]
    group_of = {names[i]: groups[i] for i in range(8)}
    rng = np.random.default_rng(seed)
    obs, infos = env.reset(seed=seed)
    steps = 0
    trace = []
    while env.agents and steps < MAX_STEPS:
        actions = {}
        for a in env.agents:
            if group_of[a] == "A":
                actions[a] = int(scripted_action(env._state, env._state.players[a]))
            else:
                actions[a] = int(rng.choice(np.flatnonzero(infos[a]["action_mask"])))
        trace.append(tuple(sorted(actions.items())))
        obs, rewards, terms, truncs, infos = env.step(actions)
        steps += 1
    placements = {a: env._state.players[a].placement for a in names}
    a_pl = [placements[a] for a in names if group_of[a] == "A"]
    b_pl = [placements[a] for a in names if group_of[a] == "B"]
    return {
        "seed": seed,
        "steps": steps,
        "completed": not env.agents,
        "a": a_pl,
        "b": b_pl,
        "trace": trace,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--lobbies", type=int, default=20)
    p.add_argument("--out", default="gate0_result.json")
    args = p.parse_args()

    content = build_sample_content()
    env = TftEnv(set_content=content)

    t0 = time.time()
    results, crashes = [], []
    for seed in range(args.lobbies):
        try:
            results.append(play(seed, env))
        except Exception as e:  # noqa: BLE001 - ghi lai moi loi
            crashes.append({"seed": seed, "error": repr(e)})
    elapsed = time.time() - t0

    completed = [r for r in results if r["completed"]]
    diffs = np.array([np.mean(r["a"]) - np.mean(r["b"]) for r in completed]) if completed else np.array([0.0])
    rng = np.random.default_rng(0)
    boots = [diffs[rng.integers(0, len(diffs), len(diffs))].mean() for _ in range(2000)]
    lo, hi = np.percentile(boots, [2.5, 97.5])

    replay_ok = None
    if results:
        again = play(results[0]["seed"], TftEnv(set_content=content))
        replay_ok = again["trace"] == results[0]["trace"] and again["a"] == results[0]["a"]

    summary = {
        "content": "synthetic (build_sample_content) - KHONG phai TFT that",
        "lobbies_requested": args.lobbies,
        "lobbies_completed": len(completed),
        "crashes": crashes,
        "mean_placement_scripted_A": float(np.mean([p for r in completed for p in r["a"]])) if completed else None,
        "mean_placement_random_B": float(np.mean([p for r in completed for p in r["b"]])) if completed else None,
        "diff_A_minus_B": float(diffs.mean()),
        "ci95_diff": [float(lo), float(hi)],
        "replay_same_seed_identical": replay_ok,
        "elapsed_s": round(elapsed, 1),
        "games_per_hour": round(len(completed) / elapsed * 3600, 1) if elapsed > 0 else None,
    }
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
