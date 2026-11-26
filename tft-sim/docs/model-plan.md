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

**Roster:** `slot_features` (`tftgoat.py` dòng 100–123) đọc `cost/5`, số trait trùng với đội hiện tại, và số bản sở hữu theo ID (chỉ làm khóa tra cứu, không one-hot). Thiết kế đạt yêu cầu "roster là thuộc tính". `bench_board_features` (`src/tft_sim/tftgoat.py:219`) đã kiểm (2026-11-25): mỗi slot ghi có unit, cost/5, sao/3, value/15 và hai cờ (trùng bản, chung trait với bàn). Không có one-hot theo tên. Đạt tiêu chí "không one-hot tên".

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

**Kết quả (2026-11-25):** xem README mục "Thí nghiệm mask nhóm HUD". Tóm tắt: bàn và bàn chờ đưa clone từ +2,18 xuống +0,50 so với teacher v4. Điều kiện c vẫn ẩn augment, nên +0,50 bị lẫn với thiếu augment. Mốc full (hậu kỳ, không đăng ký): full ≈ teacher (−0,051 [−0,157; +0,057]); full − c = −0,548 [−0,686; −0,411], tức phần +0,50 của c là do nhóm ẩn. HP và round không đổi gì (b−a = +0,13, dưới ngưỡng 0,2). Null −0,02. Kiểm tra bất biến: teacher v4 không đổi theo HP; đổi sao trên bàn có đổi hành động.

### 10.8 Giải đấu lobby hỗn hợp (đăng ký trước khi chạy)

**Đã kiểm:** `scripts/mixed_lobby.py` + `scripts/league_run.py selftest`: với bản đồ 4/4, `play_mixed` khớp `play()` trên 5 seed (150000–150004). `play()` không bị sửa. Seed 150000–150004 chỉ dùng để kiểm, không phải đánh giá.

**Điều kiện đã đo (ghi kèm):**
- Full (điều kiện đối chứng, sau đăng ký): chạy `mask_play` clone với `mask_full` trên 260000–260999, nhãn `mask_full`. Đây là kiểm tra hậu kỳ; nằm ngoài đăng ký 10.6.
- Thông lượng: một lobby ~0,55 s một tiến trình (chỉ chơi). Dữ liệu có đặc trưng chậm hơn nhiều; sẽ đo riêng khi có số.

**Giải đấu:** pool = scripted, v3, v4, mask_full, mask_c, v4_null (v4 lặp lại làm null tích hợp). Mỗi lobby: seed s, 8 ghế, mỗi ghế chọn một policy trong pool theo `numpy.default_rng(s)`, có thể trùng. Chỉ số: placement trung bình theo policy, CI95 bootstrap theo lobby (mỗi lobby cho một trung bình của policy đó). Khác biệt so sánh: theo cặp trong cùng lobby.

**Seed đánh giá:** 270000–270999 (dự trữ trong sổ, chưa dùng). Chỉ đánh giá, không huấn luyện.

**Quy tắc diễn giải:** khác biệt dưới khoảng 0,2 không phân giải được. Với v4_null, khoảng cách của nó đến v4 phải chứa 0; nếu không, lệch harness.

**Kết quả (2026-11-25):** xem README mục "Kiểm soát hậu kỳ". Full ≈ teacher (−0,05 [−0,16; +0,06]); giải đấu: v4 3,94, mask_full 4,02, v4_null 4,10, mask_c 4,31, v3 4,58, scripted 6,12. Chênh v4 với v4_null 0,16 cho thấy giải đấu chưa đủ cân bằng để xếp hạng; cần thêm lobby.

**Giới hạn:** valuemax và CEM bị bỏ vì monkeypatch `ACT._equip` toàn cục; chưa xác nhận có tách được theo ghế.

### 10.9 Giải đấu v2 (đăng ký trước khi chạy)

**Sửa so với v1 (10.8):** v1 cho mỗi ghế chọn policy ngẫu nhiên có thể trùng, nên cân bằng kém và placement trung bình bị lệch. v1 cho v4 và v4_null lệch 0,16 dù cùng policy. v2 sửa:
- 8 policy cố định mỗi lobby, mỗi policy đúng một ghế, thứ tự ghế hoán vị theo `np.random.default_rng([seed, 1])` (độc lập với luồng của env).
- Pool: scripted, v3, v4, v4_null, mask_full, mask_c, mask_a, v4_valuemax. v4_valuemax là v4 với luật trang bị valuemax chỉ trên ghế đó (monkeypatch `ACT._equip` đọc bảng `RULE_OF_SEAT` theo agent_id).
- Kiểm: `league2.py selftest`: patch với mọi ghế mặc định khớp bản gốc trên 5 seed (150000–150004). **PASS.**
- Ghi placement theo lobby, theo ghế (policy, placement, completed, illegal).

**Seed đánh giá:** 280000–283999 (4000 lobby, dự trữ trong sổ). Không huấn luyện trên đó.

**Chỉ số:** placement của từng policy; khác biệt ghép cặp với v4 theo lobby (mỗi lobby có đúng một ghế mỗi policy nên ghép cặp là chính xác); CI95 bootstrap theo lobby. Số completed và illegal báo kèm.

**Tiêu chí đạt:** v4 − v4_null có CI95 chứa 0. Nếu không, harness lệch và không xếp hạng.

**Độ rộng mục tiêu:** nửa độ rộng CI của v4 − v4_null khoảng 0,1. Nếu chạy 4000 lobby mà chưa đạt, báo đúng độ rộng và đề xuất số lobby cần thêm; không kết luận từ kết quả chưa đạt.

**Kết quả (2026-11-25):** xem README mục "Giải đấu v2". v4 − v4_null = +0,015 [−0,080; +0,110], đạt tiêu chí. valuemax −1,05 so với v4. mask_full +0,045 (không khác v4). mask_c +0,45. v3 +0,65. mask_a +2,07. scripted +2,26.

### 10.7 Việc tiếp theo (sim)

1. Chạy tiêu chí §5 gốc trên B (chỉ-universal trong 0,5 của scripted). Chưa chạy.
2. Mục 10.6 (mask) và 10.9 (giải đấu v2) đã xong. Mục 10.10 (dropout) đăng ký trước khi chạy.
3. Chờ `hud` phản hồi (HP, bàn, bàn chờ, thứ hạng). Dữ liệu thật là bước quyết định, không phải thêm mô phỏng.

### 10.10 Mô hình group-dropout (đăng ký trước khi chạy giải đấu)

**Mục tiêu:** kiểm một mô hình duy nhất cho nhiều điều kiện dữ liệu, thay vì ba mô hình mask rời. Đây là thiết kế "dữ liệu đến dần" của 10.4 chưa được thử.

**Huấn luyện:** `scripts/dropout_train.py`, dữ liệu `mask_data/ds` (cùng seed 150000–151199 với 10.6), 40 epoch, seed 0, `bc_train.train` không sửa. Mỗi dòng được gán một điều kiện trong {a, c, full} bằng `default_rng([0, 7])`, cỡ mẫu xấp xỉ bằng nhau. Đầu vào 189 chiều = 185 chiều đã mask theo điều kiện + 4 bit hiện diện (HUD, HP, BB, OTHER): a = (1,0,0,0), c = (1,1,1,0), full = (1,1,1,1). Điều kiện b bỏ vì teacher v4 không đọc HP (đã kiểm, 20/20).

**Kiểm tra trước khi chơi (không có ngưỡng, ghi số liệu):**
- Khớp test theo từng điều kiện cố định, so với mô hình mask rời (0,9966 full; 0,9927 c; 0,6355 a).
- Leak test: đổi các cột bị ẩn của điều kiện X thì logit không đổi. Tiêu chí: sai khác tuyệt đối = 0 cho cả ba điều kiện. Nếu không bằng 0, dừng và báo.

**Giải đấu:** `scripts/league2.py run 284000 288000 <out> drop`, 4000 lobby, seed 284000–287999 (dự trữ trong sổ). Pool: v4, v4_null, mask_full, mask_c, mask_a, drop@full, drop@c, drop@a. Mỗi lobby mỗi slot đúng một ghế, hoán vị ghế bằng `default_rng([seed, 1])`. `selftest` phải PASS trước khi chạy (đã chạy với pool v2).

**Phân tích:** chênh theo cặp trong cùng lobby; CI95 bootstrap theo lobby, 2000 lần lấy mẫu, seed cố định.

**Tiêu chí (đăng ký):**
1. v4 − v4_null: CI95 chứa 0 (kiểm công bằng của harness).
2. Với mỗi X ∈ {full, c, a}: CI95 của drop@X − mask_X nằm hoàn toàn trong [−0,2; +0,2].
3. Nếu một tiêu chí thất bại, báo đúng tiêu chí và đúng X đó, không lấy trung bình.

**Kết quả (2026-11-25, đã chạy):** 4000 lobby, 32000 ghế, hoàn tất 100%, illegal 0. Tiêu chí 1 đạt: v4 − v4_null = +0,034 [−0,065; +0,127]. Tiêu chí 2 đạt cho cả ba X: drop@full − mask_full = +0,030 [−0,074; +0,125]; drop@c − mask_c = +0,002 [−0,101; +0,097]; drop@a − mask_a = −0,048 [−0,152; +0,054]. Mô hình một dropout đứng ngang ba mô hình mask riêng trong khoảng ±0,2 đã đăng ký. Kết luận giới hạn ở Set 17 với bot teacher v4.

**Phạm vi:** mô phỏng Set 17 với bot teacher v4 và EngineResolver. Không nói gì về dữ liệu HUD thật, Set 18, hay trận thật.

**Khoảng cách đã biết (ghi trước khi chạy, không sửa kết luận):**
- Logic ability Set 17: 69 hàm viết tay trong `tft_goat/engine/abilities_set17` (6 file). Đây là phần engine đã có.
- Set 18: CDragon snapshot `data/cdragon/cdragon_18.7_2026-11-23.json.gz`, `sets['18']['champions']` có 91 tướng, mỗi tướng có trường `ability`. Chưa có logic ability Set 18, chưa định cỡ. Đây là khoảng cách lớn nhất để áp dụng sang Set 18.
- Vị trí (positioning) chưa xác nhận: `BoardUnit` trong `tft_goat/env/state.py:19` và `data/riot/models.py:16` không có trường vị trí. Chỉ engine `Unit` (`tft_goat/engine/unit.py:37`, `pos=(0,0)`) có, và dữ liệu HUD chưa cung cấp vị trí. Mọi kết quả sim giả định vị trí do engine tự quyết.

### 10.11 Giả định capture (2026-11-25)

Người dùng giả định app capture được mọi dữ liệu realtime cần thiết (bàn hai bên, kết quả combat). Mọi phân tích trong `docs/research/combat-public-data.md` và `scripts/combat/` dựa trên giả định này và trên dữ liệu mô phỏng (`label: sim`). Trạng thái thực tế: chưa có bản ghi trận thật nào có bàn hai bên và kết quả trong nhánh hiện có. Mọi kết quả về độ trung thực đều chờ bản ghi `fight-v1` thật.


## 10.12 Ghi chú item Set 18 (2026-11-25)

- `heldout.py`, `heldout_swap.py`, `play_clone_v2.py` và `collect_real.py` dùng `build_real_set18_clean`, nên các trận Set 18 trong các lần chạy đó dùng item `DA_*` không có hiệu ứng riêng. Chỉ có bonus chung của engine (xem `combat-public-data.md` mục 8). Không chạy lại; ghi lại để đánh giá sau.
- Alias item Set 18 có sẵn trong `tft_sim/item_alias.py` (37 alias). Quyết định (2026-11-25, theo advisor): KHÔNG chuyển các script trên sang nội dung đã alias và KHÔNG chạy lại các đánh giá cũ. `build_real_set18_clean` vẫn là mặc định cho huấn luyện và đánh giá đã có, để số liệu trong file này còn so sánh được. Đường ghi bản ghi trận thật (`fight_cli.py`, `fidelity.py`) dùng nội dung đã alias.
- Điều kiện xét lại: khi có bản ghi trận Set 18 thật, hoặc khi lên kế hoạch huấn luyện Set 18 mới. Lần đó chạy trên nội dung đã alias với seed mới, báo cáo riêng, không ghi đè số cũ.


## 11. Kế hoạch phát triển Set 18 (2026-11-25, theo advisor)

Lý do ưu tiên: Set 19 đang PBE. Khi Set 19 lên sóng, trận Set 18 mới sẽ dừng, nên thu bản ghi thật là việc có hạn thời gian.

Phase 0 (chặn): sửa đường ghi bản ghi thật
- Nội dung cho bản ghi thật = `build_real("TFTSet18")` + alias (`build_set18_records`). Bản cũ (từ bản clean) làm mất 57 item `TFT_Item_*` có hiệu ứng không phải twin.
- Selftest: item `TFT_Item_*` không phải twin cho `items_unknown == 0`. ĐÃ LÀM.

