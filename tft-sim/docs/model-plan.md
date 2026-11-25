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
