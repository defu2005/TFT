# 11. Rủi ro và câu hỏi mở

## Rủi ro kỹ thuật

| # | Rủi ro | Mức | Hậu quả | Đang làm gì |
|---|---|---|---|---|
| R1 | Quy ước `_GENERIC_ITEM` mâu thuẫn giữa chú thích và đường combat | Cao | Mọi số combat có item có thể đổi nếu chọn hướng (b) | Đã gửi câu hỏi, chờ trả lời |
| R2 | 617/731 item không có tác động dưới PRIMARY | Cao | Dự đoán có item không phản ánh đúng item thật | Phân loại xong; chưa mô hình hóa |
| R3 | Augment không tạo khác biệt đo được (0/252) | Trung bình | Có thể là lỗi mô hình, không phải tác động thật | Chưa điều tra sâu |
| R4 | Ability generic, không có kỹ năng riêng từng tướng | Cao | Mô phỏng sai ở các tướng có kỹ năng mạnh | Chưa làm |
| R5 | Số patch 18.7 chưa xác minh (tên file CDragon có thể sai) | Trung bình | Nội dung có thể lệch patch thật | Chưa xác minh |
| R6 | Đường RAM đã bỏ; dữ liệu nguồn chưa có văn bản cho phép | Cao | Dữ liệu có thể không dùng được về mặt pháp lý | Người dùng đã nhận thức |

## Rủi ro về phương pháp

| # | Rủi ro | Mức | Ghi chú |
|---|---|---|---|
| M1 | n=800 được chọn sau khi n=400 không đạt (lần thử thứ hai) | Trung bình | Phải ghi rõ khi báo cáo (xem [07](07-danh-gia.md)) |
| M2 | Chưa có kết quả nào đối chiếu trận thật | Rất cao | Mọi dự đoán hiện chỉ đúng với engine, không chắc đúng với game |
| M3 | Số "+0,015" dễ bị hiểu nhầm là kết quả mô hình | Trung bình | Đã đính chính trong các tài liệu |
| M4 | Mô hình học có thể "học" đúng cái engine làm, không phải cái game làm | Cao | Đây là lý do cần dữ liệu thật |

## Rủi ro về dữ liệu

| # | Rủi ro | Ghi chú |
|---|---|---|
| D1 | Cổng VOD đỏ; không có bản ghi đạt | Cần sửa nguồn hoặc thu lại |
| D2 | `data/blitz_set18_numbers.json` đã commit trong repo, mâu thuẫn quy tắc "không lưu nội dung blitz" | **Cần người dùng quyết** (xem dưới) |
| D3 | Nguồn live chưa chốt | Đường găng của sản phẩm |

## Câu hỏi cần người dùng trả lời

1. **Tệp blitz đã commit:** giữ, xóa, hay chuyển sang dạng khác? Agent chưa xóa vì đó là thao tác không đảo ngược và chưa có chỉ đạo.
2. **Dữ liệu VOD:** dùng lại sau khi sửa cổng, hay bỏ hẳn?
3. **Bàn giao `_GENERIC_ITEM`:** xác nhận đóng mục (chấp nhận bàn giao) hay mở tiếp?
4. **Nguồn live:** ai cung cấp, định dạng gì?

## Câu hỏi cần tác giả engine trả lời

Xem `docs/agents/requests/20261126-engine-generic-item-convention.md`: quy ước `_GENERIC_ITEM`, phạm vi hiệu ứng cho `DA_*`, và thiết kế hook.

## Câu hỏi cần advisor hoặc nghiên cứu thêm

- Có cần cấu hình mới để mô hình hóa item và augment Set 18 không?
- Cách xác minh patch thật của snapshot CDragon.
