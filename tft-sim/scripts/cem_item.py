"""CEM hoc chinh sach chon dich trang bi tren EngineResolver (chinh sach hoc duoc dau tien).
Diem unit = w . [cost, sao, items, gia tri cost*3^(sao-1), la tank]; chon unit diem cao nhat.
Nhom A dung chinh sach w, nhom B mac dinh (cost cao nhat). Fitness = trung binh A-B (cang am cang tot).
Tap tinh chinh 220000-220199 (co dinh moi the he). Giu lai: 230000-230999 (chua dung).
Args: gens pop lo hi out.json   (chay 4 tien trinh song song)."""
import json, sys
from multiprocessing import Pool
from pathlib import Path
import numpy as np

GENS, POP, OUT = int(sys.argv[1]), int(sys.argv[2]), sys.argv[5]
DEV_LO, DEV_HI = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (220000, 220200)
HELD_LO, HELD_HI = (int(sys.argv[6]), int(sys.argv[7])) if len(sys.argv) > 7 else (230000, 231000)
FEAT_N = 5

def _feat(state, u):
    from tft_goat.env import actions as ACT
    cost = ACT._champ_cost(state, u.champion_api)
    star = int(getattr(u, "star", 1))
    tank = 1.0 if "tank" in str(getattr(u, "role", "")).lower() else 0.0
    return np.array([cost, star, u.items, cost * 3 ** (star - 1), tank], dtype=float)

def _run(args):
    w, lo, hi, mode = args
    import tft_goat.env.actions as ACT
    from tft_goat.engine.resolver import EngineResolver
    from tft_goat.env.tft_env import TftEnv
    from tft_sim.params import make_aug_rule
    from tft_sim.real_content import build_real
    from tft_sim.tftgoat import play, seat_groups
    orig = ACT._equip
    GA = set()

    def equip(state, player):
        if player.agent_id not in GA or w is None:
            return orig(state, player)
        if len(player.components) < ACT.COMPONENTS_PER_ITEM:
            return
        cands = [u for u in player.board if u.items < ACT.ITEMS_MAX]
        if not cands:
            return
        item = ACT.combine_components(player.components[0], player.components[1], state.set_content)
        if item is None:
            return
        scores = [float(w @ _feat(state, u)) for u in cands]
        t = cands[int(np.argmax(scores))]
        t.item_apis = tuple(t.item_apis) + (item,)
        t.items += 1
        del player.components[0:ACT.COMPONENTS_PER_ITEM]

    ACT._equip = equip
    env = TftEnv(set_content=build_real("TFTSet17"), resolver=EngineResolver())
    v4 = make_aug_rule()
    out = []
    for s in range(lo, hi):
        GA.clear(); GA.update(k for k, g in seat_groups(s).items() if g == "A")
        l = play(env, s, v4, v4)
        out.append(float(np.mean(l.placements_a) - np.mean(l.placements_b)))
    ACT._equip = orig
    return out

def main():
    rng = np.random.default_rng(0)
    mu, sd = np.zeros(FEAT_N), np.ones(FEAT_N) * 1.0
    log = []
    with Pool(4) as pool:
        for g in range(GENS):
            cands = [rng.normal(mu, sd) for _ in range(POP)]
            jobs = [(w, DEV_LO, DEV_HI, "dev") for w in cands]
            res = pool.map(_run, jobs)
            fit = np.array([np.mean(r) for r in res])
            elite = [cands[i] for i in np.argsort(fit)[: max(2, POP // 4)]]
            mu = np.mean(elite, axis=0); sd = np.std(elite, axis=0) + 0.05
            log.append({"gen": g, "best_fit": float(fit.min()), "mean_fit": float(fit.mean()), "best_w": cands[int(np.argmin(fit))].tolist()})
            print("GEN", g, round(float(fit.min()), 4), round(float(fit.mean()), 4), flush=True)
        best = mu.tolist()
        held = pool.map(_run, [(np.array(best), HELD_LO, HELD_HI, "held"), (None, HELD_LO, HELD_HI, "held")])
    a = np.array(held[0]); b = np.array(held[1])
    rng2 = np.random.default_rng(1)
    bs = [a[rng2.integers(0, len(a), len(a))].mean() for _ in range(2000)]
    Path(OUT).write_text(json.dumps({"gens": GENS, "pop": POP, "log": log, "w": best,
        "held_mean_A_minus_B": float(a.mean()), "held_ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
        "held_n": len(a)}, indent=2), encoding="utf-8")
    print("HELD", round(float(a.mean()), 4), "(note: 2 run dau = learned vs default; so sanh qua file)", flush=True)

if __name__ == "__main__":
    main()
