# Kế hoạch mô hình (workstream sim) — 2026-11-25

Tài liệu này trả lời: model nào học gì, dựa trên dữ liệu thật đang có. Số liệu lấy từ nhánh `claude/hud-data-set18` @ `1b4c468`, thư mục `data/hud-logs/set18/` (23 file `.jsonl.gz`, 174.492 mẫu, 4 Hz). Không dùng số nào không có file nguồn.

## 1. Dữ liệu thật hiện có

| Mục | Kết quả | Ý nghĩa |
|---|---|---|
| Số file / mẫu | 23 file (mỗi file là một đoạn VOD, khóa `VOD-startSec`), 174.492 mẫu | `done-keys.txt` có 23 khóa; handoff nói 26 trận đầy đủ đã xác minh. Chưa ánh xạ được 26 trận vào 23 file. |
| Trường có trong log | `gold`, `level`, `shop`/`shopOptions`, `shopSlots`, `hudDetected`, `ocr`, `mediaTimeMs` | Đây là toàn bộ trạng thái kinh tế. |
| Trường **không có** | stage/round, HP (mình và đối thủ), bench, board, trang bị, augment, streak, thứ hạng cuối | Không có trong schema 2. |
| `hudDetected` | 59,3% mẫu | Phần còn lại không dùng được. |
| `gold` | 59,0% mẫu; 99,3% cặp liên tiếp có cả hai giá trị | Đủ để đo chi tiêu, nhưng có nhiễu (xem mục 3). |
| `level` | 34,3% mẫu; **9/23 file gần như không có cấp** (0–1,6%) | Không dùng được để nhận dạng mua XP ở các file này. |
| Shop đủ 5 tên | 18,6% mẫu | Phần lớn mẫu không đủ để tái dựng cửa hàng. |
| Biến đổi cửa hàng giữa hai mẫu liên tiếp | 11.874 cặp | Gồm mua, làm mới, và lỗi OCR; chưa tách được. |
| Biến thiên vàng bất thường | ~2.600 cặp giảm 1–9 vàng (đếm từ phân bố delta, giới hạn ở −10) không khớp chi phí hợp lệ rõ ràng | Có thể là OCR sai, chưa phân loại. |

## 2. Đầu vào mô hình có đủ không

`universal_features_v4` (185 chiều) = `universal_features` (scalars, opponents, gods, slot, augment) + `bench_board_features` (bench, board, trait, sao, giá). Nó cần: HP, stage, vàng, cấp, bàn cờ, bàn chờ, sao, giá trị đơn vị và trạng thái đối thủ.

Log hiện có chỉ có vàng, cấp và cửa hàng. **Kết luận: không mô hình nào huấn luyện trong sim có thể chạy trên đầu vào lấy từ log HUD hiện tại.** Sim chỉ là bãi thử, không phải mô hình vận hành, cho đến khi HUD thêm các trường mục 4.

Đối thủ: data-plan ghi "không có nguồn". Không được suy đoán. Mô hình không được dùng trường này.

## 3. Nhãn hành động

- Có thể suy ra mua tướng (cửa hàng đổi ở một ô + vàng giảm bằng giá), làm mới (năm ô đổi + vàng giảm 2), mua XP (vàng giảm 4 + cấp tăng). Mỗi suy luận cần kiểm chứng trên vài trận bằng nhãn mù.
- Mơ hồ: mua và làm mới cùng một khung; lỗi OCR giá; cấp thiếu ở 9 file. Chưa đo tỷ lệ mơ hồ cụ thể. Bước tiếp theo: đếm trên một trận có nhãn tay.
- Không suy được hành động đặt tướng lên bàn, bán, hay chọn augment từ log hiện tại.

## 4. Yêu cầu dữ liệu (gửi `hud`)

Xem `docs/agents/requests/20261125-sim-to-hud-state-fields.md` trên nhánh này. Tóm tắt: stage/round, HP của mình, bàn và bàn chờ theo từng round (template), trang bị nếu có. Không yêu cầu dữ liệu đối thủ vì không có nguồn.

## 5. Thứ tự (đã thay thế bởi mục 10)

> Thay thế 2026-11-25: giả định của người dùng là mọi dữ liệu cần thiết sẽ được cung cấp dần. Xem mục 10. Ràng buộc còn giữ: không huấn luyện trên log economy-only (chỉ học nhiễu OCR).

