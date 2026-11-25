"""Selftest wrapper fight.py. Fixture tu tuong that trong CDragon (nhan: fixture, khong phai du lieu tran)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import fight as F  # noqa: E402
from tft_goat.engine.simulate import run_combat as raw_run  # noqa: E402
from tft_sim.real_content import build_real  # noqa: E402

c17 = build_real("TFTSet17")
c18 = build_real("TFTSet18")
F.set_content(17, c17); F.set_content(18, c18)
names17 = sorted(c17.champions)
rng = np.random.default_rng(7)


def fixture(content, names, n=6, lvl=5):
    def side():
        return {"level": lvl, "augments": [], "units": [
            {"api": names[int(rng.integers(len(names)))], "star": 1, "items": [], "pos": None} for _ in range(n)]}
    return {"schema": "fight-v1", "set": 17, "label": "fixture", "source": "selftest", "a": side(), "b": side(),
            "result": {"winner": None}}


ok = True
# 1) full, khong vi tri: phai khop raw engine
fx = [fixture(c17, names17) for _ in range(20)]
same = 0
for rec in fx:
    ba, bb, _ = F.boards_of(rec, "full")
    for s in range(10):
        r0 = raw_run(ba, bb, c17, np.random.default_rng(s), (), ())
        with F.fight_context("full", None):
            r1 = raw_run(ba, bb, c17, np.random.default_rng(s), (), ())
        same += int(r0.winner == r1.winner and r0.survivors == r1.survivors)
tot = 20 * 10
print("full==raw", same, "/", tot)
ok &= same == tot

# 2) public (tat ability, bo item) phai khac full tren it nhat mot fight
diff = 0
for rec in fx:
    if F.predict_win(rec, 10, "full")["p_a"] != F.predict_win(rec, 10, "public")["p_a"]:
        diff += 1
print("public khac full o", diff, "/ 20 fight")
ok &= diff > 0

# 3) Set 18 chi cho public
try:
    F.predict_win({**fx[0], "set": 18}, 2, "full")
    ok = False
    print("GUARD FAIL")
except ValueError:
    print("GUARD ok (set 18 full bi chan)")

# 4) Set 18 public chay duoc tren ten tuong Set 18
names18 = sorted(c18.champions)
rec18 = {**fixture(c18, names18), "set": 18}
out = F.predict_win(rec18, 5, "public")
print("set18 public chay duoc:", out)

print("SELFTEST", "PASS" if ok else "FAIL")