Phase 1: xếp hạng đòn bẩy trên Set 17 (sim, rẻ)
- Quy tắc xếp hạng (khóa): xếp theo tỷ lệ đảo chiều so với `hand` trên cặp quyết định của `hand` (p ≥ 0,9 hoặc ≤ 0,1), CI bootstrap theo lobby 2000 lần. Script: `tft-sim/scripts/combat/phase1_levers.py`. Ghi chú thời điểm: quy tắc được ghi vào script trước khi chạy; dòng này được thêm sau khi lần chạy bắt đầu, và kết quả là tiền đề cho thứ tự Phase 3.
- Dùng bảng v3 đã có (`hand_noaug`, `hand_noitems`, `none`), thêm `hand_notraits` và generic với biến bị gỡ, trên các cặp đã lưu. Nếu file không còn, thu lại seed 288000–288099.
- Báo tỷ lệ đảo chiều so với `hand` kèm CI theo lobby. Quy tắc xếp hạng khóa trước khi chạy.
- Set 17 chỉ là sim, không phải kiểm chứng thật.

Phase 2: bản ghi thật (cổng cho mọi khẳng định về độ chính xác)
- Hỏi khóa API Riot một lần qua `request_credential`, nêu rõ nó mở khóa gì. Kiểm tra tài liệu Riot trước: host (nền tảng cho danh sách ladder, khu vực cho trận), tên header, thời hạn khóa phát triển.
- Thăm dò một trận: set number, dạng apiName item (`DA_*` hay `TFT_Item_*`), có trường vòng cuối cho mỗi người chơi không, có augment không.
- Nếu dùng được: commit pre-registration, rồi thu trận cuối của Set 18 từ tài khoản ladder công khai, không lưu ID người chơi. Chấm điểm: coin flip, hồi quy logistic theo sức mạnh, engine.

Phase 3: phủ Set 18 (wrapper theo set, không sửa `tft_goat`)
- Gỡ hai buff sai ngay (Vanguard `MaxHealthShield` là khiên, Spellweaver `APPerCast` là cộng dồn theo lần thi triển). Đây là lỗi theo mô tả dữ liệu, không cần tham chiếu.
- Trait: bảng ánh xạ tường minh cho 25 trait chưa ánh xạ, đọc từ mô tả; trait không phải chỉ số ghi là chưa hiện thực. Emblem tính vào trait.
- Ability: đưa số Blitz vào generic ability, đổi giá trị tooltip sang đơn vị engine. Lưu ý: trên Set 18 generic rơi về `ad*2` cho 88/91 tướng, nên đây là đòn bẩy thật, không phải tiểu tiết.
- Augment: chỉ làm khi có dữ liệu tần suất.

Phase 4: đánh giá
- Mỗi thay đổi Phase 3 đo bằng chênh lệch cặp trên bộ Set 18 thật; giữ những gì giúp.
- Nếu Set 19 lên mà chưa có bản ghi thật: giao engine ghi nhãn "chưa kiểm chứng" kèm báo cáo phủ, rồi dừng.

Xuyên suốt
- Mọi giá trị đặc thù set gom vào một cấu hình theo set, để Set 19 chỉ cần chạy lại.
- Quyết định duy nhất cần người dùng: khóa Riot. Nếu từ chối, Phase 0, 1 và 3 vẫn chạy.


### 11.1 Kết quả Phase 1 (sim Set 17, 2000 cặp, quy tắc khóa ở trên)
Tỷ lệ đảo chiều so với `hand` trên 1675 cặp quyết định của hand, CI bootstrap theo lobby:
- none: 18.4% [16.4; 20.3]
- hand_noitems: 17.2% [15.2; 19.2]
- generic: 16.6% [14.4; 18.7]
- generic_novars: 15.9% [14.1; 17.8]
- hand_notraits: 4.9% [3.8; 6.0]
- hand_noaug: 4.1% [3.1; 5.2]

Đọc kết quả: trên Set 17, ability và trang bị làm đổi kết quả nhiều nhất (16–18%); trait và augment đổi ít (4–5%). Biến của generic không tạo khác biệt có ý nghĩa (16,6% so với 15,9%, CI chồng lên nhau). Đây là độ nhạy của sim so với `hand`, không phải độ đúng so với thật.
Kiểm tra cặp (cùng 1675 cặp quyết định, `phase1_pairs.csv.gz`, bootstrap theo lobby 2000 lần, không chạy sim mới):
- `generic` và `generic_novars` lệch nhau ở 12,4% cặp (CI [10,7; 14,1]). Trong đó 98/1393 cặp mà cả hai đều chắc chắn (p >= 0,9 hoặc <= 0,1) vẫn đảo bên thắng (7,0%): biến số có tác động thật, nhưng nhỏ.
- Nhưng tỷ lệ đảo chiều so với hand gần như bằng nhau (16,6% so với 15,9%; chênh lệch cặp +0,7%, CI [-1,1; +2,5]).
- `generic` không gần hand hơn `none` một cách đo được: chênh lệch cặp -1,8%, CI [-3,9; +0,3] (bao gồm 0). Đây là giới hạn chính khi dự đoán Set 18, vì `hand` đang bị chặn ở Set 18.
- `generic_novars` gần hand hơn `none` (-2,5%, CI [-3,6; -1,2]), nhưng khác biệt này không có ý nghĩa khi so với `generic`.

Thứ tự Phase 3 đã ghi (ban đầu): ability trước, rồi trait, rồi augment. Ghi chú: mục cổng template đã đóng ở 11.2 (FAIL), không còn là bước kế tiếp. Lựa chọn Phase 3 đã ghi: dùng số generic thô cho ability KHÔNG được coi là cải thiện. Mục tiêu tiếp theo là template ability Set 18 (mục 9) lấy từ mô tả và biến số CDragon, rồi đo lại với `none` làm mốc. Bảng trait (25 trait không có ánh xạ stat) làm sau, vì Phase 1 cho thấy trait chỉ đổi 4,9%.



### 11.2 Cổng template (khóa quy tắc trước khi chạy, 2026-11-25)
Câu hỏi: template ability (mục 9) có tốt hơn `generic_novars` (cấu hình tốt nhất Set 18 chạy được hiện nay) không?
Mẫu: đúng 2000 cặp same-round của `phase1_levers.py` (cùng seed, cùng sample), N=20, seed0=0. Quyết định: p_hand >= 0.9 hoặc <= 0.1 (1675 cặp).
Chỉ số: hiệu cặp của tỷ lệ đảo chiều so với hand, template trừ generic_novars; bootstrap theo lobby 2000 lần.
- PASS: CI 95% của hiệu nằm hoàn toàn dưới 0 (template đảo chiều ít hơn). Khi đó mới được làm template Set 18 (bước 3).
- FAIL hoặc không rõ: không làm template Set 18. Set 18 chạy ability generic, ghi rõ là generic. Nỗ lực chuyển sang item.

- Kết quả cổng (2000 cặp, 1675 quyết định, N=20, `results/fixed/combat/gate_template/gate_template.json`): template 17,1%, generic_novars 15,9%, hiệu 0,0113, CI95 [-0,0066; +0,0297]. CI không nằm dưới 0. Kết quả: FAIL.
- Quyết định: KHÔNG làm template Set 18. Set 18 chạy ability generic (bản bỏ biến số không được chọn làm mặc định; xem 11.1).

### 11.3 Độ phủ item Set 18 theo slot (6839 bản ghi `pairs18_alias.jsonl`, build_set18_records)
- Tổng slot item: 10767. Không rõ tên (unknown): 0.
- Slot có hiệu ứng rỗng: 4375 (40,6%).
- Trong đó 4016 (91,8%) là emblem (`DA_18_Emblem*`), 359 là Tactician's Shield/Crown.
- Lưu ý: con số 40,6% là cơ cấu item của sim trên `pairs18_alias.jsonl`, không phải tần suất emblem thật ở Set 18.
- Kết luận: phần lớn slot rỗng là emblem, mà emblem cộng điểm trait. Việc cần làm trước tiên cho Set 18 là ánh xạ emblem → điểm trait (bước 3a: bảng trait), không phải template ability.
- Đã kiểm tra mã engine: `env/traits.py::active_traits` chỉ đếm `champion_api` của từng tướng. Emblem không cộng điểm trait trong engine, nên đây là lỗ hổng thật, không chỉ là slot rỗng. Set 17 có cùng cơ chế (emblem có hook riêng nhưng không tính vào điểm trait).
- Việc cần làm tiếp theo: thêm điểm trait từ emblem vào đường Set 18 (ánh xạ DA_18_Emblem* → trait) và đo lại. Chưa làm trong lần này.


### 11.4 Phase 2 (Riot), cập nhật 2026-11-25
- Sửa lại: lần trước ghi developer.riotgames.com bị DNS chặn là không đúng với sandbox này. `curl` qua proxy tới `developer.riotgames.com` và `na1.api.riotgames.com` trả về được (200 và 404 không khóa). Môi trường đang `network: unrestricted`, nên không cần đề xuất đổi allowlist.
- Tài liệu đọc được: personal key hết hạn sau 24 giờ; giới hạn 20 yêu cầu/1 giây và 100 yêu cầu/2 phút; "một key cho một sản phẩm".
- Chính sách (trang TFT Developer API Policy): không được dùng để theo dõi tướng đối thủ trên bàn (scouting), không tạo công cụ thời gian thực trong trận, không tạo MMR/ELO. Mục "Aggregate player stats (no specific players)" thuộc nhóm production key. Personal key chỉ cho dự án cá nhân nhỏ.
- Chưa tìm được điều khoản về thời gian lưu trữ hay huấn luyện mô hình trong các trang đã đọc. Điều khoản pháp lý (Terms) chưa đọc, nên việc lưu trữ và dùng dữ liệu để huấn luyện vẫn chưa được xác minh.
- Kết luận: Phase 2 cần người dùng trả lời một câu. Dự án là (a) nghiên cứu cá nhân trên dữ liệu tài khoản của chính họ bằng personal key, hay (b) mô hình tổng hợp trên dữ liệu nhiều người chơi, nên đăng ký production key? Nếu (b), việc cần làm là đăng ký sản phẩm, không phải chỉ xin key. Chưa xin credential.


### 11.5 Độ nhạy emblem (khóa trước khi chạy, 2026-11-25)
Đã làm: `fight.py` có `predict_win(..., emblems=True)`: emblem Set 18 cộng 1 điểm trait cho trait tương ứng (khớp theo tên hiển thị, ví dụ 'Ravager Emblem' -> 'Ravager'), holder nhận buff như thành viên. Selftest mục 10 PASS.
Đo: `pairs18_sample.jsonl` (1000 cặp sim Set 18, nhân alias), cấu hình generic (ability generic vì hand bị chặn), items bật, N=20, seed0=0, emblems off so với on.
Chỉ số tách riêng:
(a) tỷ lệ bàn (board) có ít nhất một trait đổi tier khi bật emblem;
(b) tỷ lệ cặp có xác suất p_a đổi hơn 0,05 khi bật emblem, và tỷ lệ đảo bên thắng (flip) với quyết định dựa trên off;
(c) chênh lệch cặp trung bình kèm bootstrap theo lobby (cặp không tách được lobby: tính theo nguồn `same`/`cross`).
Lưu ý khi đọc: flip nhỏ có thể do trait chưa có ánh xạ stat (xem mục 9 của bảng trait), không có nghĩa là emblem không quan trọng. Kết quả chỉ là độ nhạy của sim, không phải độ đúng.

- Kết quả (`results/fixed/combat/emblem_sensitivity.json`, từng cặp trong `emblem_sensitivity.pairs.csv.gz`; 1000 cặp, 10 lobby, generic, N=20): 432 cặp có emblem; 108 cặp (10,8%) có trait đổi tier; 31 cặp đổi tier ở trait có ánh xạ stat; trong 31 cặp đó trung bình |Δp| = 0,026 và 2 cặp (6,5%) đảo bên thắng. Trên toàn mẫu: flip 0,2% (CI95 theo lobby [0,0; 0,5]), 3 cặp có |Δp| > 0,05.
- Đọc: tác động của emblem nhỏ, nhưng mẫu này không đủ để kết luận vì 876/1000 cặp là quyết định (p ≤ 0,1 hoặc ≥ 0,9), nên gần như mọi cặp đã bão hòa và không thể đảo. Đây là lỗi thiết kế mẫu, không phải bằng chứng emblem không quan trọng. Cần đo lại trên cặp không quyết định (xem 11.7 và bước đo lại sau khi có bảng trait).
- Sửa: CI trong bản trước được bootstrap theo cặp; bản này bootstrap theo lobby (10 cụm), chỉ có 10 lobby nên CI rất rộng.
- Quyết định: giữ `emblems=False` làm mặc định. Bảng trait (25 trait chưa ánh xạ) vẫn cần làm, nhưng không còn là kết luận duy nhất từ độ nhạy này.

### 11.6 Cập nhật 2026-11-25 (bổ sung)
- Mục 11.4: không đuổi theo Riot key trong lượt này. Người dùng sẽ cung cấp dữ liệu. Không xin credential.
- Yêu cầu bản ghi (`docs/agents/requests/20261125-sim-to-hud-state-fields.md`): bản ghi là từng cặp bàn tại thời điểm đánh (fight-v1), không phải bảng cuối game. Điểm thứ hạng (placement) không chấm được bằng sim này; cần bản ghi per-fight để chạy Phase 4.
- Bước 5 (bảng trait) và bước đo lại sau bảng trait: chưa làm.


