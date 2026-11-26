# Bàn giao: kiểm toán HUD trận 01 (Set 18)

- Nhánh: `claude/nifty-lovelace-252i30`
- Commit dữ liệu gần nhất: `b0afbc7` (cập nhật này là commit tiếp theo)
- Agent / người: Claude (phiên trên claude.ai/code)
- Ngày: 2026-11-26
- Trạng thái: xong mốc, còn 5-6 và 6-2 chưa giải và một số trường bị chặn bởi độ phân giải nguồn

Tệp này là bàn giao cho workstream trận 01 riêng. `HANDOFF.md` ở gốc nhánh thuộc workstream chiến dịch và không bị ghi đè.

## Mục tiêu

Trích đầy đủ dữ liệu trận 01 của Set 18 từ VOD livestream vào `data/hud-audit/match01_full.json`, 38 vòng. Kiểm tra bằng `data/hud-audit/check_match01_full.py`.

## Đã xong

- 38/38 vòng đủ các trường bắt buộc (planning, combat, result, round_type, augment, actions).
- Các trường FULL đã giải: board_units 33, hexes 3, bench_units 25, stars 2, items 2, opponent 36, opponent_board 17.
- Bàn đối thủ: 4 vòng có panel, 13 vòng n/a, 21 vòng PvP chưa có panel (mỗi vòng có attempt và lý do).
- Hàng chờ đối thủ: 25/25 vòng không phải n/a đã đóng, 0 mở.
- Đối thủ 5-2 là P3, gắn theo tooltip trong khoảng 5-2 ở sweep 809 và panel khớp qua sweep 808–812.

## Kết quả đo

| Thứ đo | Phiên bản | Lệnh | Số mẫu | Kết quả | Ghi chú |
|---|---|---|---|---|---|
| Đọc lại mù vàng | blind_ocr_planning.py, crop 3x | script | 10 vòng | 10/10 | Crop được chọn sau khi xem mẫu: có tinh chỉnh |
| Đọc lại mù chuỗi thắng | cùng script, 3x | script | 10 vòng | 9/10 | Một lần 6x cho 6/10 do sai tỉ lệ, không dùng |
| Đọc lại mù cấp | cùng script, 6x | script | 10 vòng | 10/10 | Hiệu chỉnh trên khung ngoài mẫu 2-3 |
| Đọc lại mù XP | cùng script, 6x | script | 10 vòng | 10/10 | Hiệu chỉnh trên khung ngoài mẫu 2-3 |
| Vàng ngoài mẫu | cùng script | script | 13 khung | 13/13 so sánh được | 3 khung không có ô vàng (2-4, 6-1, 6-6) |

Panel, cửa hàng và bộ đếm chưa đọc lại mù, không có tỉ lệ.

## Chưa xong / bị chặn

Các trường chưa giải và lý do chính:

1. **Hexes, stars, items (107 mục):** nguồn trên đĩa là H.264 1280×720. Không tìm thấy bản độ phân giải cao hơn trong repo hoặc thư mục chiến dịch. Chưa thử tải bản khác; lệnh tải nguồn không nằm trong `docs/` hay `data/`.
2. **Bàn đối thủ 21 vòng PvP:** chưa có panel rõ được gắn với đối thủ. Các attempt ghi frame đã kiểm tra và mã chủ sở hữu quan sát được.
3. **5-6 và 6-2 (opponent):** chưa giải. Ứng viên P2, P4, ghost. Sweep 924 không có badge; sweep 1009 (6-2) có badge cấp 9, và hai hàng còn sống đều cấp 9. Thử nghiệm thanh máu không hoàn tất bằng script: chỉ có một điểm đối chứng và số đo không đủ để ánh xạ.

## Đang chạy

Không có tiến trình nền.

## Yêu cầu dữ liệu

- Chưa có yêu cầu hay trả lời dữ liệu nào.

## Quyết định đã chốt

- Không gắn đối thủ từ thanh máu (chỉ một điểm đối chứng).
- Không đổi gắn 5-2 → P3 trừ khi có bằng chứng mới.
- Không viết lại lịch sử git. Lịch sử đã push còn chứa một tên hiển thị (xem chat, không ghi ở đây).

## Rủi ro và giả định

- Các crop đọc lại mù (vàng, chuỗi thắng) được chọn sau khi xem mẫu nên kết quả bị tinh chỉnh.
- Nhãn HP trong `round_hp_change_flags.json` là đọc bằng mô hình có kiểm tra lại ở 2-3 và 4-4; không suy ra được PvE từ việc không mất HP.

## Cách tiếp tục

1. Tìm lệnh tải nguồn gốc trong môi trường của phiên trước; nếu có bản cao hơn, thử một khung đã giải làm đối chứng trước khi đọc lại các trường 720p.
2. Nếu không có bản cao hơn, giữ lý do hiện tại cho 107 mục và không mở lại.
3. Đọc lại mù panel, cửa hàng và bộ đếm nếu cần tỉ lệ cho các trường đó.
