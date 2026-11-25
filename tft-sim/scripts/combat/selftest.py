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
    rr = json.loads(json.dumps(r)); rr["label"] = "real"; rr["result"] = {"winner": 0}; rr["source"] = "selftest:1-1"; rs.append(rr)
tmp.write_text("\n".join(json.dumps(x) for x in rs), encoding="utf-8")
out = FD.score(str(tmp), 5, 0, allow_dryrun=True)
print("fidelity set17 (ngoai muc 11.7)", {k: out.get(k) for k in ("fights", "skipped")})
ok &= out["fights"] == 0 and out["skipped"].get("set_khong_ho_tro:17") == 5
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
# 10) Emblem Set 18: emblem cong diem trait; holder nhan buff; emblem tren thanh vien tu nhien khong cong them.
# Dung Blackthorn (co buff HP, khong phai no_stat_mapping: Ravager khong co buff nen khong dung de kiem).
F.set_content(18, c18)
ok10 = True
print("emblem_trait_of Ravager", F.emblem_trait_of("DA_18_EmblemSlayer", c18), "Blackthorn", F.emblem_trait_of("DA_18_EmblemBlackthorn", c18))
ok10 &= F.emblem_trait_of("DA_18_EmblemSlayer", c18) == "Ravager"
ok10 &= F.emblem_trait_of("DA_18_EmblemBlackthorn", c18) == "Blackthorn"
ok10 &= F.emblem_trait_of("DA_PhantomEmblem18", c18) is None
non_bt = [a for a, c in c18.champions.items() if "Blackthorn" not in c.traits and c.stats][:3]
bt = [a for a, c in c18.champions.items() if "Blackthorn" in c.traits and c.stats][:1]
EM = ("DA_18_EmblemBlackthorn",)


def hp_of(board, emblem_on):
    S9.apply_team_traits = F._emblem_traits if emblem_on else F._orig_apply_team_traits
    try:
        return [u.max_hp for u in S9._build_team(board, 0, c18, 0)]
    finally:
        S9.apply_team_traits = F._orig_apply_team_traits


