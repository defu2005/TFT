"""Thu thap (observation, mask, hanh dong) va chia train/val/test theo lobby_seed."""

from __future__ import annotations

import random

from .env import Env
from .harness import Policy, assign_groups


def collect(env: Env, teacher: Policy, lobby_seeds: list[int]) -> list[dict]:
    rows: list[dict] = []
    for ls in lobby_seeds:
        groups = assign_groups(ls, env.n_seats)
        rngs = {i: random.Random(ls * 1000 + i) for i in range(env.n_seats)}
        obs = env.reset(ls)
        while not env.done():
            actions = {}
            for i in range(env.n_seats):
                o = obs[i]
                a = teacher(o, rngs[i])
                rows.append({"lobby": ls, "seat": i, "group": groups[i], "obs": o, "action": a})
                actions[i] = a
            obs = env.step(actions)
    return rows


def split_by_lobby(lobby_seeds: list[int], fractions=(0.7, 0.15, 0.15)) -> dict[str, list[int]]:
    n = len(lobby_seeds)
    n_tr = int(n * fractions[0])
    n_va = int(n * fractions[1])
    return {
        "train": lobby_seeds[:n_tr],
        "val": lobby_seeds[n_tr:n_tr + n_va],
        "test": lobby_seeds[n_tr + n_va:],
    }
