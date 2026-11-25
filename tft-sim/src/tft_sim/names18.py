"""Tra ten hien thi -> apiName cho Set 18 (champion, item, augment, trait).

Nguon: data/set18_names.json (sinh tu snapshot CDragon). Quy tac:
- Ten trung nhieu apiName -> AmbiguousName (KHONG doan). Nguoi goi phai chon api khac
  (vi du: lay tu nguon co api, hoac bo qua ban ghi do).
- Item: alias twin TFT_Item_* bi bo khoi ung vien khi co ban goc DA_* cung ten. Con lai la
  ten trung that (chu yeu la ban _Upgrade, la item rieng cua CDragon).
- Augment: khong uu tien tien to; ten trung van nem AmbiguousName.
- Ten khong co trong danh muc -> UnknownName.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NAMES = ROOT / "data" / "set18_names.json"
KINDS = ("champions", "items", "augments", "traits")


class UnknownName(KeyError):
    pass


class AmbiguousName(ValueError):
    def __init__(self, kind: str, name: str, apis: list[str]):
        super().__init__(f"{kind}: '{name}' trung nhieu api: {apis}")
        self.kind, self.name, self.apis = kind, name, apis


def _norm(s: str) -> str:
    return " ".join(s.split()).casefold()


def load(path: Path = NAMES) -> dict[str, dict[str, list[str]]]:
    """{kind: {ten_chuan: [api, ...]}} (ten chuan = viet thuong, gon khoang trang).
    Item: bo ung vien la ban alias twin (TFT_Item_*) khi ban goc DA_* cung ten da co mat."""
    data = json.loads(path.read_text(encoding="utf-8"))
    twin_alias = {r["twin_tft_item"] for r in data["items"] if r.get("twin_tft_item")}
    out: dict[str, dict[str, list[str]]] = {}
    for kind in KINDS:
        idx: dict[str, list[str]] = {}
        for row in data[kind]:
            idx.setdefault(_norm(row["name"]), []).append(row["api"])
        if kind == "items":
            for n, apis in idx.items():
                idx[n] = [a for a in apis if a not in twin_alias or not any(
                    o != a and o not in twin_alias for o in apis)]
        out[kind] = idx
    return out


_INDEX = None


def _idx():
    global _INDEX
    if _INDEX is None:
        _INDEX = load()
    return _INDEX


def candidates(kind: str, name: str) -> list[str]:
    if kind not in KINDS:
        raise UnknownName(kind)
    return list(_idx()[kind].get(_norm(name), []))


def resolve(kind: str, name: str) -> str:
    """Tra ten -> mot apiName. Nem AmbiguousName neu trung, UnknownName neu khong co."""
    apis = candidates(kind, name)
    if not apis:
        raise UnknownName(f"{kind}: '{name}'")
    if len(apis) > 1:
        raise AmbiguousName(kind, name, apis)
    return apis[0]


def ambiguous_report() -> dict[str, dict[str, list[str]]]:
    """Moi kind: cac ten hien thi tro toi nhieu apiName."""
    return {kind: {n: apis for n, apis in idx.items() if len(apis) > 1}
            for kind, idx in _idx().items()}


def item_alias_map(path: Path = NAMES) -> dict[str, str]:
    """{apiName DA_*: apiName TFT_Item_* co chi so}: cap twin_tft_item trong data/set18_names.json.
    Khong gop: day la ban do ID, dung de dua item vao dung khoa content va hook engine."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return {r["api"]: r["twin_tft_item"] for r in data["items"] if r.get("twin_tft_item")}