1. **Không huấn luyện gì trước khi có trường mục 4.** Huấn luyện trên log hiện tại chỉ học nhiễu OCR.
2. Khi có trường: dựng trạng thái cho `decide.js` từ log, đo tỷ lệ đồng ý của `decide.js` trên các trận giữ lại, chia theo VOD (không chia theo mẫu). Đây là baseline và là harness Phase 4.
3. Chỉ khi có harness: calibrate ngưỡng (U8) bằng log. Mô hình mạng chỉ xem xét sau đó, và cần ít nhất vài chục trận có nhãn.
4. Không có kết quả placement, nên không dùng học tăng cường. Chỉ có bắt chước.

## 6. Quyết định (đã thay thế bởi mục 10)

> Thay thế 2026-11-25: "chưa chọn mô hình" không còn đúng. Kiến trúc đã chọn ở mục 10; chỉ mục tiêu "khớp decide.js" còn làm baseline.

- Mục tiêu học: quyết định mà `decide.js` đã đưa ra (khớp Phase 4). Không phải "chơi tốt" theo nghĩa khác.
- Chọn mô hình: **chưa chọn**. Lý do: không có trạng thái đầu vào, và không có nhãn đáng tin. Đây là hệ quả của dữ liệu, không phải lựa chọn kiến trúc.
- Chia tập: theo VOD và theo streamer, không theo mẫu.
- Báo cáo: n, CI, tỷ lệ mẫu bị bỏ, tỷ lệ OCR lỗi.

## 7. Điều cần người điều phối biết

Dòng để thêm vào roadmap hoặc claims (người dùng quyết định): "Mô hình học: dừng ở giai đoạn dữ liệu. Chờ `hud` cung cấp stage, HP, bàn và bàn chờ (yêu cầu `20261125-sim-to-hud-state-fields`). Không huấn luyện trên log economy-only."

## 8. Cập nhật 2026-11-25 (sau khi đọc `decide.js` và replay script)

- **Replay script không phải baseline.** `scripts/replay-real-match.js` (engine) đọc `captures/extracted-live.jsonl` (không có trong repo), tự sinh vàng theo mốc thời gian và dùng cửa hàng cố định. Không dùng log HUD. Vì vậy mục 5 bước 2 vẫn bị chặn.
- `decide.js` coi `hp` thiếu là 0 và `stage` thiếu là 0. Dùng log hiện tại làm đầu vào là sai, không phải chỉ thiếu.
- `standaloneSource.js` của engine có nhận `hudSchema` 1 và 2 cho ingest trực tiếp. Đây là đường live, không phải replay.
- Đếm giao dịch vàng giảm (2.803): mua ứng viên 71%, không rõ 21,5%, làm mới ứng viên 5,8%, XP 1,3%. Mục 3 đã nói "đa số là bất thường". Đúng là ngược lại: phần lớn là giao dịch mua.
- Tỷ lệ cửa hàng theo cấp (CI theo cửa hàng): cấp 8 khớp bảng Riot/R, lệch `rules.js` bậc 4. Cấp 7 không khớp bảng nào. Chi tiết ở `docs/agents/requests/20261125-sim-to-engine-set18-odds-xp.md`.
- Yêu cầu `hud` đã thu hẹp: `stage`, `timer`, `gold`, `level`, `xp`, `streak` đã nằm trong `fields4` (status mở). Chỉ còn HP, bàn và bàn chờ.

## 9. Cập nhật kiến thức 2026-11-25 (sau khi pull)

Nguồn: `origin/claude/nifty-lovelace-252i30` @ `9895e75` (`data/hud-audit/`), `origin/master` @ `013450a` (`docs/research/tft-set-agnostic-research.md`, v4.0). Các điểm dưới đây thay đổi kế hoạch.

- **Board không đọc được ở 720p.** Nhánh `hud` ghi: tên tướng trên bàn không có nhãn chữ ở 720p, nên `board` là "unknown" nếu không có khớp mẫu icon. Yêu cầu `board` (template) có thể cần 1080p hoặc icon matching. Chưa đo.
- **HP đối thủ có trong sidebar.** `hp_labels_6.jsonl` (đọc bằng mắt, `src: eye_composite`) có HP của cả 8 người chơi theo thời điểm. Điều này mâu thuẫn với "đối thủ không có nguồn" trong `data-plan.md` và trong yêu cầu của tôi. Chưa có OCR cho HP đối thủ; chỉ có nhãn mắt, 6 mẫu. Cần `hud` xác nhận trước khi đưa vào yêu cầu.
- **Kiểm định mù interim (20/100 khung, `audit_report_20.md`):** stage đúng 19/19 khi đọc được; timer sai 3 khung; level có dương giả (7 trên thanh đã ẩn); shop 1 lỗi trong 49 ô đọc được; hudDetected chặn nhầm khi thanh HUD còn hiển thị. Cấp 8 vẫn dùng mẫu số 80 cho XP (nên là 68) — lỗi của `hud`, đã biết.
- **Log schema 2 của `1b4c468` không bao gồm HP, bàn, bàn chờ.** Nhánh `hud` nay có `fields4` với `stage`, `timer`, `gold`, `level`, `xp`, `streak`, và đang kiểm chứng bằng nhãn mù (chưa đạt cỡ mẫu).
- **Nghiên cứu xuyên mùa (master):** tài liệu tri thức, không phải dữ liệu. Phần 11 mô tả kiến trúc AI xuyên mùa (board evaluator, combat predictor, decision ranker). Các thành phần này phụ thuộc trạng thái đầy đủ (bàn, HP, đối thủ) mà log hiện chưa có. Không dùng làm số liệu.
- **Không đổi:** `engine` (`dazzling` @ `48f08d6`) và `hud` (`hud-data-set18` @ `1b4c468`) không có commit mới. Yêu cầu của sim trên nhánh này chưa có phản hồi nào trong `responses/`.

## 10. Khả thi: mô hình thích ứng mọi mùa (2026-11-25)

Giả định của người dùng: mọi dữ liệu mà mô hình cần sẽ được cung cấp, nhưng đến dần theo từng loại. Đánh giá này dựa trên mã và số liệu trong repo, không dựa trên kiến thức chung. Kiến trúc xuyên mùa gốc: `docs/research/tft-set-agnostic-research.md` (master, v4.0) §11 và §13; không sửa tài liệu đó.

### 10.1 Kết luận

**Khả thi, với điều kiện: một kiến trúc chung + catalog theo từng set + hiệu chỉnh ngắn cho set đó.** Không phải mô hình chơi tốt một set mới ngay ngày đầu. Người dùng đang nhận thứ thứ nhất. Thứ thứ hai cần thêm dữ liệu cho set mới và chưa có.

### 10.2 Bằng chứng từ repo

- **Action vocabulary có cả phần chung và phần riêng.** `tft-sim/src/tft_sim/tftgoat.py` `ACTION_TYPES` gồm FIELD, BENCH_BOARD, EQUIP, PICK_AUGMENT, PICK_GOD, REROLL_AUGMENT. Các loại mua, làm mới, XP, bán chung cho mọi set. PICK_GOD, PICK_AUGMENT, REROLL_AUGMENT là riêng của Set 17 (gods, augment registry từ `augments_set17`).
- **Observation có khối riêng theo set.** `universal_features` = scalars + opponents + gods + slot + augment tiers. Khối gods và augment tiers gắn với Set 17. `universal_features_v2` thêm `bench_board_features` (94 chiều, dùng cost/star/trait qua bảng tướng, không one-hot tên). Phần này đúng nguyên tắc `research §11.1`, nhưng chưa xác minh `slot_features` có one-hot tên tướng không; cần kiểm trước khi nói roster chuyển được.
- **Transfer thật duy nhất trong README:** clone Set 17 áp dụng cho Set 18 (DA-only): −0,08 [−0,16; +0,002] so với teacher v3. Cùng mức trên Set 17: −0,086 [−0,19; +0,02]. Clone này chạy trên resolver Set 17 (`EngineResolver` chỉ có Set 17), nên đây là đo trên roster DA-only, không phải luật Set 18 đầy đủ. README kết luận: ngang teacher, chưa vượt.
- **Kiểm tra content-free** (`results/fixed/transfer/content_free_check.txt`): mô hình chỉ có scalars + opponents + gods, không có slot, đạt 81,2% BUY_SHOP trên A val, bằng flat. Quyết định mua không đọc được từ scalar; cần khối slot.
- **Transfer A→B theo `PATCH_MODEL.md` §5 chưa chạy theo tiêu chí** (chỉ-universal trong 0,5 của scripted trên B). Có file `transfer_results.json` và `reroll_control_check.txt`, chưa đối chiếu với tiêu chí §5. Việc này nằm trong công việc tiếp theo, trước khi tuyên bố bất kỳ kết quả chuyển giao nào.
- **Cơ chế theo set đã có trong engine:** `src/data/set18.json` (contentVersion 16.23.8406595), overlay trait `set18-riot-18-7.json` (chỉ thêm trait, theo ID tướng rõ ràng), `profile.js` (DEFAULT_PROFILE), và `decide(state, out, trace, rules, profile)` nhận rules và profile tùy chọn. Đây là catalog theo set; không tạo format thứ hai.
- **Combat không chuyển.** Không có simulator combat cho set mới; `EngineResolver` chỉ Set 17.

