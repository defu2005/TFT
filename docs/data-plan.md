# Kế hoạch thu thập và làm sạch dữ liệu

Cập nhật: 2026-11-24. Trạng thái đã kiểm tra: `hud` chưa trả lời yêu cầu `docs/agents/requests/20261124-user-to-hud-vod-sample-logs.md`. Không có file `responses/` hay `contracts/` nào trên bất kỳ nhánh nào. Log theo mẫu chưa có trong repo.

## 1. Mục tiêu

Có một tập dữ liệu trạng thái theo thời gian từ VOD streamer, đã làm sạch, có chỉ số nhiễu nhãn đo được, và đủ rõ để phiên mô hình chuyên trách suy ra hành động (mua, roll, lên cấp) từ các chuyển trạng thái.

Phạm vi của kế hoạch này dừng ở dữ liệu trạng thái. Việc suy hành động thành nhãn huấn luyện thuộc phiên mô hình chuyên trách.

## 2. Phụ thuộc quan trọng

**Codex (`hud`) là lane duy nhất có thể thu thập dữ liệu.** Mọi lane khác đều chờ đầu ra của `hud`. Vì vậy kế hoạch yêu cầu `hud` giao **một trận trước** làm mẫu để lane làm sạch bắt đầu ngay, không chờ toàn bộ.

## 3. Lane

Mỗi agent có một lane, không chia sẻ file nóng. Không có phiên nào sửa file của lane khác.

| Agent | ID | Việc | Đầu ra | Cổng mở |
|---|---|---|---|---|
| Codex | `hud` (có sẵn) | Trả lời yêu cầu. Giao **1 trận mẫu trước**, rồi toàn bộ. Thêm tham số set cho `hud_ocr.py` thay vì `set18-hud.json` cố định. Xuất **vùng HUD đã cắt** của 16 khung audit, không xuất khung đầy đủ. | `.jsonl.gz`, manifest có sha256, commit OCR, mã băm profile, ảnh cắt | G0 |
| Claude, phiên mới | `data` (mới) | Xây pipeline làm sạch theo đặc tả ở mục 5, có test. Chạy trên mẫu rồi trên toàn bộ. | Dữ liệu sạch và báo cáo chất lượng theo trận | G1 |
| Claude, phiên mới, có thị giác | `label` (mới) | Gán nhãn mù các ảnh cắt, không xem kết quả OCR. Lượt thứ hai cho các chỗ bất đồng. | Độ phủ và tỷ lệ sai tự tin theo từng trường | G2 |
| Cursor | vai trò `engine`, chỉ catalog | Catalog theo set cho các mùa cũ, lấy từ snapshot CDragon có phiên bản. Ánh xạ `TFT17_*` và ID cũ. Dump hiện tại chỉ có set 3, 7, 16, 17, 18. | `src/data/catalogs/<set>.json` | G3 |
| Phiên này | điều phối | Đặc tả, quét nhánh, review, PR | — | — |

**Người viết OCR không được gán nhãn.** Số đo độ chính xác phải độc lập với bộ đọc đang đo.

## 4. Cổng

- **G0:** log đã bền. `hud` đặt `status: đã giao` kèm commit, đường dẫn và schema trong `docs/agents/responses/`.
- **G1:** báo cáo làm sạch đạt trên mẫu một trận. Mọi quy tắc đều có bộ đếm từ chối.
- **G2:** có số nhiễu nhãn theo từng trường: tỷ lệ phủ và tỷ lệ sai tự tin.
- **G3:** thu thập mở rộng được: catalog mùa cũ có sẵn, và phần PBE được gắn nhãn riêng.

**Không mở rộng trước G1 và G2.** Trong lúc chờ, `hud` có thể tiếp tục xử lý backlog nhưng không thêm bố cục streamer mới.

## 5. Đặc tả làm sạch (cho lane `data`)

1. **Kiểm tra header và từng dòng.** Từ chối file không có commit OCR hoặc mã băm profile. Từ chối dòng sai schema và ghi lý do.
2. **Phân đoạn trận.** Chỉ giữ mẫu trong trận, dựa trên tín hiệu HUD đã xác nhận. Loại mẫu khởi động (warm-up). Đánh dấu `deadlineMissed`.
3. **Kiểm tra miền giá trị và catalog.** ID phải có trong catalog của set đó. Giá phải nhất quán với bậc tướng (`price` nằm trong khoảng hợp lý của `cost`).
4. **Đồng thuận theo thời gian.** Chỉ chấp nhận một giá trị khi nó ổn định qua `k` mẫu liên tiếp. Ghi nhận các giá trị chập chờn. **Không sửa âm thầm.**
5. **Không bổ sung giá trị.** Giữ null cùng cờ của nó. Giữ giá trị thô bên cạnh giá trị đã làm sạch.
6. **Khử trùng lặp** theo ID VOD cộng khoảng thời gian.
7. **Gắn nhãn cho mỗi dòng:** set, patch, streamer, độ phân giải, phiên bản OCR, mã băm profile.
8. **Đầu ra:**
   - dữ liệu đã làm sạch;
   - bảng **chênh lệch trạng thái** giữa các mẫu liên tiếp, xác định (deterministic);
   - báo cáo theo trận: độ phủ theo từng trường, và số lần từ chối theo từng quy tắc.
