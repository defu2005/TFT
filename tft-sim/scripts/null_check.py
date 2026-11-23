"""Kiem tra null: scripted vs scripted tren 2000 lobby (seed 20000-21999). Hieu phai nam quanh 0."""
import json, sys
from pathlib import Path
from tft_sim.tftgoat import default_content, make_env, play, scripted_policy, summarize
R = Path(sys.argv[1]); R.mkdir(parents=True, exist_ok=True)
env = make_env(default_content())
ev = [play(env, s, scripted_policy, scripted_policy) for s in range(20000, 22000)]
s_ = summarize(ev)
(R / "null_check.json").write_text(json.dumps(s_, indent=2), encoding="utf-8")
print("null diff", round(s_["diff_A_minus_B"], 4), s_["ci95_diff"], "completed", s_["completed"], flush=True)
