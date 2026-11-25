"""Kiem tra ro ri va bat bien truoc khi dien giai mask (model-plan 10.6).
1) Ro ri: doi HP va sao mot unit tren ban trong trang thai song; dim an (condition a) khong doi, dim HP doi o (b).
2) Bat bien cua teacher v4: doi HP / sao unit, teacher co chon cung hanh dong khong?
Args: n_states (mac dinh 60). In ket qua, khong ghi file."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from mask_exp import fmask_for, apply_fmask
from tft_goat.engine.resolver import EngineResolver
from tft_goat.env.tft_env import TftEnv
from tft_sim.features_v4 import universal_features_v4
from tft_sim.params import make_aug_rule
from tft_sim.real_content import build_real

N = int(sys.argv[1]) if len(sys.argv) > 1 else 60
env = TftEnv(set_content=build_real("TFTSet17"), resolver=EngineResolver())
v4 = make_aug_rule()
rng = np.random.default_rng(0)
obs, infos = env.reset(seed=150123)
fm = {c: fmask_for(c) for c in "abc"}
ndiff = {c: 0 for c in "abc"}
inv_total = inv_same = 0
inv_hp_total = [0, 0]
inv_star_total = [0, 0]
tested = 0
for t in range(400):
    if not env.agents or tested >= N:
        break
    a = env.agents[t % len(env.agents)]
    st = env._state
    p = st.players[a]
    if p.board and p.hp > 40:
        mask = env.encoder.action_mask(st, a)
        x0 = universal_features_v4(env.encoder.encode(st, a), env, a)
        act0 = int(v4(env, a, None, mask, rng))
        old_hp, u = p.hp, p.board[0]
        old_star = u.star
        p.hp = old_hp - 30
        x1 = universal_features_v4(env.encoder.encode(st, a), env, a)
        act1 = int(v4(env, a, None, mask, rng))
        p.hp = old_hp
        u.star = 2 if old_star == 1 else 1
        act2 = int(v4(env, a, None, mask, rng))
        u.star = old_star
        inv_hp_total[0] += 1; inv_hp_total[1] += int(act0 == act1)
        inv_star_total[0] += 1; inv_star_total[1] += int(act0 == act2)
        p.hp = old_hp - 30
        u.star = 2 if old_star == 1 else 1
        x1 = universal_features_v4(env.encoder.encode(st, a), env, a)
        p.hp, u.star = old_hp, old_star
        for c in "abc":
            if not np.array_equal(apply_fmask(x0, fm[c]), apply_fmask(x1, fm[c])):
                ndiff[c] += 1
        inv_total += 1
        inv_same += int(act0 == act1)
        tested += 1
    acts = {ag: int(v4(env, ag, None, infos[ag]["action_mask"], rng)) for ag in env.agents}
    obs, _, _, _, infos = env.step(acts)
print(f"trang thai: {tested}")
for c in "abc":
    print(f"dieu kien {c}: khac sau khi doi HP+sao = {ndiff[c]} / {tested}  (ky vong: a=0, b>0, c>0)")
print(f"teacher v4, doi HP: chon cung hanh dong {inv_hp_total[1]} / {inv_hp_total[0]}")
print(f"teacher v4, doi sao unit tren ban: chon cung hanh dong {inv_star_total[1]} / {inv_star_total[0]}")
