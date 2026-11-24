"""Noi dung that tu CDragon latest (18.7). Nhan: 'CDragon latest (18.7)'.
Set 17 block (TFTSet17) va Set 18 roster (TFTSet18) dung cung mot file. build_set_content doc hang so
SET_MUTATOR toan cuc, nen dat tam thoi trong tien trinh (khong sua TFT_GOAT)."""
import json
from pathlib import Path

RAW = Path("/home/user/mielpopsssssss/tft_goat/data/cdragon/cdragon_latest_fetched-2026-11-23.json")


def build_real(mutator: str):
    import tft_goat.data.content as dc
    old = dc.SET_MUTATOR
    try:
        dc.SET_MUTATOR = mutator
        raw = json.loads(RAW.read_text(encoding="utf-8"))
        return dc.build_set_content(raw, f"CDragon-latest-18.7-{mutator}")
    finally:
        dc.SET_MUTATOR = old


def build_real_fullrecipe(mutator: str):
    """Noi dung that + CONG THUC PLACEHOLDER cho moi cap thanh phan con thieu (sua EQUIP khong tieu thu).
    Cong thuc that van giu nguyen. Placeholder: vat pham 'it_<x>_<y>' voi AD 0.1 (chi de env tieu thu thanh phan).
    Nhan: 'CDragon latest (18.7), <mutator>, derived fullrecipe'. Khong phai du lieu game that cho cac cap nay."""
    import itertools
    from tft_goat.data.models import Item
    from tft_goat.env.items import components_and_recipes
    content = build_real(mutator)
    comps, rec = components_and_recipes(content)
    items = dict(content.items)
    added = 0
    for x, y in itertools.combinations_with_replacement(comps, 2):
        if tuple(sorted((x, y))) in rec:
            continue
        api = f"it_placeholder_{x}_{y}"
        items[api] = Item(api_name=api, name=api, composition=(x, y), effects={"AD": 0.1})
        added += 1
    out = content.model_copy(update={"items": items, "patch": f"CDragon-latest-18.7-{mutator}-fullrecipe"})
    out._placeholder_added = added  # ghi lai so cong thuc placeholder
    return out


def build_real_set18_clean():
    """Set 18 that, KHONG placeholder. Bo cac item co thanh phan 'TFT_Item_*' (vat pham Set 17 con sot trong
    bo item cua file, lam thanh phan pha tron). Con lai: 10 thanh phan DA_Component_* va 55 cap, moi cap co cong thuc that.
    Nhan: 'CDragon latest (18.7), Set 18 roster (TFTSet18), DA components only'."""
    from tft_goat.env.items import components_and_recipes
    content = build_real("TFTSet18")
    items = {k: v for k, v in content.items.items()
             if not any(c.startswith("TFT_Item_") for c in v.composition)
             and not (k.startswith("TFT_Item_") and not v.composition)}
    out = content.model_copy(update={"items": items, "patch": "CDragon-latest-18.7-TFTSet18-DAonly"})
    comps, rec = components_and_recipes(out)
    assert all(c.startswith("DA_") for c in comps), comps
    return out
