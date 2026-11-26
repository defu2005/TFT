# 4. Mô hình

Bộ tài liệu tách hai loại thành phần:

| Loại | Làm gì | Chấm bằng | Trạng thái |
|---|---|---|---|
| **Bộ dự đoán combat** | Cho hai bàn, ước lượng xác suất thắng bằng mô phỏng `tft_goat`. Không học. | Trận thật (`fidelity.score`) | PRIMARY, n=800. **Chưa có trận thật đạt.** |
| **Mô hình học chính sách** | Học chọn hành động bằng cách bắt chước teacher v4 trong mô phỏng Set 17. | Mô phỏng (giải đấu) | Có kết quả trên Set 17 sim. Chưa có trên Set 18. |

## Teacher và điều kiện

- **Teacher v4:** scripted, dùng `EngineResolver`, `TFTSet17`. Đọc được HUD, bench, board.
- **Điều kiện mask** (`scripts/mask_exp.py`, 185 chiều):
  - a: gold, level, xp, streak, slot filled, cost (14 chiều).
  - b: a + HP, round (16 chiều).
  - c: b + bench/board (94 chiều) + slot owned, traits (120 chiều).
  - full: toàn bộ.
  - Luôn ẩn: opponents, gods, augment tier/flags, scalars 6–9.
- Mask nghĩa là **ẩn đầu vào** khỏi mô hình để đo đầu vào đó quan trọng đến đâu. Không phải kỹ thuật che ảnh.

## Kết quả (mô phỏng Set 17, chi tiết ở `model-plan.md` 10.6–10.10)

**Thí nghiệm mask (10.6, 2026-11-25):** clone đi từ +2,18 xuống +0,50 so với teacher v4 khi thêm bàn và bàn chờ (c). Điều kiện c vẫn ẩn augment, nên +0,50 còn lẫn thiếu augment. Hậu kỳ (không đăng ký): full ≈ teacher, −0,051 [−0,157; +0,057]. full − c = −0,548 [−0,686; −0,411], tức phần +0,50 của c là do nhóm ẩn. HP và round: b − a = +0,13, dưới ngưỡng 0,2, không phân biệt được.

**Giải đấu v2 (10.9, 4000 lobby):** đơn vị là **placement** (thấp hơn là tốt hơn). Bảng so với v4, dương = tệ hơn:

| Policy | Chênh với v4 | CI95 |
|---|---|---|
| v4_null (đối chứng harness) | 0,015 (v4 − v4_null) | [−0,080; +0,110] |
| mask_full | +0,045 | |
| mask_c | +0,45 | |
| v3 | +0,65 | |
| mask_a | +2,07 | |
| scripted | +2,26 | |
| valuemax | −1,05 | |

Tiêu chí harness (v4 − v4_null có CI chứa 0) **đạt**. Số +0,015 là **kiểm công bằng của harness**, không phải "mô hình vượt teacher". Các bản tóm tắt cũ gọi nó như vậy là sai, đã đính chính.

**Dropout (10.10, 4000 lobby):** một mô hình thay cho ba mô hình mask riêng. Đạt tiêu chí đã đăng ký: drop@full − mask_full = +0,030 [−0,074; +0,125]; drop@c − mask_c = +0,002 [−0,101; +0,097]; drop@a − mask_a = −0,048 [−0,152; +0,054]. Giới hạn: Set 17, bot teacher v4.

**Giải đấu v1 (10.8):** bị thay bởi v2 vì chọn policy ngẫu nhiên có thể trùng, làm lệch cân bằng.

## Dự đoán thắng/thua cho Set 18

- Chưa có mô hình học nào cho Set 18.
- Chưa có kết quả nào đối chiếu trận thật.
- Bước đúng: đo bộ dự đoán combat trên bản ghi trận thật trước khi nghĩ đến học.

## Khoảng cách để áp dụng sang Set 18

- **Ability Set 17:** 69 hàm viết tay (`tft_goat/engine/abilities_set17`, 6 file).
- **Ability Set 18:** chưa có logic. Trên Set 18, generic ability rơi về `ad*2` cho 88/91 tướng, nên đây là khoảng cách lớn nhất.
- **Vị trí:** không có trong dữ liệu HUD hiện tại.
- **Item:** 617/731 không có tác động dưới PRIMARY (xem [5](05-engine-set18.md)).

## Vì sao tách

Mô hình học chỉ có ý nghĩa khi đánh giá trên dữ liệu không do chính nó sinh ra. Teacher và mô phỏng đều là engine, nên kết quả chỉ kiểm được tính nhất quán bên trong, không kiểm được độ đúng với game thật.
