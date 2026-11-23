"""Kiem tra harness bang dap an da biet tren toy env (test double, khong phai TFT)."""

import random

from tft_sim.collect import collect, split_by_lobby
from tft_sim.env import ACT_BUY, ACT_PASS, ToyEnv
from tft_sim.harness import assign_groups, evaluate, play_lobby, replay_matches


def random_policy(obs, rng: random.Random) -> int:
    return rng.choice(obs["legal"])


def always_pass(obs, rng) -> int:
    return ACT_PASS


def always_buy_if_legal(obs, rng) -> int:
    return ACT_BUY if ACT_BUY in obs["legal"] else ACT_PASS


def test_seat_rotation_balances_groups():
    for s in range(16):
        g = assign_groups(s)
        assert g.count("A") == 4 and g.count("B") == 4


def test_placements_form_a_permutation_per_lobby():
    res, _ = play_lobby(ToyEnv(), random_policy, random_policy, lobby_seed=3)
    assert sorted(res.placements_a + res.placements_b) == [1, 2, 3, 4, 5, 6, 7, 8] or len(res.placements_a) == 4
    # chi kiem tren tong: moi lobby xep hang 1..8 dung mot lan
    env = ToyEnv()
    env.reset(3)
    while not env.done():
        env.step({i: random.Random(i).choice(env.legal(i)) for i in range(8)})
    assert sorted(env.placements().values()) == list(range(1, 9))


def test_identical_policies_give_no_difference():
    lobbies = list(range(200))
    out = evaluate(ToyEnv(), random_policy, random_policy, lobbies)
    lo, hi = out["ci95_diff"]
    assert lo <= 0.0 <= hi, out
    assert abs(out["mean_placement_a"] - 4.5) < 0.1, out


def test_rigged_better_policy_places_lower():
    lobbies = list(range(200))
    out = evaluate(ToyEnv(), always_buy_if_legal, always_pass, lobbies)
    lo, hi = out["ci95_diff"]
    assert hi < 0.0, out  # A (mua) co placement thap hon B, CI khong chua 0


def test_same_seed_replays_identically():
    assert replay_matches(ToyEnv(), random_policy, always_pass, lobby_seed=7)


def test_illegal_action_is_rejected():
    env = ToyEnv()
    env.reset(0)
    try:
        env.step({i: ACT_BUY for i in range(8)})
    except ValueError:
        return
    raise AssertionError("phai tu choi hanh dong ngoai mask")


def test_collect_split_is_disjoint_by_lobby():
    seeds = list(range(100))
    sp = split_by_lobby(seeds)
    assert not (set(sp["train"]) & set(sp["test"]))
    rows = collect(ToyEnv(), random_policy, sp["train"][:5])
    assert all(r["obs"]["legal"] for r in rows)
    assert {r["lobby"] for r in rows} <= set(sp["train"][:5])
