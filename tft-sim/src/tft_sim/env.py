"""Giao dien env toi thieu va mot toy env 8 seat.

Toy env chi la TEST DOUBLE de kiem chung harness. Khong mo phong TFT. Ket qua tren toy env
khong noi gi ve suc manh cua bot TFT.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Protocol

N_SEATS = 8
ROUNDS = 10
ACT_PASS = 0
ACT_BUY = 1


class Env(Protocol):
    n_seats: int

    def reset(self, seed: int) -> dict[int, dict]: ...
    def step(self, actions: dict[int, int]) -> dict[int, dict]: ...
    def legal(self, seat: int) -> list[int]: ...
    def placements(self) -> dict[int, int]: ...
    def done(self) -> bool: ...


@dataclass
class _Seat:
    gold: int = 0
    strength: float = 0.0


@dataclass
class ToyEnv:
    """8 seat. Moi vong +5 vang. Mua (ACT_BUY, ton 3 vang) cho +2 strength. Cuoi tran
    diem = strength + 0.1*gold + nhieu nho (co seed). Xep hang cao diem -> placement thap.
    """

    n_seats: int = N_SEATS
    seats: list[_Seat] = field(default_factory=list)
    rng: random.Random = field(default_factory=random.Random)
    round_: int = 0
    _scores: dict[int, float] = field(default_factory=dict)

    def reset(self, seed: int) -> dict[int, dict]:
        self.rng = random.Random(seed)
        self.seats = [_Seat() for _ in range(self.n_seats)]
        self.round_ = 0
        self._scores = {}
        return self._obs()

    def _obs(self) -> dict[int, dict]:
        return {
            i: {"gold": s.gold, "strength": s.strength, "round": self.round_, "legal": self.legal(i)}
            for i, s in enumerate(self.seats)
        }

    def legal(self, seat: int) -> list[int]:
        acts = [ACT_PASS]
        if self.seats[seat].gold >= 3:
            acts.append(ACT_BUY)
        return acts

    def step(self, actions: dict[int, int]) -> dict[int, dict]:
        if self.done():
            raise RuntimeError("tran da ket thuc")
        for i, s in enumerate(self.seats):
            a = actions[i]
            if a not in self.legal(i):
                raise ValueError(f"hanh dong {a} khong hop le cho seat {i}")
            if a == ACT_BUY:
                s.gold -= 3
                s.strength += 2.0
            s.gold += 5
        self.round_ += 1
        if self.done():
            for i, s in enumerate(self.seats):
                self._scores[i] = s.strength + 0.1 * s.gold + self.rng.random() * 1e-6
        return self._obs()

    def done(self) -> bool:
        return self.round_ >= ROUNDS

    def placements(self) -> dict[int, int]:
        if not self.done():
            raise RuntimeError("tran chua ket thuc")
        order = sorted(self._scores, key=lambda i: -self._scores[i])
        return {seat: rank + 1 for rank, seat in enumerate(order)}
