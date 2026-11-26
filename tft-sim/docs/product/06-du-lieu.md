# 6. Dữ liệu

Phần này nói dữ liệu **cần gì**, **đang có gì**, và **cổng chất lượng** ra sao. Chi tiết nguồn thu và cách thu nằm trong `docs/data-needs.md` và `docs/handoff/`.

## Dữ liệu cần (theo nhóm)

| Nhóm | Dùng để làm gì | Trạng thái |
|---|---|---|
| Trạng thái trận từ HUD/live (vàng, cấp, HP, giai đoạn, cửa hàng, bàn cờ hai bên) | Đối chiếu dự đoán với trận thật | **Chưa có.** Nguồn chưa chốt. |
| Nội dung game (tướng, item, trait, augment) | Đầu vào engine | Có snapshot CDragon (91 tướng Set 18). Số patch cần xác minh. |
| Kết quả trận thật (`fight-v1`) | Chấm điểm bộ dự đoán | **Chưa có bản đạt.** |
| Dữ liệu VOD thu từ streamer | Tạm thời thay thế kết quả trận | **Đang đỏ**, không dùng được. |

## Định dạng `fight-v1`

Một bản ghi = một lần đánh nhau tại một round giữa hai bàn, kèm kết quả. Mỗi bàn có danh sách unit với `items`, `item_apis`, `augments`, `frames`, cấp, sao. Thiếu khóa thì bị từ chối (xem `usable.reason`).

Thứ tự kiểm trong `usable.reason`: kết quả thắng rỗng → tên placeholder → cấp không rõ → bàn không phân giải được → bàn thiếu → thiếu augment → tướng lạ → sao không hợp lệ → thiếu item → unit không có khung hình → thiếu frame.

## Hiện trạng VOD

- **1026 ván, 12.488 fight, 336 VOD Twitch** đã được thu.
- **Cổng gộp đỏ:** không slot nào đạt. Nghĩa là không bản ghi nào đủ chất lượng để vào `scoring.jsonl`.
- Lý do cụ thể từng slot nằm trong báo cáo của cổng (`merge_check_vod.py`). Đừng suy đoán lý do.

Trạng thái bàn giao (`HANDOFF_STATUS`): `pending`, `working`, `done`, `blocked`, `stale`. Trạng thái không hợp lệ bị `bad_status` từ chối.

## Quyền và rủi ro pháp lý

- Dữ liệu VOD thu từ video công khai của streamer. Người dùng đã nhận thức rủi ro về quyền và điều khoản dịch vụ.
- Chính sách của Riot về dữ liệu: đường RAM (dữ liệu bộ nhớ) đã bỏ. Chưa có văn bản cho phép cụ thể.
- Chưa có quyết định cuối về việc dùng VOD. Xem [11. Rủi ro](11-rui-ro-cau-hoi-mo.md).

## Điều cần tránh

- Không dùng dữ liệu mô phỏng làm dữ liệu thật.
- Không dùng bản ghi chưa qua cổng.
- Không lưu nội dung từ blitz.gg vào repo. Xem mục rủi ro về `data/blitz_set18_numbers.json`.
