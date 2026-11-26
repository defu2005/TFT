"""Dem ung vien alias SECONDARY moi (chi do, khong doi alias; plan 11.29). Khong dung VOD.

Ung vien: item DA_* KHONG co hieu ung trong noi dung, ma co mot item TFT_* cung ten goc
(bo tien to DA_/TFT*_Item_, bo 'Artifact_', bo hau to 'Radiant') CO hieu ung, va chua co trong alias_map.
Dung:  PYTHONPATH=<goat>/src:<sim>/src python3 scripts/combat/check_alias_candidates.py
"""
import collections
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "src"))

import fidelity as Fd  # noqa: E402
import fight as F  # noqa: E402
from tft_sim import names18 as N  # noqa: E402


def _base(api):
    b = re.sub(r"^(DA_|TFT\d*_Item_|TFT_Item_)", "", api)
    b = b.replace("Artifact_", "")
    return re.sub(r"Radiant$", "", b).lower()


def main() -> int:
    F.set_content(18, Fd._C18)
    c = F._CONTENT[18]
    amap = N.item_alias_map()
    tft_with_fx = collections.defaultdict(list)
    for a, it in c.items.items():
        if a.startswith("TFT") and it.effects:
            tft_with_fx[_base(a)].append(a)
    cands = collections.Counter()
    rows = []
    for a, it in c.items.items():
        if not a.startswith("DA_") or it.effects or a in amap:
            continue
        tw = tft_with_fx.get(_base(a))
        if not tw:
            continue
        kind = ("Radiant" if a.endswith("Radiant") else "Artifact" if a.startswith("DA_Artifact")
                else "khac")
        cands[kind] += 1
        rows.append({"api": a, "kind": kind, "twin_candidates": sorted(tw)})
    print({"ung_vien_theo_loai": dict(cands), "tong": sum(cands.values())})
    print({"vi_du": rows[:5]})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