### 11.7 Khóa Phase 4 trước khi có bản ghi thật (2026-11-25)
- Cấu hình chính: ability generic, items bật, augments bật, traits bật, emblems tắt. Cấu hình phụ: như chính nhưng emblems bật. Không thêm cấu hình nào khác.
- Chỉ số: độ chính xác và Brier, trên các fight có người thắng đã biết. CI bootstrap theo ván (game), không theo fight.
- Mốc so sánh: 50%; và quy tắc sức mạnh không tham số: bên có tổng giá × 3^(sao−1) cao hơn thắng. Giá lấy từ Set 18.
- Đạt: hiệu cặp (chính − quy tắc sức mạnh) có CI95 nằm hoàn toàn trên 0.
- Loại trừ: người thắng null, tướng không rõ. Đếm và báo cáo số bị loại, kèm lý do.
- Cỡ mẫu: với độ chính xác khoảng 60%, CI rộng khoảng ±10 điểm ở 100 fight và ±5–6 điểm ở 300 fight; khi gom theo ván thì rộng hơn.
- Chưa có bản ghi thật: không có kết quả nào được báo cáo.
- Augment (11.8): không loại id nào; giữ hook như đã khóa. Cấu hình chính dùng augments bật, và phải ghi chú sai số xấp xỉ của hook.

### 11.8 Augment Set 18 trùng id với hook Set 17 (đã kiểm tra lại 2026-11-25)
- 70 trên 594 augment Set 18 có id trùng với hook trong `AUGMENT_REGISTRY` (Set 17). Mọi id này có mặt trong danh sách augment Set 18 và mọi khóa biến mà hook đọc đều có trong effects của Set 18 (trừ `MissingHealth`, hook có đọc cả `Missinghealth`, khóa này có trong effects).
- Lưu ý khi đọc: so sánh nội dung Set 17 và Set 18 KHÔNG có sức phân biệt. Cả hai bộ được nạp từ cùng một bảng item toàn cục trong snapshot 18.7 (`tft_goat/data/content.py`), nên so sánh "giống hệt" chỉ chứng minh cùng một dòng dữ liệu, không chứng minh cơ chế giống nhau.
- Phân loại thủ công 70 augment (đọc mô tả đầy đủ, không dùng regex):
  - T, cơ chế theo thời gian, theo đòn hoặc theo sự kiện trong trận: 23 id. Trong đó 21 có hook đánh dấu xấp xỉ, 2 không đánh dấu (PlotArmor, TwoTanky).
  - P, cơ chế tích lũy qua các vòng: 5 id. Trong đó 2 có hook đánh dấu xấp xỉ, 3 không đánh dấu (EarlyLearning, Unforgotten, BodyguardTraining).
  - S, còn lại (stat tĩnh hoặc điều kiện lúc đầu trận): 42 id.
- Con số 46 trong bản trước là sai: regex khớp nhầm "Attack Speed", "Attack Damage" và "for every", và đưa vào cả augment tĩnh (Tiny But Deadly, Tons of Stats, You Have My Bow).
- Quyết định: giữ cả 70 hook, không loại id nào. Hook T và P là xấp xỉ theo nghĩa cũ của Set 17. Cấu hình chính của Phase 4 bật augments và phải ghi rõ sai số này khi báo cáo.
- Dữ liệu phân loại: `results/fixed/combat/augment_hook_classes.json`.
- Chỉ số: 1008/3616 slot augment trong mẫu sim (27,9%) chạy hook. Con số này chỉ đúng với mẫu sim.

### 11.9 Khóa bổ sung cho Phase 4 (2026-11-25, trước khi có dữ liệu thật)
- Công thức chấm: đúng phía = 1; sai phía = 0; p = 0,5 chính xác, hoặc hai bên bằng sức mạnh, = 0,5 điểm.
- n_seeds = 20, seed0 = 0 cố định. Không đổi sau khi có dữ liệu.
- Cỡ tối thiểu: dưới 30 game thì CI được báo là `inconclusive`, không đạt cũng không trượt.
- Thiên vị phía (side bias): đo trên 300 cặp mẫu sim. Nếu CI95 của trung bình (p(a,b) + p(b,a) − 1) không chứa 0, thì khi có dữ liệu thật phải chấm cả hai hướng và lấy trung bình. Kết quả đo sẽ ghi bên dưới.
- Chỉ số kèm theo: số fight, số game, tỷ lệ bên a thắng, trung bình điểm của mỗi cấu hình, chênh lệch với quy tắc sức mạnh, chênh lệch chính − phụ (cấu hình phụ = emblem bật).
- Lưu ý: game id lấy từ phần trước `:` của `source`.

### 11.10 Sửa 11.7 và bảng trait (2026-11-25)
- Cấu hình phụ (secondary) = emblem BẬT + bảng trait BẬT (`traits_table=True`). Cấu hình chính không đổi.
- Hiệu phụ − chính trên dữ liệu thật là phép thử của bảng trait cùng emblem. Không chạy thêm sim để chọn bảng.
- Cả hai cấu hình đóng băng tại commit repo và commit engine ở lần đầu tiên bản ghi thật được chấm. Scorer in `repo_commit` và `engine_commit` trong đầu ra.
- Đầu ra của scorer: số fight, số game, tỷ lệ bên a thắng, độ chính xác (có điểm 0,5 cho hòa), Brier, chênh lệch với quy tắc sức mạnh, CI theo game, và trạng thái (inconclusive khi dưới 30 game).

### 11.11 Bảng trait Set 18 (cập nhật 2026-11-25: khóa hash đã giải mã, đối chiếu mô tả)
- Quy tắc giải khóa hash: CDragon dùng khóa `{xxxxxxxx}` = FNV-1a 32-bit của tên biến viết thường. Kiểm tra trên Ravager: `EnemyHealthThreshold` -> `bef0ca90`, `BonusDamagePercentBase` -> `a9a813e7`, đều khớp. Bảng giải mã đầy đủ: `results/fixed/combat/trait_hash_resolution.json` (25 trait; Elderwood để trống 2 khóa).
- Lịch sử: bảng này đã được sửa TRƯỚC khi chấm bất kỳ bản ghi trận thật nào (repo chưa có bản ghi thật). Commit `83752fb` sửa: Juggernaut đảo ngược (bản cũ gắn `TeamDurability` cho thành viên và `JuggernautDurability` cho cả đội), các khóa Brawler/Juggernaut bị gắn cờ "suy ra", và Juggernaut cộng dồn thay vì lấy giá trị lớn hơn. Commit kế tiếp sửa Defender (phạm vi cả đội, lấy giá trị lớn hơn), thêm lại mô tả đối chiếu, và đánh dấu lại giả định còn lại.
- `TRAIT_TABLE` ánh xạ 7 trait, 10 khóa (`TABLE_MAPPED = 10`, gồm Spellweaver `SpellweaverAP` thêm ngày 2026-11-25) trên tổng 36 trait trong snapshot. (Các bản trước ghi "3 trên 25" và "5 trên 25" là đếm sai mẫu số.) Mỗi dòng đã đối chiếu tên khóa với bảng giải mã VÀ mô tả CDragon (`desc`):
  - Executioner: `CritChance` (tên có sẵn). Mô tả: "Executioners gain ... CritChance", không điều kiện. +15% crit cho thành viên ở mốc 2, cộng dồn sang mốc 3 (mốc 3 không có khóa này). XÁC MINH.
  - Brawler: `BrawlerTeamHealth` (`{da2472a7}`) = +120 HP phẳng cho cả đội. Mô tả: "Your team gains ... max Health", không điều kiện. XÁC MINH. `BrawlerHealthPercent` (`{f1ed73eb}`) = 25/40/65% cho Brawler; mô tả "Brawlers gain more" nhưng KHÔNG nói phần % tính trên HP nào. GIẢ ĐỊNH: tính trên HP gốc, cộng vào phần phẳng (selftest: tướng Brawler 1100 -> 1495 = 1100+120+0.25·1100; tướng không phải Brawler 600 -> 720). Thứ tự áp dụng không ảnh hưởng.
  - Juggernaut: `TeamDurability` (`{f8c73243}`) = dr 4/6/8% cho cả đội; `JuggernautDurability` (`{6eab9c5e}`) = dr 20/30/42% cho Juggernaut. Mô tả: "Your team gains Durability. Juggernauts gain more." XÁC MINH cả phạm vi lẫn quy tắc lấy giá trị lớn hơn (max). Dr áp dụng nhân theo `incoming_reduction` (quy ước engine, chưa đối chiếu với số liệu in-game). Selftest: Juggernaut 0.20, không phải Juggernaut 0.04.
  - Defender: `NonDefenderDefenseGain` (`{0eb6405e}`) = +12 armor và MR cho CẢ ĐỘI; `DefenderDefenseGain` (`{8c16b281}`) = +25/60/115 armor và MR cho Defender. Mô tả: "Your team gains ... Armor and Magic Resist. Defenders gain more." XÁC MINH: hai chỉ số và phạm vi cả đội. GIẢ ĐỊNH: Defender lấy giá trị lớn hơn (25), không cộng (37). Mô tả không nói rõ; cùng cách viết với Brawler, nên chưa chốt được. (Ghi chú: tên khóa "NonDefender" dễ hiểu là chỉ không phải Defender, nhưng mô tả nói "your team", nên dùng phạm vi cả đội.) Selftest: Defender +25 (không cộng thành 37), không phải Defender +12.
  - Rapidfire: `TeamAS` (`{1d98dcec}`) = +10% tốc đánh cho cả đội (0.10 ở mọi mốc). Mô tả: "Your team gains X% Attack Speed", không điều kiện. XÁC MINH phạm vi. Engine áp dụng nhân (×1.10); cộng hay nhân chưa đối chiếu. `ASPerAttack` là khóa khác (cộng dồn theo đòn), chưa ánh xạ.
  - Hunter: `HunterAD` (`{641254b6}`) = +20/30/45/60% AD cho thành viên Hunter. Mô tả: "Hunters gain Attack Damage", không điều kiện, một hạng mục (không có quy tắc kết hợp phải chọn). XÁC MINH. Selftest: 1.20 cho Hunter, 1.00 cho tướng không phải Hunter.
- Khóa chưa giải mã: Elderwood `{0f90e7a4}` và `{4013f48e}` (CDragon để trống tên và giá trị). Không suy đoán; để ngỏ.
- Chưa ánh xạ: 30 trait. Danh sách và lý do theo từng trait nằm trong mục 11.13 và `results/fixed/combat/trait_audit.json`.
- Kiểm tra engine về Brawler (grep 2026-11-25): không có tham chiếu trait Brawler phía engine. Chỉ có một dòng chú thích trong `trait_effects.py` và `_brawler_emblem` trong `items_set17/batch_1.py` (emblem, không phải trait). Bảng trait là nguồn duy nhất của hiệu ứng Brawler trong sim.
- Các giả định còn lại: (1) Defender: lấy max (25) hay cộng (37) khi là Defender; (2) % Brawler tính trên HP nào; (3) Juggernaut dr và Rapidfire AS: cộng hay nhân và đơn vị in-game; (4) toàn bộ số liệu chưa đối chiếu với trận thật hay tooltip. Cách chốt: tooltip in-game của Defender và Brawler ở mốc 2, hoặc một trận thật có Defender và Brawler.
- `bonus_units` (augment Large Quest, engine `trait_bonus`) được truyền vào bảng: đếm trait cộng 1 cho mọi trait không phải (1,), cùng quy tắc với `_emblem_traits` và engine. Selftest: một Brawler + bonus 1 đạt mốc 2.

### 11.12 Bổ sung trước dữ liệu thật (2026-11-25)
- Snapshot: kiểm tra lại sha256 của CDragon latest hôm nay khớp snapshot (xem `data/cdragon/README.md`). Không có bản mới để so sánh. Nhãn patch vẫn chưa xác định.
- fight-v1 có trường tùy chọn `patch` (chuỗi hoặc `null`). `fidelity.score` trả thêm `per_patch` (số trận theo patch). Không loại bản ghi nào vì thiếu patch.

