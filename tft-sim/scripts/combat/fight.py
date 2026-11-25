"""Schema ban ghi tran (fight-v1) va wrapper engine (model-plan / docs/research/combat-public-data.md).

Mot ban ghi = mot combat: hai ben, moi ben co cap, augment, va danh sach tuong.
  {"schema": "fight-v1", "set": 17|18, "label": "sim|fixture|real", "source": str,
   "a": {"level": int, "augments": [api...], "units": [{"api", "star", "items": [api...], "pos": [r,c] | null}]},
   "b": {...},
   "result": {"winner": 0|1|null}}     # 0 = a thang, 1 = b thang, null = chua biet

Wrapper (KHONG sua engine, chi vá trong ngữ cảnh):
  - mode "full":   engine nguyen ban (ability Set 17 + item).
  - mode "public": tat ability (thay bang no-op) va bo item. Chi dung chi so va sao.
    Dung de kiem gia thuyet "chi so cong khai du de du doan".
  - positions: neu co, ghi de unit.pos sau khi engine dat doi hinh (engine khong nhan vi tri tu ben goi).
  Canh bao: get_ability() roi ve default_ability (nuke don muc tieu) khi tuong khong co trong bang Set 17.
  Voi Set 18 chi cho mode "public", de khong am tham dung nuke mac dinh cho 91 tuong.
"""
from __future__ import annotations

import contextlib
import json
from pathlib import Path

import numpy as np

import tft_goat.engine.simulate as S
from tft_goat.env.state import BoardUnit
from tft_goat.engine.simulate import run_combat

SCHEMA = "fight-v1"
_NOOP = lambda caster, allies, enemies, ctx: None  # noqa: E731
_orig_build = S._build_team
_orig_get = S.get_ability
_STATE = {"mode": "full", "pos": None}


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
    if _STATE["mode"] == "public":
        return _NOOP
    return _orig_get(api)


S._build_team = _patched_build
S.get_ability = _patched_get


@contextlib.contextmanager
def fight_context(mode: str = "full", positions=None):
    """mode: 'full' | 'public'. positions: (list_a, list_b) moi phan tu [r,c] hoac None."""
    if mode not in ("full", "public"):
        raise ValueError(mode)
    old = dict(_STATE)
    _STATE["mode"] = mode
    _STATE["pos"] = positions
    try:
        yield
    finally:
        _STATE.update(old)


def boards_of(record: dict, mode: str = "full"):
    """Chuyen ban ghi thanh (board_a, board_b, positions) cho run_combat."""
    sides = []
    pos = []
    for k in ("a", "b"):
        units = []
        plist = []
        for u in record[k]["units"]:
            items = [] if mode == "public" else list(u.get("items", []))
            units.append(BoardUnit(u["api"], int(u["star"]), on_board=True,
                                   items=len(items), item_apis=tuple(items)))
            plist.append(u.get("pos"))
        sides.append(units)
        pos.append(plist if any(p is not None for p in plist) else None)
    return sides[0], sides[1], tuple(pos)


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


def load_jsonl(path) -> list[dict]:
    rows = [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]
    for r in rows:
        check_record(r)
    return rows


def predict_win(record: dict, n: int = 20, mode: str = "full", seed0: int = 0) -> dict:
    """Tra xac suat A thang tu n lan chay engine voi RNG khac nhau."""
    if record["set"] == 18 and mode == "full":
        raise ValueError("Set 18 chua co logic ability: chi dung mode 'public' (tranh default_ability am tham)")
    ba, bb, pos = boards_of(record, mode)
    content = _CONTENT[record["set"]]
    wins = [0, 0, 0]
    with fight_context(mode, pos):
        for i in range(n):
            r = run_combat(ba, bb, content, np.random.default_rng(seed0 + i), (), ())
            w = r.winner
            wins[0 if w == 0 else 1 if w == 1 else 2] += 1
    return {"p_a": wins[0] / n, "a": wins[0], "b": wins[1], "draw": wins[2], "n": n, "mode": mode}


_CONTENT: dict = {}


def set_content(set_no: int, content) -> None:
    _CONTENT[set_no] = content
