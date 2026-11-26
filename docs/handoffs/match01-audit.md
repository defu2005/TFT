# Bàn giao: kiểm toán HUD trận 01 (Set 18)

- Nhánh: `claude/nifty-lovelace-252i30`
- Commit dữ liệu gần nhất: xem commit đầu của tệp này trong lịch sử git (cập nhật sau mỗi lần sửa `match01_full.json`)
- Agent / người: Claude (phiên trên claude.ai/code)
- Ngày: 2026-11-26
- Trạng thái: xong mốc; 5-6 và 6-2 chưa giải; 107 mục hexes, stars, items đang bị chặn bởi nguồn 720p trên đĩa

Tệp này là bàn giao của workstream trận 01. `HANDOFF.md` ở gốc nhánh thuộc workstream chiến dịch và không bị ghi đè.

## Mục tiêu

Trích đầy đủ dữ liệu trận 01 của Set 18 từ VOD livestream vào `data/hud-audit/match01_full.json`, 38 vòng. Kiểm tra bằng `data/hud-audit/check_match01_full.py`.

## Đã xong

- 38/38 vòng đủ các trường bắt buộc (planning, combat, result, round_type, augment, actions).
- Các trường FULL đã giải: board_units 33, hexes 3, bench_units 25, stars 2, items 2, opponent 36, opponent_board 17.
- Bàn đối thủ: 4 vòng có panel, 13 vòng n/a, 21 vòng PvP chưa có panel (mỗi vòng có attempt và lý do).
- Hàng chờ đối thủ: 25/25 vòng không phải n/a đã đóng, 0 mở.
- Đối thủ 5-2 là P3, gắn theo tooltip trong khoảng 5-2 ở sweep 809 và panel khớp qua sweep 808–812.

## Kết quả đo

Đọc lại mù, 10 vòng trong mẫu (crop đã tinh chỉnh sau khi xem mẫu):

| Trường | Kết quả |
|---|---|
| Vàng | 10/10 |
| Chuỗi thắng | 9/10 |
| Cấp | 10/10 |
| XP | 10/10 |

Đọc lại mù ngoài mẫu, 19 vòng có khung kế hoạch (`data/hud-audit/blind_oos28_rates.json`, chạy cùng script với mẫu khác):

| Trường | Đúng / tổng |
|---|---|
| Vàng | 13/16 |
| Chuỗi thắng | 4/14 |
| Cấp | 11/15 |
| XP | 13/14 |

Chuỗi thắng ngoài mẫu hỏng chủ yếu vì OCR trả rỗng khi giá trị đúng là 1. Tỉ lệ 9/10 trong mẫu không đại diện cho trường này. Vàng, chuỗi thắng, cấp và XP không có tỉ lệ đáng tin ngoài mẫu hơn ngoài số liệu trên. Panel, cửa hàng và bộ đếm chưa đọc lại mù.

## Chưa xong / bị chặn

1. **Hexes, stars, items (107 mục):** nguồn trên đĩa là H.264 1280×720. VOD trên Twitch có bản 1080p60 (`yt-dlp -F` liệt kê được). Đã tải một đoạn 20 giây 1080p quanh vòng 1-2 làm đối chứng. Khung 1080p tại 340 s không khớp khung 720p cùng thời điểm (một bên là đấu trường, một bên là trang web), nên chưa xác nhận được căn thời gian và chưa có bằng chứng về độ rõ. Việc tiếp theo: căn thời gian đoạn 1080p bằng khung đã biết, rồi đọc lại một vòng đã giải làm đối chứng trước khi đọc lại 107 mục.
2. **5-6 và 6-2 (đối thủ):** chưa giải. Ứng viên P2 và ghost. Sweep 924 không có badge; sweep 1009 (6-2) có badge cấp 9. Lý do loại P4 nằm trong ghi chú attempt (người mất HP cùng với người thắng không thể là đối thủ của nhau). Thử nghiệm thanh máu không hoàn tất bằng script: chỉ có một điểm đối chứng và không đo được chiều rộng đầy đủ của thanh.
3. **Bàn đối thủ 21 vòng PvP:** chưa có panel rõ được gắn với đối thủ. Mỗi attempt ghi các frame đã kiểm tra và mã chủ sở hữu quan sát được.
4. **Panel, cửa hàng, bộ đếm:** chưa có đọc lại mù, nên không có tỉ lệ.

## Yêu cầu dữ liệu

Hai yêu cầu đang mở, gửi cho workstream `hud`. Chúng không thuộc phạm vi trận 01 này và chưa được đáp ứng:

- `docs/agents/requests/20261124-user-to-hud-fields4-status.md` (`status: mở`): lỗi đã biết của bộ đọc trường fields4 trên trận 01.
- `docs/agents/requests/20261124-user-to-hud-vod-sample-logs.md` (`status: mở`): log OCR theo mẫu của chiến dịch VOD.

Phản hồi cho kết quả trận 01 nằm ở `docs/agents/responses/20261124-hud-match01-result.md`, đã được cập nhật sang trạng thái đã giao.

## Quyết định đã chốt

- Không gắn đối thủ từ thanh máu (chỉ một điểm đối chứng).
- Không đổi gắn 5-2 → P3 trừ khi có bằng chứng mới.
- Không viết lại lịch sử git. Lý do và chi tiết nằm ngoài tệp này.

## Rủi ro và giả định

- Crop đọc lại mù vàng và chuỗi thắng được chọn sau khi xem mẫu, nên kết quả trong mẫu bị tinh chỉnh.
- Nhãn HP trong `round_hp_change_flags.json` là đọc bằng mô hình có kiểm tra lại ở 2-3 và 4-4; không suy ra được PvE từ việc không mất HP.

## Cách tiếp tục

1. Căn thời gian đoạn 1080p và đọc một vòng đã giải làm đối chứng (xem mục 1 ở trên).
2. Nếu bản 1080p đọc rõ hơn, mở lại 107 mục; nếu không, giữ lý do hiện tại.
3. Đọc lại mù panel, cửa hàng và bộ đếm nếu cần tỉ lệ cho các trường đó.
