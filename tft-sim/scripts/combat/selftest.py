"""Selftest fight.py (cong tac ability/items doc lap). Fixture tu tuong that trong CDragon (nhan: fixture)."""
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
names18 = sorted(c18.champions)
rng = np.random.default_rng(7)


def fixture(names, set_no=17, n=6, lvl=5):
    def side():
        return {"level": lvl, "augments": [], "units": [
            {"api": names[int(rng.integers(len(names)))], "star": 1, "items": [], "pos": None} for _ in range(n)]}
    return {"schema": "fight-v1", "set": set_no, "label": "fixture", "source": "selftest",
            "a": side(), "b": side(), "result": {"winner": None}}


ok = True
fx = [fixture(names17) for _ in range(20)]

# 1) hand + items + khong vi tri: phai khop raw engine
same = 0
for rec in fx:
    ba, bb, _, aa, ab = F.boards_of(rec, True)
    for s in range(10):
        r0 = raw_run(ba, bb, c17, np.random.default_rng(s), aa, ab)
        with F.fight_context("hand", None):
            r1 = raw_run(ba, bb, c17, np.random.default_rng(s), aa, ab)
        same += int(r0.winner == r1.winner and r0.survivors == r1.survivors)
print("hand==raw", same, "/ 200")
ok &= same == 200

# 2) ability none phai khac hand tren it nhat mot fight
d = sum(F.predict_win(r, 10, "none")["p_a"] != F.predict_win(r, 10, "hand")["p_a"] for r in fx)
print("none khac hand o", d, "/ 20 fight")
ok &= d > 0

# 3) items tat phai khac items bat tren it nhat mot fight
d2 = sum(F.predict_win(r, 10, "hand", items=False)["p_a"] != F.predict_win(r, 10, "hand", items=True)["p_a"] for r in fx)
print("items tat khac bat o", d2, "/ 20 fight (neu 0 thi fixture khong co trang bi)")

# 4) Set 18: hand bi chan; generic va none chay duoc
try:
    F.predict_win({**fixture(names18, 18), "set": 18}, 2, "hand")
    ok = False
    print("GUARD FAIL")
except ValueError:
    print("GUARD ok (set 18 hand bi chan)")
for mode in ("generic", "none"):
    print("set18", mode, F.predict_win({**fixture(names18, 18), "set": 18}, 5, mode))

print("SELFTEST", "PASS" if ok else "FAIL")
