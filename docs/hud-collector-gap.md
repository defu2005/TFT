# Khoảng trống bộ thu thập HUD so với file sim

Mục tiêu "100%" được định nghĩa để kiểm tra được: trên một trận có nhãn giữ riêng, số giá trị sai bằng 0 trong các giá trị bộ thu thập phát ra. Giá trị không xác nhận được thì ghi là chưa giải và đưa vào hàng chờ cho agent. Độ phủ báo riêng. Không có số liệu nào được gọi là độ chính xác nếu chưa có nhãn.

Nguồn: `docs/hud-reader.md` (trường bộ đọc phát ra), `data/hud-audit/match01_full.json` (cách đã chứng minh bằng tay trên trận 01), `data/hud-audit/blind_oos28_rates.json` và các số đo đọc lại mù trong `docs/sim/match01-rounds.md`.

| Trường trong file sim | Bộ đọc hiện tại phát ra | Phương pháp đã chứng minh trên trận 01 | Độ đúng đo được | Việc cần làm |
|---|---|---|---|---|
| HP 8 người theo thời gian | Không thấy trường HP trong `hud_ocr.py` / `hud-reader.py` | HP đọc từ rail, 38/38 vòng, 8 giá trị mỗi vòng | Chưa đo. Một lần kiểm tra thấy 39 thay vì 59 | Thêm trường HP có nhãn; đo trên nhãn mù |
| Stage/round | Có `stage` trong `hud-reader.py` | Bảng stage đơn điệu từ đọc thanh stage | Chưa đo độc lập | Đo trên nhãn mù |
| Timer | Không thấy trường timer trong bộ đọc | Đọc từ hộp timer, 28/38 vòng | Chưa đo | Thêm trường timer |
| Vàng | Có (`gold`, đọc chỉ số) | Đọc lại mù | Trong mẫu 10/10; ngoài mẫu 13/16 (3 khung không có ô vàng) | Giữ; đo thêm |
| Cấp | Có (`level`) | Đọc lại mù | Trong mẫu 10/10; ngoài mẫu 11/15 | Đo thêm, sửa lỗi OCR (13 thay cho 5 ở 2-6) |
| XP | Có (`xp`) | Đọc lại mù | Trong mẫu 10/10; ngoài mẫu 13/14 | Giữ; đo thêm |
| Streak | Không thấy trường streak | Đọc từ badge; 24/38 vòng | Ngoài mẫu 4/14; lỗi chủ yếu OCR trả rỗng khi đúng là 1 | Cần bộ đọc riêng và đo lại |
| Bàn (tướng và số) | Có `board` trong `hud-reader.py` | Suy ra từ panel và phép giải; 33 vòng suy ra, 5 chưa giải | Chưa đo | Đo trên nhãn mù |
| Bàn chờ (bench) | Không thấy trường bench | Đếm sprite bằng mắt; 25 vòng, độ tin cậy thấp | Chưa đo | Cần bộ đọc và nhãn |
| Sao của tướng | Không rõ (`star` chỉ thấy trong ngữ cảnh khác) | Không đọc được ở 720p; 2/38 vòng | Không có | Đọc ở 1080p; cần thử nghiệm đọc |
| Trang bị | Không rõ (`item` chỉ thấy trong ngữ cảnh khác) | Không đọc được ở 720p; 2/38 vòng | Không có | Đọc ở 1080p; cần thử nghiệm đọc |
| Augment kèm tier | Không thấy | Chỉ có ở vòng có màn chọn; 3/38 vòng | Không có | Cần bộ đọc và nhãn |
| Kết quả combat từng round | Không thấy | Suy ra từ màu biểu tượng, 33/38 vòng | Chưa đo | Đo trên nhãn mù |
| Thứ hạng cuối trận | Không thấy | Suy ra từ thứ tự rail, 8 vị trí | Chưa đo | Đo trên nhiều trận |
| HP của đối thủ | Không thấy | Cùng trường HP 8 người | Chưa đo | Như dòng HP |
| Đối thủ (mã P) | Không thấy | Đọc tên qua tooltip và nameplate, so với bảng alias riêng | Không đo | Cần bộ đọc và nhãn |
| Log set thứ hai | Không có | Không có | Không có | Ngoài phạm vi trận này |

## Kết luận

- Bộ đọc hiện tại phát ra vàng, cấp, XP, tên tướng và cửa hàng, cùng `hudSchema` và `oddsRow`. Hầu hết trường sim chưa có.
- Chỉ vàng, cấp, XP có tỉ lệ đo được, và chỉ trong mẫu nhỏ.
- Các trường lớn nhất còn thiếu: HP, streak, timer, bàn chờ, sao, trang bị, augment, kết quả combat, đối thủ.
- Đường đi để có 100% độ đúng là đo trên nhãn mù từng trường, không phải tuyên bố.
