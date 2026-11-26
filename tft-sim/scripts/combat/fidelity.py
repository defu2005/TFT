"""Doi chieu do trung thuc: xac suat engine du doan vs ket qua that (muc 11.7, khoa 2026-11-25).
Usage: python fidelity.py records.jsonl[.gz] [n_seeds=20] [seed0=0]
Quy tac (co dinh, khong doi sau khi co du lieu):
  - Cham ban ghi label 'real', result.winner khac null, set 18 (muc 11.7). Ban ghi label khac 'real' lam dung ca file.
  - Moi ban ghi duoc kiem trong try: exception nao cung thanh ly do bo qua (exception:<loai>), khong lam dung file.
  - Ban ghi hong bi BO QUA va dem theo ly do (skipped): json hong, schema, set khong ho tro, items null,
    vi tri, tuong la, winner null, dryrun-*.
  - Ten item khong co trong noi dung duoc dem (unknown_items); ban ghi van duoc cham.
  - Game = phan truoc ':' cua source. Nhieu fight cung game duoc gom cum khi bootstrap.
  - Hai cau hinh: PRIMARY (ability generic, items, augments, traits, khong emblem) va SECONDARY (them emblem).
  - Moc: 50% va quy tac suc manh (tong gia * 3^(sao-1), ben cao hon thang; hoa = 0,5 diem).
  - Diem cua mot fight: 1 neu dung phia, 0 neu sai, 0,5 neu p = 0,5 hoac hoa theo quy tac suc manh.
  - CI95: bootstrap theo game, 2000 lan. Duoi MIN_GAMES game thi bao 'inconclusive'.
"""
import gzip, json, sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import fight as F  # noqa: E402
from fight import predict_win, set_content  # noqa: E402
from tft_sim.item_alias import build_set18_records  # noqa: E402
from tft_sim.real_content import build_real  # noqa: E402

set_content(17, build_real('TFTSet17'))
_C18 = build_set18_records()[0]
set_content(18, _C18)  # Set 18 dung noi dung da alias (xem combat-public-data.md 8b)

SUPPORTED_SETS = (18,)  # muc 11.7 chi ap dung cho Set 18
MIN_GAMES = 30
BOOT = 2000
PRIMARY = dict(ability="generic", items=True, augments=True, traits=True, emblems=False, traits_table=False, item_alias=False)
SECONDARY = dict(PRIMARY, emblems=True, traits_table=True, item_alias=True)  # muc 11.9: emblem + bang trait; 11.16: alias item


def strength(side: dict, content) -> float:
    tot = 0.0
    for u in side["units"]:
        ch = content.champions.get(u["api"])
        cost = float(ch.cost) if ch else 0.0
        tot += cost * 3 ** (int(u["star"]) - 1)
    return tot


def rule_credit(a_strength: float, b_strength: float, y: float) -> float:
    """Diem cua quy tac suc manh tren mot fight: 1 dung, 0 sai, 0,5 neu hoa (ca hai bang nhau)."""
    if a_strength == b_strength:
        return 0.5
    pick_a = a_strength > b_strength
    return 1.0 if pick_a == (y == 1.0) else 0.0


def credit(p: float, y: float) -> float:
    if p == 0.5:
        return 0.5
    return 1.0 if (p > 0.5) == (y == 1.0) else 0.0


def _validate(r, allow_dryrun=False) -> str | None:
    """Ly do bo qua (None neu hop le). Moi kiem tra nam o day, khong de exception lan ra ngoai."""
    if "source" not in r:
        return "source_thieu"
    src = str(r["source"])
    if src.startswith("dryrun-") and not allow_dryrun:
        return "dryrun"
    if ":" not in src or not src.split(":")[0]:
        return "source_sin_game"  # game = phan truoc ':'; thieu thi moi fight thanh mot cum, CI sai
    if r.get("set") not in SUPPORTED_SETS:
        return f"set_khong_ho_tro:{r.get('set')}"  # set 17 va 19 nam ngoai muc 11.7
    try:
        F.check_record(r)
    except (ValueError, KeyError, TypeError) as e:
        return f"schema:{e}"[:90]
    if r.get("result", {}).get("winner") is None:
        return "winner_null"
    for side in ("a", "b"):
        if not r[side].get("units"):
            return f"board_trong:{side}"  # predict_win tra p_a=1.0 cho ban trong: ket qua gia
    for side in ("a", "b"):
        if r[side].get("augments") is None and "augments" in r[side]:
            return "augments_null"
        for u in r[side]["units"]:
            if u.get("items") is None and "items" in u:
                return "items_null"
            if not isinstance(u.get("star"), int) or isinstance(u.get("star"), bool):
                return "star_khong_hop_le"
            if u["api"] not in F._CONTENT[r["set"]].champions:
                return f"tuong_la:{u['api']}"
    return None


def read_real(path, allow_dryrun=False):
    """Doc tung dong. Tra ve (ban ghi cham duoc, Counter ly do bo qua, Counter item la)."""
    good, skipped, unk = [], Counter(), Counter()
    p = Path(path)
    text = (gzip.open(p, "rt", encoding="utf-8").read() if p.suffix == ".gz" else p.read_text(encoding="utf-8"))
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            skipped["json_hong"] += 1
            continue
        if not isinstance(r, dict):
            skipped["khong_phai_object"] += 1
            continue
        if r.get("label") != "real":
            raise SystemExit(f"tu choi: co ban ghi label={r.get('label')} trong file do luong")
        try:
            reason = _validate(r, allow_dryrun)
        except Exception as e:  # bat moi loi con lai theo tung ban ghi
            reason = f"exception:{type(e).__name__}"
        if reason:
            skipped[reason] += 1
            continue
        for side in ("a", "b"):
            for u in r[side]["units"]:
                for it in (u.get("items") or []):
                    if it not in F._CONTENT[r["set"]].items:
                        unk[it] += 1
        good.append(r)
    return good, skipped, unk


