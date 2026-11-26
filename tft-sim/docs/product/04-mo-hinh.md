# 4. Mô hình

Bộ tài liệu tách hai loại thành phần, vì người đọc hay nhầm:

| Loại | Làm gì | Trạng thái |
|---|---|---|
| **Bộ dự đoán combat** | Cho hai bàn, ước lượng xác suất thắng bằng mô phỏng `tft_goat`. Không học từ dữ liệu. | Đang dùng PRIMARY, n=800. Chưa đối chiếu trận thật. |
| **Mô hình học chính sách** | Học chọn hành động (mua, làm mới, đặt tướng...) bằng cách bắt chước giáo viên scripted trong mô phỏng. | Có kết quả trên mô phỏng Set 17; chưa đưa ra ngoài. |

## Mô hình học chính sách: đã làm gì

- **Giáo viên:** v4, dựa trên `EngineResolver` (Set 17).
- **Thí nghiệm mask** (mục 10.6): thử che các đặc trưng để xem mô hình phụ thuộc vào đâu.
- **Giải đấu** (mục 10.8, 10.9): các mô hình đấu với nhau trong mô phỏng.
- **Dropout** (mục 10.10).

## Kết quả, nói đúng mức

- **Clone đầy đủ ngang giáo viên** trên mô phỏng Set 17. Đây là kết quả chính.
- **Chưa có mô hình nào vượt giáo viên có ý nghĩa thống kê.** Hai biến thể c và a kém hơn v4.
- **+0,015 không phải kết quả mô hình.** Đây là kiểm công bằng của harness: chênh lệch v4 − v4_null. Giải đấu v2 chỉ dùng để kiểm harness. Một số bản tóm tắt cũ gọi +0,015 là "mô hình vượt giáo viên". Đó là sai, đã đính chính.

Số chi tiết xem `model-plan.md` mục 10.6–10.10.

## Dự đoán thắng/thua cho Set 18

- Chưa có mô hình học nào cho Set 18.
- Hiện chỉ có bộ dự đoán combat mô phỏng (PRIMARY).
- Nếu sau này có dữ liệu thật, bước đúng là đo bộ dự đoán combat trên trận thật (harness Phase 4) trước khi nghĩ đến học.

## Lý do tách hai loại

Mô hình học chỉ có ý nghĩa khi đánh giá trên dữ liệu không do chính nó sinh ra. Mô phỏng do engine sinh ra, nên nó chỉ kiểm được tính nhất quán, không kiểm được độ đúng với game thật.

## Chưa có

- Mô hình hóa augment/item Set 18 trong học chính sách.
- Mô hình cho vị trí (positioning).
- Bất kỳ mô hình nào được huấn luyện trên dữ liệu thật.
