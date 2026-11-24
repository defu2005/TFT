"""Danh gia choi (placement) tren noi dung that Set 17 (CDragon 18.7), 2000 lobby moi (seed 20000-21999).
Chay TUNG THE NGHIEM mot (tranh het bo nho):
  python scripts/play_real.py null            # scripted vs scripted (phai quanh 0)
  python scripts/play_real.py random          # random vs scripted, + kiem tra replay cung seed (100 seed dau)
  python scripts/play_real.py clone           # universal clone (huan luyen tren Set 17) vs scripted
  python scripts/play_real.py eps01           # scripted co 10% hanh dong ngau nhien vs scripted
  python scripts/play_real.py type:<LOAI>     # voi xac suat 0.1: chon deu mot hanh dong hop le loai LOAI
                                              #   (neu co); nguoc lai scripted. Vi du type:BUY_XP
Ghi: results/fixed/real/play_<name>.json gom tom tat + hieu hang tung lobby (A - B)."""
import json, sys
from pathlib import Path
import numpy as np
import torch
from tft_sim.bc_train import train
from tft_sim.real_content import build_real
from tft_sim.tftgoat import (action_type, make_env, play, random_policy, scripted_policy, summarize,
                             universal_features)

NAME = sys.argv[1]
R = Path("results/fixed/real"); R.mkdir(parents=True, exist_ok=True)
REAL = Path(sys.argv[2]) if len(sys.argv) > 2 else None
SEEDS = range(20000, 22000)
env = make_env(build_real("TFTSet17"))


def eps_policy(eps):
    def pol(env_, agent, obs, mask, rng):
        if rng.random() < eps:
            return int(rng.choice(list(np.flatnonzero(mask))))
        return scripted_policy(env_, agent, obs, mask, rng)
    return pol


def type_policy(t, p=0.1):
    def pol(env_, agent, obs, mask, rng):
        if rng.random() < p:
            legal = [int(i) for i in np.flatnonzero(mask) if action_type(int(i)) == t]
            if legal:
                return int(rng.choice(legal))
        return scripted_policy(env_, agent, obs, mask, rng)
    return pol


def clone_policy():
    z = np.load(REAL / "s17_train.npz")
    model = train(z["uni"], z["mask"], z["action"], epochs=40, seed=0)
    mu, sd = model.norm

    @torch.no_grad()
    def pol(env_, agent, obs, mask, rng):
        x = universal_features(obs, env_, agent)
        xt = torch.from_numpy(((x - mu) / sd).astype(np.float32))[None]
        m = torch.from_numpy(np.asarray(mask, dtype=bool))[None]
        return int(torch.argmax(model(xt, m), dim=1).item())
    return pol


def per_lobby(lobs):
    return [float(np.mean(l.placements_a) - np.mean(l.placements_b)) if l.completed else None for l in lobs]


if NAME == "null":
    pol_a, pol_b = scripted_policy, scripted_policy
elif NAME == "random":
    pol_a, pol_b = random_policy, scripted_policy
elif NAME == "clone":
    pol_a, pol_b = clone_policy(), scripted_policy
elif NAME == "eps01":
    pol_a, pol_b = eps_policy(0.1), scripted_policy
elif NAME.startswith("type:"):
    pol_a, pol_b = type_policy(NAME[5:]), scripted_policy
else:
    raise SystemExit(f"unknown {NAME}")

lobs = []
for i, s in enumerate(SEEDS):
    lobs.append(play(env, s, pol_a, pol_b))
    if i % 250 == 249:
        print(NAME, "progress", i + 1, flush=True)
summ = summarize(lobs)
out = {"experiment": NAME, "content": "CDragon latest (18.7), Set 17 block", "seeds": "20000-21999",
       "summary": summ, "per_lobby_diff_A_minus_B": per_lobby(lobs)}

if NAME == "random":
    # Kiem tra replay: chay lai 100 seed dau, placements phai giong het.
    replay_ok = True
    for s in list(SEEDS)[:100]:
        again = play(env, s, pol_a, pol_b)
        first = lobs[s - SEEDS.start]
        if again.placements_a != first.placements_a or again.placements_b != first.placements_b:
            replay_ok = False
            break
    out["replay_check_100_seeds"] = replay_ok

(R / f"play_{NAME.replace(':', '_')}.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("RESULT", NAME, {k: summ[k] for k in ("completed", "diff_A_minus_B", "ci95_diff", "illegal_A")},
      out.get("replay_check_100_seeds"), flush=True)
