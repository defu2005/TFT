"""Schema ban ghi tran (fight-v1) va wrapper engine (docs/research/combat-public-data.md).

Ban ghi: {"schema": "fight-v1", "set": 17|18, "label": "sim|fixture|real", "source": str,
  "a": {"level", "augments": [api...], "units": [{"api", "star", "items": [api...], "pos": [r,c]|null}]},
  "b": {...}, "result": {"winner": 0|1|null}}

Hai cong tac doc lap (khong gop):
  ability: "hand"    = ability viet tay (engine nguyen ban, chi Set 17)
           "generic" = moi tuong dung default_ability (nuke don muc tieu)
           "none"    = khong ability
  items:   True/False = co hieu ung trang bi hay khong
Vi tri (tuy chon): [row, col] TUYET DOI tren luoi 8 hang x 7 cot (engine GRID_ROWS=8, GRID_COLS=7).
  Khong xoay cho doi B (khung tuyet doi). Ben a o hang 0-3, ben b o hang 4-7 (engine dat doi hinh theo nua
  luoi cua tung ben). Moi ben: hoac tat ca unit co vi tri, hoac khong unit nao. Khong trung o.
Augment: luon truyen cho engine (run_combat nhan augment).
Set 18: chi cho ability "generic" hoac "none" (tranh am tham dung default_ability cho tuong co logic that).
"""
from __future__ import annotations

import contextlib
import json
from pathlib import Path

import numpy as np

import tft_goat.engine.simulate as S
import tft_goat.engine.trait_effects as TE

# Set 18: hai khoa trait bi ap sai (xem docs/research/combat-public-data.md muc 8). Chi bo o duong Set 18.
_SET18_BAD_KEYS = ("MaxHealthShield", "APPerCast")
_orig_attrs_for = TE.attrs_for


def _attrs_for_set18(key: str):
    if key in _SET18_BAD_KEYS:
        return []
    return _orig_attrs_for(key)
from tft_goat.env.traits import trait_counts as _trait_counts  # noqa: E402

_orig_apply_team_traits = S.apply_team_traits


def emblem_trait_of(item_api: str, content):
    """Ten trait (ten hien thi) ma emblem Set 18 cong them diem. None neu khong phai emblem trait.
    Khop theo ten hien thi: 'Ravager Emblem' -> trait 'Ravager' (khoa DA_18_Slayer). Khong khop theo khoa."""
    it = content.items.get(item_api)
    if it is None or not item_api.startswith("DA_18_Emblem") or not it.name.endswith(" Emblem"):
        return None
    base = it.name[: -len(" Emblem")]
    return base if any(t.name == base for t in content.traits.values()) else None


def _emblem_traits(units, content, bonus_units: int = 0) -> None:
    """Giong TE.apply_team_traits, cong them: moi tuong giu emblem cua trait T (khong co T tu nhien)
    tinh them 1 diem T, va nhan buff cua T nhu mot thanh vien."""
    if not units:
        return
    held = [{t for api in u.item_apis if (t := emblem_trait_of(api, content))} for u in units]
    counts = dict(_trait_counts([u.champion_api for u in units], content))
    for u, hs in zip(units, held):
        own = content.champions[u.champion_api].traits if u.champion_api in content.champions else ()
        for t in hs:
            if t not in own:
                counts[t] = counts.get(t, 0) + 1
    by_name = {t.name: t for t in content.traits.values()}
    for name, count in counts.items():
        trait = by_name.get(name)
        if trait is None or not trait.effects:
            continue
        bps = tuple(trait.breakpoints)
        n = count + (bonus_units if bps != (1,) else 0)
        tier = sum(1 for bp in bps if n >= bp)
        if tier == 0:
            continue
        effs = sorted(trait.effects, key=lambda e: e.min_units)
        eff = effs[min(tier - 1, len(effs) - 1)]
        members = [u for u, hs in zip(units, held)
                   if name in (content.champions[u.champion_api].traits if u.champion_api in content.champions else ())
                   or name in hs]
        for key, val in eff.variables.items():
            if not isinstance(val, (int, float)) or val == 0:
                continue
            targets = units if "teamwide" in key.lower() else members
            for attr in TE.attrs_for(key):
                for u in targets:
                    TE._apply_stat(u, attr, float(val))


