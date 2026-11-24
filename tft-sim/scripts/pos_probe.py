"""Do dinh vi trong engine. Nhom A doi vi tri sau khi _build_team dat mac dinh; nhom B giu mac dinh.
Mode: rev (carry ra truoc, tank sau), shuffle (xao ngau nhien cac o da dung), default (null).
Gan nhom bang id() cua list board truoc khi combat (patch rounds._fight).
Args: MODE lo hi. Ghi results/fixed/real/pos_<MODE>_<lo>.json (A-B, am = A tot hon)."""
import json, random, sys
from pathlib import Path
import numpy as np
import tft_goat.engine.simulate as SIM
import tft_goat.env.rounds as RD
from tft_goat.engine.resolver import EngineResolver
from tft_goat.env.tft_env import TftEnv
from tft_sim.params import make_aug_rule
from tft_sim.real_content import build_real
from tft_sim.tftgoat import play, seat_groups

MODE, lo, hi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
GROUP_A: set[str] = set()
GROUPMAP: dict[int, str] = {}
_orig_build = SIM._build_team
_orig_fight = RD._fight

def _fight(state, resolver, p, q):
    GROUPMAP.clear()
    GROUPMAP[id(p.board)] = "A" if p.agent_id in GROUP_A else "B"
    GROUPMAP[id(q.board)] = "A" if q.agent_id in GROUP_A else "B"
    return _orig_fight(state, resolver, p, q)

def _front(pos, team):
    row = pos[0]
    return row if team == 0 else SIM.GRID_ROWS - 1 - row

def _build(board, team, content, trait_bonus=0):
    units = _orig_build(board, team, content, trait_bonus)
    if MODE == "default" or GROUPMAP.get(id(board)) != "A" or not units:
        return units
    P = [u.pos for u in units]
    if MODE == "rev":
        carries_first = sorted(units, key=lambda u: SIM._frontline_score(u))
        front_first = sorted(P, key=lambda p: -_front(p, team))
        for u, p in zip(carries_first, front_first):
            u.pos = p
    else:  # shuffle
        rng = random.Random(len(units) * 7 + team)
        perm = list(P); rng.shuffle(perm)
        for u, p in zip(units, perm):
            u.pos = p
    return units

SIM._build_team = _build
RD._fight = _fight
env = TftEnv(set_content=build_real("TFTSet17"), resolver=EngineResolver())
v4 = make_aug_rule()
per = []
for s in range(lo, hi):
    GROUP_A.clear(); GROUP_A.update(k for k, g in seat_groups(s).items() if g == "A")
    l = play(env, s, v4, v4)
    per.append(float(np.mean(l.placements_a) - np.mean(l.placements_b)))
Path("results/fixed/real").mkdir(parents=True, exist_ok=True)
Path(f"results/fixed/real/pos_{MODE}_{lo}.json").write_text(json.dumps({"mode": MODE, "seeds": f"{lo}-{hi-1}", "per_lobby_diff_A_minus_B": per}), encoding="utf-8")
print("DONE", MODE, round(float(np.mean(per)), 4), flush=True)
