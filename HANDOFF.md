# Bàn giao TFT HUD Set 18

## Tiến độ cập nhật 24/11/2026

Ưu tiên kiểm chứng vàng, cấp, tên và giá hiển thị theo từng ô shop khi HUD rõ. Replay giữ lịch 4 Hz. Chấm riêng tỷ lệ đọc đúng, tỷ lệ mẫu đúng hạn 250 ms, trạng thái HUD ẩn và mẫu khởi động.

- Lượt Frodan 1080p `2919423875` dài 31 phút 45 giây đã xử lý 7.620/7.620 mẫu và không bỏ mẫu. P95 là 141,08 ms, 13 mẫu sau khởi động vượt 250 ms. Cả 9 mốc HUD rõ chọn trước đều đúng và kịp. Trong phép kiểm tra riêng 13 mẫu trễ, một trong 5 mẫu HUD rõ bỏ sót Xayah vì viền thẻ lóe sáng.
- Bộ đọc hiện khởi tạo Tesseract song song với FFmpeg, giảm nhận dạng lặp ở giá, đọc lại vàng và cấp khi đủ bằng chứng, rồi kiểm tra riêng nét sáng dưới tên tướng. Lượt hồi quy Xayah đạt 5/5 mốc đúng và kịp với 180/180 mẫu xử lý, trễ 0 sau khởi động. Bộ kiểm thử Python đạt 14/14 với ảnh Set 18.
- Hai nguồn 1080p mới có 154 mẫu shop thường với HUD rõ. Dishsoap `2916057333` đạt 89/89. Setsuko `2911167981` đạt 0/65 khi áp vùng đọc từ nguồn khác và 64/65 sau hiệu chỉnh. Tính phép đo cuối của mỗi nguồn, vàng và cấp đúng 154/154, tên và giá đều đúng 699/700, toàn mẫu đúng 153/154. Đây là tỷ lệ trên các đoạn đã chấm. Các mẫu Setsuko sau hiệu chỉnh là lượt hồi quy trên cùng nguồn. Trường còn thiếu là Kog'Maw tại mẫu có con trỏ sát vùng giá. Ba thẻ Phantom Armor được chấm riêng và vẫn thiếu tên lẫn giá.
- Bộ đọc có thể loại kết quả khi thiếu độ tin cậy, các mặt nạ bất đồng hoặc HUD chưa được xác nhận. Coach lưu cờ thiếu vàng, thiếu cấp hoặc ô chưa đọc khi nhận bản ghi schema 2. Kết quả được chấp nhận vẫn có thể sai do đặt lệch vùng ảnh. Cấu hình đầu của Setsuko từng trả giá 9 cho Yunara giá 2. Không có đối chiếu với ảnh đã gắn nhãn trong lúc chạy thật.
- Profile hiệu chỉnh `scripts/hud-campaign/setsuko-2911167981-1080p.json` dùng riêng cho video này. Khi chạy lại, truyền profile qua `--profile`. Các bản ghi chạy khác phải lưu cấu hình thực tế đã dùng. Đừng dùng tỷ lệ của một profile cho các bố cục chưa đo.
- Chiến dịch đã hoàn tất 40 mục và đang tải 6 chương mới, gồm ba nguồn 720p và ba nguồn 1080p. Tiến trình dùng snapshot `0983ecd7a1088a76`. `/workspace/scratch/tft-test-matches/campaign/status.json` có heartbeat, số mục tải và số mục đang OCR. Gói bàn giao nằm tại `/workspace/scratch/tft-handoff/tft-campaign-checkpoint.tar.gz`.
- Trong `/workspace/scratch/tft-hud-optimization/full-match23-audit/whole-match-prototype/`, xem `production-full-2919423875/result.json`, `late-frame-audit/paced-regression.json` và `new-source-hls/report-calibrated.json`. Phiên này lưu nhãn, log nén và cấu hình. Giữ sổ nguồn để giao nhau theo VOD và thời gian, và dọn media mẫu sau khi có kết quả kiểm tra.

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

## Phiên bản đang bàn giao `ab8aadb7d9c762ac`

