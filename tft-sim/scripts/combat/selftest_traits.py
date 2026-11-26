"""Kiem thu TRAIT_TABLE: moi (trait, khoa hash, thuoc tinh) phai khop snapshot CDragon (doc truc tiep tu file gz).

Hai nhom kiem tra:
  A. Gia tri moi tier trong noi dung engine (build_real) == gia tri trong snapshot, cho moi khoa trong bang.
  B. Khoa hash ton tai trong snapshot cho dung trait. Trait ngoai bang khong duoc them neu khong co
     gia tri ro rang trong mo ta (xem model-plan muc 11.23).
Khong kiem tra quy tac cong don (cong don hay lay max): snapshot khong ghi ro, van de mo.

Chay:  PYTHONPATH=<goat>/src:<sim>/src python3 scripts/combat/selftest_traits.py
"""
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "src"))

import fight as F  # noqa: E402
from tft_sim.real_content import build_real  # noqa: E402

SNAP = HERE.parents[1] / "data/cdragon/cdragon_18.7_2026-11-23.json.gz"


def snapshot_traits() -> dict:
    d = json.load(gzip.open(SNAP, "rt", encoding="utf-8"))
    return {t["apiName"]: t for t in d["sets"]["18"]["traits"]}


def main() -> int:
    snap = snapshot_traits()
    content = build_real("TFTSet18")
    by_api = dict(content.traits)
    ok = True
    for api, mapping in F.TRAIT_TABLE.items():
        st = snap.get(api)
        if st is None:
            print(f"FAIL {api}: khong co trong snapshot"); ok = False; continue
        ct = by_api.get(api)
        if ct is None:
            print(f"FAIL {api}: khong co trong noi dung engine"); ok = False; continue
        snap_effs = sorted(st["effects"], key=lambda e: e["minUnits"])
        eng_effs = sorted(ct.effects, key=lambda e: e.min_units)
        if len(snap_effs) != len(eng_effs):
            print(f"FAIL {api}: so tier snapshot {len(snap_effs)} != engine {len(eng_effs)}"); ok = False; continue
        for key in mapping:
            for i, (se, ee) in enumerate(zip(snap_effs, eng_effs)):
                sv = se["variables"].get(key)
                ev = ee.variables.get(key)
                good = (sv is None and ev is None) or (sv is not None and ev is not None and abs(float(sv) - float(ev)) < 1e-6)
                if not good:
                    ok = False
                    print(f"FAIL {st['name']} khoa {key} tier {i}: snapshot={sv} engine={ev}")
            print(f"{'PASS' if all(abs(float(se['variables'].get(key, 0)) - float(ee.variables.get(key, 0))) < 1e-6 for se, ee in zip(snap_effs, eng_effs)) else 'FAIL'} "
                  f"{st['name']} khoa {key} -> {mapping[key]}")
    print("SELFTEST TRAITS", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
