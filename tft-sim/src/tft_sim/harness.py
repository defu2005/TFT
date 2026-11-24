"""Harness danh gia: lobby hon hop, xoay seat, paired seed, bootstrap theo lobby, kiem tra replay.

Policy la callable (obs_seat: dict, rng) -> action. Moi lobby co 8 seat; nhom A gom 4 seat, nhom B
gom 4 seat. Seat duoc xoay theo lobby_seed de loai bo loi do vi tri.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable

import numpy as np

from .env import Env

Policy = Callable[[dict, random.Random], int]


@dataclass(frozen=True)
class LobbyResult:
    seed: int
    placements_a: list[int]
    placements_b: list[int]

    @property
    def mean_a(self) -> float:
        return float(np.mean(self.placements_a))

    @property
    def mean_b(self) -> float:
        return float(np.mean(self.placements_b))


def assign_groups(lobby_seed: int, n_seats: int = 8) -> list[str]:
    """Nhom A/B xoay vong theo lobby_seed: cung mot lobby_seed luon cho cung phan cong."""
    base = ["A"] * (n_seats // 2) + ["B"] * (n_seats // 2)
    k = lobby_seed % n_seats
    return base[k:] + base[:k]


def play_lobby(env: Env, policy_a: Policy, policy_b: Policy, lobby_seed: int) -> tuple[LobbyResult, list]:
    groups = assign_groups(lobby_seed, env.n_seats)
    policies = {i: (policy_a if g == "A" else policy_b) for i, g in enumerate(groups)}
    # rng rieng cho moi seat, dan xuat tu lobby_seed: replay duoc
    rngs = {i: random.Random(lobby_seed * 1000 + i) for i in range(env.n_seats)}
    obs = env.reset(lobby_seed)
    trace: list = []
    while not env.done():
        actions = {i: policies[i](obs[i], rngs[i]) for i in env.alive()}
        trace.append(tuple(sorted(actions.items())))
        obs = env.step(actions)
    pl = env.placements()
    a = [pl[i] for i in range(env.n_seats) if groups[i] == "A"]
    b = [pl[i] for i in range(env.n_seats) if groups[i] == "B"]
    return LobbyResult(lobby_seed, a, b), trace


def evaluate(env: Env, policy_a: Policy, policy_b: Policy, lobby_seeds: list[int]) -> dict:
    results = [play_lobby(env, policy_a, policy_b, s)[0] for s in lobby_seeds]
    diffs = np.array([r.mean_a - r.mean_b for r in results])
    rng = np.random.default_rng(0)
    boots = [diffs[rng.integers(0, len(diffs), len(diffs))].mean() for _ in range(2000)]
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {
        "n_lobbies": len(results),
        "mean_placement_a": float(np.mean([p for r in results for p in r.placements_a])),
        "mean_placement_b": float(np.mean([p for r in results for p in r.placements_b])),
        "diff_a_minus_b": float(diffs.mean()),
        "ci95_diff": (float(lo), float(hi)),
    }


def replay_matches(env: Env, policy_a: Policy, policy_b: Policy, lobby_seed: int) -> bool:
    r1, t1 = play_lobby(env, policy_a, policy_b, lobby_seed)
    r2, t2 = play_lobby(env, policy_a, policy_b, lobby_seed)
    return r1 == r2 and t1 == t2
