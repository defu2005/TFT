# Bộ đọc HUD Set 18

Bộ đọc lấy vàng, cấp và tên tướng từ chữ trên HUD qua Tesseract. Lượt đầu gộp các vùng cắt theo viewport vào một lần gọi OCR. Tên tướng được đối chiếu với [danh mục Set 18](../src/data/set18-hud.json). Vùng cấp được đọc với hai cách lọc ảnh. Hai kết quả yếu có thể xác nhận cấp nếu cùng đọc được một nhãn và giá trị hợp lệ. Nếu hai cách đọc ra số khác nhau, cấp được đánh dấu chưa xác định. Bậc giá của tướng lấy từ danh mục tham chiếu. ID đã có trong dự án được giữ để khớp snapshot. Các ID còn lại lấy từ khóa ảnh công khai và cần đối chiếu với snapshot thật nếu dùng để tính số bản sở hữu.

Khi lượt đầu nhận ra một phần HUD, bộ đọc có thể đọc lại riêng ô vàng bằng chế độ chỉ nhận chữ số. Các vùng cấp hoặc tên tướng chưa rõ được đọc lại theo từng dòng để giảm ảnh hưởng của chữ ở vùng lân cận. Khi cả vàng lẫn cấp đã được xác nhận, bước đọc lại cũng dùng ngưỡng tương phản thấp hơn cho ô tướng bị làm tối trong hiệu ứng chuyển cảnh.

Trường tùy chọn `oddsRow` (I11): năm số theo phần trăm của hàng odds đang hiển thị cho cấp hiện tại, tổng 100 ± 1. Thiếu hoặc không hợp lệ là chưa đọc (engine coi là `null`). Engine so hàng này với hồ sơ đang dùng và ghi `reason.factors.oddsMismatch`; không đổi quyết định. Trường `xp` (`{current, needed}`) được định nghĩa ở đây nhưng engine chưa đọc (I4).

Bản ghi `hudSchema: 2` xác nhận HUD nếu có ít nhất hai nhóm tín hiệu trong ba nhóm vàng, cấp và cửa hàng. Cửa hàng cần ít nhất hai tên tướng nhận dạng được để làm tín hiệu. Từng trường chưa đọc được vẫn là `null`. Trong `shopSlots`, `null` cũng có thể là ô trống hoặc thẻ Wisp. `shop` trong bản ghi OCR chỉ có dữ liệu khi xác nhận đủ năm tướng.

Nguồn standalone nhận bản ghi từ cửa sổ thật trong vòng hai giây. Với bản ghi phiên bản 2, coach chỉ xét mua những ô đã đọc được khi đã xác nhận số vàng. `cost` là bậc tướng trong danh mục để tính xác suất. `price` là số vàng hiển thị trên thẻ để xét đủ vàng và tính lãi bị mất. Khi `price` là `null`, coach giữ tên tướng và bỏ qua đề xuất mua ô đó. Bản ghi cũ không có trường `price` dùng bậc tướng như trước. `shopUnknownSlots` liệt kê các chỉ số ô chưa xác định, tính từ 0. Khi chưa xác nhận được cấp, coach có thể xét mua các ô đã đọc và để trống xác suất gặp tướng. Đề xuất lên cấp hoặc roll cần xác nhận cả vàng lẫn cấp.

## Chạy

Cài Python 3.10 trở lên, Pillow và Tesseract 5 với gói ngôn ngữ của client. Chụp cửa sổ cần Windows 10/11 và `pywin32`. Chế độ video cần FFmpeg và FFprobe.

```bash
python -m pip install Pillow
# Chỉ trên Windows
python -m pip install pywin32
```

Chạy hai tiến trình từ thư mục gốc dự án trên máy Windows đang mở TFT:

```bash
npm run hud -- --interval 0.25
npm run start:live
```

Tiến trình HUD thay thế file `captures/hud-live.json` bằng thao tác atomic. Mỗi mẫu có một dòng JSON trên stdout. Để thử ảnh hoặc phát video theo thời gian thực trên Linux hay Windows:

```bash
python scripts/hud-reader.py --image frame.png
python scripts/hud-reader.py --video match.mp4 --interval 0.25 > hud-video.jsonl
```

Nếu `PrintWindow` trả ảnh đen trên thiết bị chạy game, thử `npm run hud -- --capture screen`. Chế độ này chỉ đọc vùng client khi cửa sổ TFT ở foreground. Giữ vùng game không bị overlay hoặc cửa sổ khác che.

Có thể dùng `--profile profile.json` để chỉnh vùng theo HUD của thiết bị. `viewport` là hình chữ nhật chứa game trên ảnh đã chụp, còn các vùng `gold`, `level` và năm vùng `shop` nằm bên trong viewport. Tọa độ có dạng `[trái, trên, phải, dưới]` và nằm trong khoảng 0–1. Ví dụ, ghi `{"viewport":[0.125,0,0.875,1]}` cho video 2560×1080 chứa game 1920×1080 ở chính giữa. Tọa độ mặc định được hiệu chỉnh trên VOD desktop Set 18 của Setsuko ở 720p và thử lại trên VOD BoxBox ở 1080p. Nếu bố cục hoặc tỉ lệ HUD thay đổi, đo lại từng vùng theo ảnh mẫu. Có thể cấu hình `level_labels` và `aliases` (tên hiển thị theo ngôn ngữ → tên trong danh mục), cùng `--language` cho Tesseract. Bản mobile cần ảnh hoặc video và profile riêng.

