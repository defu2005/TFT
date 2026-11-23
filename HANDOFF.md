# Bàn giao TFT HUD Set 18

Mục tiêu là đọc vàng, cấp, tên và giá của từng ô shop theo thời gian thực ở 4 Hz, rồi đối chiếu với ảnh gốc. Mục tiêu 100% vẫn đang mở. Bộ đọc dùng vùng ảnh từ HUD, Tesseract và danh mục Set 18. `cost` là bậc tướng, còn `price` là giá đang hiện trên thẻ. Một thẻ có tên hợp lệ và `price: null` vẫn được lưu, nhưng coach bỏ qua đề xuất mua thẻ đó. Xem [cách chạy và hiệu chỉnh đầu vào](docs/hud-reader.md).

## Trạng thái lúc bàn giao

- Đã tải và kiểm tra hai đầu của 20 trận liền mạch từ Setsuko, BoxBox và robinsongz. Tổng thời lượng tệp là 12,1 giờ và 19,0 GiB, gồm 17 trận 720p và 3 trận 1080p. Có bảng đấu, linh thú, cảnh sảnh và overlay khác nhau trong nguồn VOD. Kiểm thử cửa sổ thật trên Windows và thiết bị mobile vẫn đang chờ.
- Cloud là Debian 13, AMD EPYC, 5 CPU logic hiển thị với quota 4 vCPU, RAM 32 GiB, ổ dùng chung giữa `/workspace` và `/tmp` khoảng 63 GiB. Đã kiểm tra kết nối tải Twitch HLS. Khi nhiều tiến trình chạy đồng thời, CPU đạt khoảng 100% quota và RAM làm việc khoảng 4 GiB, ngoài bộ đệm tệp. Bộ tải giữ 4 GiB trống cho quá trình ghi kết quả và tính trước dung lượng của các lượt đang tải.
- Trận Setsuko 40:29 với bản OCR trước khi sửa đồng vàng chạy hết ở lịch 4 Hz. Đã xử lý 9.356/9.715 mẫu, bỏ 359 mẫu, p95 437 ms. Ở 4.400 mốc đầu trước khi tải hàng loạt, p95 là 209 ms và bỏ 2 mẫu. Trong giai đoạn OCR song song với tải, p95 là 632 ms và bỏ 287/2.115 mẫu. Các giai đoạn lấy từ những phần khác nhau của trận.
- Trong 61 khung đối chiếu định trước của trận này, có 7 khung bị bỏ. Tính cả các khung bị bỏ, vàng đúng 33/40 lần hiện, cấp đúng 33/40, tên tướng đúng 104/130 ô và giá đúng 102/130 ô. Kiểm tra riêng ghi nhận đồng vàng sáng làm giá Akali từ 1 thành 21. Bản đang chạy cho hàng đợi đã sửa cách phân biệt đồng vàng với chữ số và đọc đúng Akali ở ảnh kiểm tra. Giá Hecarim cùng khung vẫn trống. 95 giá từng đối chiếu trên các ảnh mẫu khác vẫn đọc đúng sau thay đổi.
- Quy trình tải, chạy OCR, lưu log rồi xóa MP4 đã được xác nhận với mẫu 80 giây và trận Setsuko 40:29. Hai nguồn này đã vào sổ. Khi trận cũ được dọn, hàng đợi tự bắt đầu tải một trận mới. Bốn trận đầu của bộ 20 đã bắt đầu test. Ba trận bổ sung đã tải và được kiểm tra biên. Hàng đợi tiếp tục với bộ trận này và 15 chương TFT từ những VOD khác.

## Quy tắc tiếp quản

