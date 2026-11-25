"""Kiem tra phu thuoc thu tu va anh huong cua hook DA_* toan cuc len PRIMARY.

Hai che do, moi che do chay trong mot tien trinh rieng (de khong lan trang thai):
  registered   : import fidelity (dang ky hook DA_* toan cuc, nhu bo cham diem that), roi chay
                 PRIMARY -> SECONDARY -> PRIMARY. Hai lan PRIMARY phai giong nhau (khong phu thuoc thu tu).
  unregistered : cung noi dung, nhung khoi phuc bang hook ve truoc khi dang ky. Chay PRIMARY.
So sanh registered(PRIMARY) voi unregistered(PRIMARY): khac nhau = hook DA_* dang anh huong PRIMARY.

Dung: python3 scripts/combat/order_check_items.py [n_rows] [n_runs]
"""
import gzip
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SAMPLE = ROOT / "data/sim/pairs18_sample.jsonl.gz"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "src"))

PRIMARY = dict(ability="generic", items=True, augments=True, traits=True, emblems=False,
               traits_table=False, item_alias=False)
SECONDARY = dict(PRIMARY, emblems=True, traits_table=True, item_alias=True)


def _predict(F, rows, cfg, n):
    out = []
    for r in rows:
        p = F.predict_win(r, n, cfg["ability"], cfg["items"], 0, cfg["augments"], cfg["traits"],
                          emblems=cfg["emblems"], traits_table=cfg["traits_table"],
                          item_alias=cfg["item_alias"])
        out.append([p["a"], p["b"], p["draw"]])
    return out


def child(mode: str, n_rows: int, n_runs: int) -> dict:
    from tft_goat.engine import simulate as S
    from tft_sim.item_alias import _HOOK_TABLES
    snap = {t: dict(getattr(S, t)) for t in _HOOK_TABLES}
    import fidelity  # noqa: F401  (dang ky hook DA_* toan cuc luc import, nhu bo cham diem)
    import fight as F
    if mode == "unregistered":
        for t in _HOOK_TABLES:
            d = getattr(S, t)
            d.clear()
            d.update(snap[t])
    rows = [json.loads(l) for l in gzip.open(SAMPLE, "rt", encoding="utf-8")][:n_rows]
    res = {"mode": mode, "hook_da_keys": sorted(k for t in _HOOK_TABLES for k in getattr(S, t)
                                                 if str(k).startswith("DA_"))[:5]}
    res["primary"] = _predict(F, rows, PRIMARY, n_runs)
    if mode == "registered":
        res["secondary"] = _predict(F, rows, SECONDARY, n_runs)
        res["primary_after_secondary"] = _predict(F, rows, PRIMARY, n_runs)
    return res


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--child":
        mode, n_rows, n_runs = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
        print(json.dumps(child(mode, n_rows, n_runs)))
        return 0
    n_rows = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    n_runs = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    got = {}
    for mode in ("registered", "unregistered"):
        p = subprocess.run([sys.executable, __file__, "--child", mode, str(n_rows), str(n_runs)],
                           capture_output=True, text=True, timeout=3000)
        if p.returncode != 0:
            print(p.stderr[-2000:])
            return 1
        got[mode] = json.loads(p.stdout.strip().splitlines()[-1])
    reg, unreg = got["registered"], got["unregistered"]
    order_same = reg["primary"] == reg["primary_after_secondary"]
    hook_same = reg["primary"] == unreg["primary"]
    diff_rows = sum(1 for a, b in zip(reg["primary"], unreg["primary"]) if a != b)
    print(f"hook DA_* khi dang ky: {reg['hook_da_keys']}")
    print(f"PRIMARY truoc/sau SECONDARY giong nhau: {order_same}")
    print(f"PRIMARY co hook DA_* so voi khong hook: giong nhau={hook_same}, dong khac={diff_rows}/{n_rows}")
    report = {"n_rows": n_rows, "n_runs": n_runs, "order_same": order_same,
              "hook_registration_changes_primary": not hook_same, "rows_differing": diff_rows,
              "registered": reg, "unregistered": unreg}
    out = ROOT / "results/fixed/combat/order_check_items.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"ghi {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
