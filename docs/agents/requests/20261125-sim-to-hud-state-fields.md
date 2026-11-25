# Yêu cầu: dữ liệu HUD theo thứ tự mở khóa cho mô hình

dataset: các đoạn VOD Set 18 đã có log OCR (nhánh `claude/hud-data-set18` @ `1b4c468`, 23 file, 174.492 mẫu, schema 2, 7 VOD). Cùng khóa `VOD-startSec`, cùng lịch 4 Hz.
fields: theo thứ tự ưu tiên dưới đây. Mỗi trường kèm `confidence` và `src`. Không đọc được thì ghi `null`, không ghi 0.
  1. `stage` (đã có trong `fields4`, do hud xử lý) và `hp` (0–100) của người chơi mình.
  2. `placement` (thứ hạng cuối 1–8), một số cho mỗi trận, kèm nguồn đọc (màn kết thúc hoặc bảng cuối). Hiện chỉ có 1 trận nháp (streamer 2/8, `docs/agents/responses/20261124-hud-match01-result.md`).
  3. `board` (tướng trên bàn, `{champion_api, star}`, `src: template`) và `bench` (cùng cấu trúc). Lưu ý nhánh hud ghi tên tướng trên bàn không đọc được ở 720p: cần xác nhận độ phân giải hoặc icon matching trước khi cam kết lịch.
  4. Kết quả combat từng round (thắng/thua; sát thương nếu có).
  5. `items` và `augments` (kèm tier nếu đọc được).
  6. `hp` đối thủ: hiện chỉ có 6 mẫu nhãn bằng mắt (`data/hud-audit/hp_labels_6.jsonl`, nhánh nifty). Chờ hud xác nhận nguồn trước khi yêu cầu đầy đủ. Không yêu cầu OCR đối thủ lúc này.
  7. Log của set thứ hai (ràng buộc chính: mọi dữ liệu hiện tại là Set 18).
schema: hudSchema 3 (tăng phiên bản theo data-contracts mục 3). Schema 2 giữ nguyên để đọc file cũ.
why: mô hình thích ứng nhiều mùa cần dữ liệu đến dần theo từng loại. Mỗi loại mở khóa một bước đo khác (`tft-sim/docs/model-plan.md` mục 10). Thứ tự trên theo thứ tự mở khóa, không theo độ tiện làm. Hiện không trường nào trong schema 2 đủ để chạy `decide.js`: nó coi `hp` và `stage` thiếu là 0.
unblocks: harness đo tỷ lệ đồng ý của `decide.js` (Phase 4); thí nghiệm mask của sim (`model-plan.md` 10.6); tiêu chí placement của sim.; bàn (3) và kết quả round (4) còn dùng để kiểm độ trung thực của simulator (nhân nhóm `tft-sim`, xem model-plan 10.8)
deadline:
status: mở

## Ghi chú

- Level null ở 9 VOD: xem `20261125-sim-to-hud-level-null-vods.md`.
- `timer`, `gold`, `level`, `xp`, `streak` không yêu cầu ở đây: đã có trong `fields4`.
