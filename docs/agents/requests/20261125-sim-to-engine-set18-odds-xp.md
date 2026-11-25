# Yêu cầu: đối chiếu bảng odds và XP Set 18 với bằng chứng của sim

dataset: bảng tỉ lệ cửa hàng theo cấp và ngưỡng XP cho Set 18, từ `tft-sim/docs/handoff/set18-sources.md` trên `claude/claude-fable-5-2-awwmf5` tại commit `2136b63` (bản gộp, nội dung từ `bcf9ebe`)
fields: cấp 7 odds (5 số %), XP `7→8`, `8→9`, `9→10` (đơn vị XP), tên tướng và tộc của `DA_18_Kennen`, `DA_18_Ivern`, `DA_Krug18` trong snapshot CDragon sim dùng (commit `ee91495`, file `tft-sim/data/cdragon/cdragon_18.7_2026-11-23.json.gz`, sha256 `caed07e9b1602557b8bce09ed2c80a29d67a1d3fa83c676d85592a52b11c3a9e` đã giải nén)
schema: sim v1 (tài liệu sinh ra từ đối chiếu nguồn công khai, chưa phải dump client)
why: 
- Cấp 7: `set18-sources.md` của sim ghi 19/30/40/10/1 (Riot in ở 17.1). Bằng chứng HUD bản 18.6 trong `needs.md` của engine đọc 16/30/43/10/1 ở cùng cấp. `rules.js` ghi 19/30/40/10/1. Hai nguồn không khớp và chưa biết bản nào áp dụng cho 18.6/18.7.
- XP 7→8: sim ghi 56 (Riot 18.2); HUD 18.6 đọc 56; `needs.md` U1 đề xuất 60 từ wiki. Sim không xác nhận được 60 ở bản Set 18.
- Snapshot sim gọi là 18.7 nhưng `content-metadata.json` ghi `16.23.8413489`, và tướng `DA_18_Kennen`/`DA_18_Ivern`/`DA_Krug18` còn tộc trước 18.7. `src/data/set18.json` của engine ghi `contentVersion 16.23.8406595` từ cùng dump CDragon latest (2026-11-23), tức là cùng trạng thái. Thay đổi tộc 18.7 nằm trong overlay `src/data/overlays/set18-riot-18-7.json`, không nằm trong file gốc.
unblocks: Phase 4 mục 1 của roadmap (U1, U2: xác minh bảng odds và XP cho set đang chạy). Không chặn Phase 3.
deadline: 
status: mở
