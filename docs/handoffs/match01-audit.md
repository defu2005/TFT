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

Chuỗi thắng ngoài mẫu hỏng chủ yếu vì OCR trả rỗng khi giá trị đúng là 1; tỉ lệ 9/10 trong mẫu không đại diện cho trường này. Ba lần vàng sai ở ngoài mẫu (2-4, 6-1, 6-6) đều là OCR trả rỗng, và các khung này được ghi là không có ô vàng trong audit trước; tính trên khung có ô vàng thì vàng là 13/13. Hai lần cấp sai (2-6 đọc 13, đúng là 5; 3-7 chuỗi thắng đọc 2, đúng là 9) được kiểm tra bằng mắt: giá trị trong JSON đúng, lỗi thuộc OCR. Panel, cửa hàng và bộ đếm chưa đọc lại mù.

## Chưa xong / bị chặn

1. **Hexes, stars, items (107 mục):** file trên đĩa là đoạn cắt 720p, bắt đầu lúc 210 s của VOD (`intendedStartSec` trong `scripts/hud-campaign/seed-sources.json`), nên thời gian file + 210 = thời gian VOD. VOD có bản 1080p60. Đối chứng: vòng 5-1 (khung kế hoạch, file 1836 s = VOD 2046 s) được cắt ở 1080p, khớp khung 720p theo dải giai đoạn và bàn cờ. Sprite ở 1080p rõ hơn, nhưng chưa đo được lợi ích khi đọc sao và item, và chưa đọc lại 107 mục. Việc tiếp theo: đọc lại một vòng có sao và item trước, rồi quyết định có tải cả trận ở 1080p không (khoảng 1,8 GB).
2. **5-6 và 6-2 (đối thủ):** chưa giải. Ứng viên P2 và ghost. Sweep 924 không có badge; sweep 1009 (6-2) có badge cấp 9. Loại P4 dựa trên `result` (streamer thua) và việc P4 cũng mất HP, xem ghi chú attempt. Thanh máu: chưa hoàn tất bằng script (`not completed by script`); số đo ghi trong attempt.
3. **Bàn đối thủ 21 vòng PvP:** chưa có panel rõ được gắn với đối thủ. Mỗi attempt ghi các frame đã kiểm tra và mã chủ sở hữu quan sát được.
4. **Panel, cửa hàng, bộ đếm:** chưa có đọc lại mù, nên không có tỉ lệ.

## Yêu cầu dữ liệu

Hai yêu cầu đang mở, gửi cho workstream `hud`. Chúng không thuộc phạm vi trận 01 này và chưa được đáp ứng:

- `docs/agents/requests/20261124-user-to-hud-fields4-status.md` (`status: mở`): lỗi đã biết của bộ đọc trường fields4 trên trận 01.
- `docs/agents/requests/20261124-user-to-hud-vod-sample-logs.md` (`status: mở`): log OCR theo mẫu của chiến dịch VOD.

Phản hồi cho kết quả trận 01 nằm ở `docs/agents/responses/20261124-hud-match01-result.md`, đã được cập nhật sang trạng thái đã giao.

## Quyết định đã chốt

- Không gắn đối thủ từ thanh máu (thử nghiệm chưa hoàn tất bằng script).
- Không đổi gắn 5-2 → P3 trừ khi có bằng chứng mới.
- Không viết lại lịch sử git. Lý do và chi tiết nằm ngoài tệp này.

## Rủi ro và giả định

- Crop đọc lại mù vàng và chuỗi thắng được chọn sau khi xem mẫu, nên kết quả trong mẫu bị tinh chỉnh.
- Nhãn HP trong `round_hp_change_flags.json` là đọc bằng mô hình có kiểm tra lại ở 2-3 và 4-4; không suy ra được PvE từ việc không mất HP.

## Cách tiếp tục

1. Căn thời gian đoạn 1080p và đọc một vòng đã giải làm đối chứng (xem mục 1 ở trên).
2. Nếu bản 1080p đọc rõ hơn, mở lại 107 mục; nếu không, giữ lý do hiện tại.
3. Đọc lại mù panel, cửa hàng và bộ đếm nếu cần tỉ lệ cho các trường đó.
