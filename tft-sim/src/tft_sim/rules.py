"""Quy tac bao (wrapper) quanh teacher scripted cua TFT_GOAT. KHONG sua TFT_GOAT.

sell:  khi banc day va co the ban, ban unit banc re nhat (chi mot bien the cua quy tac 'lam thong banc').
floor: nguong vang cho BUY_XP/REROLL; thay the ECON_FLOOR=54 cua teacher (chi ha xuong, khong nang len).
"""
from __future__ import annotations
import numpy as np
from tft_sim.tftgoat import scripted_policy
from tft_goat.env.actions import BUY_XP, PASS, REROLL, SELL_BENCH_START

_NON_BLOCK = {"EQUIP", "FIELD", "PICK_AUGMENT", "PICK_GOD", "REROLL_AUGMENT", "BUY_SHOP"}


def make_rule(sell: bool = False, floor: int = 54):
    def pol(env, agent, obs, mask, rng):
        a = scripted_policy(env, agent, obs, mask, rng)
        player = env._state.players[agent]
        gold = player.gold
        if floor < 54 and a == PASS:
            if mask[BUY_XP] and gold >= floor:
                a = BUY_XP
            elif mask[REROLL] and gold >= floor:
                a = REROLL
        if sell and len(player.bench) >= 9 and a in (PASS, BUY_XP, REROLL):
            # ban unit banc re nhat (gia thap nhat; hoa ngang: vi tri som)
            costs = []
            for i, u in enumerate(player.bench):
                costs.append((env._state.set_content.champions[u.champion_api].cost, i))
            idx = min(costs)[1]
            if mask[SELL_BENCH_START + idx]:
                return SELL_BENCH_START + idx
        return a
    return pol
