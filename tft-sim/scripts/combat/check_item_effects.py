"""Phan loai item Set 18 theo tac dong trong engine (khong dung du lieu VOD).

Voi moi api item ma names18 xuat ra (tru ban alias twin), do:
  - stat: build_unit co doi chi so don vi (khong tinh khoi chung _GENERIC_ITEM) hay khong;
  - proc: api (sau alias khi SECONDARY) co hook trong cac bang *_set17 hay khong.
Chay o hai cau hinh: PRIMARY (khong alias) va SECONDARY (alias names18.item_alias_map).
Cot flag: can_ability_crit (IE/Jeweled Gauntlet, so chuoi con trong build_unit) duoc tinh vao 'stat'.
Phan lop: composition, DA_Component_*, DA_Artifact*, *Radiant, con lai.
Dung:  PYTHONPATH=<goat>/src:<sim>/src python3 scripts/combat/check_item_effects.py
"""
import collections
import importlib
import json
import pkgutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "src"))

import fidelity as Fd  # noqa: E402
import fight as F  # noqa: E402
from tft_sim import names18 as N  # noqa: E402
from tft_goat.engine.unit import build_unit  # noqa: E402

OUT = ROOT / "results/fixed/combat/item_effect_classes.json"


HOOK_TABLES = ("ITEM_ON_ATTACK", "ITEM_ON_CAST", "ITEM_ON_DAMAGED", "ITEM_HP_THRESHOLD",
               "ITEM_REVIVE", "ITEM_COMBAT_START", "ITEM_ON_TICK")


def _hook_keys():
    """Khoa CHINH XAC cua cac bang hook ma simulate.py tra cuu (khop tuyet doi, khong chuoi con)."""
    from tft_goat.engine import simulate as S
    keys = set()
    for name in HOOK_TABLES:
        tbl = getattr(S, name, None) or {}
        keys.update(k for k in tbl if isinstance(k, str))
    return keys


def _layer(api, c=None):
    it = c.items.get(api) if c is not None else None
    if it is not None and getattr(it, "composition", None):
        return "composition"
    if api.startswith("DA_Component_"):
        return "DA_Component"
    if api.startswith("DA_Artifact"):
        return "DA_Artifact"
    if api.endswith("Radiant"):
        return "Radiant"
    return "khac"


def main() -> int:
    F.set_content(18, Fd._C18)
    c = F._CONTENT[18]
    champ = next(v for v in c.champions.values() if v.stats and v.traits)
    data = json.loads(N.NAMES.read_text(encoding="utf-8"))
    twin = {r["twin_tft_item"] for r in data["items"] if r.get("twin_tft_item")}
    apis = sorted({r["api"] for r in data["items"] if r["api"] not in twin})
    alias = N.item_alias_map()
    hooks = _hook_keys()

    def stats(u):
        return (u.max_hp, u.ad, u.ap, u.armor, u.mr, u.attack_speed, u.crit_chance, u.max_mana, u.can_ability_crit)
    base = stats(build_unit(champ, 1, 0, c, (), 0))

    def classify(api):
        if api not in c.items:
            return "khong_co_noi_dung"
        stat = stats(build_unit(champ, 1, 0, c, (api,), 0)) != base
        proc = api in hooks
        if stat and proc:
            return "stat+proc"
        if stat:
            return "stat"
        if proc:
            return "proc"
        return "khong_gi"

    rows, tally = [], collections.defaultdict(collections.Counter)
    for a in apis:
        tgt = alias.get(a, a)
        p, s = classify(a), classify(tgt)
        lay = _layer(a, c)
        rows.append({"api": a, "layer": lay, "primary": p, "secondary_target": tgt, "secondary": s})
        tally[lay][("P", p)] += 1
        tally[lay][("S", s)] += 1
    rep = {"so_item_api": len(apis), "tally": {k: {f"{t}:{v}": n for (t, v), n in cnt.items()}
                                              for k, cnt in tally.items()},
           "primary_totals": dict(collections.Counter(r["primary"] for r in rows)),
           "secondary_totals": dict(collections.Counter(r["secondary"] for r in rows)),
           "rows": rows}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print({k: v for k, v in rep.items() if k != "rows"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
