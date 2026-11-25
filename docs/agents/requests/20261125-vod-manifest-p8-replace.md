# P8 manifest: thay VOD blocked của disguisedtoast

Ngày: 2026-11-25. Điều phối manifest (không thu thập fight).

## Lý do
Ba VOD P8 của `disguisedtoast` (`twitch-2935422428`, `twitch-2937597175`, `twitch-2938701039`) bị agent đánh `blocked`: lobby Normal / không ranked và set ≠ 18 (Remix Rumble / set1-style). Trên Twitch archive công khai, Toast **không** có VOD ranked Set 18 trong cửa sổ Aug 26–Nov 16 2026.

## Thay thế
Thêm VOD ranked/ladder Set 18 (category Teamfight Tactics, URL thật, đã verify GQL) vào slot **P8**:
- `imaqtpie` (grandmaster / ladder grind)
- `dankmemes011` (rank 1 grind)
- `scarra` (masters tft)

Giữ `disguisedtoast` trong `slots.P8.streamers` vì các dòng blocked vẫn thuộc P8. Cập nhật `status: blocked` trên ba VOD cũ trong manifest.

## Phạm vi
Chỉ sửa manifest (+ note này). Không đụng `vod_out/` / CLAIM P8.
