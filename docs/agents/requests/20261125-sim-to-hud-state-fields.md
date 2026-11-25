# Yêu cầu: HP, bàn và bàn chờ cho mô hình và harness đánh giá

dataset: các đoạn VOD Set 18 đã có log OCR (nhánh `claude/hud-data-set18` @ `1b4c468`, 23 file, 174.492 mẫu, schema 2). Cùng khóa `VOD-startSec`, cùng lịch 4 Hz.
fields:
- `hp`: HP của người chơi (0–100), kèm `confidence` và `src`.
- `board`: tướng trên bàn, mỗi phần tử `{champion_api, star}`, khớp mẫu icon theo round, `src: template`.
- `bench`: tướng trên bàn chờ, cùng cấu trúc.
- Không yêu cầu `stage`, `timer`, `gold`, `level`, `xp`, `streak`: đã có trong `fields4` (xem `docs/agents/requests/20261124-user-to-hud-fields4-status.md`, status mở, do `hud` xử lý).
- Không yêu cầu HP và bàn của đối thủ: không có nguồn đã biết.
schema: hudSchema 3 (tăng phiên bản theo data-contracts mục 3). Schema 2 giữ nguyên để đọc file cũ.
why: `universal_features_v4` cần HP và bàn. Các trường economy hiện có không đủ để dựng trạng thái đầy đủ cho `decide.js` (đầu vào mặc định `hp`=0 nếu thiếu, sai nghĩa). Không có HP và bàn, không đo được tỷ lệ đồng ý của `decide.js` trên trận thật.
unblocks: harness Phase 4 (đo tỷ lệ đồng ý), huấn luyện mô hình sim trên đầu vào thật.
deadline:
status: mở
