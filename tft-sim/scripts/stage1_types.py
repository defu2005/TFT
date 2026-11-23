"""Tach nhieu theo loai tren teacher hybrid (seed 40000-41999). Moi loai: voi xac suat 0.1, chon deu mot hanh dong hop le
loai do (neu co), nguoc lai hybrid. A = hybrid + nhieu loai T, B = hybrid. Am = nhieu tot hon. Chay tuan tu."""
import json, sys
from pathlib import Path
import numpy as np
from tft_sim.real_content import build_real
from tft_sim.rules import make_rule
from tft_sim.tftgoat import action_type, make_env, play, summarize

env = make_env(build_real("TFTSet17"))
hybrid = make_rule(sell=True, floor=54, pick="hybrid")
TYPES = ["PASS", "REROLL", "BUY_XP", "BUY_SHOP", "SELL_BENCH", "FIELD", "BENCH_BOARD", "EQUIP", "PICK_AUGMENT", "PICK_GOD", "REROLL_AUGMENT"]
R = Path("results/fixed/real"); R.mkdir(parents=True, exist_ok=True)
for t in TYPES if len(sys.argv) < 2 else sys.argv[1:]:
    def pol(env_, agent, obs, mask, rng, t=t):
        if rng.random() < 0.1:
            legal = [int(i) for i in np.flatnonzero(mask) if action_type(int(i)) == t]
            if legal:
                return int(rng.choice(legal))
        return hybrid(env_, agent, obs, mask, rng)
    lobs = [play(env, s, pol, hybrid) for s in range(40000, 42000)]
    s = summarize(lobs)
    out = {"type": t, "seeds": "40000-41999", "A": f"hybrid + eps=0.1 type {t}", "B": "hybrid", "summary": s,
           "per_lobby_diff_A_minus_B": [float(np.mean(l.placements_a) - np.mean(l.placements_b)) for l in lobs]}
    (R / f"stage1_types_{t}.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("RESULT", t, round(s["diff_A_minus_B"], 4), s["ci95_diff"], flush=True)
print("ALLSTAGE1TYPES", flush=True)