### 11.13 Kiểm toán mô tả 36 trait (cập nhật sau sửa lỗi của advisor)
- Công cụ: `trait_audit.py` (mô tả, biến, `engine_auto`, `hash_keys`) và `trait_probe.py` (đo hiệu ứng từng khóa có tên mà engine tự áp, trên thành viên và không thành viên, tier 1 và tier cao nhất, bằng đúng quy tắc của engine). Kết quả: `results/fixed/combat/trait_audit.json`, `results/fixed/combat/trait_probe.json`.
- SỬA LỖI ĐÃ PUSH: bản trước liệt kê Vanguard `DurabilityIncrease`, Rival `RengarADPerStack`, Maokai `UniqueTraitHealthPerStack` và capstone Riftbeast là "engine đã áp". SAI. Các khóa đó là khóa hash (engine bỏ qua) hoặc không được áp. Danh sách đúng là 15 khóa có tên dưới đây. Pointer "Vanguard đã được engine ánh xạ" cũng sai.
- Khóa có tên mà engine TỰ ÁP (15), với giá trị tier 1 và hiệu ứng đo được:
  - Sprykin `AttackSpeedIncrease` (as, chỉ thành viên): 0.15 -> +10.5% tốc đánh cho thành viên. Mô tả là rider, phạm vi gần đúng.
  - Sprykin `HealthIncrease` (hp, chỉ thành viên): 0.15 -> +75 HP.
  - Hunter `DamageAmp` (amp, thành viên): 0.10 -> +10% damage amp VĨNH VIỄN. Mô tả có điều kiện (3 giây không đổi mục tiêu): XẤP XỈ, bật luôn.
  - Monolith `Resists` (armor+mr, thành viên): 10 -> +10/+10 một lần. Mô tả là "mỗi kẻ địch đang nhắm vào": XẤP XỈ, không nhân theo số địch.
  - Attuned `DamageAmp` (amp) và `Durability` (dr), thành viên: cả hai bật cùng lúc. Mô tả là HAI NỬA "either/or" theo pha trăng. MÂU THUẪN: đây là lỗi thật. Dưới cờ `traits_table` đã bỏ cả hai (`SKIP18_TABLE`, có assert). PRIMARY giữ nguyên.
  - Vanguard `MaxHealthShield` (hp, thành viên): 0.18 -> +18% max HP. Engine áp, nhưng PRIMARY loại khóa này qua `_SET18_BAD_KEYS` (khiên theo % HP, không phải max HP). Đây là lý do khóa nằm trong bad list.
  - Blackthorn `Health` (hp, thành viên): 175 phẳng. Mô tả: "granting your champions Health" (cả đội). LỆCH PHẠM VI: engine áp cho thành viên. Chỉ ghi nhận, không đổi.
  - Fae `ADAP` (ad và ap, thành viên): 4.5 -> AP +4.5 phẳng và AD +2.025 (4.5% nhân). Không rõ đơn vị AD trong game; ghi nhận.
  - Lunar `AttackSpeed` (as, thành viên): 0.07 -> +5.6% tốc đánh. Mô tả gồm "adjacent allies" (đồng minh kề bên) mà engine không mô hình hóa. Khoảng trống phạm vi.
  - Spellweaver `APPerCast` (ap, thành viên): 0.01 -> AP +0.01 phẳng. Loại qua bad list (cộng dồn theo đòn, không áp được).
  - Spellweaver `TeamwideAP` (ap, cả đội): 0.10 -> AP +0.10 PHẲNG cho mọi tướng. LỖI ĐƠN VỊ: mô tả là 10% AP, engine cộng 0.10 điểm AP, gần như không có tác dụng. Mọi khóa AP-phần-trăm bị ảnh hưởng (TeamwideAP, APPerCast, phần ap của ADAP Blossom và Fae). PRIMARY giữ nguyên; cần quyết định sửa lớp đơn vị này (xem bên dưới).
  - Thornmaiden `BaseDurability` (dr, thành viên): 0.05 -> dr 4.75%. Mô tả: "your team gains ..." (cả đội): LỆCH PHẠM VI, chỉ ghi nhận. Khóa `IncreasedDurability` là hash nên engine KHÔNG áp, vì vậy base và increased không cộng dồn. Chỉ có base được áp, không bao giờ có 10%.
  - Blossom `ADAP` (ad và ap, thành viên): tier 1 0.12 -> AD +6, AP +0.12 phẳng; tier cao nhất 1.0 -> AD +50, AP +1.0. Cùng lỗi đơn vị AP như trên.
  - Blossom `BonusHealth` (hp, thành viên): 0.10 -> +65 HP (phần trăm, đúng).
- Khoảng trống:
  - Lunar `AbilityPower`: không có ánh xạ thuộc tính. Mô tả có AP cho Lunar và đồng minh kề bên.
  - Invoker (`InvokerManaBonus`, hash) và Flora Fatalis (mana): engine không có thuộc tính mana.
  - Solar (khiên, sát thương phép, ngưỡng 3 sao): engine không có thuộc tính.
  - Caustic (giảm kháng theo đòn): engine không có thuộc tính.
- Khóa hash không được engine áp (bỏ qua): SpellweaverAP, Vanguard DurabilityIncrease, Thornmaiden IncreasedDurability, Rival (7 khóa), Maokai, Riftbeast capstone, Coven, Solar, Inferno, Greenfather, Elderwood (hai khóa chưa giải mã), Summoner (vài khóa). Đây là khoảng trống, không phải lỗi, vì engine không biết hash.
- ĐÃ CHỐT (2026-11-25, sửa trong `fight.py` dưới cờ `traits_table`, không sửa engine, không đổi PRIMARY, không chạy lại): thang AP của engine là điểm, `BASE_AP = 100` (`tft_goat/engine/config.py`), sát thương kỹ năng nhân `ap/100`. Khóa AP với |v| ≤ 1 được hiểu là phần trăm của AP gốc (`_stat_table`: `ap += v·BASE_AP`). Áp dụng cho `TeamwideAP` (+10 điểm), phần ap của `ADAP` Blossom. Fae `ADAP` 4.5 đã là 4.5 điểm (4.5%) nên giữ nguyên. `APPerCast` bị bỏ qua dưới cờ (cộng dồn theo đòn, không có giá trị tĩnh).
- Bộ bỏ qua. `predict_win` luôn cài `TE.attrs_for = _attrs_for_set18` cho mọi Set 18 (cả PRIMARY lẫn SECONDARY), nên `_SET18_BAD_KEYS` (Vanguard MaxHealthShield, Spellweaver APPerCast) bị loại trên CẢ HAI đường, không phụ thuộc cờ. Chỉ dưới cờ `traits_table` mới thêm `SKIP18_TABLE` (Attuned Durability và DamageAmp, either/or). Selftest khẳng định cả nhánh không emblem lẫn nhánh emblem (cấu hình SECONDARY).
- Thêm `SpellweaverAP` (`{b012bed0}`, members, cộng dồn): bằng chứng từ chính bảng: ở mốc 2, `TeamwideAP` = 0.10 và `SpellweaverAP` = 0.10. Nếu lấy max hoặc thay thế, Spellweaver không nhận thêm gì ở mốc 2, mâu thuẫn với "Spellweavers gain more". Vì vậy cộng dồn. Selftest: Spellweaver +19.9 AP so với tắt, không phải Spellweaver +9.9.
- Bằng chứng về Defender, nghiêng về 37 (cộng dồn) theo cùng logic: nhưng bằng chứng Defender không mâu thuẫn với max (12 → 25 vẫn là "more"), nên mã Defender giữ nguyên là max. Vẫn là giả định.
- Lỗi còn lại trong PRIMARY (không sửa, không chạy lại): `TeamwideAP` được engine cộng như AP phẳng (0.10 điểm), nên PRIMARY gần như không có AP từ Spellweaver. `APPerCast` thì đã bị loại bởi `_SET18_BAD_KEYS` (không cộng vào PRIMARY). Ghi nhận; chỉ cờ `traits_table` (SECONDARY) sửa lỗi AP này.

### 11.14 Hạ tầng trước dữ liệu thật (2026-11-25, bước 3 và 4 theo advisor)
- Chạy `score` quy mô 40 trận (từ mẫu sim, nhãn `real` + `source` `dryrun-gK:R1`, `allow_dryrun`). Thắng gán tổng hợp theo chỉ số, chỉ để thử đường đi. KHÔNG có độ chính xác nào được báo cáo từ lần chạy này. Thời gian: 9 giây cho 40 trận, khoảng 0.23 giây mỗi trận (n=20 seed, hai cấu hình). Không cần song song hóa cho 1000 trận (khoảng 4 phút).
- Độ rộng CI trên dữ liệu tổng hợp: N=30: 0.233; N=60: 0.146; N=120: 0.106 (thắng gán tổng hợp, chỉ để đo hình dạng).
- Số TRẬN (game) cần, trần (không phải ước lượng; khi mỗi game có một fight): d = credit(model) − credit(rule) theo từng trận. Đo trên 120 trận mẫu với 3 cách gán thắng khác nhau: trung bình d² = 0.3542 ở cả ba (PRIMARY − luật). Vì vậy d² chỉ phụ thuộc việc hai bên chọn có khớp không, không phụ thuộc ai thắng (không hòa). Phương sai của d ≤ E[d²] = 0.354, nên trần: N ≥ (1.96/h)² × 0.354, làm tròn lên. Với h = ±0.10: N ≥ 137. Với h = ±0.05: N ≥ 545 (bản trước ghi 136/544 là làm tròn xuống).
- Trần cho các so sánh SECONDARY (cùng 120 trận, cấu hình SECONDARY hiện tại có `item_alias`; số cũ không còn áp dụng):
  - SECONDARY − PRIMARY: trung bình d² = 0.0708, trung bình d = 0.0000. Trần: N ≥ 28 (h=±0.10), N ≥ 109 (h=±0.05).
  - SECONDARY − luật: trung bình d² = 0.3750, trung bình d = 0.0583. Trần: N ≥ 145 (h=±0.10), N ≥ 577 (h=±0.05).
  - Đây là trần theo phân bố trên mẫu sim-sinh; chỉ dùng để lập kế hoạch số trận, không phải ước lượng độ chính xác. Thực tế nhỏ hơn vì Var(d) < E[d²]. Trần này khớp với hệ số 1.15/√N ở trên (1.96·√0.354 ≈ 1.17). Tỉ lệ khớp của chính mẫu này có thể khác dữ liệu thật; con số phải đo lại khi có bản ghi thật.
- `MIN_GAMES = 30` là sàn an toàn, không phải tính công suất.
- Nguồn kiểm tra nội dung (mục 11.12 bổ sung; kiểm lại 2026-11-25): `latest/cdragon/tft/en_us.json` và `pbe/cdragon/tft/en_us.json` đều có sha256 `caed07e9…`, trùng snapshot; PBE không khác `latest` (giống từng byte). `16.24/cdragon/tft/en_us.json`: 404. Các thư mục phiên bản 16.21–16.23 đã kiểm trước đó. Chuỗi `content-metadata.json` của `latest` hiện là `16.23.8418428`, khác `16.23.8413489` mà handoff ghi. Vì PBE không chứa nội dung khác `latest`, đường PBE này KHÔNG cho thấy Set 19 (người dùng báo Set 19 đang PBE): cần nguồn khác để xác nhận, chưa xác định. Thư mục gốc `raw.communitydragon.org/` trả 521, không liệt kê được phiên bản. Không tìm thấy snapshot có Kennen = Sprykin, Ivern = Elderwood hay Krug = Summoner.
- Bộ phân giải tên `src/tft_sim/names18.py`: tra tên hiển thị -> apiName cho champion, item, augment, trait. Trùng tên thì ném `AmbiguousName`, không đoán. Selftest: mọi apiName đều tra ngược đúng qua tên của nó (0 lỗi trên 793 dòng). Tên trùng sau khi bỏ alias twin: item 248 (37 cặp alias đã bỏ; còn lại chủ yếu là bản `_Upgrade`, là item riêng của CDragon), augment 189 (không ưu tiên tiền tố), trait 0. Champion trùng 4 tên, không đoán: `Krug` (DA_Krug18 cost 3 [Riftbeast, Brawler] | TFT_Krug cost 1 không trait), `Elder Dragon` (DA_18_ElderDragon cost 5 [Apex Predator, Riftbeast] | TFT_ElderDragon cost 1 không trait), `Murkwolf` (DA_Murkwolf18 cost 2 [Riftbeast, Ravager] | TFT_MurkwolfMini cost 1 không trait), `Razorbeak` (TFT_Razorbeak | TFT_RazorbeakMini, đều cost 1 không trait). Quyết định: để trùng. Các bản TFT_* không có trait, cost 1, và xuất hiện trên bàn mô phỏng (ví dụ TFT_Krug 68 lần trong mẫu), nhưng không có bằng chứng từ dữ liệu rằng chúng không nằm trong pool chơi được, nên không mã hóa quy tắc loại. Báo cáo: `results/fixed/combat/name_ambiguity18.json`.
- Bản ghi trận thật: vẫn chưa có. Không có converter.

### 11.15 Tóm tắt những gì cờ `traits_table` làm (cập nhật 2026-11-25, bổ sung trước dữ liệu)
- Cờ `item_alias` (SECONDARY, thêm 2026-11-25, mục 11.16): đổi id item `DA_*` sang `TFT_Item_*` có chỉ số và hook. PRIMARY không đổi.
- Cờ `traits_table` (SECONDARY) áp: (1) `TRAIT_TABLE` gồm 10 khóa, 7 trait (Executioner, Brawler, Juggernaut, Defender, Rapidfire, Hunter, Spellweaver); (2) bỏ 4 khóa `SKIP18_TABLE`; (3) đổi thang AP cho khóa phần trăm (`_stat_table`).
- PRIMARY không có gì trong số này (`traits_table=False`, không đổi `_SET18_BAD_KEYS`).
- `fidelity.score` báo thêm `secondary_minus_rule` (SECONDARY − luật sức mạnh) kèm CI. Đây là bổ sung trước dữ liệu thật: headline vẫn là `primary_minus_rule`, nhưng SECONDARY đã gồm các sửa, nên cũng cần đọc `secondary_minus_rule`. Không dùng để chọn cấu hình sau khi có dữ liệu.



