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

Giả định của người dùng: mọi dữ liệu mà mô hình cần sẽ được cung cấp, nhưng đến dần theo từng loại. Đánh giá này dựa trên mã và số liệu trong repo. Kiến trúc xuyên mùa gốc: `docs/research/tft-set-agnostic-research.md` (master, v4.0) §11 và §13; không sửa tài liệu đó.

### 10.1 Kết luận

**Khả thi, với điều kiện: một kiến trúc chung + catalog theo từng set + hiệu chỉnh ngắn cho set đó.** Không phải mô hình chơi tốt một set mới ngay ngày đầu. Người dùng đang nhận thứ thứ nhất. Thứ thứ hai cần dữ liệu của set mới, chưa có.

Mọi bằng chứng dưới đây là sim hoặc nội dung tổng hợp (8 tướng, 2 trait) hoặc resolver heuristic. **Không có bằng chứng nào trên TFT thật.**

### 10.2 Bằng chứng

**Chuyển giao trên nội dung tổng hợp** (README, mục "Transfer A -> B", 5 seed; `transfer_seeds.json`). Nội dung B hoán vị cost và trait giữa 8 tướng, giữ nguyên multiset. Penalty = B→B trừ A→B, theo BUY_SHOP, trung bình 5 seed:

| Biến thể | Epoch 10 | Epoch 20 | Epoch 40 |
|---|---|---|---|
| flat | 2,0 | 5,3 | 9,7 |
| flat+slot | 1,1 | 1,4 | 1,7 |
| universal | 0,1 | 0,2 | −0,1 |

- Flat tăng penalty theo epoch vì B→B tăng (82,4 → 88,9) còn A→B gần như giữ (80,4 → 79,1). README đọc đây là học danh tính tướng. Đây là dấu hiệu tốt cho việc đọc thuộc tính, không phải chứng minh tổng quát hóa.
- Universal penalty gần 0 là kết quả kỳ vọng do cấu trúc: khối slot xây từ chính đầu vào của teacher (owned, trait chung). Đo này cho thấy cài đặt không làm hỏng suy luận trên 8 tướng. Không phải bằng chứng cho mọi set.
- Hoán vị giữ multiset, nên không bắt được mô hình đếm thuộc tính sai. Chỉ 8 tướng, 2 trait.
- Tiêu chí §5 gốc (chỉ-universal trong 0,5 của scripted trên B): **chưa chạy.** Đo placement vs scripted đã có, nhưng trên nội dung A, không phải B: universal +0,082 [0,005; 0,157] (2000 lobby), null scripted-vs-scripted +0,034 [−0,040; 0,110]. Clone cao hơn null khoảng 0,05, nên "clone kém scripted" chưa được chứng minh (README, mục Độ phân giải placement).

**Sang Set 18 DA-only (không phải chuyển giao sang set mới):** clone huấn luyện trên Set 17 so với teacher v3: −0,08 [−0,16; +0,002]. Dòng này chạy trên **HeuristicResolver** (README dòng 3: giai đoạn 1 và 2 trên HeuristicResolver). Chỉ số đồng ý 99,3% của cùng phép này bão hòa, README ghi rõ nó "không phân biệt được nhiều" (dòng 193), nên không dùng làm bằng chứng.

**Engine chỉ có Set 17.** README dòng 28: "Set 18 khong danh gia duoc tren engine." Mọi đánh giá combat cho set mới cần resolver theo set hoặc nhãn kết quả combat thật.

**Catalog theo set đã có cơ chế (chưa xác minh nội dung):** `src/data/profile.js` `DEFAULT_PROFILE` lấy từ `rules.js` (số Set 17). `src/data/profileFile.js` dựng profile từ file set + overlay theo patch; bảng thiếu rơi về mặc định và được ghi là caveat. `src/data/profiles/set18.candidate.json` tồn tại, liệt kê mục chưa mô hình (Wisp, Lux, Item Forge). Đây là candidate.

