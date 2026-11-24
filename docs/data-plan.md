# Kế hoạch thu thập dữ liệu (điểm vào duy nhất)

Cập nhật: 2026-11-24 (16:40 UTC). Quy tắc chi tiết nằm ở `docs/data-rules.md`. Runbook chạy máy nằm ở `docs/collector-runbook.md`. File này là nơi bắt đầu.

## 1. Dự án cần dữ liệu gì

| Trường | Dùng cho | Nguồn hiện tại | Trạng thái |
|---|---|---|---|
| Vàng, cấp, 5 ô shop, giá | engine (live), huấn luyện kinh tế, audit | OCR `hud_ocr.py` trên VOD | Chỉ kiểm chứng trên VOD Linux. Chưa trên client thật. |
| Odds theo cấp, XP `x/y` | engine (so với hồ sơ), huấn luyện | chưa có vùng đọc (I11 phía HUD) | Không có nguồn. |
| Stage, round, phase | engine, huấn luyện | OCR vùng nhãn (chưa kiểm chứng); `TFT.log` parse offline (`extract-live.js`) | Parse có, chưa nối vào engine. |
| HP, streak | engine, huấn luyện | chưa có vùng đọc | Không có nguồn. |
| Đội hình, trang bị | huấn luyện đội hình | khớp icon (CDragon có icon `.tex`), chưa làm | Chưa có. |
| Kết quả trận | nhãn kết quả | màn hình kết thúc (chưa làm) | Chưa có. |
| HP, bàn của 7 đối thủ | — | không có | Không có nguồn. |
| EoG `TFTEoGStats.json` | HP, bàn cuối trận | file cục bộ trên Windows | Thời điểm ghi giữa trận chưa xác minh. |

Không trường nào đã được kiểm chứng trên client thật của người dùng. Đây là khoảng trống lớn nhất, và chỉ có một phiên trên máy Windows lấp được.

## 2. Đang chạy (lúc 16:40 UTC)

- **Thu thập:** `scripts/hud-campaign/run.py` trên máy cloud, thư mục `/home/user/campaign/campaign`, 45 nguồn seed. Đã sửa hai lỗi: cgroup không có sẵn, và đo CPU chỉ tính tiến trình cha (đã đổi sang `/proc/stat`). Tiến trình chạy trước khi sửa đã bị cách ly tại `/home/user/campaign/campaign/discarded-before-cpu-fix/`.
- **Claim:** `docs/agents/sources/collector-claude-seed.md` (45 key seed, trên `claude/nifty-lovelace-252i30`).
- **Nơi lưu dữ liệu:** nhánh `claude/hud-data-set18`, thư mục `data/hud-logs/set18/`, chỉ `.jsonl.gz` đã hoàn tất và `done-keys.txt`. Đẩy bằng `/home/user/campaign/push_results.sh`.
- **Lịch đánh thức:** trigger `trig_01Na6BicueyYv2gi9FFigFXr`, mỗi 50 phút kiểm tra và đẩy kết quả. Hủy bằng `delete_trigger` với ID này.
- **Đĩa:** giảm nhanh, khoảng 14 GB lúc 16:38. `verified-matches.json` chưa được tạo, nên MP4 không bị xóa tự động. Khi đĩa dưới 4 GB, tải tạm dừng. Cần biết danh sách trận đã kiểm chứng (khóa là `row['match']`, số 1–45) để bật dọn MP4.
- **Dừng thủ công:** `pkill -f "hud-campaign/run.py"`, rồi `pkill -f ffmpeg`.

## 3. Quy trình chuẩn

1. **Claim:** nguồn được ghi trong `docs/agents/sources/` trước khi tải.
2. **Tải:** `media.py` (yt-dlp, HLS, ffmpeg).
3. **OCR:** `hud_ocr.py` theo profile của bố cục, đầu ra theo mẫu 4 Hz.
4. **Log:** `results/<key>.jsonl.gz` (không ảnh, không MP4).
5. **Đẩy:** `push_results.sh` lên `claude/hud-data-set18`.
6. **Làm sạch:** theo đặc tả trong `data-rules.md` mục 3 (đồng thuận k mẫu, kiểm catalog, không bổ sung giá trị).
7. **Audit:** lượt mù trên crop, đọc viên khác với đọc viên đang đo.
8. **Đọc dự phòng bằng Gemini:** chỉ khi crop đã được xuất. Hiện chưa có.

## 4. Prompt để dán (không tự khởi chạy được từ phiên này)

**Codex (`hud`), trên nhánh được giao, làm trong repo:**
> Đọc `docs/data-plan.md` và `docs/data-rules.md` trên `origin/master`. Việc của bạn: (1) thêm trường confidence cho từng trường vào bản ghi đầu ra, tăng `hudSchema`; (2) xuất crop vùng HUD của ô không đạt ngưỡng vào scratch, không commit; (3) thêm tham số set cho `scripts/hud_ocr.py` thay cho catalog cố định; (4) xuất 16 crop audit không kèm kết quả OCR; (5) hợp nhất bản vá `run.py` tại commit `d5d6bdf` và `f8b021a`, không viết lại file này. Seed đã được collector Claude sở hữu (`docs/agents/sources/collector-claude-seed.md`), nên bạn không xử lý lại các seed đó, chỉ xử lý nguồn mới.

**Cursor (vai trò `engine`, chỉ catalog):**
> Đọc `docs/data-plan.md` trên `origin/master`. Tạo `src/data/catalogs/<set>.json` cho các mùa cũ từ snapshot CDragon có phiên bản ghi rõ. Chỉ dùng các set có trong dump (3, 7, 16, 17, 18). Ánh xạ `TFT17_*` và ID cũ, ghi rõ ánh xạ không chắc. Không sửa `src/engine/` hay `src/ingest/`.

**Phiên Claude sau này (đọc Gemini, sau khi có crop):**
> Đọc `docs/data-plan.md` mục 3 bước 8 và `docs/data-rules.md` mục 2–3. Viết script sidecar đọc crop ô không chắc, gọi model qua gateway đã cấu hình (proxy gắn khóa, không đưa khóa vào file), ghi `src: model`, không bao giờ ghi đè giá trị OCR. Đo độ đồng ý trên 30 crop có OCR tự tin trước khi bật.

## 5. Blocker

- Chưa kiểm chứng trên client thật. Cần một phiên Windows.
- Đọc dự phòng chưa bật, vì chưa có crop.
- Đĩa sẽ đầy trước khi có danh sách trận đã kiểm chứng để dọn MP4.
- Đường gateway Gemini: model trả về có tên khác (`gemini-3.8-flash-n`), chưa xác nhận là Gemini 3.8 Flash thật. Phải đo trên ảnh có nhãn.
- Chưa có danh sách khóa được claim từ phiên Codex (chưa có phản hồi `responses/`).
- Các trận chạy trước khi sửa CPU đã bị cách ly, không trộn vào dữ liệu.