### 11.16 Probe trang bị Set 18 (sửa 2026-11-25 sau hai vòng kiểm tra của advisor)
Bản đầu của mục này kết luận "CDragon thiếu chỉ số item". Kết luận đó SAI. Bản này thay thế nó.
- Công cụ: `scripts/combat/item_probe.py` -> `results/fixed/combat/item_probe.json`. 20 item phổ biến nhất trong mẫu sim-sinh (không tính emblem) + 8 thành phần: 28 item. Champion `DA_Krug18` (bản đầu dùng nhầm `TFT_Krug`, AD 110, nên số AD 16.5 sai; đúng là 8.25). Alias lấy từ `twin_tft_item`, không đoán theo tên.
- Đo:
  1. Đường đi như sim (`items=1, item_apis=(DA_x,)`): mọi item cho cùng chênh lệch: max_hp +150, armor +15, MR +15, AD +8.25, AP +15. Đây là `_GENERIC_ITEM`, không có chỉ số riêng nào.
  2. Đối chứng: `items=1, item_apis=()` cho đúng chênh lệch trên; `items=0, item_apis=(DA_x,)` cho 0.
  3. 18/18 item probe có alias `TFT_Item_*` đều có `effects` khác rỗng. Ví dụ DA_HandOfJustice -> TFT_Item_UnstableConcoction (CritChance 20); DA_GuinsoosRageblade -> TFT_Item_GuinsoosRageblade (AP 10, AS 10, mỗi tầng +7 AS). Đưa id `TFT_*` vào `build_unit`: crit +0.2 (HoJ), AP +25 và AS +6 (Guinsoo) so với chỉ bonus chung.
  4. Hook engine: các bảng `ITEM_*` (`engine/items_set17`) chỉ có khóa `TFT_Item_*` (và vài `TFT17_*`). Với 39 id mẫu, 0 id `DA_*` khớp hook; 27 id có alias khớp hook, chiếm 740/1002 ô item. Vậy có MẤT THỨ BA: hook không bao giờ chạy với id `DA_*`.
  5. `content.items['DA_*'].effects` rỗng; bản snapshot CDragon cho DA_* cũng rỗng. Chỉ số nằm ở `TFT_Item_*`.
- Phạm vi (mẫu sim-sinh, `data/sim/pairs18_sample.jsonl.gz`): 1,002 ô item, 39 item duy nhất; 37 item có alias, cả 37 đều có effects. Hai item không alias: DA_TacticiansShield, DA_TacticiansCrown. Đây là phạm vi; độ lớn ảnh hưởng lên fidelity CHƯA ĐO.
- Thành phần `DA_Component_*` (10 item probe): không có alias trong names18 và không có trong mẫu (n=0). Không ảnh hưởng số liệu mẫu.
- Hai vấn đề về cộng dồn và một vấn đề về trạng thái toàn cục:
  (a) Bonus chung cộng cho mọi item có tên: `fight.py` `boards_of` truyền `items=len(its)`; `simulate.py:321` truyền `generic_items=bu.items`. Đây là QUY ƯỚC của engine: `tft_goat/env/actions.py::_equip` tăng `items` cho item thật (`items += 1` và thêm vào `item_apis`). Nên bonus chung cộng thêm cho item thật là hành vi có sẵn của engine, không phải lỗi của wrapper. Ghi nhận và giữ. Mâu thuẫn với chú thích `_GENERIC_ITEM` ("items abstraits (compteur env)") cần làm rõ với tác giả engine; chưa quyết.
  (b) Trạng thái toàn cục: `tft_sim/item_alias.py::build_set18_aliased` và `build_set18_records` ghi hook `DA_*` vào bảng `ITEM_*` của engine (toàn cục). Selftest và `fight_cli.py` gọi chúng, nên tiến trình đó có hook DA_* (đã kiểm: selftest thấy khóa DA_* trong bảng sau khi gọi). Fidelity không gọi (chỉ import), nên điểm PRIMARY/SECONDARY không bị ảnh hưởng bởi lệnh này; nhưng mọi kết quả đo trong cùng tiến trình sau lệnh đó là không sạch. Cần thay bằng remap id (dưới đây) rồi bỏ đăng ký toàn cục.
- Sửa đã làm (2026-11-25, theo advisor): cờ `item_alias` (chỉ Set 18, mặc định False):
  - `names18.item_alias_map()` đọc cặp `twin_tft_item`.
  - `fight.boards_of(record, items, item_alias)` thay id `DA_*` bằng `TFT_Item_*` khi có bản đồ; số lượng `items` không đổi.
  - `predict_win(..., item_alias=False)`: chỉ dùng bản đồ có đích trong `content.items`.
  - `fidelity.PRIMARY` có `item_alias=False` (đóng băng, không đổi). `fidelity.SECONDARY` có `item_alias=True` (cùng với `emblems`, `traits_table`).
  - Cách này sửa cả hai: chỉ số (content) và hook (khóa TFT_*), không đăng ký toàn cục.
  - Selftest: `crit TFT +0.2, DA 0.0`; `boards` ra `TFT_Item_GuinsoosRageblade`; `predict_win` chạy với cờ.
- Chưa chạy lại điểm (theo chỉ dẫn: không rerun). Mọi con số SECONDARY cũ (kể cả dryrun) không còn áp dụng cho cấu hình mới; phải ghi rõ khi báo cáo.
- Việc còn lại (không làm trong bước này): (i) thay `build_set18_*` để không đăng ký hook toàn cục; (ii) id đúng của 10 `DA_Component_*`; (iii) làm rõ chú thích `_GENERIC_ITEM` với tác giả engine.

### 11.17 Đối chiếu ba trait Defender / Brawler / Spellweaver với nguồn ngoài (2026-11-25)
- Rút yêu cầu đọc chỉ số trong game: bỏ, không cần người dùng đọc số. Giả định vẫn là giả định.
- Snapshot CDragon (đã có): Defender 12 giáp và kháng phép cho cả đội; Defender thêm 25/60/115 (mốc 2/4/6); Brawler 120 máu tối đa cho cả đội, Brawler thêm 25%/40%/65%; Spellweaver 10% AP cho cả đội, Spellweaver thêm 10%/30%/55%, mỗi lần thi triển thêm 1%/1%/2%.
- Nguồn ngoài đã thử:
  - Tìm kiếm web (chế độ thường và mở rộng): Mobafire 18.1 báo Brawler +120 máu cả đội và Spellweaver +10% AP cả đội (khớp snapshot). Một trang Indonesia (bản 18.3) ghi Spellweaver 55% AP, +2% mỗi lần thi triển (khớp mốc cao nhất của snapshot). Không có số Defender từ nguồn này.
  - Mobalytics (trang Defender, Brawler, Spellweaver): không truy cập được (DNS lỗi).
  - Mobafire 18.1 trực tiếp và tactics.tools/info/units: không truy cập được (DNS lỗi).
- Kết quả: không nguồn nào phân biệt được "thêm" với "tổng" cho Defender (25 hay 37), và không xác định được phần trăm Brawler áp lên cái gì. Hai điểm này vẫn là giả định, không đổi bảng.
- Đối chiếu với snapshot: các số cả đội và mốc cao nhất khớp nguồn ngoài. Chỗ lệch duy nhất là bản 18.3 so với snapshot ở mức phụ; chưa rõ có phải lệch bản vá không.

### 11.18 Quyết định về chưng cất (2026-11-25)
- Không chưng cất gì lúc này. Không huấn luyện mới.
- Ba nghĩa của "chưng cất model lớn", và quyết định cho từng nghĩa:
  1. LLM làm thầy, mô hình dự đoán trận nhỏ làm học trò: BỎ. LLM không có sự thật nền về ai thắng trận Set 18, nên nhãn của nó chỉ là phỏng đoán; không bao giờ gắn `label: real` trong fight-v1.
  2. Simulator làm thầy, mạng nơ-ron nhanh làm học trò: HOÃN. Mô phỏng chỉ khoảng 0.23 s mỗi trận, nên tốc độ không phải nút thắt. Học trò sẽ sao chép các khuyết điểm đã biết: khả năng chung (chưa có khả năng riêng cho từng tướng), 7/36 trait trong bảng, PRIMARY không có chỉ số item riêng lẫn hook, và SECONDARY vừa đổi (`item_alias`). Chỉ mở lại khi đủ hai điều kiện: (a) điểm trên bản ghi thật cho thấy mô phỏng thắng luật sức mạnh; (b) có tiêu thụ (ví dụ HUD) cần độ trễ mà mô phỏng không đạt.
  3. LLM/mô hình thị giác trích xuất quan sát thật từ ảnh màn hình hoặc video: là hướng duy nhất có giá trị. Cần video hoặc ảnh do người dùng cung cấp và quyền gọi API qua form thông tin xác thực.
- Bối cảnh: student behavior-cloning cũ (`bc_v2.log`, `clone_v5_seed0.pt`) học bắt chước hành động của policy trong sim, độ chính xác theo hành động ~0.997. Nó không dự đoán thắng thua và không đo fidelity.
- Ngưỡng dữ liệu: đo chênh lệch ±0.05 cần khoảng 545 trận thật (mục 11.14), nên huấn luyện trên kết quả thật còn xa.
- Đã từ chối chưng cất model bên thứ ba (sản phẩm thương mại hoặc model đóng) theo câu trả lời trước.

### 11.19 Hook DA_* toàn cục làm đổi PRIMARY: đã sửa (2026-11-25, theo advisor)
- Phát hiện: `fidelity.py` gọi `build_set18_records()` lúc import, và hàm này (cùng `build_set18_aliased`) ghi hook `DA_*` vào bảng `ITEM_*` của engine (toàn cục). Mục 11.16 viết "fidelity không gọi": SAI. Ngoài ra `build_set18_records` còn copy `effects` của twin vào content DA_*, nên PRIMARY không phải là "không alias" như định nghĩa.
- Đo (`scripts/combat/order_check_items.py`, 150 trận mẫu sim-sinh, 4 lượt, trước khi sửa; `results/fixed/combat/order_check_items_before_fix.json`):
  - PRIMARY chạy trước và sau SECONDARY trong cùng tiến trình: GIỐNG NHAU (không phụ thuộc thứ tự).
  - PRIMARY có hook DA_* so với không hook: KHÁC ở 8/150 trận. Hook toàn cục làm đổi PRIMARY.
- Sửa:
  - `build_set18_records()` trả về CDragon nguyên gốc: không copy effects, không đăng ký hook.
  - `build_set18_aliased()` chỉ còn để chẩn đoán (`alias18.py`, selftest): copy effects, không đăng ký hook.
  - Ánh xạ item chỉ qua id: SECONDARY (`item_alias=True`) đổi `DA_*` → `TFT_Item_*` trong `fight.boards_of`. Hook và chỉ số của `TFT_*` chạy theo bảng gốc.
  - Selftest: ca 7b so sánh đường DA/TFT bằng `item_alias=True` (không còn dựa vào hook); thêm assert không có khóa `DA_*` trong bảng hook sau khi dựng nội dung.
- Kết quả sau sửa: thứ tự vẫn giống nhau; hook DA_* = 0; PRIMARY khác bản cũ ở 30/150 trận. Đây là THAY ĐỔI MỐC của PRIMARY, không phải kết quả mô hình. Mọi số PRIMARY trước 11.19 không còn so sánh được với sau đó.
- Phạm vi: chưa đo độ lớn tác động lên fidelity trên bản ghi thật. Không báo cáo độ chính xác từ mẫu sim.
- Vẫn mở (không làm trong bước này): id đúng của 10 `DA_Component_*`; làm rõ chú thích `_GENERIC_ITEM` với tác giả engine; ba giả định trait (mục 11.17).

### 11.20 Ingest VOD (2026-11-25)
- `scripts/combat/ingest_vod.py`: lobby_id = sha1 của 8 tên đã chuẩn hóa (12 ký tự đầu); khử trùng theo (lobby_id, stage, cặp); viết lại `source` thành `lobby_id:stage`; nguồn còn lại vào `fight_extra.jsonl`. Từ chối nếu `merge_check_vod.py` có ERR.
- Kiểm thử `selftest_ingest_vod.py`: hai VOD cùng lobby + một lobby khác → 3 fight, 1 fight_extra, 2 cụm (raw: 3 cụm). Dầu ra qua `validate_vod.py` thoát 0. Ca gộp có lỗi bị từ chối.
- Chọn VOD có `vod_id` nhỏ nhất khi trùng; không dùng chất lượng khung hình vì chưa có số đo.