### 10.3 Phân tầng

| Lớp | Chuyển giữa các set | Cần gì cho set mới |
|---|---|---|
| Kinh tế và cửa hàng (hold, buy, XP, roll, sell) | Gần như có, qua bảng | Odds, bảng XP, pool, giá, số bản để lên sao (catalog) + hiệu chỉnh ngắn. Odds Set 18 hiện lệch `rules.js` ở cấp 7–8 (yêu cầu engine đang mở) |
| Đơn vị (roster) | Có, nếu thuộc tính đi từ catalog | Catalog tướng: id, cost, trait. Không dùng tên làm đầu vào |
| Bàn cờ, combat, trang bị | Không zero-shot | Resolver hoặc simulator theo set, hoặc nhãn kết quả combat |
| Augment, god, cơ chế set (Wisps, Unlocks) | Không | Module cơ chế riêng theo set (`PATCH_MODEL.md` §3); core không đổi |

### 10.4 Thiết kế cho dữ liệu đến dần

- Một schema cố định. Mỗi nhóm trường có presence mask (`null` khi không đọc được, không ghi 0).
- Huấn luyện với group dropout: mô hình học với nhóm nào đang có mặt. Khi thêm nhóm mới, kiến trúc không đổi; chỉ thêm nhánh.
- Hiện tại: không có nhóm nào đủ để chạy `decide.js` (thiếu HP và stage).
- Thứ tự mở khóa (đã sắp trong `docs/agents/requests/20261125-sim-to-hud-state-fields.md`): (1) stage và HP mình; (2) thứ hạng cuối mỗi trận, vì đây là nhãn duy nhất cho phép hơn bắt chước; (3) bàn và bàn chờ theo sao; (4) kết quả combat từng round; (5) trang bị và augment; (6) HP đối thủ, chờ `hud` xác nhận nguồn; (7) log set thứ hai.

### 10.5 Ràng buộc chính

- Khối lượng và độ phủ set quyết định, không phải loại dữ liệu. Toàn bộ 23 file là Set 18, từ 7 VOD. "Mọi mùa" không kiểm được trên dữ liệu thật khi chưa có set thứ hai.
- Mỗi set cần HUD profile riêng.
- Không báo cỡ mẫu chưa đo. Lập đường cong học theo số VOD: đo ở một số mốc (ví dụ 2, 4, 7 VOD) khi đã có thứ hạng cuối.

### 10.6 Thí nghiệm sim (một lần, chưa chạy)

Huấn luyện lại clone với mask nhóm: (a) chỉ HUD hiện có; (b) + HP và stage; (c) + bàn và bàn chờ. So sánh thứ hạng trên khối seed chưa dùng. Đề xuất khối **260000–260999**; khối này chưa có trong sổ `cloud-agents.md`, phải ghi vào sổ trước khi chạy. Nhãn: bằng chứng bot, không phải kết quả trên dữ liệu thật. Mục đích: xếp hạng loại dữ liệu và kiểm thiết kế mask. Chưa chạy.

### 10.7 Việc tiếp theo (sim)

1. Đối chiếu `transfer_results.json` với tiêu chí §5 (chỉ-universal trong 0,5 của scripted trên B).
2. Kiểm `slot_features` có phụ thuộc tên tướng không.
3. Ghi khối 260000–260999 vào sổ rồi chạy thí nghiệm mask (mục 10.6).
4. Chờ `hud` phản hồi yêu cầu (HP, bàn, bàn chờ, thứ hạng).
