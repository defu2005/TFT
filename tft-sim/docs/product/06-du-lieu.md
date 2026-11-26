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

Một bản ghi = một lần đánh nhau tại một round giữa hai bàn, kèm kết quả (`result.winner`), `fight_key`, `source`. Mỗi bàn có `level` và `units`. Mỗi unit có `api`, `star`, `items`, `frames`. Ở cấp bàn có `augments`.

Quy tắc khóa, đúng theo `usable.py`: thiếu khóa `items` hoặc `augments` là **không biết**, bị từ chối (`items_thieu`, `augments_thieu`), không coi là rỗng. Giá trị `null` bị từ chối riêng (`items_null`, `augments_null`). Mỗi unit phải có ít nhất một khung hình (`unit_khong_khung_hinh`).

Thứ tự kiểm trong `usable.reason`: kết quả thắng rỗng → tên placeholder → cấp không rõ → bàn không phân giải được → bàn thiếu → thiếu augment → tướng lạ → sao không hợp lệ → thiếu item → unit không có khung hình → thiếu frame.

## Hiện trạng VOD

- **1026 ván, 12.488 fight** đã được thu (số tại thời điểm chạy, `model-plan.md` mục liên quan đến VOD; **336 VOD Twitch chưa đối chiếu lại**).
- **Cổng gộp đỏ:** không slot nào đạt. Nghĩa là không bản ghi nào đủ chất lượng để vào `scoring.jsonl`.
- Lý do cụ thể từng slot nằm trong báo cáo của cổng (`merge_check_vod.py`). Đừng suy đoán lý do.

Trạng thái bàn giao (`HANDOFF_STATUS`): `pending`, `working`, `done`, `blocked`, `stale`. Trạng thái không hợp lệ bị `bad_status` từ chối.

## Quyền và rủi ro pháp lý

- Dữ liệu VOD thu từ video công khai của streamer. Người dùng đã nhận thức rủi ro về quyền và điều khoản dịch vụ.
- Đường RAM (đọc bộ nhớ): trạng thái chưa rõ trong roadmap (xem [3](03-lo-trinh.md)). Chưa có văn bản cho phép cụ thể.
- Chưa có quyết định cuối về việc dùng VOD. Xem [11. Rủi ro](11-rui-ro-cau-hoi-mo.md).

## Blitz.gg: trạng thái và việc cần xác nhận

- Đã crawl 74 trang blitz.gg Set 18 (patch 18.7). Văn bản thô ở scratchpad, **không vào repo**. Số liệu đã rút ra được commit ở `data/blitz_set18_numbers.json` (`docs/research/combat-public-data.md` mục 10c).
- Điều khoản Blitz: chỉ dùng cá nhân phi thương mại. `robots.txt` chặn ClaudeBot/GPTBot.
- `combat-public-data.md` ghi người dùng đã chấp nhận rủi ro điều khoản và cho phép dùng, kể cả cho mô hình. Ghi nhận đó có trong tài liệu nghiên cứu; không tìm thấy quy tắc "không lưu blitz" nào trong `docs/`.
- **Cần người dùng xác nhận lại** vì file đã nằm trong repo. Tài liệu `combat-public-data.md` mục 10 vẫn ghi "chưa commit" trước khi mục 10c ghi đã commit; đây là mâu thuẫn trong ghi chú cũ.
- Vì mục 10c nói số Blitz giữ nguyên, không tự sửa chúng.

## Điều cần tránh

- Không dùng dữ liệu mô phỏng làm dữ liệu thật.
- Không dùng bản ghi chưa qua cổng.