1. Kiểm tra `git status --short --branch` và đọc trạng thái Cloud trước khi khởi động tiến trình. Hàng đợi hiện chạy trong `/workspace/scratch/tft-test-matches/campaign`. Đọc `status.json`, `campaign.log` và PID trong `pid` ở thư mục đó. Nếu heartbeat mới và PID đang chạy, dùng phiên hiện tại. Trình điều phối dùng khóa tệp để tránh chạy hai bản trong cùng thư mục.
2. Giữ SQLite `campaign.sqlite3` làm sổ nguồn, khoảng thời gian, trạng thái và kết quả. `tested-sources.csv` là bản xuất để đọc. Kiểm tra giao nhau theo VOD ID và thời điểm nguồn trước khi thêm việc, kể cả đoạn đã xóa MP4. Khi biết các VOD là góc nhìn của cùng một trận, chọn một góc nhìn cho bộ dữ liệu độc lập. Các lần chạy so sánh lại cùng mẫu phải được ghi rõ là chạy hồi quy.
3. Ghi phiên bản mã, URL VOD, khoảng thời gian trong VOD, mùa, độ phân giải, số mẫu, số mẫu bỏ, số vượt 250 ms, p95 và số lỗi OCR. Chỉ gọi một tỷ lệ là độ chính xác khi đã đối chiếu dữ liệu với ảnh. Báo riêng ô bị che, ô không đọc được, mẫu bị bỏ và giá đọc sai. Dùng trường `mediaTimeMs` để đối chiếu đúng khung. Đo đơn luồng và đo bão hòa CPU thành hai nhóm kết quả.
4. Với một trận đầy đủ, kiểm tra phần vào trận và kết quả hoặc màn rời trận trước khi đánh dấu `verified-matches.json`. Giữ trận có chuyển cảnh, bảng đấu và linh thú khác nhau để kiểm tra các trạng thái khó. Một chương VOD có thể chứa nhiều trận và đoạn ngoài game. Ghi loại mẫu trong `sampleType` khi bổ sung hàng đợi.
5. Theo yêu cầu hiện tại, xóa MP4 mẫu sau khi job hoàn tất và đã lưu báo cáo JSON, log khung `.jsonl.gz` cùng bản ghi SQLite. Giữ mã, hồ sơ tọa độ và danh sách nguồn trong Git. Video, tệp trạng thái, URL media đã ký và các đoạn dùng khi chẩn đoán tải ở thư mục `scratch` hoặc `/tmp`.
6. Khi chuyển sang Cloud khác, sao lưu SQLite bằng API `sqlite3.Connection.backup` trong khi job chạy, hoặc sao lưu sau khi tiến trình dừng. Mang theo `results/`, danh sách xác minh và hồ sơ ROI đã dùng. Đối chiếu tệp MP4 đang tải/dang dở với các bản ghi `ready` và `downloading` khi tiếp tục. Hàng đợi dùng mã OCR và danh mục đã chụp theo phiên bản lúc khởi động, vì vậy kết quả hồi quy của những thay đổi tiếp theo cần ghi phiên bản mới.

## Tệp và lệnh tiếp tục

- `scripts/hud-campaign/run.py` và `media.py` điều phối test, tải HLS, xác minh thời lượng và dọn video. Các tệp `seed-sources.json` và `profile-1080p.json` giúp dựng lại hàng đợi và cấu hình. Danh sách hiện tại có sẵn ở `/workspace/scratch/tft-test-matches/manifest.csv`.
- Báo cáo của trận Setsuko nằm ở `/workspace/scratch/tft-full-match/hud-price-full-metrics.json`; nhãn đối chiếu ở `hud-price-full-reference.json` cùng thư mục. Kết quả và log của từng mẫu đã hoàn thành nằm dưới `campaign/results/`. `campaign/cloud-environment.json` ghi cấu hình và một lần đo tài nguyên.
- Nếu bắt đầu lại trên Linux cgroup v2, cài FFmpeg/FFprobe, Tesseract tiếng Anh, Pillow và yt-dlp. Chỉ khởi động khi thư mục không còn tiến trình điều phối đang chạy. Hàng đợi dùng `TFT_CAMPAIGN_DIR` nếu muốn chọn thư mục khác. Trong thư mục mới, bổ sung danh sách `verified-matches.json` sau khi kiểm tra biên trận để cho phép tự dọn.

```bash
python3 scripts/hud-campaign/run.py
python3 scripts/hud-reader.py --video /path/to/match.mp4 --interval 0.25
npm test
TFT_SET18_ART_ZIP=/path/to/set18-assets.zip python3 scripts/test_hud_ocr.py -v
```

Kết quả kiểm thử trước bàn giao là 42 bài Node và 8 bài Python đạt. Tiến trình Cloud đang chạy tiếp với phiên bản OCR `f7334be22fdf61a0`.