# a) hai holder khong co Blackthorn tu nhien -> dat moc 2 -> tier 1 -> ca hai nhan HP
b_a = [BU(non_bt[0], 1, on_board=True, items=1, item_apis=EM), BU(non_bt[1], 1, on_board=True, items=1, item_apis=EM)]
off_a, on_a = hp_of(b_a, False), hp_of(b_a, True)
print("a) 2 holders off", off_a, "on", on_a)
ok10 &= all(on > off for on, off in zip(on_a, off_a))
# b) mot holder duy nhat: 1 diem, khong dat moc 2 -> khong doi
b_b = [BU(non_bt[0], 1, on_board=True, items=1, item_apis=EM), BU(non_bt[1], 1, on_board=True, items=0)]
print("b) 1 holder off", hp_of(b_b, False), "on", hp_of(b_b, True))
ok10 &= hp_of(b_b, True) == hp_of(b_b, False)
# c) holder tu nhien (Blackthorn) + khong Blackthorn co emblem: chi 1 diem Blackthorn (tu nhien) + 0 -> khong doi
b_c = [BU(bt[0], 1, on_board=True, items=1, item_apis=EM), BU(non_bt[0], 1, on_board=True, items=0)]
print("c) native holder off", hp_of(b_c, False), "on", hp_of(b_c, True))
ok10 &= hp_of(b_c, True) == hp_of(b_c, False)
# d) predict_win Set 18: emblem bat/tat, va patch duoc khoi phuc
rec10 = fixture(names18, 18)
rec10["a"]["units"][0]["items"] = ["DA_18_EmblemBlackthorn"]
rec10["a"]["units"][1]["items"] = ["DA_18_EmblemBlackthorn"]
x_off = F.predict_win(rec10, 3, "generic", True, 0, emblems=False)
x_on = F.predict_win(rec10, 3, "generic", True, 0, emblems=True)
print("d) predict_win emblems off/on", (x_off["a"], x_off["b"]), (x_on["a"], x_on["b"]))
ok10 &= F.TE.attrs_for is F._orig_attrs_for
ok10 &= S9.apply_team_traits is F._orig_apply_team_traits
# e) Spellweaver: APPerCast bi bo nen AP khac voi khi day du (khong vacuous: so sanh khac 0)
sw = [a for a, c in c18.champions.items() if "Spellweaver" in c.traits][:2]
bsw = [BU(a, 1, on_board=True) for a in sw]
F.TE.attrs_for = F._orig_attrs_for
ap_full = [u.ap for u in S9._build_team(bsw, 0, c18, 0)]
F.TE.attrs_for = F._attrs_for_set18
ap_skip = [u.ap for u in S9._build_team(bsw, 0, c18, 0)]
F.TE.attrs_for = F._orig_attrs_for
print("e) spellweaver ap full", ap_full, "skip", ap_skip)
ok10 &= any(abs(a - b) > 1e-6 for a, b in zip(ap_full, ap_skip))
ok &= ok10
print("emblem block", "PASS" if ok10 else "FAIL")
# 11) Duong ban ghi that Set 18 (fidelity, muc 11.7): fixture 10 ban ghi
import fidelity as FD2  # noqa: E402
fx_path = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "set18_dryrun.jsonl"
out11 = FD2.score(str(fx_path), 5, 0, allow_dryrun=True)
print("fidelity set18 fixture", {k: out11.get(k) for k in ("fights", "games", "skipped", "unknown_items")})
ok11 = out11["fights"] == 5 and out11["games"] == 4 and out11["inconclusive"] is True
sk = out11["skipped"]
ok11 &= sk.get("winner_null") == 1 and sk.get("tuong_la:TFT_NotAChampion_Dryrun") == 1
ok11 &= any(k.startswith("schema:") for k in sk) and sk.get("set_khong_ho_tro:19") == 1 and sk.get("items_null") == 1
ok11 &= out11["unknown_items"].get("TFT_Item_NoSuchItem_Dryrun") == 1
out11b = FD2.score(str(fx_path), 5, 0)  # mac dinh: dryrun bi bo
ok11 &= out11b["fights"] == 0 and out11b["skipped"].get("dryrun") == 13
# quy tac suc manh tinh tay: 1 tuong gia 1 (sao 1) + 1 tuong gia 5 (sao 2) = 1 + 15 = 16 ; doi b: gia 4 sao 1 = 4
c1 = next(a for a, c in c18.champions.items() if c.cost == 1 and c.stats)
c5 = next(a for a, c in c18.champions.items() if c.cost == 5 and c.stats)
c4 = next(a for a, c in c18.champions.items() if c.cost == 4 and c.stats)
sa = {"units": [{"api": c1, "star": 1}, {"api": c5, "star": 2}]}
sb = {"units": [{"api": c4, "star": 1}]}
ok11 &= FD2.strength(sa, c18) == 16.0 and FD2.strength(sb, c18) == 4.0
ok11 &= FD2.rule_credit(16.0, 4.0, 1.0) == 1.0 and FD2.rule_credit(16.0, 4.0, 0.0) == 0.0
ok11 &= FD2.rule_credit(4.0, 4.0, 1.0) == 0.5 and FD2.credit(0.5, 0.0) == 0.5
print("strength rule hand check", FD2.strength(sa, c18), FD2.strength(sb, c18))
ok &= ok11
print("fidelity block", "PASS" if ok11 else "FAIL")
# 12) Bang trait Set 18 (muc 11.7): moi gia tri ap dung phai khop CDragon; ngoai bang khong doi
import gzip as _gz  # noqa: E402
F.set_content(18, c18)
ok12 = True
exe = c18.traits["DA_18_Executioner"]
eff2 = sorted(exe.effects, key=lambda e: e.min_units)[0]
ok12 &= abs(eff2.variables["CritChance"] - 0.15) < 1e-6  # khop CDragon: Executioner moc 2 = 15%
ok12 &= F.TRAIT_TABLE["DA_18_Executioner"]["CritChance"][0] == "crit"
brw = c18.traits["DA_18_Brawler"]
eb2 = sorted(brw.effects, key=lambda e: e.min_units)[0]
ok12 &= abs(eb2.variables["{da2472a7}"] - 120.0) < 1e-6 and abs(eb2.variables["{f1ed73eb}"] - 0.25) < 1e-6
# Executioner x2 (tier 1): crit tang 0.15 cho ca hai thanh vien (ca hai la Executioner)
ex = [a for a, c in c18.champions.items() if "Executioner" in c.traits and c.stats][:2]
if len(ex) == 2:
    bx = [BU(a, 1, on_board=True) for a in ex]
    S9.apply_team_traits = lambda u, c, bonus_units=0: F._set18_traits(u, c, bonus_units, emblems=False, table=True)
    cr = [u.crit_chance for u in S9._build_team(bx, 0, c18, 0)]
    S9.apply_team_traits = F._orig_apply_team_traits
    cr0 = [u.crit_chance for u in S9._build_team(bx, 0, c18, 0)]
    print("executioner crit table", cr0, "->", cr)
    ex3 = [a for a, c in c18.champions.items() if "Executioner" in c.traits and c.stats][:3]
    if len(ex3) == 3:  # moc 3 khong co khoa CritChance: crit van phai con +0.15 (cong don)
        b3 = [BU(a, 1, on_board=True) for a in ex3]
        S9.apply_team_traits = lambda u, c, bonus_units=0: F._set18_traits(u, c, bonus_units, emblems=False, table=True)
        c3 = [u.crit_chance for u in S9._build_team(b3, 0, c18, 0)]
        S9.apply_team_traits = F._orig_apply_team_traits
        c30 = [u.crit_chance for u in S9._build_team(b3, 0, c18, 0)]
        print("executioner crit moc 3", c30, "->", c3)
        ok12 &= all(abs((a - b) - 0.15) < 1e-6 for a, b in zip(c3, c30))
    ok12 &= all(abs((a - b) - 0.15) < 1e-6 for a, b in zip(cr, cr0))