def _game(r) -> str:
    return str(r["source"]).split(":")[0]


def _cfg_p(rec, cfg, n, seed0):
    return predict_win(rec, n, cfg["ability"], cfg["items"], seed0, cfg["augments"], cfg["traits"],
                       False, cfg["emblems"], cfg.get("traits_table", False),
                       cfg.get("item_alias", False))["p_a"]


def _boot_mean_diff(games, per_fight_diff, rng):
    """Bootstrap theo game: trung binh chenh lech tren fight, gom theo game."""
    G = sorted(set(games))
    idx = {g: [] for g in G}
    for i, g in enumerate(games):
        idx[g].append(i)
    vals = []
    for _ in range(BOOT):
        pick = rng.choice(len(G), len(G), replace=True)
        ii = np.concatenate([idx[G[k]] for k in pick])
        vals.append(per_fight_diff[ii].mean())
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def _commit(path) -> str:
    import subprocess
    try:
        return subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def _engine_dir() -> Path:
    """Thu muc goc cua engine tu vi tri module that su duoc import (khong hard-code)."""
    import tft_goat
    # .../tft_goat/src/tft_goat/__init__.py -> thu muc goc la parents[2]
    return Path(tft_goat.__file__).resolve().parents[2]


def score(path, n=800, seed0=0, allow_dryrun=False):  # n=800: 11.28 (dang ky truoc; n=400 khong dat tren ban co item)
    good, skipped, unk = read_real(path, allow_dryrun)
    if not good:
        return {"skipped": dict(skipped), "unknown_items": dict(unk), "n_min_games": MIN_GAMES,
                "fights": 0, "games": 0, "inconclusive": True, "note": "chua co ban ghi real co ket qua"}
    rows = []
    for r in good:
        try:
            p1 = _cfg_p(r, PRIMARY, n, seed0)
            p2 = _cfg_p(r, SECONDARY, n, seed0)
        except Exception as e:
            skipped[f"predict:{type(e).__name__}:{str(e)[:50]}"] += 1
            continue
        y = 1.0 if r["result"]["winner"] == 0 else 0.0
        rule = rule_credit(strength(r["a"], F._CONTENT[r["set"]]), strength(r["b"], F._CONTENT[r["set"]]), y)
        rows.append((_game(r), y, p1, p2, rule, credit(p1, y), credit(p2, y)))
    base = {"skipped": dict(skipped), "unknown_items": dict(unk), "n_min_games": MIN_GAMES}
    if not rows:
        return dict(base, fights=0, games=0, note="moi ban ghi real deu bi bo")
    games = [x[0] for x in rows]
    y = np.array([x[1] for x in rows]); p1 = np.array([x[2] for x in rows]); p2 = np.array([x[3] for x in rows])
    rule = np.array([x[4] for x in rows]); c1 = np.array([x[5] for x in rows]); c2 = np.array([x[6] for x in rows])
    rng = np.random.default_rng(0)
    d_rule = c1 - rule
    d_sec = c2 - c1
    lo, hi = _boot_mean_diff(games, d_rule, rng)
    lo2, hi2 = _boot_mean_diff(games, d_sec, rng)
    lo3, hi3 = _boot_mean_diff(games, c2 - rule, rng)  # SECONDARY - rule (them 2026-11-25, sau sua AP/Attuned/Spellweaver)
    G = len(set(games))
    inconclusive = G < MIN_GAMES
    def verdict(lo_, hi_):
        if inconclusive:
            return "inconclusive"
        return "PASS" if lo_ > 0 else ("FAIL" if hi_ < 0 else "chua_ket_luan")
    from collections import Counter
    return dict(base, fights=len(rows), games=G, inconclusive=inconclusive,
                per_patch=dict(Counter(str(r.get("patch")) for r in good)),  # ghi nhan, KHONG loai ban ghi
                n_seeds=n, seed0=seed0, repo_commit=_commit(Path(__file__).resolve().parents[2]),
                engine_commit=_commit(_engine_dir()),
                share_side_a_won=round(float(y.mean()), 4),
                primary={"config": PRIMARY, "accuracy_credit": round(float(c1.mean()), 4),
                         "brier": round(float(np.mean((p1 - y) ** 2)), 4)},
                secondary={"config": SECONDARY, "accuracy_credit": round(float(c2.mean()), 4),
                           "brier": round(float(np.mean((p2 - y) ** 2)), 4)},
                strength_rule={"accuracy_credit": round(float(rule.mean()), 4)},
                primary_minus_rule={"diff": round(float(d_rule.mean()), 4), "ci95": [round(lo, 4), round(hi, 4)],
                                    "verdict": verdict(lo, hi)},
                secondary_minus_rule={"diff": round(float((c2 - rule).mean()), 4), "ci95": [round(lo3, 4), round(hi3, 4)],
                                      "verdict": verdict(lo3, hi3)},
                secondary_minus_primary={"diff": round(float(d_sec.mean()), 4), "ci95": [round(lo2, 4), round(hi2, 4)],
                                         "verdict": verdict(lo2, hi2)},
                note="PASS = CI95 cua (chinh - quy tac suc manh) nam tren 0 (muc 11.7)")


if __name__ == "__main__":
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 800
    s0 = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    print(json.dumps(score(sys.argv[1], n, s0), ensure_ascii=False, indent=1))
