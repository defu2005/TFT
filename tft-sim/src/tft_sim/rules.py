"""Quy tac bao (wrapper) quanh teacher scripted cua TFT_GOAT. KHONG sua TFT_GOAT.

sell:  khi banc day va co the ban, ban unit banc re nhat (chi mot bien the cua quy tac 'lam thong banc').
floor: nguong vang cho BUY_XP/REROLL; thay the ECON_FLOOR=54 cua teacher (chi ha xuong, khong nang len).
"""
from __future__ import annotations
import numpy as np
from tft_sim.tftgoat import scripted_policy
from tft_goat.env.actions import BUY_XP, PASS, REROLL, SELL_BENCH_START

_NON_BLOCK = {"EQUIP", "FIELD", "PICK_AUGMENT", "PICK_GOD", "REROLL_AUGMENT", "BUY_SHOP"}


def make_rule(sell: bool = False, floor: int = 54, pick: str = "cheapest"):
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
            champs = env._state.set_content.champions
            idx = _pick_sell_hybrid(player, champs) if pick == "hybrid" else _pick_sell(player, champs, pick)
            if idx is not None and mask[SELL_BENCH_START + idx]:
                return SELL_BENCH_START + idx
        return a
    return pol


def _pick_sell(player, champs, pick):
    """Chon unit banc de ban. 'cheapest': gia thap nhat. 'useless': chi unit mot ban (khong co ban sao
    khac tren board/banc) va khong chung trait voi board; trong nhom do chon gia thap nhat; khong co thi None."""
    board_traits = set(t for v in player.board for t in champs[v.champion_api].traits)
    cand = []
    for i, u in enumerate(player.bench):
        cost = champs[u.champion_api].cost
        if pick == "cheapest":
            cand.append((cost, i))
            continue
        same = any(v.champion_api == u.champion_api for v in player.board) or any(
            j != i and v.champion_api == u.champion_api for j, v in enumerate(player.bench))
        shares = bool(set(champs[u.champion_api].traits) & board_traits)
        if not same and not shares:
            cand.append((cost, i))
    return min(cand)[1] if cand else None


def _pick_sell_hybrid(player, champs):
    """Ban 'useless' truoc; neu khong co unit nao thi ban unit re nhat."""
    idx = _pick_sell(player, champs, "useless")
    return idx if idx is not None else _pick_sell(player, champs, "cheapest")