from tft_goat.engine.abilities import default_ability
from tft_goat.env.state import BoardUnit
from tft_goat.engine.simulate import run_combat

SCHEMA = "fight-v1"
ABILITY_MODES = ("hand", "generic", "none", "template")
_NOOP = lambda caster, allies, enemies, ctx: None  # noqa: E731
_orig_build = S._build_team
_orig_get = S.get_ability
_STATE = {"ability": "hand", "pos": None, "content": None, "traits": True, "novars": False}


def _patched_build(board, team, content, trait_bonus=0):
    if not _STATE.get("traits", True):
        saved = S.apply_team_traits
        S.apply_team_traits = lambda *a, **k: None
        try:
            units = _orig_build(board, team, content, trait_bonus=trait_bonus)
        finally:
            S.apply_team_traits = saved
    else:
        units = _orig_build(board, team, content, trait_bonus=trait_bonus)
    if _STATE.get("novars", False):
        for u in units:
            u.variables = {}  # Set 18 thuc te: generic rơi ve ad*2 neu khong co bien
    pos = _STATE["pos"]
    if pos is not None and pos[team] is not None:
        if len(units) != len(pos[team]):
            raise ValueError(f"so unit {len(units)} != so vi tri {len(pos[team])} (team {team})")
        for u, p in zip(units, pos[team]):
            if p is not None:
                u.pos = (int(p[0]), int(p[1]))
    return units


def _patched_get(api):
    m = _STATE["ability"]
    if m == "none":
        return _NOOP
    if m == "generic":
        return default_ability
    if m == "template":
        from templates import get_ability_template
        return get_ability_template(_STATE["content"], api)
    return _orig_get(api)


S._build_team = _patched_build
S.get_ability = _patched_get


@contextlib.contextmanager
def fight_context(ability: str = "hand", positions=None, content=None, traits: bool = True, novars: bool = False):
    if ability not in ABILITY_MODES:
        raise ValueError(ability)
    if novars and ability != "generic":
        raise ValueError("novars chi dung voi ability generic")
    old = dict(_STATE)
    _STATE["ability"] = ability
    _STATE["pos"] = positions
    _STATE["content"] = content
    _STATE["traits"] = traits
    _STATE["novars"] = novars
    try:
        yield
    finally:
        _STATE.update(old)


def boards_of(record: dict, items: bool = True):
    """(board_a, board_b, positions, augments_a, augments_b) cho run_combat."""
    sides, pos, augs = [], [], []
    for k in ("a", "b"):
        units, plist = [], []
        for u in record[k]["units"]:
            its = list(u.get("items", [])) if items else []
            units.append(BoardUnit(u["api"], int(u["star"]), on_board=True,
                                   items=len(its), item_apis=tuple(its)))
            plist.append(u.get("pos"))
        sides.append(units)
        pos.append(plist if any(p is not None for p in plist) else None)
        augs.append(tuple(record[k].get("augments", [])))
    return sides[0], sides[1], tuple(pos), augs[0], augs[1]