- Bản trong Git tái sử dụng phiên Tesseract trên Linux, chọn profile theo nguồn, đọc trước một khung replay và chỉ truyền vùng HUD qua FFmpeg. Bản mới nhất bỏ lượt OCR giá ở những ô có mặt nạ tên trống và quá tối để thử đọc lại tên.
- Hai clip hồi quy 4 Hz từ trận 23 có đầu ra giống nhau tại cả 291 mốc. Số ô đi qua OCR giá giảm từ 1.455 xuống 503. p95 đầu-cuối giảm từ 125 xuống 109 ms ở clip sảnh và từ 84 xuống 64 ms ở clip shop. Bản mới đủ 291 mẫu và không có mẫu vượt 250 ms sau khởi động trong hai clip. Báo cáo và log nén nằm trong `/workspace/scratch/tft-hud-optimization/price-gate-replay.json` và cùng thư mục. Đã chạy đạt 42 bài Node và 11 bài Python.
- Lượt 45 phút có khóa `2927052824-13230000`, nguồn Twitch `2927052824`, bắt đầu ở giây nguồn 13.230 và dùng profile `robinsongz-2927052824.json`. Lượt vẫn chạy bản ghim `af62626a1074d621`. Ở mốc 1.041,25 giây đã ghi 4.165 mẫu, bỏ 1 mẫu, p95 244,03 ms và có 190 mẫu vượt 250 ms sau khởi động. Khi tiếp quản, xem `campaign/native-match23.json` cùng `campaign/results/2927052824-13230000.part.jsonl` khi đang chạy hoặc hai tệp `.json` và `.jsonl.gz` sau khi hoàn tất. Để lượt này chạy xong bằng snapshot hiện tại.
- Bước tiếp theo là ghi tay vàng, cấp, tên và giá ở năm ô từ 16 ảnh HUD đã lưu trong `/workspace/scratch/tft-hud-optimization/full-match23-audit/`. `frames.json` ghép ảnh với `frame` và `mediaTimeMs`. Đọc ảnh và ghi nhãn trước khi mở log OCR. Ghi riêng ô trống, HUD bị che, trường sai và khung bị bỏ. So sánh theo `mediaTimeMs`; dùng thêm `deadlineMissed` để đếm mốc đọc đúng và kịp 250 ms. Các ảnh chưa được chấm. Việc chấm vẫn tiếp tục được sau khi hàng đợi dọn MP4.
- Sau khi thu kết quả toàn trận, dùng bản trong Git cho nguồn mới chưa có trong sổ hoặc ghi rõ mục đích nếu chạy lại nguồn cũ. Số liệu clip chỉ xác nhận mức khớp giữa hai phiên bản. Độ chính xác trên cả trận, cửa sổ Windows và mobile vẫn cần được đối chiếu.

## Kết quả tiếp tục sau commit `0b2a97c`

- Bản Linux dùng lại phiên Tesseract ở từng luồng. Với 111 khung thử nghiệm, đầu ra khớp với Tesseract dòng lệnh và p95 riêng bước OCR giảm từ 780 ms xuống 188 ms. Đường gọi CLI vẫn dùng được qua `--tesseract /usr/bin/tesseract`.
- Đã sửa lỗi gán profile giá BoxBox cho mọi video 1080p. Hàng đợi dùng profile mặc định hoặc profile đã chỉ định trong từng nguồn. Khi đối chiếu thủ công 12 khung từ hai clip, vàng đúng 11/11, cấp đúng 11/11, tên tướng đúng 39/39, giá đúng 39/39. Profile gán nhầm chỉ đọc đúng 24/39 giá trên cùng bộ khung.
- Trong phép đo tải song song ở 4 Hz, bản mới xử lý 212/214 mẫu so với 98/214 qua CLI. Lần chạy lại clip 1080p ở mức ưu tiên mặc định xử lý 108/108, p95 267 ms và 6 lượt vượt 250 ms sau mẫu khởi động. Xem `/workspace/scratch/tft-hud-optimization/report.json` cùng ảnh đối chiếu. Các kết quả này áp dụng cho hai clip đã thử.
- Bản mới đạt 42 bài Node và 9 bài Python. Hàng đợi đang chạy tiếp bằng phiên bản `f7334be22fdf61a0`; phần tối ưu thuộc phiên bản `6f422b3601410480` và nằm trong working tree.

## Trận robinsongz và giá bị bỏ trống

- Bản `1d704f708246f8f8` thử thêm hai cấu hình đọc giá trở lên khi các ảnh nhị phân ban đầu không đủ tin cậy. Bước này khôi phục hai giá 3 từng bị bỏ trống và giữ đúng 95/95 giá đã đối chiếu trước đó.
- Trận 23 dùng `scripts/hud-campaign/robinsongz-2927052824.json`. Hai nhóm 8 khung dùng để hiệu chỉnh và kiểm tra lại đều khớp toàn bộ sau sửa. Ở tám khung rà soát cuối, cấp đúng 8/8, tên tướng đúng 33/33, vàng đúng 7/8 và giá đúng 31/33. Hai giá còn thiếu ở giây 1897 và 2450. Vàng 17 ở giây 630 vẫn thiếu dù đã đọc được shop và cấp.
- Replay 31,15 giây của trận 23 ở 4 Hz đủ 125/125 mẫu, p95 290 ms và 10 mẫu vượt 250 ms sau khởi động. Xem báo cáo và ảnh đối chiếu trong `/workspace/scratch/tft-hud-optimization/price-and-profile.json` và thư mục chứa tệp này.
- Trận đầy đủ được dành cho bản mới trong sổ SQLite với khóa `2927052824-13230000`. Xem `campaign/native-match23.json` để biết đã bắt đầu hoặc hoàn tất. Trạng thái đang chờ là `reserved_native` và khi chạy là `testing_native`. Khi hoàn tất, kết quả trở về sổ chung để bộ dọn xóa MP4.

