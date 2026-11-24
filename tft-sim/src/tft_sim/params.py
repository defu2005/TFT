"""Chinh sach tham so hoa tren v3 (giai doan 3). theta = (xp_floor, reroll_floor, dup_w, trait_w).
Chi thay doi: nguong vang cho BUY_XP/REROLL, va diem chon slot mua. Ban sell/swap giu nguyen v3.
v3 (theta mac dinh) = (54, 54, 5, 1), voi scoring cua teacher.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from tft_goat.env.actions import BUY_SHOP_START, BUY_XP, PASS, REROLL
from tft_sim.rules import make_swap_rule
from tft_sim.tftgoat import scripted_policy

V3_THETA = (54, 54, 5, 1)


@dataclass(frozen=True)
class Theta:
    xp_floor: int = 54
    reroll_floor: int = 54
    dup_w: int = 5
    trait_w: int = 1

    @classmethod
    def from_vec(cls, v):
        return cls(int(round(v[0])), int(round(v[1])), int(round(v[2])), int(round(v[3])))


def _buy_score(player, champs, slot_api, dup_w, trait_w):
    owned = {u.champion_api for u in player.all_units()}
    owned_traits = set(t for u in player.all_units() for t in champs[u.champion_api].traits)
    s = dup_w if slot_api in owned else 0
    s += trait_w * sum(1 for t in champs[slot_api].traits if t in owned_traits)
    return s


def make_param_policy(theta: Theta):
    base = make_swap_rule(key="value", sell=True, floor=54)  # v3: floor 54 cung cho ca hai

    def pol(env, agent, obs, mask, rng):
        a = base(env, agent, obs, mask, rng)  # v3 (co swap + sell)
        player = env._state.players[agent]
        champs = env._state.set_content.champions
        gold = player.gold
        # nguong vang: bo XP/REROLL neu duoi nguong; mo them neu nguong thap hon 54
        if a == BUY_XP and gold < theta.xp_floor:
            a = PASS
        elif a == REROLL and gold < theta.reroll_floor:
            a = PASS
        elif a == PASS:
            if mask[BUY_XP] and gold >= theta.xp_floor and theta.xp_floor < 54:
                a = BUY_XP
            elif mask[REROLL] and gold >= theta.reroll_floor and theta.reroll_floor < 54:
                a = REROLL
        # chon slot mua theo diem tham so
        if BUY_SHOP_START <= a < BUY_SHOP_START + 5:
            legal = [i for i in range(5) if mask[BUY_SHOP_START + i]]
            scored = []
            for i in legal:
                api = player.shop[i]
                if api is None or api not in champs:
                    continue
                scored.append((_buy_score(player, champs, api, theta.dup_w, theta.trait_w), -i, i))
            if scored:
                a = BUY_SHOP_START + max(scored)[2]
        return a
    return pol


def make_endgame(hp_threshold: int):
    """v3 + chi tieu vang khi may: neu hp <= hp_threshold thi PASS -> BUY_XP (neu hop le) hoac REROLL (neu hop le).
    Vang con lai khi chet khong co gia tri (bottom-4 chet voi ~62 vang), nen tieu het la khong mat gi."""
    from tft_sim.rules import make_swap_rule as _mk
    base = _mk(key="value", sell=True, floor=54)

    def pol(env, agent, obs, mask, rng):
        a = base(env, agent, obs, mask, rng)
        player = env._state.players[agent]
        if a == PASS and player.hp <= hp_threshold:
            if mask[BUY_XP]:
                return BUY_XP
            if mask[REROLL]:
                return REROLL
        return a
    return pol
