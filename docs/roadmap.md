# Lộ trình phát triển TFT Coach

Cập nhật: 2026-11-23. Tài liệu này dựa trên `docs/data-sources.md`, `docs/network-and-ram-layer.md` (master), `docs/needs.md` và `docs/engine-state.md` (nhánh `claude/dazzling-feynman-g7a0b9`), cùng `HANDOFF.md` (nhánh `codex/hud-realtime-handoff`) và `tft-sim/README.md` (nhánh `claude/claude-fable-5-2-awwmf5`).

## Điểm xuất phát

- Engine đã chạy được trên replay tổng hợp (master: 39 test đạt). **Chưa có kiểm thử nào trên dữ liệu live.**
- Đường dữ liệu live chưa được chốt. Có ba hướng và chưa hướng nào được xác nhận là đủ:
  1. **Live Client `127.0.0.1:2999`**: `ECONNREFUSED` với client TFT Standalone (`data-sources.md`). Hướng này không dùng được với bản hiện tại.
  2. **Snapshot và log client** (`src/ingest/standaloneSource.js`, `TFTEoGStats.json`, `TFT.log`): có HP, bàn cờ, trang bị. **Không có shop, vàng, và chưa kiểm chứng đủ.**
  3. **HUD OCR** (`scripts/hud-reader.py` trên master, `scripts/hud_*.py` và chiến dịch VOD trên nhánh codex): đọc vàng, cấp, tên và giá shop. Đây là hướng duy nhất có kết quả đo, nhưng độ chính xác chưa đạt mục tiêu.
- **Mâu thuẫn cần giải quyết trên master:** `data-sources.md` ghi RAM bị Vanguard chặn (lỗi `ACCESS_DENIED`), còn `network-and-ram-layer.md` ghi `OpenProcess` với `PROCESS_VM_READ` thành công. Hai kết luận không thể cùng đúng. Ngoài ra cả hai tài liệu ghi "100% chính xác real-time" cho các trường, nhưng không có số đo nào đi kèm. Các con số này không được dùng làm căn cứ. Ghi chú 2026-11-24: bài hỗ trợ của Riot (29/9/2026, hiệu lực 6/10/2026) chặn truy cập bộ nhớ mặc định với ứng dụng bên thứ ba chưa được biết đến, gồm TFT. Đường RAM không đóng: người dùng sẽ tự phát triển đường này sau (2026-11-26). Chính sách này chặn đọc bộ nhớ của app chưa được phê duyệt, gồm TFT; cần đối chiếu khi phát triển.
- **Dữ liệu tướng và bảng odds chưa khớp:** `rules.js` chưa được xác minh cho Set 18, và `needs.md` U2 vẫn mở. Live dùng id `DA_18_*`, còn `set17.json` dùng `TFT17_*`, nên line tự động chưa có tác dụng trong game.
- `tft-coach` MCP đã kết nối (2026-11-24). `tft_status` cho thấy nguồn live `ECONNREFUSED` tại `127.0.0.1:2999`, khớp với `data-sources.md`. Việc sửa đường live vẫn là đường găng ở Phase 3.

## Đường găng (critical path)

**Không phase nào sau đây đo được trên dữ liệu thật cho đến khi có một nguồn live tạo ra đủ trạng thái engine cần: vàng, cấp, HP, giai đoạn, shop.** Ưu tiên cao nhất là chốt nguồn đó, kể cả khi tạm thời chậm.

## Các phase

Mỗi phase kết thúc bằng một cổng đo được. Không chuyển phase khi cổng chưa đạt.

### Phase 1: Củng cố