## Xác minh bản `b6365799fcaa9947`

- Bản này khôi phục vàng ở giây 338 và 630, giá Ashe ở giây 1897 và giá Brambleback ở giây 2450. Đã đối chiếu và đọc đúng toàn bộ trường trên 32 khung robinsongz 720p và 8 khung Setsuko 1080p. Đã kiểm tra lại 95 giá cũ và chạy đạt 42 bài Node, 11 bài Python.
- Replay 4 Hz xử lý 146/146 mẫu ở cả hai phiên bản, với cùng đầu ra trên từng mẫu. p95 bản mới là 189 ms, còn 4 lượt vượt 250 ms sau khởi động. Lượt chạy này bắt đầu lúc CPU đang dùng gần 99% quota với bốn job OCR cũ.
- Lượt trận đầy đủ đã được chuyển sang bản này khi còn chờ CPU. Nhật ký, nhãn đối chiếu và log replay nằm trong `/workspace/scratch/tft-hud-optimization/contrast-retry.json` và các tệp cùng thư mục. Mục tiêu 100% toàn trận và trên thiết bị thật vẫn đang mở.

## Đọc trước khung hình khi replay

- Bản `af62626a1074d621` đọc trước một khung RGB trong khi OCR xử lý khung hiện tại. Trên clip 720p, p95 chờ khung giảm từ 97 ms xuống 17 ms và p95 toàn lượt giảm từ 253 ms xuống 194 ms. Trên clip 1080p, hai số tương ứng là 133 xuống 62 ms và 287 xuống 227 ms. Các phép đo ghi lại tải nền ở đầu và cuối lượt vì số job nền có thay đổi trong phép đo 1080p.
- Bản mới xử lý đủ 294 mẫu ở 4 Hz và khớp đầu ra bản cũ trên 293 mốc cả hai cùng đọc. Kiểm tra gây trễ có chủ ý đã xác minh số khung và dữ liệu vẫn khớp khi bỏ một mẫu. Báo cáo `/workspace/scratch/tft-hud-optimization/prefetch-replay.json` giữ số vượt 250 ms cùng nhật ký nén. Đã chạy đạt 42 bài Node và 11 bài Python, gồm chế độ dừng sau khung đầu `--once`.
- Đã cập nhật bản cho lượt 45 phút khi lượt này còn chờ. `campaign/run-native-match23.py` quyết định khởi động dựa trên tải CPU dưới 90% và RAM làm việc dưới 90% giới hạn. Số lượt nền và tải CPU lúc vào trận được ghi vào `native-match23.json`.

## Giảm dữ liệu khung truyền qua FFmpeg

- Bản `2d1b7847130af4b1` chỉ truyền vùng bao quanh HUD sau khi FFmpeg chuyển khung sang RGB. So sánh từng pixel trên 8 khung mỗi độ phân giải đều khớp. Lượng byte qua pipe giảm khoảng 89%, và `resolution` vẫn là kích thước gốc.
- Hai clip xử lý đủ 286 mẫu ở 4 Hz, với đầu ra OCR giống bản trước tại cả 286 mốc. p95 chờ khung giảm từ 25 xuống 11 ms ở 720p và từ 65 xuống 14 ms ở 1080p. p95 đầu-cuối ở 720p tăng từ 186 lên 205 ms, còn ở 1080p giảm từ 154 xuống 141 ms trong hai lượt thử. Xem `/workspace/scratch/tft-hud-optimization/roi-replay.json`. Đã chạy đạt 42 bài Node, 11 bài Python và phép kiểm tra giữ đúng số khung khi có một mẫu bị bỏ.
- Lượt 45 phút tiếp tục bằng bản đã ghim `af62626a1074d621`. Qua khoảng 8 phút, đã ghi 1.924 mẫu, chưa bỏ mẫu, p95 218 ms và có 70 mẫu vượt 250 ms. OCR là phần chiếm nhiều thời gian nhất ở 44 mẫu trễ. Kết quả này đo trên đoạn đầu của trận.
