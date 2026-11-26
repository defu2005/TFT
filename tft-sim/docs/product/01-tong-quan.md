# 1. Tổng quan

## Dự án làm gì

Đây là nhánh nghiên cứu **mô phỏng và dự đoán** trong sản phẩm lớn hơn là **TFT Coach** (trợ giúp quyết định khi chơi Teamfight Tactics). Sản phẩm lớn gồm đọc trạng thái trận từ màn hình (HUD), chạy engine quyết định, và hiển thị gợi ý. Nhánh này lo phần **đánh giá quyết định và dự đoán kết quả combat** bằng mô phỏng, và thử nghiệm học chính sách.

## Để làm gì

Trả lời hai câu hỏi cho từng set mới:
1. Với một trạng thái bàn cờ, bên nào có khả năng thắng combat? (dự đoán thắng/thua)
2. Quyết định nào (mua, làm mới, đặt tướng, trang bị) tốt hơn một quyết định cơ sở? (chính sách)

## Ngoài phạm vi (hiện tại)

- Giao diện người dùng, đọc HUD, OCR: thuộc nhánh `hud`.
- Danh sách tướng và luật chính thức của set đang chạy: thuộc nhánh `engine` (chủ roster Set 18 là `engine`, theo quyết định 2026-11-24).
- Triển khai sản phẩm: Phase 6 của lộ trình sản phẩm, chưa bắt đầu.

## Trạng thái thật (tính đến 2026-11-26)

| Câu hỏi | Trả lời | Nguồn |
|---|---|---|
| Đã đối chiếu dự đoán với trận thật chưa? | **Chưa.** Không có trận nào đủ điều kiện. | `../progress/STATUS.md` |
| Mô hình học có vượt giáo viên (luật viết tay v4) có ý nghĩa thống kê không? | **Chưa.** Clone đầy đủ ngang giáo viên trên mô phỏng Set 17. | [4. Mô hình](04-mo-hinh.md) |
| Engine Set 18 đã mô hình hóa đủ để dự đoán chưa? | **Chưa.** Item, augment, ability Set 18 còn thiếu. | [5. Engine Set 18](05-engine-set18.md) |
| Dữ liệu thật đã dùng được chưa? | **Chưa.** Cổng VOD đang đỏ. | [6. Dữ liệu](06-du-lieu.md) |
| Đường găng của sản phẩm là gì? | Nguồn dữ liệu live đủ trạng thái (vàng, cấp, HP, giai đoạn, shop). Chưa chốt. | [3. Lộ trình](03-lo-trinh.md) |

## Nếu chỉ đọc một thứ

Nhánh sim đã làm được công cụ kiểm tra, kế hoạch và một số thí nghiệm mô phỏng có đăng ký trước. Chưa có bằng chứng nào rằng dự đoán đúng trên trận thật. Muốn có bằng chứng đó, cần dữ liệu thật đủ điều kiện, và sản phẩm cần chốt nguồn live.
