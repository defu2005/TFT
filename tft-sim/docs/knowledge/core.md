# Kien thuc loi choi TFT: phan on dinh (core)

Trang thai nguon: `[official]` = trang Riot da mo; `[summary]` = chi co tom tat tim kiem tu bai bao thu cap, chua mo trang chinh thuc; `[conflict]` = cac nguon khac nhau; `[pending]` = chua tim duoc.

| Muc | Gia tri | Nguon | Trang thai |
|---|---|---|---|
| Cau truc vong (choi, chuan bi, combat) | co ban giong nhau qua cac set | TFT_GOAT `env/tft_env.py` | [pending] doi chieu voi Riot |
| Lai suat | 1 vang / 10 vang, toi da 5 | TFT_GOAT `env/economy.py` (ghi xac minh 17.4) | [summary] |
| Chi phi roll 2, mua XP 4 | | TFT_GOAT `env/economy.py` | [summary] |
| Bang XP level 7 -> 10 | 56/80/100 (repo) vs 48/72/84 (tft.ninja) | TFT_GOAT `economy.py` ghi chu | [conflict] |
| Danh sach shop odds theo level | khop giua repo va bai bao cho L1-L6, L10-L11 | TFT_GOAT `data/odds.py` | [summary] |
| Hieu ung mua tuong (star-up 3 ban = len sao) | | TFT_GOAT `env/actions.py` | [pending] |
| Trang bi: ghep 2 thanh phan thanh vat pham | can cong thuc hop le | TFT_GOAT `env/items.py` | [conflict] voi noi dung tong hop: nhieu cap khong co cong thuc (xem README) |

Ghi chu: moi con so cua core chay theo patch. Khong coi day la hang so co dinh.