### 11.21 Kiểm tra nguồn gốc dữ liệu VOD và cổng gộp (2026-11-26, theo advisor)
- Công cụ chỉ đọc: `scripts/combat/audit_vod_provenance.py` -> `results/fixed/combat/vod_provenance_audit.json`; `scripts/combat/audit_overlap_pairs.py` -> `results/fixed/combat/overlap_pairs_audit.json`.
- Kết quả theo slot (tại thời điểm chạy, 1.026 ván, 12.488 fight):

| Slot | ván | fight | ván có placeholder | fight có placeholder key | ván ghi chú stub/densify | bàn cờ lặp giữa VOD | ván thiếu fight |
|---|---|---|---|---|---|---|---|
| P1 | 95 | 1.722 | 7 | 848 | 9 | 0 | 0 |
| P2 | 34 | 388 | 32 | 0 | 33 | 0 | 0 |
| P3 | 93 | 363 | 0 | 286 | 88 | 2 | 0 |
| P4 | 322 | 4.179 | 240 | 3.501 | 94 | 0 | 0 |
| P5 | 109 | 1.460 | 72 | 153 | 106 | 0 | 0 |
| P6 | 41 | 431 | 9 | 302 | 23 | 0 | 0 |
| P7 | 27 | 267 | 8 | 235 | 27 | 0 | 0 |
| P8 | 39 | 490 | 23 | 126 | 38 | 0 | 0 |
| P9 | 126 | 1.631 | 45 | 794 | 61 | 0 | 2 |
| P10 | 140 | 1.557 | 40 | 1.101 | 112 | 0 | 0 |

- Quan sát chính:
  - `side_of_streamer` là `a` ở toàn bộ 12.488 fight. [Đính chính 11.22] Đây là quy ước (bàn của streamer luôn là `a`), chưa được kiểm chứng bằng khung hình; nên `winner_0` = tỉ lệ streamer thắng. Tỉ lệ đó lệch rõ: P10 397/463 (86%), P8 38/128 (30%).
  - Ván có giây bắt đầu chia hết cho 60 chiếm 26%–77% tùy slot. Dấu hiệu mốc tròn, cần kiểm tra thủ công.
  - Khung hình được tham chiếu gần như đều tồn tại (chỉ 1–16 file thiếu mỗi slot). Phần này không phải lo ngại.
  - [Đính chính 11.22] Số 21 ván là SAI. Có 399 ván (trên 1.026) có ít nhất một fight biết người thắng. Tỉ lệ `winner_null` theo fight là 71%.
  - Cặp lobby lệch (chung 4–7 tên): 2.999 cặp; 2.583 cặp khác streamer; 2.852 cặp chung ≥6 tên. [Đính chính 11.22] Con số 796 cặp "ghi hai lần" là ARTEFACT: sau khi bỏ placeholder và bàn rỗng, còn 1.423 cặp sạch và 0 cặp có bàn giống hệt ở cùng stage.
- Kết luận: không slot nào đạt tiêu chí (không placeholder, không ghi chú stub, không mốc tròn, quan sát được bên thắng). Theo chỉ dẫn, toàn bộ 10 slot không được coi là dữ liệu `real`. Không có ván nào được chấm điểm từ các slot này.
- Cổng gộp đã đổi:
  - `bad_lobby` chỉ còn ERR khi trùng tên hoặc hơn 8 tên.
  - `incomplete_lobby` là WARN; ingest giữ fight của các lobby này trong `held.jsonl`.
  - `placeholder_name` là ERR (tên `unknown_*`, `unk_*` trong lobby hoặc fight_key).
  - `game_without_fights` là ERR.
  - Kết quả hiện tại: `merge_check_vod.py` thoát 1 (7.822 `placeholder_name`, 2 `game_without_fights`). Đây là trạng thái đúng; không sửa dữ liệu của các slot ở phiên này.
- Điểm sản lượng (theo 11.14): ngưỡng 137 ván và 545 ván. Hiện có 0 ván đạt tiêu chí, nên chưa có số nào để so.
- Việc còn lại (không làm ở đây): các agent phải thay placeholder bằng tên thật, hoặc ghi lỗi và để trống; xác minh bàn cờ lặp và mốc tròn; xác định nguồn `winner` và `side_of_streamer`.


### 11.22 Đo sản lượng dùng được, đính chính và đóng băng cấu hình (2026-11-26, theo advisor)
- Đính chính 11.21: (a) số 21 ván sai, đúng là 399 ván có ≥1 fight biết người thắng; (b) 796 cặp trùng là artefact của placeholder và bàn rỗng, đã loại, còn 0; (c) `side_of_streamer = a` là quy ước, không phải bằng chứng bỏ sót. Chưa kiểm chứng quy ước này.
- Lỗ hổng đã sửa: `fidelity._validate` chấp nhận bàn rỗng, và `predict_win` trả `p_a = 1.0` giả cho bàn rỗng (đã kiểm chứng). Thêm lý do `board_trong:<bên>`; ca kiểm thử trong `selftest.py`.
- Sản lượng dùng được (`scripts/combat/scoreable_yield.py`; điều kiện: winner biết, cả hai bên có unit với api phân giải được, tên người chơi thật, khung hình tồn tại):
  - Tổng: 19 fight, **12 ván** trên 1.026. Mục tiêu 137 (±0,10) và 545 (±0,05) đều chưa đạt.
  - Lý do loại chủ yếu: winner null (rất lớn ở P4, P9, P10), bên bàn không phân giải được (P1, P5), tên placeholder (P1, P6, P10).
- Kiểm tra khung hình (7 khung đọc được, 1 đường dẫn sai): chỉ quan sát được băng ghế và một phần bàn, không đủ để đối chiếu từng unit với bản ghi. Không ghi tỉ lệ khớp, vì phương pháp hiện tại không đo đúng thứ cần đo. Cần một phương pháp khác (ví dụ chụp đúng lúc bắt đầu combat, độ phân giải cao).
- Đóng băng cấu hình (để so sánh về sau):
  - PRIMARY = `dict(ability="generic", items=True, augments=True, traits=True, emblems=False, traits_table=False, item_alias=False)`
  - SECONDARY = PRIMARY với `emblems=True, traits_table=True, item_alias=True`
  - n = 800 lượt mặc định (20 → 400 ở 11.26 → 800 ở 11.28 sau khi n=400 không đạt trên bàn có item), seed0 = 0, MIN_GAMES = 30, BOOT = 2000
  - Commit: ghi ở commit chứa mục này. Snapshot CDragon: `data/cdragon/cdragon_18.7_2026-11-23.json.gz`, sha256 = d02fa168934b24abdcc2dfe523b3d4ca04861cb171c373128214cc762c4498c9
- Quy tắc prompt: bản ghi `fight` cần đủ hai bàn quan sát được. Chỉ thấy bàn của streamer thì ghi `state` vào `others.jsonl`, không ghi `fight`.

### 11.23 Phát triển không cần dữ liệu VOD (2026-11-26, theo advisor; dữ liệu VOD tạm gác)

Không đo độ chính xác, không chấm điểm, không đọc lại thư mục `vod_out` để đếm kết quả. Các thay đổi dưới đây kiểm thử bằng fixture và snapshot.

**1. Bộ lọc fight dùng được, đăng ký trước (`scripts/combat/usable.py`).** Điều kiện loại theo thứ tự: `winner_null`, `nombre_placeholder`, `level_khong_ro` (level không phải số nguyên), `board_<bên>_khong_phan_giai`, `board_<bên>_thieu` (số unit < level), `augments_null`, `tuong_la`, `star_khong_hop_le`, `items_null` (bốn mã cuối khớp `fidelity._validate`, để số đếm không lớn hơn những gì scorer nhận), `frame_thieu`. Không có ngưỡng nào do dữ liệu quyết định.
- Lưu ý chi phí: điều kiện `số unit >= level` loại cả những bàn thật nhưng có ít unit hơn level. Đây là đánh đổi có chủ ý (không bao giờ nhận bàn có khả năng sai), không phải bằng chứng rằng các bàn đó sai. Chi phí này phải được báo cáo cùng số lượng.
- Đã bỏ kiểm tra `số unit > level`. Bàn có thể vượt level (ví dụ DA_TacticiansCrown, Sprykin BFF, Elderwood placeable plants), nên đây không phải lỗi dữ liệu.
- `scoreable_yield.py` dùng chung module này. Selftest: `selftest_usable.py` (12 ca, gồm bàn b một unit ở level 5 bị loại, level null bị loại, tướng lạ trong bàn đủ bị loại, bàn vượt level vẫn qua).

**2. File chấm điểm.** `ingest_vod.py` ghi thêm `scoring.jsonl` (chỉ fight qua bộ lọc, kiểm khung hình theo thư mục VOD của bản giữ lại) và `ingest_report.json` có `scoring_fights`, `scoring_games`. `run_vod_pipeline.sh` có bốn bước: gộp, khử trùng, `validate_vod.py` trên `fights.jsonl` (thông tin), và `validate_vod.py` trên `scoring.jsonl` với điều kiện dừng nếu có bản ghi bị bỏ. Đường thành công đã chạy trên fixture (exit 0, không tính điểm).
- Khi bản sao trùng khóa bị bộ lọc loại, ingest không thay bằng bản sao khác của cùng khóa. Khóa đó mất khỏi `scoring.jsonl`. Lý do đặt trong ingest: ingest bỏ đường dẫn thư mục VOD, nên bước sau không kiểm được khung hình.

**3. Trạng thái handoff.** `merge_check_vod.py` thêm mã ERR `bad_status`: `handoff.status` ngoài (`pending`, `working`, `done`, `blocked`, `stale`). Agent đang dùng `ok`, `partial`, `skipped`, nên cổng gộp sẽ đỏ thêm cho đến khi agent sửa. Selftest `trang_thai_ngoai_spec` đã pass.

**4. Bảng trait (`TRAIT_TABLE`).** Không thêm trait nào. Lý do theo từng nhóm:
- Engine đã đọc khóa có tên (named keys) cho mọi trait. Bảng chỉ bổ sung khóa hash mà engine không đọc được, và hiện chỉ có 7 trait trong bảng (không phải "7 trên 36 trait được xử lý": các trait còn lại có thể đã được engine xử lý qua khóa có tên, hoặc nằm trong `SKIP18_TABLE`).
- Các khóa hash còn lại chưa ánh xạ được vì mô tả là điều kiện hoặc cơ chế, không phải chỉ số đơn giản: Adaptor (max AD/AP), Summoner (phụ thuộc loại summon), Riftbeast, Coven, Inferno, Rival, Solar, Sprykin, Eclipse, Greenfather, Invoker, Blossom, Maokai, Lunar, Vanguard, Zyra, Elderwood, Slayer. Thêm chúng là đoán cơ chế.
- Đối chiếu snapshot (`selftest_traits.py`, 10 khóa): giá trị theo tier trong engine khớp snapshot. Defender 25/60/115 khớp; Brawler 120 và 25/40/65 khớp; Spellweaver 10/30/55 khớp.
- Vẫn mở, snapshot không ghi: cộng dồn hay lấy max khi Defender (12 đội + 25 thành viên có thể là 37, hiện đang lấy max là 25); phần trăm máu của Brawler áp trên máu gốc hay sau khi cộng; Spellweaver cộng dồn với TeamwideAP.
- Không có thay đổi số: PRIMARY và SECONDARY không đổi vì bảng không đổi.

**5. Alias item (thay đổi SECONDARY).** Nguồn alias dùng khi chấm là `data/set18_names.json` (trường `twin_tft_item`), không phải `alias_map` trong `item_alias.py`. Hai nguồn trước đây lệch nhau: `alias_map` có 37 mục, file tên không có mục nào cho `DA_Component_*`.
- Đã thêm 8 mục `DA_Component_*` có twin `TFT_Item_*` có hiệu ứng, theo đúng quy tắc tên: BFSword, ChainVest, GiantsBelt, NeedlesslyLargeRod, NegatronCloak, RecurveBow, SparringGloves, Spatula. `alias_map` mở rộng cùng phạm vi (45 mục).
- Chưa alias: `DA_Component_FryingPan` (twin không có hiệu ứng, nên alias không thay đổi gì); `DA_Component_TearOfTheGoddess` (không có twin, cần dữ liệu khác).
- Kiểm tra trên fixture: SECONDARY từ 0.45 lên 0.5 khi hai bàn có cùng item; PRIMARY giữ 0.45. Đây là kiểm tra logic, không phải đo độ chính xác.
- Giả định giữ nguyên như craftable: hiệu ứng của `DA_Component_X` cùng tên với `TFT_Item_X` có hiệu ứng. Chưa kiểm chứng trên Set 18 thật.
- Hệ quả trên tra tên: `names18.candidates("items", "B.F. Sword")` trước đây trả về hai id (`DA_Component_BFSword`, `TFT_Item_BFSword`), nay chỉ trả `DA_Component_BFSword` (đã kiểm tra bằng `HEAD~1` và `HEAD`). Tra tên sang id sẽ không còn mơ hồ, và id được trả về không có hiệu ứng dưới PRIMARY, giống craftable. Cùng kiểu đã xảy ra với craftable từ trước.
- Đây là thay đổi baseline SECONDARY. Mọi so sánh SECONDARY trước đó không còn áp dụng; ghi rõ khi có điểm.

