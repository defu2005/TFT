"""Lap lai tren seed MOI 50000-51999 (chua dung): (a) null hybrid vs hybrid, (b) hybrid + nhieu BENCH_BOARD vs hybrid.
Hieu am = nhieu tot hon. Ghi results/fixed/real/stage1_replicate.json."""
import json
from pathlib import Path
import numpy as np
from tft_sim.real_content import build_real
from tft_sim.rules import make_rule
from tft_sim.tftgoat import action_type, make_env, play, summarize

env = make_env(build_real("TFTSet17"))
hybrid = make_rule(sell=True, floor=54, pick="hybrid")

def bb_noise(env_, agent, obs, mask, rng):
    if rng.random() < 0.1:
        legal = [int(i) for i in np.flatnonzero(mask) if action_type(int(i)) == "BENCH_BOARD"]
        if legal:
            return int(rng.choice(legal))
    return hybrid(env_, agent, obs, mask, rng)

out = {"seeds": "50000-51999 (fresh)"}
for name, pol in [("null_hybrid_vs_hybrid", hybrid), ("bench_board_noise_vs_hybrid", bb_noise)]:
    lobs = [play(env, s, pol, hybrid) for s in range(50000, 52000)]
    s = summarize(lobs)
    out[name] = {"summary": s, "per_lobby_diff_A_minus_B": [float(np.mean(l.placements_a) - np.mean(l.placements_b)) for l in lobs]}
    print("RESULT", name, round(s["diff_A_minus_B"], 4), s["ci95_diff"], flush=True)
Path("results/fixed/real/stage1_replicate.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("ALLREP", flush=True)
