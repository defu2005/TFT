"""Giai dau v2 (model-plan 10.8, sau khi sua): 8 ghe, moi ghe MOT policy, thu tu ghe hoan vi theo lobby
bang luong ngau nhien DOC LAP: np.random.default_rng([seed, 1]). Luat trang bi theo ghe: 'valuemax' cho ghe
duoc chi dinh (RULE_OF_SEAT, monkeypatch ACT._equip); ghe khac giu luat goc.
Args: selftest | run LO HI OUT.json [v2|drop]  (mac dinh v2 = nhu 10.9)"""
import json, random, sys
from pathlib import Path
import numpy as np
import torch
sys.path.insert(0, str(Path(__file__).parent))
from mask_exp import apply_fmask
from tft_goat.engine.resolver import EngineResolver
from tft_goat.env import actions as ACT
from tft_goat.env.tft_env import TftEnv
from tft_sim.bc_train import MaskedMLP
from tft_sim.features_v4 import universal_features_v4
from tft_sim.params import make_aug_rule, make_swap_rule
from tft_sim.real_content import build_real
from tft_sim.tftgoat import scripted_policy

torch.set_num_threads(1)
RULE_OF_SEAT = {}  # agent_id -> "default" | "valuemax"
_orig_equip = ACT._equip


def _value(state, u):
    return ACT._champ_cost(state, u.champion_api) * 3 ** (int(getattr(u, "star", 1)) - 1)


def _alt_equip(state, player):
    if RULE_OF_SEAT.get(player.agent_id, "default") != "valuemax":
        return _orig_equip(state, player)
    if len(player.components) < ACT.COMPONENTS_PER_ITEM:
        return
    cands = [u for u in player.board if u.items < ACT.ITEMS_MAX]
    if not cands:
        return
    item_api = ACT.combine_components(player.components[0], player.components[1], state.set_content)
    if item_api is None:
        return
    target = max(cands, key=lambda u: _value(state, u))
    target.item_apis = tuple(target.item_apis) + (item_api,)
    target.items += 1
    del player.components[0:ACT.COMPONENTS_PER_ITEM]


ACT._equip = _alt_equip


def clone_policy(ckpt):
    from tft_sim.bc_train import MaskedMLP as _M
    ck = torch.load(ckpt, weights_only=False)
    model = _M(ck["in_dim"]); model.load_state_dict(ck["state"]); model.eval()
    mu, sd, fm = ck["mu"], ck["sd"], ck["fmask"]

    @torch.no_grad()
    def pol(env_, agent, obs, mask, rng):
        x = apply_fmask(universal_features_v4(obs, env_, agent), fm)
        xt = torch.from_numpy(((x - mu) / sd).astype(np.float32))[None]
        return int(torch.argmax(model(xt, torch.from_numpy(np.asarray(mask, dtype=bool))[None]), dim=1).item())
    return pol


# Pool v2 (model-plan 10.9, 280000-283999) va pool drop (model-plan 10.10, 284000-287999).
SLOTS = ["scripted", "v3", "v4", "v4_null", "mask_full", "mask_c", "mask_a", "v4_valuemax"]
SLOTS_DROP = ["v4", "v4_null", "mask_full", "mask_c", "mask_a", "drop@full", "drop@c", "drop@a"]
POOLS = {"v2": SLOTS, "drop": SLOTS_DROP}


def build_pool(v4, slots=SLOTS):
    from dropout_exp import drop_policy
    builders = {
        "scripted": lambda: scripted_policy,
        "v3": lambda: make_swap_rule(key="value"),
        "v4": lambda: v4,
        "v4_null": lambda: v4,
        "mask_full": lambda: clone_policy("results/checkpoints/mask_full.pt"),
        "mask_c": lambda: clone_policy("results/checkpoints/mask_c.pt"),
        "mask_a": lambda: clone_policy("results/checkpoints/mask_a.pt"),
        "v4_valuemax": lambda: v4,
        "drop@full": lambda: drop_policy("results/checkpoints/drop.pt", "full"),
        "drop@c": lambda: drop_policy("results/checkpoints/drop.pt", "c"),
        "drop@a": lambda: drop_policy("results/checkpoints/drop.pt", "a"),
    }
    return {name: builders[name]() for name in slots}


def seat_assignment(seed: int, slots=SLOTS):
    """Hoan vi cac policy len 8 ghe, doc lap voi luong cua env. Moi slot chi mot ghe."""
    assert len(slots) == 8
    perm = np.random.default_rng([seed, 1]).permutation(8)
    agents = [f"player_{i}" for i in range(8)]
    return {agents[i]: slots[perm[i]] for i in range(8)}


def play_lobby(env, seed, pool, seat_policy):
    RULE_OF_SEAT.clear()
    for a, name in seat_policy.items():
        RULE_OF_SEAT[a] = "valuemax" if name == "v4_valuemax" else "default"
    rngs = {a: random.Random(seed * 100 + i) for i, a in enumerate(sorted(seat_policy))}
    obs, infos = env.reset(seed=seed)
    step, illegal = 0, 0
    while env.agents and step < 20000:
        actions = {}
        for a in list(env.agents):
            mask = infos[a]["action_mask"]
            act = pool[seat_policy[a]](env, a, obs[a], mask, rngs[a])
            illegal += int(not mask[act])
            actions[a] = act
        obs, _, _, _, infos = env.step(actions)
        step += 1
    return {a: {"policy": seat_policy[a], "placement": env._state.players[a].placement,
                "completed": not env.agents, "illegal": illegal} for a in seat_policy}


def selftest(env, seeds, v4):
    ok = True
    for s in seeds:
        ACT._equip = _orig_equip
        ref = {}
        for i, (a) in enumerate(sorted([f"player_{k}" for k in range(8)])):
            pass
        pool = {"v4": v4}
        seat = {f"player_{k}": "v4" for k in range(8)}
        ref = play_lobby(env, s, pool, seat)  # ban goc (khong patch)
        ACT._equip = _alt_equip
        got = play_lobby(env, s, pool, seat)  # da patch, moi ghe mac dinh
        same = all(ref[a]["placement"] == got[a]["placement"] for a in seat)
        ok &= same
        print("seed", s, "khop", same, flush=True)
    print("SELFTEST", "PASS" if ok else "FAIL", flush=True)
    return ok


if __name__ == "__main__":
    env = TftEnv(set_content=build_real("TFTSet17"), resolver=EngineResolver())
    v4 = make_aug_rule()
    if sys.argv[1] == "selftest":
        selftest(env, range(150000, 150005), v4)
    else:
        lo, hi, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        slots = POOLS[sys.argv[5] if len(sys.argv) > 5 else "v2"]
        pool = build_pool(v4, slots)
        rows = []
        for s in range(lo, hi):
            sp = seat_assignment(s, slots)
            res = play_lobby(env, s, pool, sp)
            for a, r in res.items():
                rows.append({"seed": s, "agent": a, **r})
        Path(out).write_text(json.dumps(rows), encoding="utf-8")
        print("DONE", len(rows), flush=True)
