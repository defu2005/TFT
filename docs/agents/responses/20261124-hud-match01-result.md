# Kết quả trận 01 (mùa 18, `01-boxbox`) — phần đã xác minh

dataset: kết quả cuối trận cho trận 01. Không có log mẫu theo thời gian trong file này.
status: đã giao

Dữ liệu đầy đủ 38 vòng nằm ở `data/hud-audit/match01_full.json`; xem `docs/handoffs/match01-audit.md` để biết các trường còn chưa giải.

## Đã xác minh

- Thứ hạng của streamer: **2/8** (màn hình bảng xếp hạng ở khoảng 2620 s).
- LP thay đổi: **+23**, tổng **1.116** (đọc từ màn hình kết thúc).
- Mốc bắt đầu trận: 311,8 s (giai đoạn 1-1, timer 15).

## Bí danh người chơi

P1–P8: streamer là một trong các bí danh này. Không lưu tên người chơi thật hoặc Riot ID trong bất kỳ file nào của repo.

## Đã giao (cập nhật)

path: `data/hud-audit/match01_full.json` (38 vòng, kiểm tra bằng `data/hud-audit/check_match01_full.py`)
schema: không có phiên bản chính thức; cấu trúc theo checker tại commit giao
commit: (điền ở commit tiếp theo)

## Chưa có (cũ, đã cập nhật ở trên)

- Thứ hạng của 7 đối thủ còn lại.
- Đội hình cuối của 8 người chơi (màn hình bảng xếp hạng chỉ hiện biểu tượng tướng và sao, một số hàng bị cắt "+2"/"+1").
- Toàn bộ dữ liệu trong trận: HP, bàn và hàng chờ, trait, augment, item, hành động, kết quả vòng.

## Lưu ý

Tệp này đã được commit trên nhánh `hud` và cập nhật theo `docs/agents/data-contracts.md`.
