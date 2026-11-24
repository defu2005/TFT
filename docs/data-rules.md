# Quy tắc dữ liệu

Cập nhật: 2026-11-24. File này là nguồn chuẩn. Mọi agent thu thập hoặc làm sạch phải đọc file này trước khi tải thêm bất kỳ nguồn nào. Nguồn chưa được ghi trong `docs/agents/sources/` (mục 5) thì không được tải.

## 1. Trường dữ liệu cần thu

Mỗi trường có một đọc viên chính, tần suất lấy mẫu và nguồn kiểm chứng.

| Nhóm | Trường | Đọc viên chính | Tần suất | Ghi chú |
|---|---|---|---|---|
| Kinh tế | vàng, cấp, 5 ô shop, giá từng ô | OCR (`hud_ocr.py`) | 1–4 Hz | Đang có. Cần thêm trường confidence vào bản ghi đầu ra. |
| Kinh tế | odds theo cấp (5 tỷ lệ), XP `x/y` | OCR, vùng mới | theo round | Chưa có. I11 phía HUD. |
| Giai đoạn | stage, round, phase | OCR trên nhãn vùng cố định, đối chiếu thời gian trận | theo round | Cần kiểm chứng nhãn. |
| Người chơi | HP, streak | OCR trên vùng cố định | theo round | Chưa có vùng đọc. |
| Đội hình | tướng trên bàn, bàn chờ | khớp mẫu icon (template) trước, model chỉ đọc phần còn lại | một lần mỗi round | CDragon có icon TFT (`assets/maps/tft/icons/`, định dạng `.tex`, cần chuyển đổi). |
| Trang bị | item trên tướng | khớp mẫu icon | một lần mỗi round | Như trên. |
| Augment | augment đã chọn, lựa chọn đang hiện | khớp mẫu icon, OCR trên tên | theo sự kiện | Chưa có. |
| Đối thủ | HP và bàn của 7 người còn lại | chưa có nguồn đọc | — | Ghi là không có nguồn, không suy đoán. |
| Kết quả | thứ hạng cuối | màn hình kết thúc | một lần mỗi trận | Dùng để gắn nhãn kết quả trận. |
| Ngữ cảnh | set, patch, mùa, streamer, độ phân giải, bố cục | metadata nguồn | một lần mỗi nguồn | Bắt buộc có để lọc sau này. |

Trường nào không có đọc viên được ghi là "không có nguồn". Không được điền giá trị suy đoán cho các trường này.

## 2. Schema và nguồn gốc (provenance)

- Mỗi giá trị đi kèm `src`: `ocr`, `model`, hoặc `template`. Một giá trị do model đọc **không bao giờ được ghi đè** giá trị đã được OCR xác nhận.
- Mỗi giá trị có cờ null khi không đọc được. Không thay bằng 0, 1 hay giá trị đoán.
- Giữ giá trị thô cạnh giá trị đã làm sạch.
- Mỗi dòng có: set, patch, streamer, độ phân giải, phiên bản OCR (commit), mã băm profile, mã băm catalog.
- Dòng có `schemaVersion`. Thay đổi schema phải tăng phiên bản.

## 3. Ngưỡng chất lượng

- **Chấp nhận một giá trị** khi nó ổn định qua `k` mẫu liên tiếp (giá trị ban đầu của `k` do pilot quyết định). Giá trị chập chờn được ghi là chập chờn, không được sửa âm thầm.
- **Giá phải nhất quán với bậc tướng** trong catalog của set. Vi phạm thì từ chối và ghi lý do.
- **ID tướng phải có trong catalog** của set đó. ID lạ được ghi vào danh sách chờ, không đoán.
- **Model fallback chỉ được dùng khi OCR không đạt ngưỡng.** Tỷ lệ fallback là một chỉ số: nếu tăng đột biến, đó là dấu hiệu bố cục mới, phải hiệu chỉnh lại trước khi tiếp tục.
- **Ngưỡng sai tự tin** (giá trị có cờ chắc chắn nhưng sai) do lượt audit đo. Chưa đo thì chưa được kết luận về độ chính xác.

## 4. Quy tắc nguồn

- **Phân vùng streamer.** Mỗi agent thu thập sở hữu một tập streamer riêng, không chồng lấp. Đây là cách duy nhất chắc chắn tránh hai agent tải trùng VOD vì không thấy nhau.
- **Claim theo từng VOD.** Trước khi tải, tạo `docs/agents/sources/<vodId>-<startSec>.md` trên nhánh của mình, ghi trạng thái `đang tải`. Sau đó quét mọi nhánh đã push để chắc không có claim trùng.
- **Không tải nguồn chưa claim** và không tải nguồn đã có trong ledger.
- **Lịch sự với nguồn:** giới hạn tốc độ tải, không song song quá số luồng đã cấu hình, không gọi API công khai dồn dập.
- **Không lưu thông tin nhận dạng cá nhân** (tên người chơi thật, Riot ID, PUUID) vào log hay tài liệu. Tên trên màn hình không được ghi nếu không cần thiết cho việc đọc.
- **Chỉ lưu vùng crop của HUD**, không lưu khung đầy đủ, không lưu MP4, không lưu URL media đã ký.
- **Mọi nguồn phải có ghi chú điều khoản** trong ledger. Chưa có ghi chú thì chưa được thu.
- PBE thuộc diện riêng: chỉ thu trong phần được gắn nhãn PBE, và điều khoản của Riot cho PBE chưa được kiểm chứng.

## 5. Sổ nguồn (ledger)

- Thư mục: `docs/agents/sources/`. Mỗi VOD một file claim.
- Trường bắt buộc: nguồn, streamer, set, patch, khoảng thời gian, người claim, trạng thái (`đang tải`, `đã thu`, `đã làm sạch`, `từ chối`), lý do từ chối nếu có, số mẫu, số mẫu bị bỏ, tỷ lệ fallback, commit đã giao.
- Trạng thái chỉ được đổi bởi chính agent đã claim, trên nhánh của mình.

## 6. Trần (caps)

Các trần này là bắt buộc. Không có "không dừng" nào được vượt qua chúng.

- **Chi phí API:** trần USD mỗi ngày, do người dùng đặt (mục quyết định).
- **Dung lượng đĩa:** trần GiB cho scratch, theo `RESERVE_BYTES` đã có trong `run.py`.
- **Số mẫu fallback mỗi trận:** trần, để một trận lỗi không đốt hết ngân sách.
- **Số lần thử lại mỗi nguồn:** tối đa 2.

Khi chạm bất kỳ trần nào, hàng đợi dừng và ghi lý do vào trạng thái. Không tự nới trần.

## 7. Điều kiện dừng bắt buộc

- Trần chi phí, đĩa, fallback bị vượt.
- Tỷ lệ fallback tăng đột biến (bố cục mới).
- Lượt audit thất bại (tỷ lệ sai tự tin vượt ngưỡng đã định).
- Nguồn trả lỗi liên tục (có thể là đã bị gỡ hoặc giới hạn tốc độ).

## 8. Dữ liệu huấn luyện

- Log trạng thái không phải nhãn huấn luyện. Chuyển trạng thái thành nhãn hành động là việc của phiên mô hình chuyên trách, theo quy tắc riêng.
- Mỗi mẫu được gắn set và patch để lọc.
- Dữ liệu mùa cũ chỉ chuyển được sang kinh tế, không chuyển đội hình.
