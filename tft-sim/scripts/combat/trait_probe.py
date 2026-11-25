"""Probe: voi moi khoa CO TEN ma engine tu ap (engine_auto trong trait_audit.json), in hieu ung
that cua no len 1 thanh vien va 1 tuong khong phai thanh vien, o moc dau (tier 1) va moc cao nhat,
kem mo ta CDragon. Dung DUNG quy tac cua engine (attrs_for, teamwide/members, _apply_stat),
khong ap cac khoa khac, nen hieu ung la cua rieng khoa do.

Dung: python3 trait_probe.py [out.json]
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
AUDIT = ROOT / "results/fixed/combat/trait_audit.json"
OUT = ROOT / "results/fixed/combat/trait_probe.json"
ATTR_FIELDS = ("max_hp", "armor", "mr", "ap", "ad", "attack_speed", "incoming_reduction", "damage_amp")


def _snap(u):
    return {f: getattr(u, f) for f in ATTR_FIELDS}


def main(out: Path) -> None:
    sys.path.insert(0, str(HERE))
    sys.path.insert(0, str(ROOT / "src"))
    from tft_goat.engine import simulate as S9
    from tft_goat.engine.trait_effects import attrs_for, _apply_stat
    from tft_goat.env.state import BoardUnit as BU
    from tft_sim.real_content import build_real
    import fight as F

    c18 = build_real("TFTSet18")
    F.set_content(18, c18)
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    rows = []
    for t in audit["traits"]:
        auto_keys = {}
        for e in t["effects"]:
            for k, attrs in e["engine_auto"].items():
                auto_keys.setdefault(k, attrs)
        if not auto_keys:
            continue
        trait = c18.traits.get(t["apiName"])
        mem = [a for a, c in c18.champions.items() if trait.name in c.traits and c.stats][:1]
        non = [a for a, c in c18.champions.items() if trait.name not in c.traits and c.stats][:1]
        if not mem or not non:
            continue
        effs = sorted(trait.effects, key=lambda e: e.min_units)
        tiers = {"t1": 0, "top": len(effs) - 1}
        for k in auto_keys:
            entry = {"trait": t["apiName"], "name": trait.name, "key": k, "attrs": auto_keys[k],
                     "desc": t["desc"][:160], "scope": "teamwide" if "teamwide" in k.lower() else "members"}
            for tname, ti in tiers.items():
                val = effs[ti].variables.get(k)
                if not isinstance(val, (int, float)):
                    entry[tname] = None
                    continue
                res = {}
                for role, champ in (("member", mem[0]), ("nonmember", non[0])):
                    u = S9._build_team([BU(champ, 1, on_board=True)], 0, c18, 0)[0]
                    before = _snap(u)
                    hit = (entry["scope"] == "teamwide") or (role == "member")
                    if hit:
                        for attr in attrs_for(k):
                            _apply_stat(u, attr, float(val))
                    after = _snap(u)
                    res[role] = {f: round(after[f] - before[f], 6) for f in ATTR_FIELDS
                                 if abs(after[f] - before[f]) > 1e-9}
                entry[tname] = {"value": val, **res}
            rows.append(entry)
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in rows:
        print(r["name"], r["key"], r["attrs"], r["scope"], "t1:", r["t1"], "| top:", r["top"])
    print(f"{len(rows)} khoa co ten -> {out}")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else OUT)
