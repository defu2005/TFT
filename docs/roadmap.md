# Lộ trình phát triển TFT Coach

Cập nhật: 2026-11-23. Tài liệu này dựa trên `docs/data-sources.md`, `docs/network-and-ram-layer.md` (master), `docs/needs.md` và `docs/engine-state.md` (nhánh `claude/dazzling-feynman-g7a0b9`), cùng `HANDOFF.md` (nhánh `codex/hud-realtime-handoff`) và `tft-sim/README.md` (nhánh `claude/claude-fable-5-2-awwmf5`).

## Điểm xuất phát

- Engine đã chạy được trên replay tổng hợp (master: 39 test đạt). **Chưa có kiểm thử nào trên dữ liệu live.**
- Đường dữ liệu live chưa được chốt. Có ba hướng và chưa hướng nào được xác nhận là đủ:
  1. **Live Client `127.0.0.1:2999`**: `ECONNREFUSED` với client TFT Standalone (`data-sources.md`). Hướng này không dùng được với bản hiện tại.
  2. **Snapshot và log client** (`src/ingest/standaloneSource.js`, `TFTEoGStats.json`, `TFT.log`): có HP, bàn cờ, trang bị. **Không có shop, vàng, và chưa kiểm chứng đủ.**
  3. **HUD OCR** (`scripts/hud-reader.py` trên master, `scripts/hud_*.py` và chiến dịch VOD trên nhánh codex): đọc vàng, cấp, tên và giá shop. Đây là hướng duy nhất có kết quả đo, nhưng độ chính xác chưa đạt mục tiêu.
- **RAM đã đóng (2026-11-24):** Riot Support (29/9/2026) xác nhận từ 6/10/2026 chặn truy cập bộ nhớ mặc định với ứng dụng bên thứ ba chưa được biết đến, gồm cả TFT. Không phát triển đường RAM. Mâu thuẫn giữa `data-sources.md` và `network-and-ram-layer.md` không còn cần giải quyết. Đường mạng bị mã hóa, cũng đóng.
- **Dữ liệu tướng và bảng odds chưa khớp:** `rules.js` chưa được xác minh cho Set 18, và `needs.md` U2 vẫn mở. Live dùng id `DA_18_*`, còn `set17.json` dùng `TFT17_*`, nên line tự động chưa có tác dụng trong game.
- `tft-coach` MCP đã kết nối (2026-11-24). `tft_status` cho thấy nguồn live `ECONNREFUSED` tại `127.0.0.1:2999`, khớp với `data-sources.md`. Việc sửa đường live vẫn là đường găng ở Phase 3.

## Đường găng (critical path)

**Không phase nào sau đây đo được trên dữ liệu thật cho đến khi có một nguồn live tạo ra đủ trạng thái engine cần: vàng, cấp, HP, giai đoạn, shop.** Ưu tiên cao nhất là chốt nguồn đó, kể cả khi tạm thời chậm.

## Các phase

Mỗi phase kết thúc bằng một cổng đo được. Không chuyển phase khi cổng chưa đạt.

### Phase 1: Củng cố

- **Mục tiêu:** một nền chung, một bộ dữ liệu được xác nhận, một đường live có chính sách rõ ràng.
- **Việc:**
  1. Đưa quy tắc agent (`docs/agents/`) lên `master` qua PR. Cần người dùng yêu cầu.
  2. Xác định set đang chạy: `set17.json` và tóm tắt Set 17 trên master, nhánh codex đọc Set 18, nhánh fable ghi CDragon latest là 18.7. Kiểm chứng từ nguồn chính thức trước khi chọn.
  3. Chính sách sản phẩm: sau trận là mặc định (xem Quyết định 2026-11-24).
  4. Chọn một đường dữ liệu làm chính.
- **Cổng:** set đang chạy đã xác định; một đường live đã chọn và chính sách đã được xác nhận; quy tắc agent đã lên `master`.
- **Phụ thuộc:** PR (người dùng), chính sách (người dùng).

### Phase 2: Tích hợp nhánh

- **Mục tiêu:** một `master` có đủ các nhánh, mọi bộ test xanh.
- **Thứ tự merge đề xuất:** PR #1 (tài liệu), rồi `dazzling`, rồi `codex/hud-realtime-progress`, rồi `fable`. Mỗi nhánh một PR, chạy đủ bộ test sau mỗi lần merge.
- **Sau mỗi lần merge:** chạy `npm test` (39/168/42 test Node tùy nhánh), `python3 scripts/test_hud_ocr.py -v` (cần `TFT_SET18_ART_ZIP`), và `PYTHONPATH=src python3 -m pytest -q` trong `tft-sim/`.
- **Cổng:** `master` có đủ nội dung, tất cả bộ test xanh.
- **Phụ thuộc:** Phase 1 (để biết set và đường live).

### Phase 3: Đường live

- **Mục tiêu:** đọc đúng trạng thái trận trên dữ liệu thật.
- **Việc:**
  1. Hoàn thành bước tiếp theo của handoff: ghi tay vàng, cấp, tên và giá cho 5 ô từ 16 ảnh HUD đã lưu.
  2. Đo độ chính xác toàn trận trên các trận giữ lại (không dùng các khung đã dùng để hiệu chỉnh).
  3. Kiểm thử cửa sổ game trên Windows, vì việc chụp cửa sổ chưa được kiểm chứng ngoài Linux.
  4. Mục tiêu độ trễ 250 ms không còn là yêu cầu cứng (xem Quyết định 2026-11-24): chỉ cần ghi nhật ký khoảng 1 Hz. Mục tiêu độ chính xác: tách riêng tỷ lệ phủ và tỷ lệ sai nhưng tự tin.