**Roster:** `slot_features` (`tftgoat.py` dòng 100–123) đọc `cost/5`, số trait trùng với đội hiện tại, và số bản sở hữu theo ID (chỉ làm khóa tra cứu, không one-hot). Thiết kế đạt yêu cầu "roster là thuộc tính". Chưa kiểm `bench_board_features` cùng cách (mới đọc chữ ký hàm).

**Augment và god:** registry augment (`augments_set17`) và khối gods là Set 17. Đây là lập luận thiết kế, chưa có số đo chuyển giao cho hai loại này.

**Phản chứng cho làm mới (REROLL):** trên seed 0, universal A→A 89,9% → A→B 86,3%, CI theo lobby [−6,5; −0,7]. Trên 5 seed ở epoch 40, penalty REROLL nằm trong khoảng min–max [−1,8; 2,8], tức hiệu ứng không lặp lại. Nguyên nhân chưa rõ, loại này chỉ ~1% hàng.

### 10.3 Phân tầng (cập nhật theo 10.2)

| Lớp | Bằng chứng | Chuyển giữa set? | Cần cho set mới |
|---|---|---|---|
| Cửa hàng (BUY_SHOP) và XP | Synthetic: penalty ~0 với khối slot, 2–10 với flat | Có, có điều kiện khối slot | Odds, bảng XP, pool, giá (catalog). Odds Set 18 lệch `rules.js` ở cấp 7–8 |
| Làm mới (REROLL) | Seed-0 drop không lặp lại ở 5 seed | Chưa rõ | Theo dõi; không đủ để kết luận |
| Đơn vị (roster) | Thiết kế đọc thuộc tính; hoán vị đạt | Có, nếu đọc thuộc tính | Catalog tướng: id, cost, trait |
| Augment, god | Lập luận thiết kế (registry và gods là Set 17); chưa đo | Chưa có bằng chứng | Module cơ chế riêng theo set |
| Bàn, combat, trang bị | Engine chỉ Set 17; HeuristicResolver không phải combat thật | Không zero-shot | Resolver theo set hoặc nhãn kết quả combat |
| Cơ chế set (Wisp, Unlocks) | `set18.candidate.json` liệt kê chưa mô hình | Không | Module riêng (`PATCH_MODEL.md` §3) |

### 10.4 Thiết kế cho dữ liệu đến dần

- Một schema cố định. Mỗi nhóm trường có presence mask. Không đọc được thì ghi `null`, không ghi 0.
- Huấn luyện với group dropout: mô hình học với nhóm đang có mặt. Thêm nhóm mới thì thêm nhánh, không đổi kiến trúc.
- Hiện tại: không nhóm nào đủ để chạy `decide.js` (thiếu HP và stage).
- Thứ tự mở khóa (đã sắp trong `docs/agents/requests/20261125-sim-to-hud-state-fields.md`): (1) stage và HP mình; (2) thứ hạng cuối mỗi trận; (3) bàn và bàn chờ theo sao; (4) kết quả combat từng round; (5) trang bị và augment; (6) HP đối thủ, chờ `hud` xác nhận nguồn; (7) log set thứ hai.

### 10.5 Ràng buộc chính

- Khối lượng và độ phủ set quyết định, không phải loại dữ liệu. Log hiện có: 23 file, 7 VOD (đã đếm từ `done-keys.txt`), toàn Set 18. "Mọi mùa" không kiểm được trên dữ liệu thật khi chưa có set thứ hai.
- Mỗi set cần HUD profile riêng.
- Không báo cỡ mẫu chưa đo. Lập đường cong học theo số VOD khi đã có thứ hạng cuối.

### 10.6 Thí nghiệm sim: mask nhóm (đăng ký trước khi chạy)

**Mục đích:** xếp hạng nhóm dữ liệu HUD theo tác động lên chơi, trên đầu vào mà teacher thực sự đọc. Không phải dự đoán cho set mới.

