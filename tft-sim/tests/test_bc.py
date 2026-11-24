import random

import pytest

torch = pytest.importorskip("torch")

from tft_sim.bc import make_policy, train_bc  # noqa: E402
from tft_sim.collect import collect  # noqa: E402
from tft_sim.env import ToyEnv  # noqa: E402


def teacher(obs, rng):
    return 1 if 1 in obs["legal"] and obs["gold"] >= 6 else 0


def test_bc_never_outputs_illegal_action():
    rows = collect(ToyEnv(), teacher, list(range(20)))
    model = train_bc(rows, epochs=50)
    policy = make_policy(model)
    for r in rows[:200]:
        assert policy(r["obs"], random.Random(0)) in r["obs"]["legal"]
