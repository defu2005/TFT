# Snapshot CDragon "18.7" (dữ liệu thật, dùng cho mô phỏng)

> **Cảnh báo nhãn (cập nhật 2026-11-25):** tên file và nhãn "18.7" KHÔNG đúng. Snapshot có `DA_18_Kennen` = Inferno + Executioner, `DA_18_Ivern` = Greenfather, `DA_Krug18` = Riftbeast + Brawler, tức là trạng thái trước các đổi tộc của 18.7 (Kennen Sprykin, Ivern Elderwood, Kruggs Summoner). Chuỗi `content-metadata.json` của CDragon nhánh latest ghi `16.23.8413489`. Chưa kiểm chứng snapshot thuộc patch TFT nào. Tên file và chuỗi patch trong `real_content.py` được giữ nguyên vì kết quả đã dùng chúng. Coi đây là "CDragon latest, ngày 2026-11-23, patch chưa xác định".

- File: `cdragon_18.7_2026-11-23.json.gz` (gzip, khoảng 2 MB).
- Nội dung gốc: `cdragon_latest_fetched-2026-11-23.json` (nhãn 18.7 là sai, xem cảnh báo ở trên), lấy từ CDragon "latest" ngày 2026-11-23 (`CDRAGON_LATEST_URL` trong `tft_goat/src/tft_goat/data/cdragon.py`).
- sha256 của file đã giải nén: `caed07e9b1602557b8bce09ed2c80a29d67a1d3fa83c676d85592a52b11c3a9e`.
- sha256 của file .gz: `d02fa168934b24abdcc2dfe523b3d4ca04861cb171c373128214cc762c4498c9`.
- Dùng bởi: `tft-sim/src/tft_sim/real_content.py` (đọc tự động; có thể ghi đè bằng biến `TFT_CDRAGON`).

## Điều khoản: CHƯA XÁC MINH

Đây là dữ liệu trò chơi do Riot Games sở hữu, lấy qua CDragon (dự án cộng đồng). `docs/agents/hygiene.md` yêu cầu ghi giấy phép hoặc điều khoản cho mọi nguồn dữ liệu thật. Nguồn này chưa có ghi chú như vậy trong `docs/data-sources.md`. Trước khi giữ file này trong repo công khai, người điều phối cần quyết định: giữ, hoặc thay bằng bước tải theo sha256 ở trên.

Lệnh tải lại (nếu cần thay thế): dùng `download_snapshot()` trong `tft_goat`, rồi kiểm tra sha256 khớp.

## Kiểm tra lại nguồn (2026-11-25)
- Tải lại `https://raw.communitydragon.org/latest/cdragon/tft/en_us.json` hôm nay: sha256 = `caed07e9b1602557b8bce09ed2c80a29d67a1d3fa83c676d85592a52b11c3a9e`, khớp với snapshot đã giải nén. Nghĩa là CDragon "latest" chưa đổi kể từ ngày lấy snapshot, và nhãn "18.7" vẫn sai như cảnh báo ở trên.
