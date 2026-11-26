# 3. Lộ trình

## Vị trí trong sản phẩm lớn (TFT Coach)

Lộ trình sản phẩm có 6 giai đoạn. Nguồn: `docs/roadmap.md` trên nhánh `origin/claude/nifty-lovelace-252i30` (cập nhật 2026-11-23). **Bộ tài liệu này chưa sao chép toàn văn lộ trình**; nội dung Phase 1–3 cần đọc trực tiếp từ nguồn đó.

| Phase | Nội dung (tóm tắt) | Trạng thái nhánh sim |
|---|---|---|
| 1–3 | Xem nguồn lộ trình. | Ngoài phạm vi nhánh sim. |
| 4 | Harness đánh giá trên dữ liệu thật. | **Bị chặn**: chưa có trận thật đủ điều kiện. |
| 5 | Nghiên cứu chính sách và dự đoán combat (tft-sim). | **Đang làm** ở mức mô phỏng. |
| 6 | Triển khai sản phẩm. | Chưa bắt đầu. |

## Quy tắc cổng

- **Đường găng:** dữ liệu live (đủ trạng thái: vàng, cấp độ, HP, giai đoạn, cửa hàng). Chưa chốt nguồn.
- **tft-sim không vào engine sản phẩm** trước khi qua harness Phase 4 trên dữ liệu thật.
- Số liệu mô phỏng không được dùng làm bằng chứng cho sản phẩm.

## Cái gì đang chặn (theo thứ tự ảnh hưởng)

1. Dữ liệu thật đủ điều kiện: cổng VOD đang đỏ, chưa slot nào đạt.
2. Nguồn live chưa chốt (ai cung cấp, định dạng gì).
3. Quy ước `_GENERIC_ITEM` chưa được tác giả engine xác nhận. Ảnh hưởng mọi số combat có item.
4. Item và augment Set 18 chưa mô hình hóa đủ (617/731 item không có tác động dưới PRIMARY).

## Việc có thể làm khi chưa có dữ liệu

Danh sách do advisor đề xuất và nhánh đã làm (mục 11.29 của `model-plan.md`): kiểm công cụ, đăng ký cấu hình, phân loại item, đo chi phí, tài liệu. Việc nào cần trận thật thì để lại, không làm giả.

## Cái chưa có ngày

Không có mốc ngày nào được cam kết trong bộ tài liệu này. Mỗi mốc cần nguồn dữ liệu và quyết định của chủ sản phẩm.
