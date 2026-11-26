"""Kiem thu HANH VI cua TRAIT_TABLE theo tung tier (chenh lech on/off tren bo engine, khong chi so loader).

Voi moi trait trong bang va moi tier (min_units), dung m thanh vien (m = min_units) + 1 phi thanh vien,
so sanh chenh lech thuoc tinh khi bat bang (table=True) voi khi tat, va voi gia tri ky vong tu snapshot.
Quy tac cong don (max cho dr/resist, cong cho cac thuoc tinh khac) lay tu fight._table_extra; kiem thu
kiem tra dung tier duoc chon va dung pham vi (team/members/nonmember) va dung gia tri, khong kiem tra quy tac.

Gia tri ky vong:
  Executioner  CritChance tier1 (m=2): +0,15 cho thanh vien.
  Brawler      hp_flat 120 cho ca doi (moi tier); hp_pct tier t cho thanh vien = v * max_hp goc.
  Juggernaut   dr: thanh vien = max(team, members) = members; phi thanh vien = team.
  Defender     resist: thanh vien = max(12, v); phi thanh vien = 12. (armor va mr deu vay)
  Rapidfire    as: ca doi x (1 + 0,10).
  Hunter       ad: thanh vien x (1 + v), voi v theo tier (0,20/0,30/0,45/0,60).
  Spellweaver  ap: chenh lech thanh vien - phi thanh vien = 100 * v (v = 0,10/0,30/0,55) (bo TeamwideAP chung).

Chay:  PYTHONPATH=<goat>/src:<sim>/src python3 scripts/combat/selftest_trait_tiers.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "src"))

import fight as F  # noqa: E402
from tft_goat.engine import simulate as S9  # noqa: E402
from tft_goat.env.state import BoardUnit as BU  # noqa: E402
from tft_sim.real_content import build_real  # noqa: E402

c18 = build_real("TFTSet18")
F.set_content(18, c18)
TABLE_TRAITS = {c18.traits[a].name for a in F.TRAIT_TABLE if a in c18.traits}


def _onoff(board, attrs):
    S9.apply_team_traits = lambda u, c, bonus_units=0: F._set18_traits(u, c, bonus_units, emblems=False, table=True)
    on = S9._build_team(board, 0, c18, 0)
    S9.apply_team_traits = F._orig_apply_team_traits
    off = S9._build_team(board, 0, c18, 0)
    return ([tuple(getattr(u, a) for a in attrs) for u in on],
            [tuple(getattr(u, a) for a in attrs) for u in off])


def _members(trait, m):
    apis = [a for a, c in c18.champions.items() if trait in c.traits and c.stats]
    return apis[:m]


def _outsiders(trait, k):
    out = []
    for a, c in c18.champions.items():
        if c.stats and trait not in c.traits and not (set(c.traits) & TABLE_TRAITS):
            out.append(a)
        if len(out) >= k:
            break
    return out


def _board(trait, m):
    mem = _members(trait, m)
    outs = _outsiders(trait, 1)
    if len(mem) != m or len(outs) != 1:
        return None, None
    return [BU(a, 1, on_board=True) for a in mem + outs], m


def _tiers(trait_name):
    t = next(t for t in c18.traits.values() if t.name == trait_name)
    return t, sorted(t.effects, key=lambda e: e.min_units)


def _check(label, ok, detail):
    print(f"{'PASS' if ok else 'FAIL'} {label}: {detail}")
    return ok


def main() -> int:
    ok = True
    # Executioner tier 1 (m=2): crit +0,15 cho thanh vien; tier 2 va 3 khong co CritChance (chi kiem tra tang >= 0)
    board, m = _board("Executioner", 2)
    if board:
        on, off = _onoff(board, ("crit_chance",))
        d = [round(a[0] - b[0], 6) for a, b in zip(on, off)]
        ok &= _check("Executioner tier1 crit", abs(d[0] - 0.15) < 1e-6 and abs(d[1] - 0.15) < 1e-6 and abs(d[2]) < 1e-6,
                     f"delta={d} (ky vong 0,15 0,15 0)")
    # Brawler: hp_flat 120 cho ca doi; hp_pct thanh vien tier t
    for m, pct in ((2, 0.25), (4, 0.40), (6, 0.65)):
        board, _ = _board("Brawler", m)
        if not board:
            ok &= _check(f"Brawler m={m}", False, "khong du thanh vien/phi thanh vien de dung board")
            continue
        on, off = _onoff(board, ("max_hp",))
        d = [round(a[0] - b[0], 4) for a, b in zip(on, off)]
        exp_mem = [120 + pct * b[0] for b in off[:m]]
        got_mem = d[:m]
        good = all(abs(g - e) < 1e-3 for g, e in zip(got_mem, exp_mem)) and abs(d[m] - 120) < 1e-3
        ok &= _check(f"Brawler tier m={m}", good, f"delta={d} (thanh vien = 120 + {pct}*base, phi thanh vien = 120)")
    # Juggernaut tier m=2,4,6: dr thanh vien = members, phi = team
    for m, mem_v, team_v in ((2, 0.20, 0.04), (4, 0.30, 0.06), (6, 0.42, 0.08)):
        board, _ = _board("Juggernaut", m)
        if not board:
            ok &= _check(f"Juggernaut m={m}", False, "khong du bo"); continue
        on, _off = _onoff(board, ("incoming_reduction",))
        d = [round(a[0] - b[0], 6) for a, b in zip(on, _off)]
        good = all(abs(x - mem_v) < 1e-6 for x in d[:m]) and abs(d[m] - team_v) < 1e-6
        ok &= _check(f"Juggernaut m={m}", good, f"dr={d} (ky vong {mem_v} x{m}, {team_v})")
    # Defender tier m=2,4,6: resist thanh vien = max(12, v), phi = 12
    for m, v in ((2, 25.0), (4, 60.0), (6, 115.0)):
        board, _ = _board("Defender", m)
        if not board:
            ok &= _check(f"Defender m={m}", False, "khong du bo"); continue
        on, _off = _onoff(board, ("armor", "mr"))
        d = [(round(a[0] - b[0], 6), round(a[1] - b[1], 6)) for a, b in zip(on, _off)]
        good = all(abs(x - v) < 1e-6 and abs(y - v) < 1e-6 for x, y in d[:m]) and all(
            abs(x - 12) < 1e-6 and abs(y - 12) < 1e-6 for x, y in d[m:m + 1])
        ok &= _check(f"Defender m={m}", good, f"(armor,mr)={d} (ky vong {v} cho thanh vien, 12 cho phi)")
    # Rapidfire: as x1,10 cho ca doi (m=2,3,4,5)
    for m in (2, 3, 4, 5):
        board, _ = _board("Rapidfire", m)
        if not board:
            ok &= _check(f"Rapidfire m={m}", False, "khong du bo"); continue
        on, _off = _onoff(board, ("attack_speed",))
        r = [round(a[0] / b[0], 6) for a, b in zip(on, _off)]
        ok &= _check(f"Rapidfire m={m}", all(abs(x - 1.10) < 1e-6 for x in r), f"ratio={r} (ky vong 1,10)")
    # Hunter: ad thanh vien x (1+v)
    for m, v in ((2, 0.20), (3, 0.30), (4, 0.45), (5, 0.60)):
        board, _ = _board("Hunter", m)
        if not board:
            ok &= _check(f"Hunter m={m}", False, "khong du bo"); continue
        on, _off = _onoff(board, ("ad",))
        r = [round(a[0] / b[0], 6) for a, b in zip(on[:m], _off[:m])]
        ok &= _check(f"Hunter m={m}", all(abs(x - (1 + v)) < 1e-4 for x in r), f"ratio thanh vien={r} (ky vong {1 + v})")
    # Spellweaver: chenh lech thanh vien - phi = 100*v (bo TeamwideAP chung)
    for m, v in ((2, 0.10), (4, 0.30), (6, 0.55)):
        board, _ = _board("Spellweaver", m)
        if not board:
            ok &= _check(f"Spellweaver m={m}", False, "khong du bo"); continue
        on, _off = _onoff(board, ("ap",))
        diff = round((on[0][0] - on[m][0]) - (_off[0][0] - _off[m][0]), 3)
        ok &= _check(f"Spellweaver m={m}", abs(diff - 100 * v) < 0.5, f"chenh lech={diff} (ky vong {100 * v:.1f})")
    print("SELFTEST TRAIT TIERS", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
