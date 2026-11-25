"""Probe trang bi: voi moi item (top trong mau + thanh phan co ban), so sanh 3 thu:
  (a) effects tho cua CDragon (snapshot), (b) effects engine dang dung (content.items[api].effects),
  (c) chenh lech thuc te tren mot tuong co ban: build_unit co item - khong item.
Chi doc, khong sua gi. Ghi results/fixed/combat/item_probe.json.

Dung: python3 item_probe.py [out.json] [n_top]
"""
import gzip
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SAMPLE = ROOT / "data/sim/pairs18_sample.jsonl.gz"
SNAP = ROOT / "data/cdragon/cdragon_18.7_2026-11-23.json.gz"
OUT = ROOT / "results/fixed/combat/item_probe.json"
FIELDS = ("max_hp", "armor", "mr", "ad", "ap", "attack_speed", "crit_chance", "max_mana")


def main(out: Path, n_top: int) -> None:
    sys.path.insert(0, str(HERE))
    sys.path.insert(0, str(ROOT / "src"))
    from tft_goat.engine import simulate as S9
    from tft_goat.env.state import BoardUnit as BU
    from tft_sim.real_content import build_real
    import fight as F

    c18 = build_real("TFTSet18")
    F.set_content(18, c18)
    raw = {x["apiName"]: x for x in json.load(gzip.open(SNAP, "rt", encoding="utf-8"))["items"]}
    rows = [json.loads(l) for l in gzip.open(SAMPLE, "rt", encoding="utf-8")]
    cnt = Counter(it for r in rows for s in ("a", "b") for u in r[s]["units"] for it in u.get("items", []))
    top = [api for api, _ in cnt.most_common() if not api.startswith("DA_18_Emblem")][:n_top]
    comps = sorted(api for api in c18.items if api.startswith("DA_Component_"))[:8]
    probe_items = list(dict.fromkeys(top + comps))
    champ = next(a for a, c in c18.champions.items() if c.stats and "Krug" in a)  # DA_Krug18
    base_u = S9._build_team([BU(champ, 1, on_board=True)], 0, c18, 0)[0]
    base = {f: getattr(base_u, f) for f in FIELDS}
    rows_out = []
    for api in probe_items:
        ci = c18.items.get(api)
        u = S9._build_team([BU(champ, 1, on_board=True, items=1, item_apis=(api,))], 0, c18, 0)[0]
        delta = {f: round(getattr(u, f) - base[f], 6) for f in FIELDS if abs(getattr(u, f) - base[f]) > 1e-9}
        rows_out.append({
            "api": api,
            "name": ci.name if ci else None,
            "in_sample_count": cnt.get(api, 0),
            "raw_effects": (raw.get(api) or {}).get("effects"),
            "engine_effects": dict(ci.effects) if ci else None,
            "unit_delta": delta,
        })
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"champion": champ, "base": base, "items": rows_out},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    for r in rows_out:
        print(r["api"], "n=", r["in_sample_count"], "| engine:", r["engine_effects"], "| delta:", r["unit_delta"])
    print(f"{len(rows_out)} items -> {out}")


if __name__ == "__main__":
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else OUT, n)
