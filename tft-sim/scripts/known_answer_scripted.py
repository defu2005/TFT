"""Doi chung: scripted vs scripted tren 200 lobby. Hieu so phai ~0 va CI chua 0."""
import json, sys, time
from pathlib import Path
from tft_sim.tftgoat import default_content
from tft_sim.tftgoat import make_env, play, scripted_policy, summarize

out = Path(sys.argv[1])
env = make_env(default_content())
t0 = time.time()
lobbies = [play(env, s, scripted_policy, scripted_policy) for s in range(200)]
res = summarize(lobbies)
res["content"] = "synthetic (full-recipe content, tft_sim.content)"
res["elapsed_s"] = round(time.time() - t0, 1)
out.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(res, ensure_ascii=False, indent=2))
