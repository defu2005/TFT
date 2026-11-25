# Yêu cầu: dữ liệu HUD theo thứ tự mở khóa cho mô hình

dataset: các đoạn VOD Set 18 đã có log OCR (nhánh `claude/hud-data-set18` @ `1b4c468`, 23 file, 174.492 mẫu, schema 2). Cùng khóa `VOD-startSec`, cùng lịch 4 Hz.
status: mở
why: mô hình thích ứng nhiều mùa cần dữ liệu đến dần theo từng loại (xem `tft-sim/docs/model-plan.md` mục 10). Mỗi loại mở khóa một bước đo khác. Yêu cầu này sắp theo thứ tự mở khóa, không theo độ tiện làm.

## Thứ tự ưu tiên

1. **Stage và HP của người chơi (mình).** `stage` đã có trong `fields4` (status mở, do `hud`). Cần thêm `hp` (0–100, kèm `confidence`, `src`). Mở khóa: đo tỷ lệ đồng ý của `decide.js` (`decide.js` hiện coi `hp` và `stage` thiếu là 0, nên log hiện tại không chạy được).
2. **Thứ hạng cuối của mỗi trận (1–8).** Một số cho mỗi trận. Đây là nhãn duy nhất cho phép hơn bắt chước. Nguồn đã có: `docs/agents/responses/20261124-hud-match01-result.md` cho 1 trận (streamer 2/8, bản nháp chưa công bố). Cần: thứ hạng cho mọi trận có log, kèm nguồn đọc (màn kết thúc hoặc bảng cuối).
3. **Bàn và bàn chờ, kèm sao (`board`, `bench`).** Mỗi phần tử `{champion_api, star}`, `src: template`. Lưu ý: nhánh `hud` ghi tên tướng trên bàn không đọc được ở 720p. Cần xác nhận độ phân giải cần thiết (1080p hoặc khớp icon) trước khi cam kết lịch.
4. **Kết quả combat từng round (thắng/thua, sát thương nếu có).** Nhãn trung gian, dùng cho lớp combat.
5. **Trang bị và augment** (`items`, `augments`), kể cả tier nếu đọc được.
6. **HP đối thủ.** Hiện chỉ có 6 mẫu nhãn bằng mắt trong `data/hud-audit/hp_labels_6.jsonl` (nhánh `nifty`). Cần `hud` xác nhận nguồn trước khi đưa vào yêu cầu đầy đủ. Không yêu cầu OCR đối thủ cho đến lúc đó.
7. **Log của set thứ hai.** Đây là ràng buộc chính: toàn bộ 23 file hiện là Set 18, từ 7 VOD. Không kiểm được "mọi mùa" trên dữ liệu thật khi chưa có set thứ hai.

## Quy định chung

- schema: `hudSchema` 3 (tăng phiên bản theo data-contracts mục 3). Schema 2 giữ nguyên để đọc file cũ.
- Mỗi trường có `confidence` và `src`. Trường không đọc được ghi `null`, không ghi 0.
- Không yêu cầu `timer`, `gold`, `level`, `xp`, `streak` ở đây: đã có trong `fields4`.
- Level null ở 9 VOD: xem `20261125-sim-to-hud-level-null-vods.md`.

deadline:
