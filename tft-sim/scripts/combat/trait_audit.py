"""Dump mo ta (desc) va bien da giai ma cua moi trait Set 18 de doi chieu thu cong.

Dung:  python3 trait_audit.py [out.json]   (mac dinh results/fixed/combat/trait_audit.json)
Khong tinh toan gi khac: chi doc snapshot CDragon va bang giai ma hash.
Moi trait: apiName, ten, mo ta (bo the @...@ de doc), va voi moi moc: min/max va cac bien
(ten da giai ma neu co, chi de DOC; engine khong tu ap khoa hash). `engine_auto`: khoa co ten ma engine tu ap. `hash_keys`: khoa hash goc. `in_table`: da co trong TRAIT_TABLE.
"""
import gzip
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SNAP = ROOT / "data/cdragon/cdragon_18.7_2026-11-23.json.gz"
RES = ROOT / "results/fixed/combat/trait_hash_resolution.json"


def _plain(desc: str) -> str:
    desc = re.sub(r"<[^>]+>", "", desc or "")
    desc = re.sub(r"@[^@]*@", "_", desc)
    desc = re.sub(r"%i:[A-Za-z]+%", "", desc)
    return re.sub(r"\s+", " ", desc).strip()


def main(out: Path) -> None:
    data = json.load(gzip.open(SNAP, "rt", encoding="utf-8"))
    traits = data["sets"]["18"]["traits"]
    res = json.load(open(RES, encoding="utf-8"))
    sys.path.insert(0, str(HERE))
    import fight as F  # noqa: E402  (TRAIT_TABLE)
    from tft_goat.engine import trait_effects as TE  # noqa: E402

    rows = []
    for t in traits:
        api = t["apiName"]
        names = res.get(api, {})
        effs = []
        for e in sorted(t.get("effects", []), key=lambda x: x.get("minUnits", 0)):
            vs = {}
            for k, v in (e.get("variables") or {}).items():
                if k.startswith("{") and k.endswith("}"):
                    hk = k[1:-1]
                    nm = (names.get(hk) or [None])[0]
                    key = nm or k
                else:
                    key = k
                vs[key] = v
            # engine tu ap dung khoa CO TEN qua attrs_for; khoa hash bi bo qua (attrs_for tra [] voi "{...}")
            auto = {k: TE.attrs_for(k) for k in (e.get("variables") or {}) if not k.startswith("{") and TE.attrs_for(k)}
            hashed = [k for k in (e.get("variables") or {}) if k.startswith("{")]
            effs.append({"min": e.get("minUnits"), "max": e.get("maxUnits"), "vars": vs,
                         "engine_auto": auto, "hash_keys": hashed})
        rows.append({
            "apiName": api,
            "name": t.get("name"),
            "desc": _plain(t.get("desc", "")),
            "effects": effs,
            "in_table": api in F.TRAIT_TABLE,
        })
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"set": 18, "snapshot": SNAP.name, "traits": rows},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(rows)} traits -> {out}; in_table={sum(r['in_table'] for r in rows)}")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "results/fixed/combat/trait_audit.json")