# Brawler: doi gom 120 HP phang cho ca doi (tier 1 = 2 Brawler)
bw = [a for a, c in c18.champions.items() if "Brawler" in c.traits and c.stats][:2]
other = [a for a, c in c18.champions.items() if "Brawler" not in c.traits and c.stats][:1]
if len(bw) == 2 and other:
    bb12 = [BU(a, 1, on_board=True) for a in bw + other]
    S9.apply_team_traits = lambda u, c, bonus_units=0: F._set18_traits(u, c, bonus_units, emblems=False, table=True)
    h_t = [u.max_hp for u in S9._build_team(bb12, 0, c18, 0)]
    S9.apply_team_traits = F._orig_apply_team_traits
    h_0 = [u.max_hp for u in S9._build_team(bb12, 0, c18, 0)]
    print("brawler hp table", h_0, "->", h_t)
    ok12 &= h_t[2] - h_0[2] >= 120 - 1e-6  # tuong khong phai Brawler van nhan 120 HP phang (ca doi)
# Juggernaut / Defender / Rapidfire: dinh danh nhom (ai nhan gia tri nao), so sanh bat/tat bang
def _onoff(board, attrs):
    S9.apply_team_traits = lambda u, c, bonus_units=0: F._set18_traits(u, c, bonus_units, emblems=False, table=True)
    on = S9._build_team(board, 0, c18, 0)
    S9.apply_team_traits = F._orig_apply_team_traits
    off = S9._build_team(board, 0, c18, 0)
    return [tuple(getattr(u, a) for a in attrs) for u in on], [tuple(getattr(u, a) for a in attrs) for u in off]
def _pick(trait, n, other=False):
    return [a for a, c in c18.champions.items() if (trait in c.traits) != other and c.stats][:n]
jg = _pick("Juggernaut", 2); jo = _pick("Juggernaut", 1, other=True)
if len(jg) == 2 and jo:
    on, off = _onoff([BU(a, 1, on_board=True) for a in jg + jo], ("incoming_reduction",))
    d = [round(a[0] - b[0], 6) for a, b in zip(on, off)]
    print("juggernaut dr delta (members, members, nonmember)", d)
    ok12 &= abs(d[0] - 0.20) < 1e-6 and abs(d[1] - 0.20) < 1e-6 and abs(d[2] - 0.04) < 1e-6  # max, khong cong don