- **Cổng:** đạt mục tiêu trên các trận giữ lại; báo cáo tách riêng ô bị che, ô không đọc được, mẫu bị bỏ, giá đọc sai.
- **Phụ thuộc:** Phase 2, và chính sách từ Phase 1.

### Phase 4: Đúng đắn của engine trên dữ liệu thật

- **Mục tiêu:** engine ra quyết định hợp lý trên trạng thái thật.
- **Việc:**
  1. Xác minh bảng odds, pool và XP cho set đang chạy (`rules.js` chưa xác minh; `needs.md` U1, U2 mở).
  2. Dùng log OCR của chiến dịch làm trạng thái thật, chạy engine qua đó (`scripts/replay-real-match.js` có sẵn), và so quyết định với hành động thực của người chơi.
  3. Đây là harness đánh giá thật đầu tiên. Chi phí thấp vì dữ liệu VOD đã có.
  4. Tinh chỉnh các trọng số trong `decide.js` (`needs.md` U7, U8) bằng log thật, không bằng cảm tính.
- **Cổng:** tỉ lệ đồng ý và các loại bất đồng được báo cáo kèm cỡ mẫu.
- **Phụ thuộc:** Phase 3.

### Phase 5: Nghiên cứu chính sách (`tft-sim`)

- **Mục tiêu:** tìm quy tắc tốt hơn, nhưng không đưa vào engine khi chưa được kiểm chứng.
- **Việc:**
  1. Gate 0 của `tft-sim` đang bị chặn vì chưa có snapshot CDragon đúng patch 17.4. Kiểm tra xem có thể chạy trên bản đang dùng cho set hiện tại không (CDragon 18.7 đã được tải).
  2. Kết quả trong mô phỏng với bot scripted **không** đủ để đưa vào engine. Quy tắc chỉ được đưa vào sau khi thắng trên harness Phase 4.
- **Cổng:** quy tắc vượt qua harness Phase 4, không phải mô phỏng.
- **Ngoài đường găng:** không chặn các phase khác.

### Phase 6: Sản phẩm

- **Việc:** đóng gói cho Windows, đo độ trễ đầu cuối, trải nghiệm MCP, `src/llm/hint.js`.
- **Hạ tầng:** `tft-coach` MCP đã kết nối từ 2026-11-24. Nếu gặp lại `CONNECTION_CLOSED` ở phiên mới, kiểm tra `node_modules` (đã thử: `npm ci`), rồi thêm bước này vào thiết lập môi trường.
- **Cổng:** do người dùng xác định khi đến lúc.

## Quyết định 2026-11-24

Các quyết định này do người điều phối ghi, theo tư vấn của advisor. Người dùng chỉ cần xác nhận những mục đánh dấu **cần ok**.

| # | Quyết định | Lý do | Trạng thái |
|---|---|---|---|
| 1 | **RAM đóng.** Không phát triển `scripts/probe-ram.py` hay `src/ingest/ramSource.js`. Không chạy `npm run probe:ram*` trên tài khoản thật. Việc gỡ mã là follow-up của `engine`. | Bài hỗ trợ của Riot (`support.riotgames.com/en-us/riot/performance/game-memory-access-removed-for-third-party-apps`, 29/9/2026, hiệu lực 6/10/2026) | Đã ghi |
| 2 | **Sản phẩm: sau trận là mặc định.** Lời khuyên "mua/roll ngay" trong trận đặt sau cờ tắt mặc định, không dùng khi phân phối. | Chính sách TFT của Riot (`developer.riotgames.com/docs/tft`): "An app cannot make suggestions based on the player's current game state", và không duyệt "Apps that dictate player decisions" hay "Apps that provide dynamic, real-time information". | Đã ghi. **Cần ok** để gỡ tính năng trong trận khỏi đường chính. |
| 2b | Công cụ mô tả (`tft_hit_chance`, `tft_interest`) trong trận: chưa xác định là được phép. | Chính sách chỉ nói đến "suggestions", chưa nói đến số liệu mô tả. | Chưa kết luận. Không mở rộng thêm cho đến khi hỏi Riot. |
| 3 | **Chủ roster Set 18: `engine`.** Chi tiết ở `docs/agents/data-contracts.md` mục 5. | Catalog của `dazzling` và `progress` đều khớp mẫu EoG. `CHAMPION_COSTS` trên master sai 3 tướng. | **Cần ok.** |
| 4 | **Thứ tự tích hợp:** PR #1, rồi `dazzling`, rồi `progress`, rồi `fable`. Mỗi nhánh một PR. | Kiểm tra `merge-tree` từng cặp đều sạch. | **Cần ok** để mở và merge. |
| 5 | **Dừng mở rộng chiến dịch VOD.** `hud` làm tiếp: 16 khung nhãn mù, tỷ lệ phủ và tỷ lệ sai tự tin cho từng trường, một phiên Windows. | Số liệu VOD đo trên khung đã dùng để hiệu chỉnh. | Đã ghi |
| 6 | **Ảnh chụp EoG giữa trận.** Người dùng chạy đoạn PowerShell chỉ đọc, sinh ảnh chụp trên Desktop, rồi gửi 3–5 file (đã ẩn tên và PUUID). | Trả lời câu hỏi thời điểm ghi file. | **Bạn cần làm.** |
## Lịch sử

- 2026-11-23: bản đầu tiên, dựa trên các nhánh hiện có.
- 2026-11-24: đóng nhánh RAM, chuyển sản phẩm sang sau trận làm mặc định, chốt chủ roster, thứ tự tích hợp (xem mục Quyết định 2026-11-24).
