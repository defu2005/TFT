"""Noi dung tong hop co day du cong thuc: moi cap thanh phan deu co mot vat pham hoan chinh.

Ly do: noi dung build_sample_content chi co 1 cong thuc. Teacher scripted chon EQUIP truoc,
nen moi cap khong co cong thuc tao ra vong lap no-op (xem README). Ban nay bo sung du 6 cap
tu 4 thanh phan, de kiem chung teacher khong bi ket. Dung patch rieng de tranh dung nham cache
cua tft_goat.env.items (cache theo patch).
"""
from __future__ import annotations

import itertools

from tft_goat.data.models import Item
from tft_goat.data.sample import build_sample_content

FULL_RECIPE_PATCH = "synth-fullrecipe"
COMPONENTS = ["cmp_a", "cmp_b", "cmp_c", "cmp_d"]


def build_full_recipe_content():
    base = build_sample_content()
    items = {}  # chi giu vat pham cua chung toi: cac cmp_bf/cmp_bow cu khong co du cong thuc
    for c in COMPONENTS:
        items[c] = Item(api_name=c, name=c, composition=())
    for x, y in itertools.combinations_with_replacement(COMPONENTS, 2):
        api = f"it_{x}_{y}"
        items[api] = Item(api_name=api, name=api, composition=(x, y), effects={"AD": 0.1})
    return base.model_copy(update={"items": items, "patch": FULL_RECIPE_PATCH})