df = _pick("Defender", 2); do = _pick("Defender", 1, other=True)
if len(df) == 2 and do:
    on, off = _onoff([BU(a, 1, on_board=True) for a in df + do], ("armor", "mr"))
    d = [(round(a[0] - b[0], 6), round(a[1] - b[1], 6)) for a, b in zip(on, off)]
    print("defender armor/mr delta (def, def, nondef)", d)
    # GIA DINH hien tai (xem 11.11): Defender lay MAX (25), khong cong thanh 37. Mo ta CDragon khong noi ro.
    ok12 &= all(abs(x - 25) < 1e-6 and abs(y - 25) < 1e-6 for x, y in d[:2]) and abs(d[2][0] - 12) < 1e-6 and abs(d[2][1] - 12) < 1e-6
rf = _pick("Rapidfire", 2); rfo = _pick("Rapidfire", 1, other=True)
if len(rf) == 2 and rfo:
    on, off = _onoff([BU(a, 1, on_board=True) for a in rf + rfo], ("attack_speed",))
    r = [round(a[0] / b[0], 6) for a, b in zip(on, off)]
    print("rapidfire AS ratio (rf, rf, other)", r)
    ok12 &= all(abs(x - 1.10) < 1e-6 for x in r)  # TeamAS 10% cho ca doi
# Predict_win: bang tat thi khong doi, bat thi doi duoc; patch duoc khoi phuc
rec12 = fixture(names18, 18)
x0 = F.predict_win(rec12, 3, "generic", True, 0, traits_table=False)
x1 = F.predict_win(rec12, 3, "generic", True, 0, traits_table=True)
ok12 &= F.S.apply_team_traits is F._orig_apply_team_traits
# Hunter: 2 Hunter (tier 1) -> +20% AD cho Hunter, khong thay doi tuong khong phai Hunter
hn = _pick("Hunter", 2); hno = _pick("Hunter", 1, other=True)
if len(hn) == 2 and hno:
    on, off = _onoff([BU(a, 1, on_board=True) for a in hn + hno], ("ad",))
    r = [round(a[0] / b[0], 6) for a, b in zip(on, off)]
    print("hunter AD ratio (hunter, hunter, other)", r)
    ok12 &= abs(r[0] - 1.20) < 1e-6 and abs(r[1] - 1.20) < 1e-6 and abs(r[2] - 1.0) < 1e-6
# bonus_units (augment Large Quest, engine trait_bonus): 1 Brawler + bonus 1 phai dat moc 2 -> +120 HP cho ca doi
bb1 = [BU(bw[0], 1, on_board=True)] + [BU(other[0], 1, on_board=True)] if bw and other else []
if bb1:
    S9.apply_team_traits = lambda u, c, bonus_units=0: F._set18_traits(u, c, bonus_units, emblems=False, table=True)
    hb1 = [u.max_hp for u in S9._build_team(bb1, 0, c18, 1)]
    hb0 = [u.max_hp for u in S9._build_team(bb1, 0, c18, 0)]
    S9.apply_team_traits = F._orig_apply_team_traits
    print("bonus_units table (bonus 1 vs 0)", hb1, hb0)
    ok12 &= abs((hb1[1] - hb0[1]) - 120) < 1e-6 and abs((hb1[0] - hb0[0]) - 395) < 1e-6  # khong Brawler +120; Brawler +120 + 25% of 1100
print("table predict_win off/on", (x0["a"], x0["b"]), (x1["a"], x1["b"]), "mapped", F.TABLE_MAPPED)
ok &= ok12
print("trait table block", "PASS" if ok12 else "FAIL")
# Names18: moi apiName phai nam trong candidates(ten cua no); ten trung phai nem AmbiguousName, khong doan
from tft_sim import names18 as _N18  # noqa: E402
_nm = json.loads((_N18.ROOT / "data" / "set18_names.json").read_text(encoding="utf-8"))
_rt_bad = [(k, r["api"]) for k in _N18.KINDS for r in _nm[k] if r["api"] not in _N18.candidates(k, r["name"])]
_amb_ok = True
try:
    _N18.resolve("champions", "Krug")
    _amb_ok = False
except _N18.AmbiguousName:
    pass
ok &= (not _rt_bad) and _amb_ok
print("names18 roundtrip bad", len(_rt_bad), "ambiguous ok", _amb_ok)
print("SELFTEST", "PASS" if ok else "FAIL")
