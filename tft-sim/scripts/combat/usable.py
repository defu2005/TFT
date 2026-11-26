"""Bo loc fight DUNG DUOC de cham diem (dung chung cho scoreable_yield va buoc cham diem).

Quy tac TIEN DANG KY TRUOC (khong chinh theo ket qua; khong co so duoc tinh):
Mot fight dung duoc khi du tat ca dieu kien sau, kiem theo ly do dau tien vi pham:
  1. winner_null            winner la 0 hoac 1;
  2. nombre_placeholder     ten hai nguoi choi trong fight_key la ten that (khong unk_/unknown_);
  3. level_khong_ro         a.level va b.level la so nguyen (khong null, khong bool);
  4. board_<side>_khong_phan_giai   co it nhat mot unit co api da phan giai duoc trong noi dung Set 18;
  5. board_<side>_thieu     so unit >= level, ca hai ben (ban co day du theo level);
  6. board_<side>_vuot_level    so unit > level (khong the xay ra trong TFT: that la loi du lieu);
  7. frame_thieu            moi khung hinh duoc tham chieu deu ton tai trong thu muc VOD.
Mot van (game) dung duoc khi co it nhat mot fight dung duoc.

Ghi chu: dieu kien 5 loai bo ca ban co that nhung it unit hon level. Day la chu y co chu dich
(uu tien khong cham ban co sai), khong phai bang chung rang ban do khong hop le.
"""
import re

PH = re.compile(r"(unknown_|unk_)", re.I)


def _is_int(x) -> bool:
    return isinstance(x, int) and not isinstance(x, bool)


def reason(f: dict, champs, vdir=None) -> str | None:
    """Tra ve ly do loai (chuoi) hoac None neu fight dung duoc."""
    w = (f.get("result") or {}).get("winner")
    if w not in (0, 1):
        return "winner_null"
    pair = str(f.get("fight_key", "")).split("|")[-2:]
    if PH.search("|".join(pair)):
        return "nombre_placeholder"
    for side in ("a", "b"):
        lv = (f.get(side) or {}).get("level")
        if not _is_int(lv):
            return "level_khong_ro"
    for side in ("a", "b"):
        units = (f.get(side) or {}).get("units", []) or []
        if not any(u.get("api") in champs for u in units):
            return f"board_{side}_khong_phan_giai"
    for side in ("a", "b"):
        units = (f.get(side) or {}).get("units", []) or []
        lv = f[side]["level"]
        if len(units) < lv:
            return f"board_{side}_thieu"
        if len(units) > lv:
            return f"board_{side}_vuot_level"
    if vdir is not None:
        for side in ("a", "b"):
            for u in (f.get(side) or {}).get("units", []) or []:
                for fr in u.get("frames", []) or []:
                    if not (vdir / fr).exists():
                        return "frame_thieu"
    return None


def game_of(f: dict) -> str:
    return str(f.get("source", "")).split(":")[0]
