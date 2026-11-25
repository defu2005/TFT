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
  Khong xoay cho doi B. Moi ben: hoac tat ca unit co vi tri, hoac khong unit nao. Khong trung o, nam trong luoi.
Augment: luon truyen cho engine (run_combat nhan augment).
Set 18: chi cho ability "generic" hoac "none" (tranh am tham dung default_ability cho tuong co logic that).
"""
from __future__ import annotations

import contextlib
import json
from pathlib import Path

import numpy as np

import tft_goat.engine.simulate as S
from tft_goat.engine.abilities import default_ability
from tft_goat.env.state import BoardUnit
from tft_goat.engine.simulate import run_combat

SCHEMA = "fight-v1"
ABILITY_MODES = ("hand", "generic", "none")
_NOOP = lambda caster, allies, enemies, ctx: None  # noqa: E731
_orig_build = S._build_team
_orig_get = S.get_ability
_STATE = {"ability": "hand", "pos": None}


def _patched_build(board, team, content, trait_bonus=0):
    units = _orig_build(board, team, content, trait_bonus=trait_bonus)
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
    return _orig_get(api)


S._build_team = _patched_build
S.get_ability = _patched_get


@contextlib.contextmanager
def fight_context(ability: str = "hand", positions=None):
    if ability not in ABILITY_MODES:
        raise ValueError(ability)
    old = dict(_STATE)
    _STATE["ability"] = ability
    _STATE["pos"] = positions
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
        for p in known:
            if not (0 <= p[0] < 8 and 0 <= p[1] < 7):
                raise ValueError(f"{k}: vi tri {p} ngoai luoi 8x7")
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


def predict_win(record: dict, n: int = 20, ability: str = "hand", items: bool = True, seed0: int = 0,
                augments: bool = True) -> dict:
    """Xac suat A thang tu n lan chay engine (RNG seed0..seed0+n-1). augments=False: bo augment."""
    if record["set"] == 18 and ability == "hand":
        raise ValueError("Set 18 chua co logic ability viet tay: dung 'generic' hoac 'none'")
    ba, bb, pos, aa, ab = boards_of(record, items)
    if not augments:
        aa, ab = (), ()
    content = _CONTENT[record["set"]]
    wins = [0, 0, 0]
    with fight_context(ability, pos):
        for i in range(n):
            r = run_combat(ba, bb, content, np.random.default_rng(seed0 + i), aa, ab)
            w = r.winner
            wins[0 if w == 0 else 1 if w == 1 else 2] += 1
    return {"p_a": wins[0] / n, "a": wins[0], "b": wins[1], "draw": wins[2], "n": n,
            "ability": ability, "items": items}