Năm vùng `shop_price` bao quanh số giá ở bên phải mỗi thẻ. Khi chỉnh tọa độ `shop`, hãy khai báo cả `shop_price` để bộ đọc dùng đúng bố cục. `shop_price: null` tắt đọc giá cho bố cục đó.

Hàng đợi dùng tọa độ mặc định khi nguồn không khai báo `profile`. Chỉ thêm tên tệp JSON vào `profile` sau khi kiểm tra vị trí trên ảnh gốc của nguồn. `scripts/hud-campaign/profile-1080p.json` là vùng giá đã hiệu chỉnh cho một bố cục BoxBox. Áp vùng đó cho video Setsuko 1080p sẽ cắt một phần chữ số. Báo cáo giữ mã băm và bản sao của profile đã dùng.

## Đo độ trễ và kiểm thử

Trên Linux với `/usr/bin/tesseract` và thư viện `libtesseract`, bộ đọc dùng lại một phiên OCR cho mỗi luồng xử lý. Khi thư viện không sẵn sàng, bộ đọc gọi Tesseract qua dòng lệnh. Truyền `--tesseract /usr/bin/tesseract` để đo lại bằng tiến trình riêng cho mỗi lượt nhận dạng.

Bộ đọc bỏ lượt OCR giá ở ô có mặt nạ tên trống và độ sáng dưới ngưỡng thử đọc lại tên. Giá của ô đó giữ `null`.

- `captureLatencyMs` đo bước lấy ảnh hoặc đọc khung hình đã giải mã. `recognitionLatencyMs` đo tiền xử lý, OCR và đối chiếu danh mục.
- Khi phát lại video, bộ đọc nhận trước tối đa một khung RGB để giảm thời gian chờ FFmpeg ở mốc lấy mẫu kế tiếp. Bộ OCR vẫn đọc theo lịch và ghép kết quả với `mediaTimeMs` của đúng khung.
- FFmpeg chuyển khung sang RGB rồi chỉ gửi hình chữ nhật chứa các vùng OCR trong profile. `resolution` trong bản ghi giữ kích thước video gốc. Tọa độ OCR vẫn tính từ viewport gốc, kể cả khi có viền đen.
- `endToEndLatencyMs` đo từ lịch dự kiến tới khi nhận dạng xong. `publishLatencyMs` trong stdout đo riêng thời gian ghi file khi bật đầu ra file. Hai số này không bao gồm thời gian coach chờ tick kế tiếp.
- So sánh `deadlineMissed` và `droppedFrames` với chu kỳ. Với video, `mediaTimeMs` cho biết mốc cần đối chiếu với hình gốc. Nếu xử lý chậm, bộ đọc bỏ qua mẫu cũ để bắt kịp nhịp phát.
- Mẫu video đầu tiên ghi nhận cả thời gian khởi động bộ giải mã. Đồng hồ phát bắt đầu sau kết quả đầu tiên để độ trễ khởi động không làm mất các mẫu kế tiếp.

Bài kiểm thử mặc định kiểm tra parser. Để chạy cả OCR và video, lấy [ảnh tile Set 18 tại commit đã ghim](https://github.com/kokoforme1987-cmd/tft-set18-assets/tree/cd0655631cba5b59782d7670b62c25004e59f7dc), tải ZIP và truyền đường dẫn dưới đây. Các bài kiểm thử ảnh cần font DejaVu Sans Bold. Ảnh tướng đến từ bộ ảnh Set 18, còn sàn, linh thú và bố cục kiểm thử được dựng. Bộ kiểm thử bao gồm 1080p, 720p, ultrawide có viền, đổi sàn và linh thú, số vàng bằng 0, ô trống, HUD bị che và video đổi shop theo thời gian.

```bash
TFT_SET18_ART_ZIP=/path/to/set18-assets.zip python scripts/test_hud_ocr.py -v
npm test
```

Để kiểm chứng client Set 18 thật, dùng clip có HUD hiển thị rõ và ghi tay vàng, cấp cùng năm ô tại các mốc trong clip. Chạy chế độ video, đối chiếu đầu ra tại từng `mediaTimeMs`, ghi tỷ lệ đọc đúng của từng trường và tỷ lệ bỏ mẫu. Lặp lại trên các độ phân giải, DPI, tỉ lệ HUD, ngôn ngữ, sàn và linh thú cần hỗ trợ. Đo lại bằng cửa sổ Windows để kiểm tra bước `PrintWindow`, với các tình huống như đổi cửa sổ, thu nhỏ và chuyển màn hình.