**6. Những gì chưa xử lý và lý do.**
- **Rút lại (kiểm tra 2026-11-26):** một khẳng định trước đó nói augment Kayle scrapper làm PRIMARY có bonus item không có trong dữ liệu. Sai. Handler `_kayle_scrapper` đăng ký dưới khóa `TFT17_Augment_KayleGodAugment_Scrapper`, khóa này không có trong nội dung Set 18 (`TFTSet18`), nên không augment Set 18 nào tới được handler. (Phần về `_GENERIC_ITEM` trong câu này là SAI; đã sửa ở 11.25.)
- `pos`, mapping carousel, apiName của item: giữ mở (không kiểm chứng được nếu không có frame hoặc dữ liệu thật).
- `side_of_streamer`: vẫn là quy ước, chưa kiểm bằng khung hình.

**Chặn trước lần chấm điểm đầu tiên:** cổng gộp xanh (còn lỗi `placeholder_name` và `bad_status` của agent), ≥ 30 ván dùng được theo bộ lọc 11.23 mục 1, và đếm lại sản lượng với điều kiện số unit.

**Kiểm tra đối xứng bên và ổn định theo seed (2026-11-26, `scripts/combat/check_symmetry_seed.py`, không dùng dữ liệu VOD).** Bàn tổng hợp từ nội dung Set 18, level 6–8, số unit = level, không item, không augment; PRIMARY, n = 20.
- Ngưỡng đăng ký trước khi chạy: tỷ lệ đảo dự đoán giữa seed 0 và seed 1000 > 5% thì tăng n và ghi thành thay đổi cấu hình đông lạnh.
- 40 bàn: 0 đảo. Cận trên 95% của tỷ lệ đảo khoảng 7,5%, vượt ngưỡng, nên 40 bàn chưa đủ.
- 300 bàn: 1 đảo (0,33%), cận trên khoảng 1%, dưới ngưỡng. Quy tắc không kích hoạt, giữ n = 20.
- Đối xứng: độ lệch trung bình của p_ab + p_ba − 1 là +0,0012 (không đáng kể). Theo từng bàn, 12/300 bàn lệch trên 0,1 và lớn nhất là 0,3 (3 bàn từ 0,2 trở lên). Đây là nhiễu từng bàn của n = 20, không phải thiên vị hệ thống.
- Chênh lệch seed trung bình 0,0098, lớn nhất 0,3.
- Đây là chẩn đoán nhiễu mô phỏng. Không phải đo độ chính xác dự đoán, không dùng để chọn cấu hình.
- Giới hạn: bàn tổng hợp không có item và augment, nên không đại diện cho bàn thật.

### 11.24 Sửa theo advisor: đối xứng, seed, lọc khung hình, prompt, kiểm thử hành vi trait, augment (2026-11-26, không dùng dữ liệu VOD)

**Đính chính mục 11.23 và câu trả lời trước.**
- Đã rút lại "giữ n = 20" và "không phải thiên vị hệ thống" nói về bộ 300 bàn ngẫu nhiên. Bộ đó gần như bão hòa: chỉ 28/300 bàn có 0,1 ≤ p ≤ 0,9, nên hầu hết không thể đảo và số hạng đối xứng bằng 0. Kết luận trên chỉ đúng cho 28 bàn đó (xem dưới), không đúng cho toàn bộ bộ mẫu.
- Đã rút lại khẳng định "70 augment có handler cho Set 18" nếu hiểu là pool Set 18. Xem mục 5.

**1. Kiểm tra đối xứng và seed trên cặp gần nhau** (`check_symmetry_seed.py --mode close`). B là bản sao của A, đổi một unit sang tướng khác (chỉ tướng có cost và trait) hoặc đổi sao 1↔2. 1000 cặp, PRIMARY. Quy tắc đăng ký trước: tỷ lệ đảo dự đoán giữa seed 0 và seed 1000 trên các bàn không bão hòa (0,1 ≤ p ≤ 0,9) > 5% thì tăng n và ghi thành thay đổi cấu hình đông lạnh.
- n = 20: 319 bàn không bão hòa, 31 đảo, tỷ lệ 9,7%. **Quy tắc kích hoạt.** Kết quả: `results/fixed/combat/symmetry_seed_close_n20.json`.
- n = 100 (bước tăng duy nhất theo quy tắc): 294 bàn không bão hòa, 17 đảo, tỷ lệ 5,8%. **Quy tắc vẫn kích hoạt.** Kết quả: `results/fixed/combat/symmetry_seed_close_n100.json`.
- Trạng thái: n = 100 chưa đủ theo quy tắc. Chưa đổi `n` trong `fidelity.py` (cấu hình đông lạnh vẫn ghi n = 20 đến khi có quyết định). Bước tiếp theo nếu cần: n = 400, ước khoảng một giờ CPU cho 1000 cặp. Đây là nhiễu mô phỏng, không phải độ chính xác.

**2. Bộ lọc fight: khung hình ở cấp unit.** Spec 4.2 đặt `frames` ở cấp unit, không có `frames` ở cấp fight của bản ghi `fight`. Bộ lọc nay yêu cầu mọi unit có ít nhất một khung hình (`unit_khong_khung_hinh`) và mọi khung hình tồn tại (`frame_thieu`). Trước đó bộ lọc chỉ kiểm khung hình đã có, nên cho qua fight không có bằng chứng nào. Selftest 13 ca pass.

**3. Prompt và tài liệu handoff.**
- Prompt: slot `P1–P10 hoặc V1` (trước là P1–P6). `fight` chỉ được ghi khi level hai bên là số nguyên và mọi unit có `api`, `star`, `frames`. `timestamp_s` không thay thế khung hình.
- Trạng thái hợp lệ: `pending`, `working`, `done`, `blocked`, `stale`. `ok`, `partial`, `skipped` không hợp lệ và bị `bad_status` báo lỗi. Quy đổi: đang làm dở → `working`; bỏ qua vì lý do nêu trong `remaining` → `blocked`.

**4. Kiểm thử hành vi theo tier** (`selftest_trait_tiers.py`, 27 ca, pass). Với mỗi trait trong bảng và mỗi tier, đo chênh lệch on/off trên engine và so với snapshot. Các giá trị khớp: Brawler (120 đội, v·base thành viên), Juggernaut (0,20/0,30/0,42 thành viên; 0,04/0,06/0,08 phi thành viên), Defender (25/60/115 thành viên; 12 phi thành viên), Rapidfire (×1,10 cả đội), Hunter (×(1+v) thành viên), Spellweaver (100·v chênh lệch), Executioner (+0,15 tier 1).
- Defender kiểm tra quy tắc max (25, không phải 37). Đây là hồi quy của giả định mở, không xác nhận quy tắc đó đúng.
- `selftest_traits.py` (so loader với snapshot) vẫn giữ nguyên, bổ sung cho kiểm thử trên.

**5. Độ phủ augment (đã kiểm chứng).**
- Nội dung Set 18 có 252 augment `DA_*`. **Không có augment `DA_*` nào có handler** trong `augments_set17`.
- Thử trực tiếp: một bàn có augment `DA_18_BlossomTraitAugment` cho cùng `p_a` với bàn không có augment (PRIMARY). Augment không có hiệu ứng trong PRIMARY.
- 70 khóa có handler đều là augment của set cũ (TFT6–TFT11 và các khóa `TFT_`). Cả 70 có mặt trong nội dung Set 17, và mô tả cùng khóa biến giữa Set 17 và Set 18 (0/70 khác nhau).
- **Giới hạn engine:** PRIMARY bật `augments=True` nhưng không mô hình hóa augment Set 18. Đây là giới hạn chính, cần nêu khi báo bất kỳ điểm nào.
- Đính chính mục 11.23: khẳng định về Kayle scrapper đã rút lại đúng. Thêm: câu về `_GENERIC_ITEM` không chạm tới đường record là SAI; đã sửa ở 11.25.

**6. Tên item.** Giữ nguyên thay đổi đã ghi ở 11.23 (`B.F. Sword` nay chỉ còn `DA_Component_BFSword`).

**7. Chạy thử fidelity trên `scoring.jsonl` của fixture.** Thoát 0; báo `inconclusive` (2 ván dưới ngưỡng 30). Không có số điểm nào được báo.

**Chưa xử lý:** n chưa ổn định theo quy tắc (xem mục 1). Khung hình chỉ kiểm tra tồn tại, không kiểm tra nội dung. `pos`, carousel, apiName item vẫn mở.

### 11.25 Đính chính và kết quả không cần dữ liệu VOD (2026-11-26)

**Đính chính.** Khẳng định "`_GENERIC_ITEM` luôn là 0 khi chấm bản ghi" (11.23 và 11.24 mục 5) là SAI. `fight.boards_of` đặt `items=len(item_apis)` cho mọi unit có item, nên `build_unit` cộng `_GENERIC_ITEM` (+150 HP, +15 AP, +15 giáp, +15 kháng phép, +0,15 AD) một lần cho mỗi item trên bản ghi. Mục 475 đã ghi đây là quy ước của engine (`_equip` tăng `items`), giữ nguyên và chờ tác giả engine xác nhận. Không sửa mã trong commit này.

**Đo tác động của generic item** (`check_generic_items.py`, không dùng VOD). 20 bàn ngẫu nhiên, mỗi unit 0–2 item lấy từ `TFT_Item_*` có hiệu ứng, n=60, PRIMARY. So `items=len` (hiện tại) với `items=0`:
- Δp trung bình −0,041; |Δp| lớn nhất 0,9; 8/20 bàn có |Δp| ≥ 0,1.
- File: `results/fixed/combat/generic_items_effect.json`.
- Đây là đo độ nhạy trên mẫu nhỏ, không chứng minh cách nào đúng, và chưa có khoảng tin cậy.

**Chưa quyết, chưa sửa.** Nội dung Set 18 có 776 item, 448 có hiệu ứng. Nhiều item hoàn chỉnh (ví dụ `DA_GuinsoosRageblade`, `DA_InfinityEdge`) có `composition` nhưng không có hiệu ứng, và PRIMARY tắt `item_alias`. Với `items=0` các item này mất hết giá trị, nên không thể bỏ `_GENERIC_ITEM` mà không đổi nền PRIMARY. Hai hướng: (a) giữ nguyên, hoặc (b) chỉ cộng generic cho item không có hiệu ứng thật. Quyết định cần kiểm tra thêm bằng danh sách api item trong nội dung và quy tắc engine. Mọi thay đổi là đổi cấu hình đông lạnh (mục 357) và phải ghi thành mục mới.

**Kết quả các kiểm tra và phạm vi của từng kết quả:**
- **Đối xứng và seed tiệm cận** (`check_adaptive_n.py`): 1000 cặp gần nhau, 319 cặp có 0,1 ≤ p(n=20) ≤ 0,9, chạy n=400 với seed 0 và seed 1000. Đảo 13/319 = 4,08%, ngưỡng 5% → đạt. Bàn trong kiểm tra này không có item (`check_symmetry_seed._board` đặt `items: []`), nên kết quả không áp dụng cho bản ghi có item và không phụ thuộc lỗi generic item.
- **Lệch bên** (`check_mirror.py`): A đấu A, 50 bàn không item, n=400. Lệch trung bình +0,0075 (SE 0,0059), ngưỡng 0,01 → không bị đánh dấu. Độ chính xác khoảng ±0,012, nên chỉ kết luận được "không thấy lệch vượt 0,01", không kết luận engine không thiên vị.
- **Augment** (`check_augment_sweep.py`): 252 augment `DA_*` trên một bàn cân bằng (chọn trong khoảng 0,3–0,7), n=200, không item. Số augment làm đổi p: 0/252. Đây là một bàn, một seed; cùng với việc Set 18 không có handler (11.24 mục 5) thì PRIMARY không mô hình hóa augment.
- **Số lượt mô phỏng n:** quy tắc 11.24 mục 1 yêu cầu tăng n khi tỷ lệ đảo ở n=20 vượt 5%. Tỷ lệ đảo là 9,7% (n=20) và 5,8% (n=100). Kết quả n=400 ở trên đạt 4,08%, nhưng cấu hình đông lạnh trong `fidelity.py` vẫn là **n=20**. Chưa đổi `fidelity.py`. Đạt ở n=400 không có nghĩa là n=20 đủ; việc chuyển sang n=400 (chi phí CPU khoảng 20 lần) và đăng ký lại là quyết định còn lại.

**Mô hình PRIMARY hiện làm gì** (tham chiếu, không phải kết luận về độ đúng):

| Thành phần | Trạng thái trong PRIMARY | Kiểm thử hoặc kết quả |
|---|---|---|
| Ability | generic | chưa có kiểm thử hành vi riêng |
| Item | đếm số item cộng `_GENERIC_ITEM`; chỉ 114/731 item có tác động thật (chỉ số hoặc hook), còn lại không phân biệt được item nào (xem 11.26) | `check_item_effects.py` |
| Augment | bật, nhưng không có handler Set 18 nên không tác động | augment sweep 0/252 |
| Trait | bật, bảng theo tier | `selftest_trait_tiers.py`, 27 ca |
| Emblem | tắt (SECONDARY bật) | — |
| Item alias | tắt (SECONDARY bật, 45 alias) | `selftest.py` |
| Vị trí, carousel, apiName phía client | chưa mô hình | — |

