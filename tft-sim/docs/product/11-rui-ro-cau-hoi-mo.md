# 11. Rủi ro và câu hỏi mở

## Rủi ro kỹ thuật

| # | Rủi ro | Mức | Đang làm gì |
|---|---|---|---|
| R1 | `_GENERIC_ITEM`: chú thích và đường combat mâu thuẫn. Chọn hướng (b) sẽ đổi mọi số có item. | Cao | Đã gửi câu hỏi; chờ tác giả |
| R2 | 617/731 item không có tác động dưới PRIMARY | Cao | Đã phân loại; chưa mô hình hóa |
| R3 | Ability generic: không có kỹ năng riêng từng tướng. Set 18 rơi về `ad*2` cho 88/91 tướng. | Cao | Chưa làm |
| R4 | Vị trí không có trong dữ liệu và engine (`pos=(0,0)`) | Cao | Chưa làm |
| R5 | Augment không đổi xác suất (0/252): có thể là lỗi mô hình, không phải tác động thật | Trung bình | Chưa điều tra sâu |
| R6 | Số patch 18.7 chưa được kiểm chứng từ nguồn chính thức. Tên file CDragon là "18.7" nhưng snapshot ngày 2026-11-23. | Trung bình | Roadmap yêu cầu kiểm chứng trước khi chọn |
| R7 | Mô phỏng có thể "học" đúng cái engine làm, không phải cái game làm | Cao | Cần dữ liệu thật |

## Rủi ro phương pháp

| # | Rủi ro | Mức | Ghi chú |
|---|---|---|---|
| M1 | n=800 chọn sau khi n=400 không đạt: đây là lần thử thứ hai trên cùng dữ liệu | Trung bình | Phải nói rõ khi báo cáo ([7](07-danh-gia.md)) |
| M2 | Chưa có kết quả nào đối chiếu trận thật | Rất cao | Mọi dự đoán chỉ đúng với engine |
| M3 | +0,015 dễ bị đọc là kết quả mô hình | Trung bình | Đã đính chính trong tài liệu |
| M4 | Mô hình học mới chỉ đo trên Set 17 với bot teacher v4 | Cao | Chưa đo Set 18 |

## Rủi ro dữ liệu và pháp lý

| # | Rủi ro | Mức | Ghi chú |
|---|---|---|---|
| D1 | Cổng VOD đỏ; không slot nào đạt | Cao | Cần sửa nguồn hoặc thu lại |
| D2 | Số liệu blitz.gg đã commit. Điều khoản: chỉ cá nhân phi thương mại; robots.txt chặn ClaudeBot/GPTBot. Người dùng đã cho phép theo ghi chú nghiên cứu. | Cao | Ghi nhận cho phép; cần xác nhận lại |
| D3 | Dữ liệu VOD dùng cho huấn luyện; rủi ro pháp lý chưa kiểm | Cao | Người dùng đã nhận thức và quyết định |
| D4 | Đường RAM: roadmap có hai câu trái nhau về việc đã đóng hay đã bỏ việc đóng; chính sách Riot (hiệu lực 6/10/2026) chặn đọc bộ nhớ với app bên thứ ba | Cao | Cần người dùng xác nhận trạng thái |
| D5 | Nguồn live chưa chốt; không có shop/vàng từ log client | Cao | Đường găng sản phẩm |
| D6 | Mục tiêu "100% trong 250 ms" cho đường live chưa được xác nhận | Trung bình | Người dùng xác nhận |

## Câu hỏi cho người dùng

1. **Đường RAM:** đã đóng hay đã bỏ việc đóng? (Xem [3](03-lo-trinh.md).)
2. **Lô VOD 2026-11-25:** xác nhận lô này là thu `fight-v1` do người dùng yêu cầu, tách khỏi chiến dịch OCR đã dừng.
3. **VOD:** dùng lại sau khi sửa cổng, hay bỏ?
4. **`_GENERIC_ITEM`:** chấp nhận bàn giao và đóng mục, hay mở tiếp?
5. **Nguồn live:** chọn hướng nào trong ba hướng? Ai cung cấp?
6. **Khóa Riot API:** cho phép cấp để làm Phase 2 Set 18 không? Nếu không, Phase 0, 1, 3 vẫn chạy.
7. **Mục tiêu 250 ms và 100%:** có giữ không?

Ghi chú (không chặn): số liệu Blitz đã commit theo ghi nhận người dùng cho phép (`combat-public-data.md` 10c). Điều khoản phi thương mại vẫn áp dụng.

## Câu hỏi cho tác giả engine

Xem `docs/agents/requests/20261126-engine-generic-item-convention.md`: quy ước `_GENERIC_ITEM` (a hay b); `composition`, `DA_Component_*`, `DA_Artifact*`, `*Radiant` có trong phạm vi không; hook khóa `TFT_Item_*` có chủ đích không; `DA_*` có identity qua alias không.

## Câu hỏi nghiên cứu

- Cần cấu hình mới nào để mô hình hóa item và augment Set 18?
- Xác minh patch thật của snapshot CDragon từ nguồn chính thức.
- Logic ability Set 18: thứ tự ưu tiên khi có số Blitz.
