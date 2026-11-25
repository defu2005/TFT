"""Do phu item va trait (Set 17 lam moc doi chieu, Set 18 dich). Do hanh vi cua engine, khong do ma nguon.

Item: moi item duoc phan loai theo (a) co nam trong bang hook nao cua engine, (b) co lam doi chi so
       don vi sau _build_team khi trang bi duoc gan (so sanh co/khong trang bi, tren cung tuong, sao 1).
Trait: moi trait duoc phan loai theo (a) co bien chi so ap dung duoc cho don vi (attrs_for) hay khong,
       (b) khi kich hoat dung moc min_units (doi gom dung so tuong co trait) co lam doi chi so nao khong,
       (c) ten trait co xuat hien trong ma engine ngoai trait_effects.py hay khong (tham chieu, khong chung minh logic).
Usage: python coverage_items_traits.py  -> results/fixed/combat/coverage_items_traits.json
"""
import json, re, sys
from collections import Counter
from pathlib import Path

import tft_goat.engine.simulate as S
from tft_goat.env.state import BoardUnit
from tft_goat.engine.unit import build_unit
from tft_goat.engine.trait_effects import attrs_for
from tft_sim.real_content import build_real

ENGINE_DIR = Path(S.__file__).parent
HOOK_TABLES = ["ITEM_COMBAT_START", "ITEM_HP_THRESHOLD", "ITEM_ON_ATTACK", "ITEM_ON_CAST",
               "ITEM_ON_DAMAGED", "ITEM_ON_TICK", "ITEM_REVIVE"]


def _num_state(u):
    out = {}
    for k, v in vars(u).items():
        if isinstance(v, bool):
            out[k] = float(v)
        elif isinstance(v, (int, float)):
            out[k] = float(v)
    return out


def _diff(a, b):
    keys = set(a) | set(b)
    return {k: (a.get(k, 0.0), b.get(k, 0.0)) for k in keys if abs(a.get(k, 0.0) - b.get(k, 0.0)) > 1e-9}


def item_coverage(content, probe_champ, set_no):
    hooks = {t: set(getattr(S, t, {}).keys()) for t in HOOK_TABLES}
    base = _num_state(build_unit(content.champions[probe_champ], 1, 0, content, item_apis=(), generic_items=0))
    rows, cls = {}, Counter()
    for api in sorted(content.items):
        tables = [t for t in HOOK_TABLES if api in hooks[t]]
        u = build_unit(content.champions[probe_champ], 1, 0, content, item_apis=(api,), generic_items=0)
        stat = bool(_diff(base, _num_state(u)))
        kind = ("stat+hook" if stat and tables else "stat" if stat else "hook" if tables else "none")
        cls[kind] += 1
        rows[api] = {"class": kind, "hook_tables": tables, "stat_change": stat}
    return {"set": set_no, "n_items": len(content.items), "by_class": dict(cls), "items": rows}


def trait_coverage(content, set_no):
    engine_src = "\n".join(p.read_text(encoding="utf-8") for p in ENGINE_DIR.rglob("*.py")
                           if p.name != "trait_effects.py")
    out, cls = {}, Counter()
    orig = S.apply_team_traits
    for tname, trait in content.traits.items():
        if not trait.effects:
            kind = "no_effects"
            cls[kind] += 1; out[tname] = {"class": kind}; continue
        keys = {k for e in trait.effects for k in e.variables}
        static_attrs = {k: attrs_for(k) for k in keys if attrs_for(k)}
        members = [c for c in content.champions.values() if trait.name in c.traits]
        need = min(e.min_units for e in trait.effects)
        probe_stat = None
        if len(members) >= max(need, 1):
            board = [BoardUnit(m.api_name, 1, on_board=True) for m in members[:max(need, 1)]]
            try:
                S.apply_team_traits = orig
                on = [_num_state(u) for u in S._build_team(board, 0, content)]
                S.apply_team_traits = lambda *a, **k: None
                off = [_num_state(u) for u in S._build_team(board, 0, content)]
                probe_stat = any(_diff(a, b) for a, b in zip(on, off))
            finally:
                S.apply_team_traits = orig
        ref = bool(re.search(r"\b" + re.escape(trait.name) + r"\b", engine_src))
        if static_attrs and probe_stat:
            kind = "generic_stat_applied"
        elif static_attrs:
            kind = "generic_stat_mapped_no_effect"
        else:
            kind = "no_stat_mapping"
        cls[kind] += 1
        out[tname] = {"class": kind, "name": trait.name, "n_members_in_set": len(members), "min_units": need,
                      "stat_keys_mapped": static_attrs, "probe_changed_stats": probe_stat, "name_referenced_in_engine": ref}
    return {"set": set_no, "n_traits": len(content.traits), "by_class": dict(cls), "traits": out}


if __name__ == "__main__":
    res = {}
    for set_no, mutator in ((17, "TFTSet17"), (18, "TFTSet18")):
        content = build_real(mutator)
        probe = next(a for a, c in content.champions.items() if c.stats is not None)
        res[f"set{set_no}"] = {"items": item_coverage(content, probe, set_no), "traits": trait_coverage(content, set_no)}
        print(set_no, json.dumps({"items": res[f"set{set_no}"]["items"]["by_class"],
                                  "traits": res[f"set{set_no}"]["traits"]["by_class"]}), flush=True)
    out = Path("/home/user/TFT/tft-sim/results/fixed/combat/coverage_items_traits.json")
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print("wrote", out)