def check_record(record: dict) -> None:
    if record.get("schema") != SCHEMA:
        raise ValueError("schema")
    if record.get("label") not in ("sim", "fixture", "real"):
        raise ValueError("label")
    for k in ("a", "b"):
        side = record[k]
        if not isinstance(side.get("units"), list):
            raise ValueError(f"{k}.units")
        for u in side["units"]:
            if not {"api", "star"} <= set(u):
                raise ValueError(f"{k}: unit thieu truong")
    if record.get("result", {}).get("winner") not in (0, 1, None):
        raise ValueError("result.winner")
    for k in ("a", "b"):
        ps = [u.get("pos") for u in record[k]["units"]]
        known = [p for p in ps if p is not None]
        if known and len(known) != len(ps):
            raise ValueError(f"{k}: vi tri phai co du hoac khong co (thieu {len(ps) - len(known)})")
        lo, hi = (0, 3) if k == "a" else (4, 7)
        for p in known:
            if not (lo <= p[0] <= hi and 0 <= p[1] < 7):
                raise ValueError(f"{k}: vi tri {p} ngoai nua luoi cua ben {k} (hang {lo}-{hi}, cot 0-6)")
        if len({tuple(p) for p in known}) != len(known):
            raise ValueError(f"{k}: trung o")


def load_jsonl(path) -> list[dict]:
    rows = [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]
    for r in rows:
        check_record(r)
    return rows


_CONTENT: dict = {}


def set_content(set_no: int, content) -> None:
    _CONTENT[set_no] = content


def coverage(record: dict) -> dict:
    """Bao phu cho mot ban ghi: unit/trang bi/augment co anh huong hay khong. Ten la khong duoc phep la."""
    content = _CONTENT[record["set"]]
    from tft_goat.engine.simulate import ITEM_COMBAT_START
    from tft_goat.engine.augments_set17 import AUGMENT_REGISTRY
    out = {}
    for k in ("a", "b"):
        units = record[k]["units"]
        unknown = [u["api"] for u in units if u["api"] not in content.champions]
        items_total = sum(len(u.get("items", [])) for u in units)
        items_unknown = sum(1 for u in units for it in u.get("items", []) if it not in content.items)
        items_hooked = sum(1 for u in units for it in u.get("items", []) if it in ITEM_COMBAT_START)
        items_empty = sum(1 for u in units for it in u.get("items", [])
                          if it in content.items and not content.items[it].effects)
        augs = record[k].get("augments", [])
        out[k] = {"units": len(units), "unknown_champions": unknown,
                  "items_total": items_total, "items_unknown": items_unknown, "items_with_combat_hook": items_hooked,
                  "items_empty_effects": items_empty,
                  "augments": len(augs), "augments_with_hook": sum(1 for a in augs if a in AUGMENT_REGISTRY)}
    return out


def predict_win(record: dict, n: int = 20, ability: str = "hand", items: bool = True, seed0: int = 0,
                augments: bool = True, traits: bool = True, novars: bool = False, emblems: bool = False) -> dict:
    """Xac suat A thang tu n lan chay engine (RNG seed0..seed0+n-1). augments=False: bo augment."""
    if record["set"] == 18 and ability == "hand":
        raise ValueError("Set 18 chua co logic ability viet tay: dung 'generic' hoac 'none'")
    cov = coverage(record)
    for k in ("a", "b"):
        if cov[k]["unknown_champions"]:
            raise ValueError(f"{k}: tuong khong co trong noi dung set {record['set']}: {cov[k]['unknown_champions']}")
    ba, bb, pos, aa, ab = boards_of(record, items)
    if not augments:
        aa, ab = (), ()
    content = _CONTENT[record["set"]]
    wins = [0, 0, 0]
    skip = record["set"] == 18
    if emblems and record["set"] != 18:
        raise ValueError("emblems chi cho Set 18")
    if skip:
        TE.attrs_for = _attrs_for_set18
    if emblems:
        S.apply_team_traits = _emblem_traits
    try:
        with fight_context(ability, pos, content, traits, novars):
            for i in range(n):
                r = run_combat(ba, bb, content, np.random.default_rng(seed0 + i), aa, ab)
                w = r.winner
                wins[0 if w == 0 else 1 if w == 1 else 2] += 1
    finally:
        TE.attrs_for = _orig_attrs_for
        S.apply_team_traits = _orig_apply_team_traits
    return {"p_a": wins[0] / n, "a": wins[0], "b": wins[1], "draw": wins[2], "n": n,
            "ability": ability, "items": items, "emblems": emblems, "coverage": cov}