**Hạn chế đã biết trước khi chạy:**
- Teacher v4 chỉ đọc đầu vào mà nó dùng. Nếu nó không đọc HP hay round, điều kiện (b) bằng (a) theo cấu trúc, và kết quả chỉ nói về teacher, không nói về TFT. Mục kiểm tra bất biến (`scripts/mask_leak_test.py`) xác nhận điều này trước khi diễn giải.
- Rò rỉ: "copies owned" và "trait trùng đội" của slot đọc bench/board. Trong (a) và (b) hai dim này bị ẩn, cùng với mọi dim bench/board.
- Vì teacher đọc bench/board khi quyết định, (a) và (b) bị giới hạn bởi thông tin, không phải bởi kiến trúc.

**Dữ liệu huấn luyện:** `collect_v4.py` (teacher v4, EngineResolver, TFTSet17, cùng nội dung như README), seed 150000–150399 (train), 151000–151199 (test). Các khối này đã dùng cho v4 trước đây; `ledger` cho phép huấn luyện trên đó. Không huấn luyện trên 240000 trở lên.

**Điều kiện** (định nghĩa trong `scripts/mask_exp.py`; 185 chiều universal_features_v4):
- a: gold, level, xp, streak; slot filled, cost/5 (14 chiều)
- b: a + hp, round (16 chiều)
- c: b + bench/board 94 chiều + slot owned, traits (120 chiều)
- full: 185 chiều. Đối chứng: mask toàn 1 phải cho độ đồng ý kiểm tra khớp với huấn luyện đầy đủ.
- Luôn ẩn: opponents, gods, augment tier và flags, scalars 6–9.

**Huấn luyện:** `scripts/mask_train.py`, 40 epoch, seed 0, cùng hàm `bc_train.train`. Mask áp lên X trước khi chuẩn hóa, nên cột ẩn có mu=0, sd=1 và đầu vào bằng 0. Checkpoint lưu `fmask` và `cond`.

**Chỉ số BC:** độ đồng ý với teacher v4 trên test, theo loại hành động (hàng có ≥2 hợp lệ).

**Chỉ số chơi:** `scripts/mask_play.py`, seed **260000–260999** (1000 lobby, dự trữ trong sổ). A = clone (một điều kiện), B = teacher v4, EngineResolver. Mỗi điều kiện chạy riêng. Null = v4 vs v4 trên cùng seed.
- Chỉ số chính: diff A−B (âm = clone tốt hơn), CI95 bootstrap theo lobby (`summarize`), n lobby hoàn tất, và per-lobby diff.
- So sánh đã đăng ký: (b)−(a) và (c)−(b) theo cặp per-lobby; mỗi điều kiện so với null.

**Quy tắc diễn giải:** với 1000 lobby, khác biệt dưới khoảng 0,2 không phân giải được. Khi đó báo "không phân biệt được", không xếp hạng. Không dùng số mẫu chưa đo.

**Không thuộc lần chạy này:** mô hình dropout nhóm đơn. Làm sau, trên khối seed dự trữ mới.

**Kết quả (2026-11-25):** xem README mục "Thí nghiệm mask nhóm HUD". Tóm tắt: bàn và bàn chờ đưa clone từ +2,18 xuống +0,50 so với teacher v4. Điều kiện c vẫn ẩn augment, nên +0,50 bị lẫn với thiếu augment; chưa chơi full để có mốc. HP và round không đổi gì (b−a = +0,13, dưới ngưỡng 0,2). Null −0,02. Kiểm tra bất biến: teacher v4 không đổi theo HP; đổi sao trên bàn có đổi hành động.

### 10.7 Việc tiếp theo (sim)

1. Chạy tiêu chí §5 gốc trên B (chỉ-universal trong 0,5 của scripted).
2. Kiểm `bench_board_features` theo tiêu chí "không one-hot tên".
3. Chạy thí nghiệm mask (10.6).
4. Chờ `hud` phản hồi (HP, bàn, bàn chờ, thứ hạng).
