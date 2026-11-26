"""Kiem thu usable.py tren fixture (khong dung du lieu VOD).

Chay:  PYTHONPATH=<goat>/src:<sim>/src python3 scripts/combat/selftest_usable.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "src"))

import fight as F  # noqa: E402
import usable as U  # noqa: E402
from tft_sim.real_content import build_real  # noqa: E402

F.set_content(18, build_real("TFTSet18"))
CH = F._CONTENT[18].champions
API = next(iter(CH))  # mot tuong that trong noi dung Set 18


def unit(api=API, star=1):
    return {"api": api, "star": star, "items": [], "pos": None, "frames": ["frames/f.png"]}


def fight(a_units, b_units, a_lv=5, b_lv=5, winner=0, key="g|3-2|Alpha|Beta", frames=None):
    f = {"schema": "fight-v1", "set": 18, "label": "real", "source": "g-1:3-2", "fight_key": key,
         "a": {"level": a_lv, "augments": [], "units": a_units},
         "b": {"level": b_lv, "augments": [], "units": b_units},
         "result": {"winner": winner}}
    if frames is not None:
        f["a"]["units"][0]["frames"] = frames
    return f


FULL5 = [unit() for _ in range(5)]
_noaug = fight(FULL5, FULL5)
del _noaug["a"]["augments"]
CASES = [
    ("ban_day_du_pass", fight(FULL5, FULL5), None),
    ("b_mot_unit_lv5_bi_loai", fight(FULL5, [unit()]), "board_b_thieu"),
    ("level_null_bi_loai", fight(FULL5, FULL5, a_lv=None), "level_khong_ro"),
    ("level_bool_bi_loai", fight(FULL5, FULL5, b_lv=True), "level_khong_ro"),
    ("vuot_level_van_pass", fight(FULL5 + [unit()], FULL5), None),  # ban vuot level la hop le (xem usable.py)
    ("tuong_la_trong_ban_day_du_bi_loai", fight([unit("KHONG_CO_TUONG")] + FULL5[1:], FULL5), "tuong_la"),
    ("star_khong_hop_le_bi_loai", fight([unit(star="2")] + FULL5[1:], FULL5), "star_khong_hop_le"),
    ("items_null_bi_loai", fight([dict(unit(), items=None)] + FULL5[1:], FULL5), "items_null"),
    ("unit_khong_frames_bi_loai", fight([dict(unit(), frames=[])] + FULL5[1:], FULL5), "unit_khong_khung_hinh"),
    ("items_thieu_key_bi_loai", fight([{k: v for k, v in unit().items() if k != "items"}] + FULL5[1:], FULL5), "items_thieu"),
    ("augments_thieu_key_bi_loai", _noaug, "augments_thieu"),
    ("winner_null_bi_loai", fight(FULL5, FULL5, winner=None), "winner_null"),
    ("placeholder_bi_loai", fight(FULL5, FULL5, key="g|3-2|unk_1|Beta"), "nombre_placeholder"),
    ("api_la_bi_loai", fight([unit("KHONG_CO_TUONG")] * 5, FULL5), "board_a_khong_phan_giai"),
]


def main() -> int:
    ok = True
    for name, f, want in CASES:
        got = U.reason(f, CH)
        good = got == want
        ok &= good
        print(f"{'PASS' if good else 'FAIL'} {name}: ly do={got} (ky vong {want})")
    # khung hinh thieu phai bi loai khi co vdir
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        f = fight(FULL5, FULL5, frames=["khong_co.png"])
        got = U.reason(f, CH, Path(d))
        good = got == "frame_thieu"
        ok &= good
        print(f"{'PASS' if good else 'FAIL'} frame_thieu: ly do={got}")
    print("SELFTEST USABLE", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
