# Snapshot CDragon 18.7 (dữ liệu thật, dùng cho mô phỏng)

- File: `cdragon_18.7_2026-11-23.json.gz` (gzip, khoảng 2 MB).
- Nội dung gốc: `cdragon_latest_fetched-2026-11-23.json`, lấy từ CDragon "latest" ngày 2026-11-23 (`CDRAGON_LATEST_URL` trong `tft_goat/src/tft_goat/data/cdragon.py`).
- sha256 của file đã giải nén: `caed07e9b1602557b8bce09ed2c80a29d67a1d3fa83c676d85592a52b11c3a9e`.
- sha256 của file .gz: `d02fa168934b24abdcc2dfe523b3d4ca04861cb171c373128214cc762c4498c9`.
- Dùng bởi: `tft-sim/src/tft_sim/real_content.py` (đọc tự động; có thể ghi đè bằng biến `TFT_CDRAGON`).

## Điều khoản: CHƯA XÁC MINH

Đây là dữ liệu trò chơi do Riot Games sở hữu, lấy qua CDragon (dự án cộng đồng). `docs/agents/hygiene.md` yêu cầu ghi giấy phép hoặc điều khoản cho mọi nguồn dữ liệu thật. Nguồn này chưa có ghi chú như vậy trong `docs/data-sources.md`. Trước khi giữ file này trong repo công khai, người điều phối cần quyết định: giữ, hoặc thay bằng bước tải theo sha256 ở trên.

Lệnh tải lại (nếu cần thay thế): dùng `download_snapshot()` trong `tft_goat`, rồi kiểm tra sha256 khớp.
