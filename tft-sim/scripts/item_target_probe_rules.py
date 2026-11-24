"""Luat chon dich item dung chung (tach khoi probe de tai su dung)."""
from tft_goat.env import actions as ACT


def value(state, u):
    return ACT._champ_cost(state, u.champion_api) * 3 ** (int(getattr(u, "star", 1)) - 1)


def pick(rule, state, player, cands):
    import random
    if rule == "cheapest":
        return min(cands, key=lambda u: ACT._champ_cost(state, u.champion_api))
    if rule == "random":
        return random.Random(state.round_index * 131 + len(player.board)).choice(cands)
    if rule == "spread":
        return min(cands, key=lambda u: (u.items, -value(state, u)))
    if rule == "valuemax":
        return max(cands, key=lambda u: value(state, u))
    return max(cands, key=lambda u: ACT._champ_cost(state, u.champion_api))
