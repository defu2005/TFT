"""Runner dung chung cho TFT_GOAT: lobby 8 seat, xoay seat bang shuffle co seed, thu thap,
danh gia theo placement. Moi policy co chu ky (env, agent, obs, mask, rng) -> action.

Ghi chu: nhan 'synthetic' trong moi ket qua nghia la dung build_sample_content (khong phai TFT that).
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

import numpy as np

N_SEATS = 8
MAX_STEPS = 20000
ACTION_TYPES = [
    ("PASS", 0, 1), ("REROLL", 1, 2), ("BUY_XP", 2, 3), ("BUY_SHOP", 3, 8), ("SELL_BENCH", 8, 17),
    ("FIELD", 17, 26), ("BENCH_BOARD", 26, 35), ("EQUIP", 35, 36), ("PICK_AUGMENT", 36, 39),
    ("PICK_GOD", 39, 42), ("REROLL_AUGMENT", 42, 43),
]


def action_type(a: int) -> str:
    for name, lo, hi in ACTION_TYPES:
        if lo <= a < hi:
            return name
    return "UNKNOWN"


def make_env(content):
    from tft_goat.env.tft_env import TftEnv

    return TftEnv(set_content=content)  # luon truyen content: TftEnv() mac dinh se tai mang


def default_content():
    """Noi dung tong hop DA SUA cong thuc (xem tft_sim/content.py)."""
    from tft_sim.content import build_full_recipe_content

    return build_full_recipe_content()


def seat_groups(seed: int) -> dict[str, str]:
    """Chia 4/4 bang shuffle co seed: khong phu thuoc thu tu ghe lien tiep."""
    rng = random.Random(seed)
    seats = list(range(N_SEATS))
    rng.shuffle(seats)
    a = set(seats[: N_SEATS // 2])
    return {f"player_{i}": ("A" if i in a else "B") for i in range(N_SEATS)}


def scripted_policy(env, agent, obs, mask, rng) -> int:
    from tft_goat.agent.scripted import scripted_action

    return int(scripted_action(env._state, env._state.players[agent]))


def random_policy(env, agent, obs, mask, rng) -> int:
    return int(rng.choice(np.flatnonzero(mask)))


def teacher_action(env, agent) -> int:
    return scripted_policy(env, agent, None, None, None)


_TIER_RANK = {"silver": 1, "gold": 2, "prismatic": 3}


def augment_tiers(env, agent) -> np.ndarray:
    """Tier cua 3 augment dang duoc chao (1 silver, 2 gold, 3 prismatic; 0 = khong co hoac khong ro).
    Day la thong tin ma nguoi choi that nhin thay; khong nam trong observation cua TFT_GOAT."""
    out = np.zeros(3, dtype=np.float32)
    p = env._state.players[agent]
    aug = env._state.set_content.augments
    for i, name in enumerate(list(p.augment_offer)[:3]):
        a = aug.get(name)
        out[i] = _TIER_RANK.get(a.tier, 0) if a is not None else 0
    return out


def universal_features(obs: dict, env, agent) -> np.ndarray:
    """Dac trung 'universal' DUY NHAT dung cho ca thu thap, huan luyen va policy.
    Gom theo KEY (khong cat theo offset): scalars, opponents, gods, slot (aux), tier augment."""
    return np.concatenate([
        np.asarray(obs["scalars"], np.float32).ravel(),
        np.asarray(obs["opponents"], np.float32).ravel(),
        np.asarray(obs["gods"], np.float32).ravel(),
        slot_features(env, agent),
        augment_tiers(env, agent),
    ])


def owned_counts(player) -> dict[str, int]:
    counts: dict[str, int] = {}
    for u in player.all_units():
        counts[u.champion_api] = counts.get(u.champion_api, 0) + int(getattr(u, "copies", 1))
    return counts


def slot_features(env, agent) -> np.ndarray:
    """Dac trung moi o shop, tinh tu trang thai cua CHINH nguoi choi va noi dung tinh:
    [co_tuong, so_ban_dang_so_huu, cost/5, so_trait_trung_voi_doi_hien_tai] x 5 o."""
    state = env._state
    player = state.players[agent]
    owned = owned_counts(player)
    owned_traits: set[str] = set()
    for api in owned:
        ch = state.set_content.champions.get(api)
        if ch:
            owned_traits.update(ch.traits)
    out = np.zeros((5, 4), dtype=np.float32)
    for i in range(5):
        api = player.shop[i] if i < len(player.shop) else None
        if not api:
            continue
        ch = state.set_content.champions.get(api)
        out[i, 0] = 1.0
        out[i, 1] = owned.get(api, 0) / 3.0
        out[i, 2] = (ch.cost if ch else 0) / 5.0
        out[i, 3] = (sum(1 for t in ch.traits if t in owned_traits) if ch else 0) / 3.0
    return out.ravel()


def flat_obs(obs: dict) -> np.ndarray:
    parts = []
    for key in ("scalars", "shop", "bench", "board", "traits", "opponents", "gods"):
        parts.append(np.asarray(obs[key], dtype=np.float32).ravel())
    return np.concatenate(parts)


@dataclass
class Lobby:
    seed: int
    placements_a: list[int] = field(default_factory=list)
    placements_b: list[int] = field(default_factory=list)
    completed: bool = False
    steps: int = 0
    illegal: dict = field(default_factory=lambda: {"A": 0, "B": 0})
    type_hits: dict = field(default_factory=dict)  # clone vs teacher theo loai hanh dong (chi khi check_teacher)
    type_total: dict = field(default_factory=dict)
    rows: list = field(default_factory=list)  # (flat, slot_feat, mask, action, seed, seat, step)
    uni: list = field(default_factory=list)  # universal_features cho moi dong (cung thu tu rows)
    tiers: list = field(default_factory=list)  # (3,) hang tuong ung, bang rows: tier augment dang duoc chao (0 = khong co)


def play(env, seed: int, policy_a, policy_b, *, collect: bool = False, check_teacher: bool = False,
         featurize_aux: bool = True) -> Lobby:
    groups = seat_groups(seed)
    rngs = {a: random.Random(seed * 100 + i) for i, a in enumerate(groups)}
    obs, infos = env.reset(seed=seed)
    lob = Lobby(seed=seed)
    step = 0
    while env.agents and step < MAX_STEPS:
        actions = {}
        for a in list(env.agents):
            g = groups[a]
            pol = policy_a if g == "A" else policy_b
            mask = infos[a]["action_mask"]
            if collect:
                flat = flat_obs(obs[a])
                aux = slot_features(env, a) if featurize_aux else None
            act = pol(env, a, obs[a], mask, rngs[a])
            if not mask[act]:
                lob.illegal[g] += 1
            if collect:
                lob.rows.append((flat, aux, mask.copy(), int(act), seed, int(a.split("_")[1]), step))
                lob.tiers.append(augment_tiers(env, a))
                lob.uni.append(universal_features(obs[a], env, a))
            if check_teacher and g == "A" and int(mask.sum()) >= 2:
                t = teacher_action(env, a)
                name = action_type(t)
                lob.type_total[name] = lob.type_total.get(name, 0) + 1
                lob.type_hits[name] = lob.type_hits.get(name, 0) + int(t == act)
            actions[a] = act
        obs, rewards, terms, truncs, infos = env.step(actions)
        step += 1
    lob.steps = step
    lob.completed = not env.agents
    for a, g in groups.items():
        pl = env._state.players[a].placement
        (lob.placements_a if g == "A" else lob.placements_b).append(pl)
    return lob


def bootstrap_ci(diffs: np.ndarray, n: int = 2000, seed: int = 0) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    boots = [diffs[rng.integers(0, len(diffs), len(diffs))].mean() for _ in range(n)]
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return float(lo), float(hi)


def summarize(lobbies: list[Lobby]) -> dict:
    done = [l for l in lobbies if l.completed]
    if not done:
        return {"lobbies": len(lobbies), "completed": 0}
    diffs = np.array([np.mean(l.placements_a) - np.mean(l.placements_b) for l in done])
    lo, hi = bootstrap_ci(diffs)
    return {
        "lobbies": len(lobbies),
        "completed": len(done),
        "mean_placement_A": float(np.mean([p for l in done for p in l.placements_a])),
        "mean_placement_B": float(np.mean([p for l in done for p in l.placements_b])),
        "diff_A_minus_B": float(diffs.mean()),
        "ci95_diff": [lo, hi],
        "illegal_A": sum(l.illegal["A"] for l in lobbies),
        "illegal_B": sum(l.illegal["B"] for l in lobbies),
    }


BENCH_SLOTS = 9
BOARD_SLOTS = 9  # BENCH_BOARD chi co 9 hanh dong; board 10 (cap 10) khong duoc mo ta o day (xem README)


def _unit_value(champs, u) -> float:
    c = champs[u.champion_api]
    return float(c.cost * 3 ** (u.star - 1))


def bench_board_features(env, agent) -> np.ndarray:
    """Dac trung bench/board cho v2 (uni2 = uni + phan nay). Moi slot: co unit, gia/5, sao/3, value/15.
    Bench them: co ban sao khac, chung trait voi board. Tong: 4 + 9*6 + 9*4 = 94 chieu."""
    p = env._state.players[agent]
    champs = env._state.set_content.champions
    board_traits = set(t for v in p.board for t in champs[v.champion_api].traits)
    out = [len(p.bench) / BENCH_SLOTS, len(p.board) / max(1, p.board_cap),
           float(len(p.bench) >= BENCH_SLOTS), float(len(p.board) >= p.board_cap)]
    for i in range(BENCH_SLOTS):
        if i < len(p.bench):
            u = p.bench[i]
            same = any(v.champion_api == u.champion_api for v in p.board) or any(
                j != i and v.champion_api == u.champion_api for j, v in enumerate(p.bench))
            shares = bool(set(champs[u.champion_api].traits) & board_traits)
            out += [1.0, champs[u.champion_api].cost / 5, u.star / 3, _unit_value(champs, u) / 15,
                    float(same), float(shares)]
        else:
            out += [0.0] * 6
    for i in range(BOARD_SLOTS):
        if i < len(p.board):
            u = p.board[i]
            out += [1.0, champs[u.champion_api].cost / 5, u.star / 3, _unit_value(champs, u) / 15]
        else:
            out += [0.0] * 4
    return np.asarray(out, np.float32)


def universal_features_v2(obs: dict, env, agent) -> np.ndarray:
    """uni2 = universal_features (85) + bench_board_features (4 + 9*6 + 9*4 = 94) -> 179 chieu."""
    return np.concatenate([universal_features(obs, env, agent), bench_board_features(env, agent)])
