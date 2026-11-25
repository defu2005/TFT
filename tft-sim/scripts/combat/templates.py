"""Template ability tu MO TA + BIEN CDragon (khong chinh theo tung tuong sau khi thay ket qua).

Quy tac (co dinh truoc khi do):
  - Loai sat thuong: tag trong mo ta (magicDamage | physicalDamage | trueDamage). Khong co tag -> khong ap dung.
  - So sat thuong: bien dau tien co ten chua 'damage' (cung quy tac voi default_damage). Khong co -> khong ap dung.
  - Ti le theo chi so: 'scaleAP' trong mo ta -> nhan AP/100; 'scaleAD' -> nhan AD/100; khac -> nhan 1.
  - Hieu ung: 'stun' trong mo ta va co bien 'duration' -> choang muc tieu bang gia tri do.
Tuong khong ap dung duoc: dung default_ability (nuke mac dinh). Dem coverage de bao cao.
"""
from __future__ import annotations

import re

from tft_goat.engine.abilities import default_ability

_DTYPE = re.compile(r"<(magicDamage|physicalDamage|trueDamage)>")


def _damage_name(variables: dict) -> str | None:
    for name in variables:
        if "damage" in name.lower():
            return name
    return None


def _duration_name(variables: dict) -> str | None:
    for name in variables:
        if "duration" in name.lower():
            return name
    return None


def describe(champion):
    """Tra ve dict mo ta quy tac ap dung, hoac None neu khong co template."""
    ab = champion.ability
    if ab is None or not ab.desc:
        return None
    m = _DTYPE.search(ab.desc)
    dname = _damage_name(ab.variables or {})
    if not m or not dname:
        return None
    dtype = m.group(1)
    scale = "ap" if "scaleAP" in ab.desc else ("ad" if "scaleAD" in ab.desc else "flat")
    stun_dur = _duration_name(ab.variables or {}) if "stun" in ab.desc.lower() else None
    return {"dtype": dtype, "dmg_var": dname, "scale": scale, "stun_var": stun_dur}


def build(champion):
    spec = describe(champion)
    if spec is None:
        return None
    dname, dtype, scale, stun_var = spec["dmg_var"], spec["dtype"], spec["scale"], spec["stun_var"]

    def fn(caster, allies, enemies, ctx):
        tgt = ctx.target_of(caster)
        if tgt is None:
            return
        base = caster.ability_value(dname)
        if scale == "ap":
            raw = base * (caster.ap / 100.0)
        elif scale == "ad":
            raw = base * (caster.ad / 100.0)
        else:
            raw = base
        if dtype == "magicDamage":
            ctx.deal_magic(caster, tgt, raw)
        elif dtype == "physicalDamage":
            ctx.deal_physical(caster, tgt, raw)
        else:
            ctx.deal_true(caster, tgt, raw)
        if stun_var is not None:
            ctx.stun(tgt, caster.ability_value(stun_var))
    return fn


_CACHE: dict = {}


def template_for(content):
    """Dict api -> ham template cho mot noi dung set (cache theo id)."""
    key = id(content)
    if key not in _CACHE:
        _CACHE[key] = {api: build(ch) for api, ch in content.champions.items()}
    return _CACHE[key]


def get_ability_template(content, api):
    fn = template_for(content).get(api)
    return fn if fn is not None else default_ability


def coverage(content) -> dict:
    tmap = template_for(content)
    n = len(content.champions)
    covered = sum(1 for v in tmap.values() if v is not None)
    return {"champions": n, "template_covered": covered, "fraction": round(covered / n, 4) if n else None}
