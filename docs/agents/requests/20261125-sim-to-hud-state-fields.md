# Yêu cầu: trường trạng thái trận cho mô hình và harness đánh giá

dataset: log OCR schema 3 cho các đoạn VOD Set 18 đã có (nhánh `claude/hud-data-set18` @ `1b4c468`, 23 file, 174.492 mẫu). Cùng khóa `VOD-startSec`, cùng lịch 4 Hz.
fields:
- `stage`: chuỗi dạng `X-Y` (stage-round), đọc từ nhãn cố định, kèm `confidence` và `src`.
- `hp`: HP của người chơi (số nguyên, 0–100), kèm `confidence` và `src`.
- `board`: danh sách tướng trên bàn, mỗi phần tử `{champion_api, star, slot}`, khớp mẫu icon theo round (không theo từng mẫu), kèm `src: template`.
- `bench`: danh sách tướng trên bàn chờ, cùng cấu trúc.
- `items` (tùy chọn, sau): trang bị trên từng tướng trên bàn, khớp mẫu icon.
- Không yêu cầu: HP và bàn của đối thủ (không có nguồn đã biết; data-rules ghi "không có nguồn, không suy đoán").
schema: hudSchema 3 (tăng phiên bản theo data-contracts mục 3). Schema 2 giữ nguyên để đọc các file cũ.
why: sim cần `universal_features_v4` (cần HP, stage, bàn, bàn chờ). Log schema 2 chỉ có vàng, cấp, cửa hàng. Không có các trường này, không dựng được trạng thái để đo tỷ lệ đồng ý của `decide.js` (baseline, harness Phase 4) và không huấn luyện được mô hình nào chạy trên đầu vào thật.
unblocks: Phase 4 mục 2–3 (harness đánh giá, U8 calibrate). Phase 5 của sim.
deadline:
status: mở
