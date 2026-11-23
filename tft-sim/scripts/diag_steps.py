"""Do so buoc va phan bo pha cua v3 so voi tran 50 (MAX_PLANNING_STEPS), 200 lobby, seed 100000-100199 (dev moi).
Ghi results/fixed/real/diag_steps.json."""
import json, time
from collections import Counter
from pathlib import Path
import numpy as np
from tft_sim.real_content import build_real
from tft_sim.rules import make_swap_rule
from tft_sim.tftgoat import make_env, play, scripted_policy
env = make_env(build_real("TFTSet17"))
v3 = make_swap_rule(key="value")
t0 = time.time()
lobs = [play(env, s, v3, v3) for s in range(100000, 100200)]
dt = time.time() - t0
steps = np.array([l.steps for l in lobs])
out = {"lobbies": 200, "lobbies_per_s": round(200 / dt, 2), "steps_mean": float(steps.mean()), "steps_p50": float(np.median(steps)),
       "steps_p90": float(np.percentile(steps, 90)), "steps_max": int(steps.max()), "completed": int(sum(l.completed for l in lobs))}
Path("results/fixed/real/diag_steps.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print(out)
