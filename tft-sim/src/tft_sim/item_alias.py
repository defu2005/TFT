"""Alias item Set 18: craftable DA_* co effects rong trong CDragon; item cung ten TFT_Item_* co hieu ung that.

Gia dinh (ghi ro, chua kiem chung tren Set 18 that): hieu ung cua item TFT_Item_<Ten> cung la hieu ung
cua craftable DA_<Ten> cung ten. Ap dung: (1) copy effects vao content DA_* khi DA rong; (2) dang ky hook
cua twin cho DA_* trong cac bang ITEM_* cua engine (thay doi trang thai toan cuc cua tien trinh).
Khong thay doi build_real_set18_clean. Moi alias duoc liet ke de bao cao.
MOT NOI DUNG MOI TIEN TRINH: build_set18_aliased() ghi vao bang hook ITEM_* cua engine (toan cuc).
Chay sau no trong cung tien trinh se thay doi hook cua ten DA_*; khong tron voi duong clean.
"""
from __future__ import annotations

from tft_goat.engine import simulate as S
from tft_sim.real_content import build_real, build_real_set18_clean

_HOOK_TABLES = ["ITEM_COMBAT_START", "ITEM_HP_THRESHOLD", "ITEM_ON_ATTACK", "ITEM_ON_CAST",
                "ITEM_ON_DAMAGED", "ITEM_ON_TICK", "ITEM_REVIVE"]


def alias_map(full) -> dict[str, str]:
    """DA_* craftable (co thanh phan) -> TFT_Item_* cung ten co effects, chi khi DA rong."""
    by_name = {}
    for api, it in full.items.items():
        if api.startswith("TFT_Item_") and it.effects:
            by_name.setdefault(it.name, api)
    out = {}
    for api, it in full.items.items():
        if api.startswith("DA_") and it.composition and not it.effects and it.name in by_name:
            out[api] = by_name[it.name]
    return out


def build_set18_aliased():
    """Noi dung Set 18 da alias. Tra ve (content, alias_dict)."""
    full = build_real("TFTSet18")
    amap = alias_map(full)
    clean = build_real_set18_clean()
    items = dict(clean.items)
    for da, tw in amap.items():
        if da in items:
            items[da] = items[da].model_copy(update={"effects": full.items[tw].effects})
        items[tw] = full.items[tw]  # twin phai co trong content de engine tra duoc effects
    out = clean.model_copy(update={"items": items, "patch": clean.patch + "-aliased"})
    for table in _HOOK_TABLES:
        d = getattr(S, table)
        for da, tw in amap.items():
            if tw in d and da not in d:
                d[da] = d[tw]
    return out, amap


if __name__ == "__main__":
    c, m = build_set18_aliased()
    print("aliases", len(m))
    for k, v in sorted(m.items()):
        print(k, "->", v)
