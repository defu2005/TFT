"""Alias item Set 18: craftable DA_* co effects rong trong CDragon; item cung ten TFT_Item_* co hieu ung that.

Gia dinh (ghi ro, chua kiem chung tren Set 18 that): hieu ung cua item TFT_Item_<Ten> cung la hieu ung
cua craftable DA_<Ten> cung ten. Ap dung qua id (fight.boards_of khi item_alias=True), khong qua content hay hook.
Khong dang ky hook toan cuc (xem order_check_items.py: hook DA_* lam PRIMARY doi 8/150 tran).
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
    """Noi dung Set 18 co copy effects tu twin vao DA_* rong. CHI DUNG DE CHAN DOAN (alias18.py, selftest).
    KHONG dang ky hook: hook DA_* toan cuc lam PRIMARY doi ket qua (scripts/combat/order_check_items.py)."""
    full = build_real("TFTSet18")
    amap = alias_map(full)
    clean = build_real_set18_clean()
    items = dict(clean.items)
    for da, tw in amap.items():
        if da in items:
            items[da] = items[da].model_copy(update={"effects": full.items[tw].effects})
        items[tw] = full.items[tw]
    out = clean.model_copy(update={"items": items, "patch": clean.patch + "-aliased-diag"})
    return out, amap


def build_set18_records():
    """Noi dung cho PRIMARY va cho ghi ban ghi that: CDragon nguyen goc, KHONG copy effects, KHONG dang ky hook.
    Ban do DA_* -> TFT_Item_* chi ap dung theo co item_alias (SECONDARY) trong fight.boards_of.
    Tra ve (content, alias_dict) de giu chu ky cu."""
    full = build_real("TFTSet18")
    return full, alias_map(full)


if __name__ == "__main__":
    c, m = build_set18_aliased()
    print("aliases", len(m))
    for k, v in sorted(m.items()):
        print(k, "->", v)

