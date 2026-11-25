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

# 5) Vi tri: ghi de pos theo toa do TUYET DOI (khong xoay cho doi B). Kiem tren _build_team truc tiep.
import tft_goat.engine.simulate as S
rec = fixture(names17)
rec["a"]["units"][0]["pos"] = [2, 3]; rec["b"]["units"][0]["pos"] = [5, 1]
ba, bb, pos, aa, ab = F.boards_of(rec, True)
with F.fight_context("hand", pos):
    ua = S._build_team(ba, 0, c17, 0)
    ub = S._build_team(bb, 1, c17, 0)
got_a = ua[0].pos; got_b = ub[0].pos
print("pos team0", got_a, "team1", got_b, "(ky vong (2,3) va (5,1))")
ok &= got_a == (2, 3) and got_b == (5, 1)

# 6) Duong cham diem fidelity: ban ghi real co ket qua; sim bi tu choi
import json, tempfile, fidelity as FD
tmp = Path(tempfile.mkdtemp()) / "real.jsonl"
rs = []
for r in fx[:5]:
    rr = json.loads(json.dumps(r)); rr["label"] = "real"; rr["result"] = {"winner": 0}; rs.append(rr)
tmp.write_text("\n".join(json.dumps(x) for x in rs), encoding="utf-8")
out = FD.score(str(tmp), "none", True, 5)
print("fidelity", out)
ok &= out["n"] == 5 and 0.0 <= out["accuracy"] <= 1.0
sim_file = Path(tempfile.mkdtemp()) / "sim.jsonl"
rr = json.loads(json.dumps(fx[0])); rr["result"] = {"winner": 0}
sim_file.write_text(json.dumps(rr), encoding="utf-8")
try:
    FD.score(str(sim_file), "hand", True, 2); ok = False; print("SIM REJECT FAIL")
except SystemExit:
    print("SIM REJECT ok")

# 7) Alias item Set 18: DA_* rong va twin TFT_Item_* cho cung chi so don vi (generic 0 va 1)
from tft_sim.item_alias import build_set18_aliased
c18a, amap = build_set18_aliased()

ch18 = next(a for a, x in c18a.champions.items() if x.stats)
alias_ok = bool(amap)
def _st(u):
    return (round(u.ad, 3), round(u.ap, 3), u.max_hp, u.armor, u.mr, round(u.attack_speed, 4))
for da, tw in amap.items():
    for gi in (0, 1):
        from tft_goat.engine.unit import build_unit
        a = _st(build_unit(c18a.champions[ch18], 1, 0, c18a, item_apis=(da,), generic_items=gi))
        b = _st(build_unit(c18a.champions[ch18], 1, 0, c18a, item_apis=(tw,), generic_items=gi))
        alias_ok &= a == b
print("alias set18", len(amap), "DA==twin", alias_ok)
# 7b) Duong thuc: cung mot ban ghi, DA_Bloodthirster va TFT_Item_Bloodthirster cho cung p_a
F.set_content(18, c18a)  # dat noi dung da alias truoc khi do, khong phu thuoc import fidelity
# Ban ghi doi xung (hai ben giong het): so tran thang/hoa theo 20 seed phai giong nhau giua DA va TFT_Item
rec_da = fixture(names18, 18)
rec_da["b"] = json.loads(json.dumps(rec_da["a"]))
rec_tw = json.loads(json.dumps(rec_da))
for side in ("a", "b"):
    rec_da[side]["units"][0]["items"] = ["DA_Bloodthirster"]
    rec_tw[side]["units"][0]["items"] = ["TFT_Item_Bloodthirster"]
oda = F.predict_win(rec_da, 20, "generic", True, 0)
otw = F.predict_win(rec_tw, 20, "generic", True, 0)
same_counts = (oda["a"], oda["b"], oda["draw"]) == (otw["a"], otw["b"], otw["draw"])
print("alias path counts DA", (oda["a"], oda["b"], oda["draw"]), "TW", (otw["a"], otw["b"], otw["draw"]))
alias_ok &= same_counts
ok &= alias_ok

# 8) Phase 0: duong ban ghi that khong lam mat TFT_Item_* khong phai twin
from tft_sim.item_alias import build_set18_records
rec_content, amap2 = build_set18_records()
F.set_content(18, rec_content)
twins = set(amap2.values())
nontwin = next(k for k, v in rec_content.items.items() if k.startswith("TFT_Item_") and v.effects and k not in twins)
rec_nt = fixture(names18, 18)
rec_nt["a"]["units"][0]["items"] = [nontwin]
cov_nt = F.coverage(rec_nt)
print("records content: non-twin", nontwin, "items_unknown", cov_nt["a"]["items_unknown"])
ok &= cov_nt["a"]["items_unknown"] == 0
F.set_content(18, c18)

from tft_goat.engine import simulate as S9  # noqa
# 9) Set 18: Vanguard khong con tang max HP tu MaxHealthShield; trait khac (Blossom/Sprykin...) van ap dung
F.set_content(18, c18)
vg = [a for a, c in c18.champions.items() if "Vanguard" in c.traits]
from tft_goat.env.state import BoardUnit as BU
board = [BU(a, 1, on_board=True) for a in vg[:2]]
F.TE.attrs_for = F._orig_attrs_for
hp_full = [u.max_hp for u in S9._build_team(board, 0, c18, 0)]
F.TE.attrs_for = F._attrs_for_set18
hp_skip = [u.max_hp for u in S9._build_team(board, 0, c18, 0)]
F.TE.attrs_for = F._orig_attrs_for
print("vanguard max_hp full", hp_full, "skip", hp_skip)
ok &= hp_full != hp_skip
bl = [a for a, c in c18.champions.items() if "Blossom" in c.traits][:3]
if len(bl) >= 2:
    bb = [BU(a, 1, on_board=True) for a in bl]
    F.TE.attrs_for = F._orig_attrs_for
    ad_full = [u.ad for u in S9._build_team(bb, 0, c18, 0)]
    F.TE.attrs_for = F._attrs_for_set18
    ad_skip = [u.ad for u in S9._build_team(bb, 0, c18, 0)]
    F.TE.attrs_for = F._orig_attrs_for
    print("blossom ad full", ad_full, "skip", ad_skip)
    ok &= ad_full == ad_skip  # trait khong lien quan khong bi anh huong
print("SELFTEST", "PASS" if ok else "FAIL")
