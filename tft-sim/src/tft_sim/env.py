"""Giao dien env toi thieu va mot toy env 8 seat co loai tru seat.

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
START_HP = 6


class Env(Protocol):
    n_seats: int

    def reset(self, seed: int) -> dict[int, dict]: ...
    def step(self, actions: dict[int, int]) -> dict[int, dict]: ...
    def alive(self) -> list[int]: ...
    def legal(self, seat: int) -> list[int]: ...
    def placements(self) -> dict[int, int]: ...
    def done(self) -> bool: ...


@dataclass
class _Seat:
    gold: int = 0
    strength: float = 0.0
    hp: int = START_HP


@dataclass
class ToyEnv:
    """8 seat. Moi vong +5 vang. Mua (ACT_BUY, ton 3 vang) cho +2 strength.

    Seat co strength < 0.5 * vong hien tai mat 3 HP moi vong; het HP thi bi loai.
    Ket thuc khi con <= 1 seat hoac het ROUNDS. Diem cuoi = strength + 0.1*gold + nhieu nho.
    Seat con song xep truoc; seat bi loai xep theo thu tu nguoc (loai muon hon = hang cao hon).
    """

    n_seats: int = N_SEATS
    seats: list[_Seat] = field(default_factory=list)
    rng: random.Random = field(default_factory=random.Random)
    round_: int = 0
    _eliminated: list[int] = field(default_factory=list)
    _scores: dict[int, float] = field(default_factory=dict)

    def reset(self, seed: int) -> dict[int, dict]:
        self.rng = random.Random(seed)
        self.seats = [_Seat() for _ in range(self.n_seats)]
        self.round_ = 0
        self._eliminated = []
        self._scores = {}
        return self._obs()

    def alive(self) -> list[int]:
        return [i for i in range(self.n_seats) if self.seats[i].hp > 0]

    def _obs(self) -> dict[int, dict]:
        return {
            i: {"gold": s.gold, "strength": s.strength, "round": self.round_, "legal": self.legal(i)}
            for i, s in enumerate(self.seats)
            if s.hp > 0
        }

    def legal(self, seat: int) -> list[int]:
        if self.seats[seat].hp <= 0:
            return []
        acts = [ACT_PASS]
        if self.seats[seat].gold >= 3:
            acts.append(ACT_BUY)
        return acts

    def step(self, actions: dict[int, int]) -> dict[int, dict]:
        if self.done():
            raise RuntimeError("tran da ket thuc")
        alive = self.alive()
        if set(actions) != set(alive):
            raise ValueError(f"can hanh dong cho dung cac seat con song {alive}")
        for i in alive:
            s = self.seats[i]
            a = actions[i]
            if a not in self.legal(i):
                raise ValueError(f"hanh dong {a} khong hop le cho seat {i}")
            if a == ACT_BUY:
                s.gold -= 3
                s.strength += 2.0
            s.gold += 5
        self.round_ += 1
        for i in alive:
            s = self.seats[i]
            if s.strength < 0.5 * self.round_:
                s.hp -= 3
                if s.hp <= 0:
                    self._eliminated.append(i)
        if self.done():
            for i in range(self.n_seats):
                s = self.seats[i]
                self._scores[i] = s.strength + 0.1 * s.gold + self.rng.random() * 1e-6
        return self._obs()

    def done(self) -> bool:
        return self.round_ >= ROUNDS or len(self.alive()) <= 1

    def placements(self) -> dict[int, int]:
        if not self.done():
            raise RuntimeError("tran chua ket thuc")
        survivors = sorted(self.alive(), key=lambda i: -self._scores[i])
        order = survivors + list(reversed(self._eliminated))
        return {seat: rank + 1 for rank, seat in enumerate(order)}