**Thay đổi mã trong commit này:** `usable.py` (kiểm `items`/`augments` thiếu, khung hình ở cấp unit), `fidelity.py` (`inconclusive` khi rỗng), `selftest_usable.py`, prompt và tài liệu handoff, các script `check_*.py`, `selftest_empty_scoring.py`, và các file kết quả JSON. Không đổi PRIMARY, SECONDARY hay n.

**Còn mở:** quyết định generic item (trên); n=20 hay n=400; augment Set 18 chưa có handler; vị trí, carousel, apiName; ba giả định trait còn mở (Defender lấy max hay cộng dồn, gốc của Brawler theo pct, Spellweaver cộng dồn); nhãn "18.7" của snapshot CDragon là sai (bản vá thực tế chưa rõ); khung hình chỉ kiểm tra tồn tại, không kiểm tra nội dung.

### 11.26 Phân loại item theo tác động trong engine; giữ `items=len`; n đổi sang 400 (2026-11-26, không dùng dữ liệu VOD)

**Đính chính.** Bản trước của 11.26 có ba sai: (a) "65/776 item không có hiệu ứng, khoảng 8%" đếm sai phạm vi; (b) "cộng trùng chỉ ở SECONDARY" là sai; PRIMARY cũng có 9 item `DA_*` đổi chỉ số, nên cộng trùng xảy ra ở cả hai; (c) đo chỉ số thiếu cờ `can_ability_crit` và bảng hook chưa đúng.

**Cách đo** (`scripts/combat/check_item_effects.py`, kết quả `results/fixed/combat/item_effect_classes.json`). 731 api item mà `names18` xuất ra (bỏ ba mục alias twin). Với mỗi api: `build_unit` một unit cố định, có và không có item, không tính khối chung; đo chín giá trị, gồm cả `can_ability_crit`. Hook: khóa chính xác của bảng `ITEM_ON_ATTACK`, `ITEM_ON_CAST`, `ITEM_ON_DAMAGED`, `ITEM_HP_THRESHOLD`, `ITEM_REVIVE`, `ITEM_COMBAT_START`, `ITEM_ON_TICK` trong `tft_goat.engine.simulate` (khớp tuyệt đối, không chuỗi con).

**Kết quả.**

| Lớp | PRIMARY: stat / stat+proc / không gì | SECONDARY (alias): stat / stat+proc / không gì |
|---|---|---|
| khác | 72 / 1 / 484 | 72 / 1 / 484 |
| composition | 2 / 0 / 55 | 9 / 27 / 21 |
| DA_Component_* | 0 / 0 / 10 | 7 / 0 / 3 |
| DA_Artifact* | 0 / 0 / 31 | 0 / 0 / 31 |
| *Radiant | 39 / 0 / 37 | 39 / 0 / 37 |
| **Tổng** | **113 / 1 / 617** | **127 / 28 / 576** |

Trong 113 item `stat` của PRIMARY: 104 có tiền tố `TFT*_Item_*`, 9 là `DA_*` (`DA_Flow18`, `DA_Flow18_Upgrade`, `DA_Hugify18`, `DA_InfinityEdge`, `DA_InfinityEdgeRadiant`, `DA_JeweledGauntlet`, `DA_JeweledGauntletRadiant`, `DA_MarksmensGale18`, `DA_StandAlone18`).

Trong 617 "không gì" của PRIMARY: 328 không có hiệu ứng trong nội dung; 289 có hiệu ứng nhưng khóa không được `_apply_effects` nhận (ví dụ `DamageAmp`, `NumUnits`, `starLevel`, `Duration`, `UnitTier`, khóa băm `{...}`).

**Cộng trùng (chỉ số thật + khối chung).** Với `items=len`, mọi item trên bản ghi đều nhận khối `_GENERIC_ITEM`. Vì vậy cộng trùng xảy ra cho cả 114 item có tác động ở PRIMARY và 155 ở SECONDARY. Với 617 item PRIMARY còn lại, khối chung là toàn bộ tác động. Mô hình item của PRIMARY gần như không phân biệt item nào.

**Bằng chứng nguồn cho quy ước.**
- `unit.py:14` ghi khối chung là "item trung bình khi không biết identity".
- `surrogate/dataset.py:92` dùng đúng trường hợp đó: `BoardUnit(..., items=len(u.items))` không có `item_apis`.
- Đường combat của engine (`simulate.py:321`, `generic_items=bu.items`) và đường env (`env/actions.py:223-224`, `items += 1` cùng lúc với `item_apis`) đều cộng khối chung cho item có identity.
- Kết luận: `boards_of` của chúng ta làm đúng như đường combat của engine tại `d5358e94`. Chú thích của `unit.py` lại gợi ý khối chung chỉ dành cho item không có identity. Hai điều này mâu thuẫn; đó là câu hỏi cho tác giả `tft_goat`, không phải lỗi của wrapper.

**Quyết định: giữ `items=len` (không đổi `boards_of`).** Lý do: đổi sang `items=0` hoặc sang "chỉ khối chung khi không có identity" là thay đổi cấu hình đông lạnh, không có dữ liệu thật để chọn, và phải ghi thành mục mới với kiểm tra lại. Việc này chờ tác giả engine.

**Hook (chỉ ở SECONDARY, và PRIMARY gần như không có).** Hook khóa theo `TFT_Item_*` nên 27 item composition ở SECONDARY có proc. Dưới PRIMARY chỉ 1 item có proc.

**Alias SECONDARY chưa phủ** (không có tác động sau alias):
- `DA_TacticiansCrown`, `DA_TacticiansShield`, `TFT_Item_ForceOfNature`, `TFT_Item_TacticiansScepter`;
- `DA_Component_FryingPan`, `DA_Component_Spatula`, `DA_Component_TearOfTheGoddess`;
- `DA_TacticiansCape` được alias sang `TFT_Item_TacticiansRing`, nhưng alias đó không có hiệu ứng.

**Emblem không thuộc nhóm item.** 16 mục `DA_18_Emblem*` nằm trong danh sách item của `names18` và được gắn lớp `composition`. Chúng do cờ `emblems` xử lý, không phải item trang bị. Khi báo cáo, trừ 16 mục này.

**n đổi từ 20 sang 400.** Quy tắc 11.24 mục 1 yêu cầu tăng n khi tỷ lệ đảo ở n=20 vượt 5%. Tỷ lệ là 9,7% (31/319); n=100 là 5,8% (17/294).
- Kiểm tra thích ứng n=400 chạy lại tại `58f26fce`: kết quả giống hệt lần đầu (13/319 = 4,08%, `git diff` rỗng), nên tái lập được.
- Với mẫu số theo p ở n=400 (X = 269 cặp có 0,1 ≤ p ≤ 0,9): 13/269 = 4,83%, vẫn dưới 5%. Hai cách đếm đều đạt, nhưng biên khá mỏng.
- Đã đổi mặc định `score(path, n=400, ...)` và dòng lệnh trong `scripts/combat/fidelity.py`.
- **Lưu ý:** kiểm tra chỉ dùng bàn không có item (`check_symmetry_seed._board` đặt `items: []`), nên chưa được xác nhận cho bản ghi có item.
- Chi phí CPU khoảng 20 lần so với n=20 khi chấm dữ liệu thật; chưa đo thời gian thực.

**Kiểm thử.** `selftest.py`, `selftest_empty_scoring.py`, `selftest_ingest_vod.py`, `selftest_usable.py` đều PASS sau khi đổi n.

**Phạm vi.** Đây là kết luận về cấu hình mô phỏng và về mô hình engine, không phải độ đúng so với trận thật.

### 11.26 (bổ sung) Câu hỏi bàn giao cho tác giả `tft_goat`

Mục generic item được coi là **bàn giao**, không còn treo ở phía chúng ta. Câu hỏi:

1. `unit.py:14` ghi `_GENERIC_ITEM` là "item trung bình khi không biết identity", và `surrogate/dataset.py:92` chỉ dùng khối này khi `items` không kèm `item_apis`. Nhưng `env/actions.py:223-224` và `simulate.py:321` lại cộng khối này cho cả item có identity. Quy ước đúng là gì: (a) khối chung cho mọi item (như hiện tại), hay (b) chỉ cho phần item không có identity (`items - len(item_apis)`)?
2. Nếu (b), đường record của chúng ta sẽ không còn khối chung nào, và 617 item trong PRIMARY sẽ không có tác động nào (xem bảng 11.26). Có chấp nhận được không, hay cần bổ sung hiệu ứng cho các lớp `composition`, `DA_Component_*`, `DA_Artifact*`, `*Radiant` không có chỉ số?
3. Hook proc khóa theo `TFT_Item_*`, còn `DA_*` không có hook. Đây có phải thiết kế có chủ đích?

Bằng chứng để tái hiện: `scripts/combat/check_item_effects.py`, kết quả `results/fixed/combat/item_effect_classes.json`.

**Giới hạn chưa kiểm:** kiểm tra thích ứng n=400 (13/319, 4,08%) chỉ dùng bàn không có item. Chưa đo cho bàn có item; kết luận đổi n chưa được xác nhận cho bản ghi có item.

### 11.27 Đăng ký trước: kiểm tra thích ứng n=400 trên bàn CÓ item (2026-11-26, không dùng VOD)

Quy tắc đăng ký trước, không đổi sau khi chạy:
- Tập cặp: 1000 cặp gần nhau như `check_adaptive_n.py` (Random(7), B là bản sao của A với một unit đổi tướng hoặc sao). Khác: mỗi unit của A được gắn 0–2 item lấy ngẫu nhiên (Random(13)) từ item Set 18 có nội dung, không tính emblem và mục alias twin. B kế thừa item của A, rồi đổi một unit như cũ.
- Chọn cặp: p ở n=20, seed0=0, giữ 0,1 ≤ p ≤ 0,9.
- Đo: với mỗi cặp giữ lại, p ở n=400 với seed0=0 và seed0=1000. Đếm đảo chiều (khác phía 0,5, cả hai khác 0,5 chính xác).
- Ngưỡng: tỷ lệ đảo ≤ 5% trên mẫu số là số cặp giữ lại. Mẫu số thứ hai: cặp có p(seed0=0, n=400) trong 0,1–0,9 (ghi kèm, không dùng để quyết định).
- Nếu vượt 5%: ghi rõ, không đổi n lần nữa mà không đăng ký mới.
- Script: `scripts/combat/check_adaptive_n_items.py`; kết quả: `results/fixed/combat/adaptive_n_items_check.json`.

**Kết quả (chạy tại commit hiện tại; `results/fixed/combat/adaptive_n_items_check.json`):**
- 398 cặp có item giữ lại (0,1 ≤ p(n=20) ≤ 0,9); 4 cặp p = 0,5 chính xác bị loại; 20 cặp đảo chiều.
- Tỷ lệ đảo trên mẫu số chính: 20/398 = **5,03%**, vượt ngưỡng 5%. **KHÔNG ĐẠT.**
- Mẫu số thay thế (p(n=400) trong 0,1–0,9): 20/344 = 5,81%, cũng không đạt.

**Hệ quả theo quy tắc đã đăng ký:**
- Đổi n từ 20 sang 400 ở 11.26 được kiểm trên bàn không có item (4,08%, đạt) nhưng **không được xác nhận cho bàn có item**: trên bàn có item, n=400 vẫn vượt ngưỡng 5% (5,03%).
- Theo quy tắc, không đổi n thêm lần nào mà không đăng ký mới. Chưa đổi cấu hình; `fidelity.py` giữ n=400 như đã ghi ở 11.26.
- Việc cần quyết định: (a) đăng ký một mức n cao hơn (ví dụ 800) với quy tắc mới, hoặc (b) chấp nhận rủi ro đảo ~5% ở n=400 và ghi rõ là giới hạn đã biết khi báo cáo số liệu. Không tự chọn trong lúc chưa có đăng ký.

### 11.28 Đăng ký trước: n=800 trên bàn có item (quyết định của advisor, 2026-11-26, không dùng VOD)

Lý do: 11.24 mục 1 yêu cầu tăng n khi tỷ lệ đảo trên 5%. Bản ghi thật có item nên kết quả trên bàn có item là kết quả quyết định. 11.27 ở n=400 không đạt (20/398 = 5,03%).
- Tập: đúng 398 cặp của 11.27 (seed0 = 0 và 1000), cùng định nghĩa đảo chiều, mẫu số chính 398, ngưỡng 5%. Script assert `len(mid) == 398`.
- Luật dừng: đạt → đổi mặc định n sang 800 trong `fidelity.py` và cập nhật 11.26; không đạt → giữ n = 400, ghi cả hai con số là giới hạn đã biết. Cả hai trường hợp đóng câu hỏi về n; không tăng n thêm.
- Kết quả ghi ra `results/fixed/combat/adaptive_n_items_n800.json`.
- Chỉ chạy trên PRIMARY.

