"""Noi dung B cho transfer test: cung 8 tuong (cung thu tu, cung so chieu flat), nhung hoan vi
cost va trait giua cac tuong bang seed co dinh. Patch rieng de tranh dung nham cache.
Assert: so tuong, ten tuong va thu tu khop A, nen mo hinh huan luyen tren A chay duoc tren B."""
from __future__ import annotations

import random

from tft_sim.content import build_full_recipe_content

B_SEED = 1234
B_PATCH = "synth-fullrecipe-B"


def build_shuffled_content(seed: int = B_SEED):
    a = build_full_recipe_content()
    keys = list(a.champions.keys())  # thu tu co dinh, giong A
    rng = random.Random(seed)
    costs = [a.champions[k].cost for k in keys]
    traits = [tuple(a.champions[k].traits) for k in keys]
    for _ in range(100):
        rng.shuffle(costs)
        if costs != [a.champions[k].cost for k in keys]:
            break
    for _ in range(100):
        rng.shuffle(traits)
        if traits != [tuple(a.champions[k].traits) for k in keys]:
            break
    champs = {}
    for k, c, t in zip(keys, costs, traits):
        champs[k] = a.champions[k].model_copy(update={"cost": c, "traits": t})
    b = a.model_copy(update={"champions": champs, "patch": B_PATCH})
    assert list(b.champions.keys()) == keys
    assert sorted(c.cost for c in b.champions.values()) == sorted(c.cost for c in a.champions.values())
    assert [c.cost for c in b.champions.values()] != [c.cost for c in a.champions.values()]
    return b