- **Mục tiêu:** một nền chung, một bộ dữ liệu được xác nhận, một đường live có chính sách rõ ràng.
- **Việc:**
  1. Đưa quy tắc agent (`docs/agents/`) lên `master` qua PR. **Đã xong:** PR #1 (2026-11-24).
  2. Xác định set đang chạy: `set17.json` và tóm tắt Set 17 trên master, nhánh codex đọc Set 18, nhánh fable ghi CDragon latest là 18.7. Kiểm chứng từ nguồn chính thức trước khi chọn.
  3. Xác định kế hoạch phát triển đường RAM và cách xử lý chính sách Riot (xem trên). Ghi rõ chính sách với từng đường: Riot API, log client, đọc bộ nhớ, sniff mạng, OCR màn hình. Đọc bộ nhớ và sniff mạng có rủi ro về điều khoản và anti-cheat, nên đây là quyết định của người dùng, không phải của agent.
  4. Chọn một đường dữ liệu làm chính.
- **Cổng:** set đang chạy đã xác định; một đường live đã chọn và chính sách đã được xác nhận; quy tắc agent đã lên `master`.
- **Phụ thuộc:** PR (người dùng), chính sách (người dùng).

### Phase 2: Tích hợp nhánh

- **Mục tiêu:** một `master` có đủ các nhánh, mọi bộ test xanh. **Đã xong (2026-11-24):** PR #1–#4 đã merge, test xanh (182 Node, 8 pytest).
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
  4. Người dùng đặt mục tiêu độ chính xác và độ trễ. Handoff ghi mục tiêu 100% trong 250 ms, cần xác nhận lại vì 100% là rất chặt.
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

Người dùng ủy quyền advisor quyết các mục còn treo (2026-11-26). Đây không phải là người dùng duyệt. Đường RAM không đóng (xem trên). Mục 1, 2 và 2b không áp dụng vào lộ trình.

| # | Quyết định | Trạng thái |
|---|---|---|
| 3 | **Chủ roster Set 18: `engine`** (`src/data/set18.json`, có trên `master`). Chi tiết ở `docs/agents/data-contracts.md` mục 5. | Giữ hiệu lực. Advisor quyết, ủy quyền người dùng (2026-11-26) |
| 4 | **Thứ tự tích hợp:** PR #1, rồi `dazzling`, rồi `codex/hud-realtime-progress`, rồi `fable`. Mỗi nhánh một PR, chạy test sau mỗi lần merge. | Đã thực hiện: PR #1–#4 merge đúng thứ tự 2026-11-24 (15:09–15:11 UTC). Người merge chưa xác minh |
| 5 | **Dừng mở rộng chiến dịch OCR VOD của `hud`.** `hud` làm tiếp: 16 khung nhãn mù, tỷ lệ phủ và tỷ lệ sai tự tin cho từng trường, một phiên Windows. Không áp cho lô `fight-v1` 2026-11-25. | Giữ hiệu lực. Advisor quyết, ủy quyền người dùng (2026-11-26) |
| — | **Việc chờ người dùng (không phải quyết định):** gửi 3–5 file ảnh EoG giữa trận (đã ẩn tên và PUUID). | Chờ người dùng |

Đã bỏ: 1 (đóng đường RAM), 2 (sản phẩm sau trận là mặc định), 2b (công cụ mô tả trong trận).

**Bổ sung 2026-11-24 (người dùng đã cho phép dùng dữ liệu):**
- **Dữ liệu huấn luyện:** dùng VOD của streamer cho việc huấn luyện. Rủi ro pháp lý chưa được kiểm tra. Người dùng đã nhận thức và quyết định.
- **Giai đoạn hiện tại:** thu thập và làm sạch dữ liệu. Yêu cầu `hud` commit log OCR theo mẫu: `docs/agents/requests/20261124-user-to-hud-vod-sample-logs.md`.
- **Mô hình:** quyết định mô hình học gì trước do một phiên chuyên trách đảm nhiệm. Chưa thuộc phạm vi của phiên này.
## Lịch sử

- 2026-11-23: bản đầu tiên, dựa trên các nhánh hiện có.
- 2026-11-24: RAM được ghi là đóng; ngày 2026-11-26 người dùng xác nhận đường RAM không đóng. Ghi sản phẩm sau trận, chủ roster, thứ tự tích hợp (xem mục Quyết định 2026-11-24).
