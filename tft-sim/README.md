# tft-sim

Harness danh gia policy (env-agnostic) va pipeline BC cho bai toan TFT. Trang thai: **giai doan 0**.

Ghi chu: toy env trong `src/tft_sim/env.py` chi la test double. Ket qua tren no khong noi gi ve suc manh bot TFT.

## Bang do pham vi (scoreboard)

Moi hang la mot loai quyet dinh. "Chua" nghia la chua co.

| Quyet dinh | Trong sim | Co teacher | Da hoc (BC) | Da danh gia tren TFT |
|---|---|---|---|---|
| Mua tuong tu shop | chua | chua | chua | chua |
| Roll | chua | chua | chua | chua |
| Mua XP / len level | chua | chua | chua | chua |
| Ban tuong | chua | chua | chua | chua |
| Dat tuong len board / ban | chua | chua | chua | chua |
| Trang bi (gan item) | chua | chua | chua | chua |
| Chon augment | chua | chua | chua | chua |
| Chon tuong tu god/vote | chua | chua | chua | chua |
| Dinh vi trong tran (positioning) | **mo** (chua co trong 43 action cua TFT_GOAT) | - | - | - |
| Nhắm muc tieu item | **mo** | - | - | - |

## Trang thai cong viec

- Harness trung lap, test voi dap an da biet tren toy env: viet, chua duoc chay trong phien nay (xem bao cao).
- Adapter TFT_GOAT: `adapter_tftgoat.py`, **chua kiem thu**.
- Gate 0 (chay TFT_GOAT, 4 scripted vs 4 random): **chua qua**. Bi chan boi quyen chay code ben thu ba.