9. **Ranh giới:** chuyển chênh lệch thành nhãn mua, roll, lên cấp thuộc về phiên mô hình chuyên trách. Lane `data` không làm bước này.

## 6. Tiêu chí chấp nhận

- Chạy lại cho cùng đầu vào cho đầu ra giống hệt nhau.
- Mỗi quy tắc có ít nhất một test có dữ liệu cố ý sai.
- Báo cáo mẫu đạt: không có quy tắc nào từ chối quá tỷ lệ đã định trước, và không có trường nào bị sửa âm thầm.

## 7. Mức model

Chọn theo việc, không xếp hạng model mà không kiểm chứng được:

- **Viết đặc tả, review, xử lý xung đột:** mức mạnh nhất người dùng có. Phiên điều phối hiện chạy trên model Haiku 5.5. Với việc này, nên chuyển sang model mạnh hơn hoặc tạo lại phiên điều phối.
- **Pipeline làm sạch (`data`):** Python có đặc tả rõ, có test. Sonnet 5.5 đủ. Chất lượng đặc tả quan trọng hơn kích thước model.
- **Gán nhãn thị giác (`label`):** model Opus 5.5 hoặc mức có thị giác mạnh nhất. Lỗi nhãn làm sai chính chỉ số đang đo.
- **Kiểm tra cơ học (manifest, sha256, định dạng):** Haiku 5.5.
- **Codex và Cursor:** dùng model lập trình mạnh nhất người dùng đang có. Phiên này không biết tên model của hai bên nên không ghi.

## 8. Lộ trình

1. Yêu cầu `hud`: trận mẫu trước, sau đó toàn bộ, kèm crop 16 khung audit. Đã cập nhật trong yêu cầu.
2. Lane `data` và `label` bắt đầu khi có G0 (trận mẫu).
3. Lane `engine` (Cursor) làm catalog song song, không phụ thuộc G0.
4. G1, G2 đo trên mẫu. Quyết định mở rộng sau khi có G1 và G2.

## 9. Prompt cho từng agent

Codex và Cursor không khởi chạy được từ phiên này, nên người dùng dán prompt dưới đây. Mỗi prompt tự đủ thông tin.

**Codex (`hud`):**
> Đọc `docs/agents/README.md` và `docs/agents/data-contracts.md` trên `origin/master`. Làm việc trên nhánh đã được giao cho phiên này. Quét `docs/agents/requests/` trên mọi nhánh đã push để tìm yêu cầu `-to-hud-`, rồi làm theo `docs/agents/requests/20261124-user-to-hud-vod-sample-logs.md`. Thứ tự: (1) ước tính dung lượng; (2) giao một trận mẫu, ghi `status: đã giao` trong `docs/agents/responses/`; (3) giao toàn bộ kèm manifest sha256; (4) thêm tham số set cho `scripts/hud_ocr.py`; (5) xuất vùng HUD đã cắt của 16 khung audit. Không đưa thông tin nhận dạng cá nhân vào log. Không commit MP4 hay ảnh khung đầy đủ.

**Cursor (catalog):**
> Đọc `docs/agents/README.md` và `docs/data-plan.md` (mục 3, lane `engine`) trên `origin/master`. Làm việc trên nhánh đã được giao. Tạo catalog theo set trong `src/data/catalogs/<set>.json` từ snapshot CDragon có phiên bản ghi rõ. Chỉ dùng các set có trong dump (3, 7, 16, 17, 18). Ánh xạ `TFT17_*` và ID cũ, ghi rõ ánh xạ nào không chắc. Không sửa `src/engine/` hay `src/ingest/`. Không đoán ID thiếu.

**Claude, phiên `data`:**
> Đọc `docs/agents/README.md` và `docs/data-plan.md` mục 5 trên `origin/master`. Làm việc trên nhánh được giao. Xây pipeline làm sạch theo đặc tả mục 5, có test cho từng quy tắc. Chạy trên mẫu một trận khi có, rồi trên toàn bộ. Xuất dữ liệu sạch, bảng chênh lệch trạng thái và báo cáo theo trận. Không gán nhãn hành động. Không bổ sung giá trị thiếu.

**Claude, phiên `label`:**
> Đọc `docs/agents/README.md` và `docs/data-plan.md` mục 4 (G2) trên `origin/master`. Làm việc trên nhánh được giao. Gán nhãn mù các ảnh cắt HUD trong thư mục đã được giao: gold, level, từng ô shop và giá. Không xem đầu ra OCR. Ghi nhãn và độ tin cậy của bạn vào file riêng. Sau đó lượt thứ hai cho các chỗ bất đồng. Báo cáo tỷ lệ phủ và tỷ lệ sai tự tin theo từng trường.

## 10. Việc cần làm ngay

- Thêm `data` và `label` vào bảng ID trong `docs/agents/ownership.md` và `docs/agents/data-contracts.md` mục 1.
- Cập nhật yêu cầu `hud` để hỏi trận mẫu trước và crop ảnh audit.
- Người dùng thêm dòng vào `docs/agents/claims.md` trên `master` khi khởi chạy từng agent.
- PBE: điều khoản của Riot chưa được kiểm chứng. Không mở rộng sang PBE trước G3.
