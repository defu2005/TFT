"""Tra ten hien thi -> apiName cho Set 18 (champion, item, augment, trait).

Nguon: data/set18_names.json (sinh tu snapshot CDragon). Quy tac:
- Ten trung nhieu apiName -> AmbiguousName (KHONG doan). Nguoi goi phai chon api khac
  (vi du: lay tu nguon co api, hoac bo qua ban ghi do).
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
    """{kind: {ten_chuan: [api, ...]}} (ten chuan = viet thuong, gon khoang trang)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, dict[str, list[str]]] = {}
    for kind in KINDS:
        idx: dict[str, list[str]] = {}
        for row in data[kind]:
            idx.setdefault(_norm(row["name"]), []).append(row["api"])
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
