# Cần gì để tiếp tục

File này ghi mọi thứ engine cần từ người dùng hoặc phiên ingest, và các quyết định đã tự đưa ra khi người dùng vắng mặt. Mỗi mục có trạng thái: **mở**, **đã có**, hoặc **đã quyết**.

## 1. Từ người dùng

| # | Cần gì | Vì sao | Mở khóa | Trạng thái |
| --- | --- | --- | --- | --- |
| U1 | Bảng XP theo level (xp mỗi lần mua, xp để lên từng level) | Quyết định lên level và thời điểm lên level | Bước 3 của quyết định XP | **mở** |
| U2 | Dùng bảng odds nào: `rules.js` (chưa xác minh, lệch nguồn Set 17 ở level 8, 9) hay nguồn khác | Xác suất gặp tướng, quyết định roll | Mọi tính toán hit chance | **mở** |
| U3 | File dữ liệu của set hiện tại (tướng, tộc, mốc, cost) | Chọn line tự động, thay `tft_set_line` nhập tay. Id trong file phải khớp id shop và board: hiện id live là `DA_18_*`, còn `set17.json` là `TFT17_*`, nên line tự động chưa có tác dụng trong game. `scripts/export-set.js` chỉ giữ id bắt đầu bằng `TFT<set>_`, trong khi `docs/tft-knowledge.md` ghi tướng Set 18 là `DA_*`; chạy như hiện tại sẽ không xuất được tướng Set 18 nào | Line tự động (`TFT_AUTO_LINE=1`) | **mở** |
| U7 | Trọng số line tự động (2 khi trùng tướng trên bàn, 2 khi đạt mốc, 1 khi trùng tộc chưa đạt mốc, trần 5) là heuristic của phiên engine; cần người dùng điều chỉnh | Chất lượng line tự động | **mở** |
| U8 | Trọng số và ngưỡng trong `decide.js` (0.45 cho roll, 0.5 cho xp, hệ số điểm mua, mốc level theo stage) chưa được tinh chỉnh. Tinh chỉnh cần log trận thật hoặc capture | Chất lượng quyết định | **mở** |
| U4 | Xác nhận: mua tướng hoàn thành sao khi bench đầy có hợp lệ trong client không | Engine đang khuyến nghị lượt này | Quy tắc gate bench đầy | **mở** |
| U5 | Lượt roll miễn phí có cộng dồn sang stage sau không? | Quy tắc tính roll miễn phí | Giá trị `freeRolls` | **mở** |
| U6 | Roll miễn phí chỉ được khuyến nghị khi đã đặt mục tiêu (`tft_set_target`). Có đúng ý không? | Hành vi roll miễn phí | Khuyến nghị roll | **mở** |
| U9 | Ba quy tắc, đã có trong code nhưng tắt mặc định: roll khi còn từ 50 vàng; lên level trước 50 vàng ở stage đầu; dùng mốc level của guide metabot thay `LEVEL_BY_STAGE` (chi tiết ở đề xuất bên dưới) | Mỗi quy tắc đổi quyết định mua/roll/level | Quyết định roll và lên level | **mở** |

**Đề xuất từ nghiên cứu (`docs/tft-strategy.md`), chờ người dùng xác nhận. Chưa đóng mục nào:**
- **U1 (đề xuất):** bảng XP theo level từ wiki Riot, TFT:Experience (`verified`, không ghi set): 2→3 = 2 XP, 3→4 = 6, 4→5 = 10, 5→6 = 20, 6→7 = 36, 7→8 = 60, 8→9 = 68, 9→10 = 68. Đoạn tìm kiếm cho Set 14 ghi khác (7→8 = 48, 8→9 = 76). Cần xác nhận bảng nào áp dụng cho Set 18.
- **U2 (kiểm tra lại, bảng dữ liệu):** trang metabot Set 18 leveling (đăng 2026-10-24) không có bảng đầy đủ. Chỉ có câu "on patch 16.20, level 8 shows 4-costs 30%", "level 9 shows 4-costs 33% and 5-costs 15%", "level 10 shows 4-costs 40% and 5-costs 25%". Trang không nói gì về level 11. Ở level 10 các số khớp `rules.js`. Ở level 8 và 9 trang khớp bảng Set 17 và bảng của metabot, và lệch `rules.js`. Đây là một site, nên không tính là nguồn độc lập. Bảng Set 17 trong `docs/tft-knowledge.md` chỉ có level 6–11; level 1–5 không có nguồn trong file đó. Seemeta ghi odds của Set 18 chưa có trong client data. Cùng một site nên các số của metabot không độc lập.
- **U2 (đề xuất):** bảng odds của metabot (`single-source`, không ghi set) khớp Set 17 trong `docs/tft-knowledge.md` ở level 8 (15/20/32/30/3) và level 9 (10/17/25/33/15). `rules.js` lệch ở hai level này và khớp ở level 4–7. Trang metabot ghi rõ đây là "Approximate shop odds by level... use them as a map, not a precise contract" (xấp xỉ, dùng như bản đồ, không phải hợp đồng chính xác). Ô 4 vàng ở level 8: `rules.js` 24% (khớp số Set 14 trong đoạn tìm kiếm), metabot 30%. Đề xuất: dùng bảng của metabot cho level 8 và 9 sau khi xác nhận set.
- **U4 (đề xuất):** chưa có nguồn xác nhận. Trạng thái `pending`.
- **U5 (đề xuất):** chưa có nguồn. Trạng thái `pending`.
- **Mới, từ nghiên cứu (G8):** `rules.js` không có dòng odds hay pool cho cost trên 5. Engine nhận tướng cost 7 mà không báo lỗi và cho hit 0. Không đề xuất giới hạn cost 1–5, vì làm vậy sẽ bỏ tướng cost 7 của Set 19 (đoạn tìm kiếm, `search summary`). Cần người dùng xác nhận bảng odds và pool cho cost 6–7 nếu muốn tính xác suất cho chúng.
- **Mới, từ nghiên cứu (G11):** `LEVEL_BY_STAGE` đặt level 8 ở stage 4. Metabot, Set 18 leveling guide (`single-source`, patch 16.20, đăng 2026-10-24) đặt level 7 quanh 4-1 và level 8 quanh 4-5 hoặc 5-1. Chưa đóng; cần người dùng chọn mốc (xem U9).
- **Mới:** ngày Set 19 còn xung đột giữa 1/12 và 2/12. Cần người dùng xác nhận nếu muốn dùng làm mốc.
- **Mới, chuỗi thắng/thua:** mục Income của wiki ghi 3–4 +1, 5 +2, 6+ +3. Metabot ghi "Typical streak bonuses" 2–3 +1, 4 +2, 5+ +3 (`single-source`, bảng "thường gặp", không phải quy tắc). Ghi chú V10.8 của wiki là lịch sử đã thay thế. Lịch sử bản vá của wiki chỉ đến V10.x nên không định ngày được mục Income. Cần người dùng xác nhận set và giá trị.
- **Mới, U1:** trang wiki TFT:Experience đã lưu không có mục lịch sử bản vá. Lịch sử bản vá của TFT:Gold chỉ đến V10.x, nên cả hai không định ngày được bảng nào áp dụng. Chuỗi "48 XP", "76 XP", "84 XP" không có trong trang; bảng có 60 và 68.

**U9 (đề xuất, tắt mặc định, chờ người dùng đồng ý).** Ba quy tắc sau đã được triển khai, bật bằng `TFT_RULES` (xem `docs/architecture.md`). Mặc định tắt, nên hành vi hiện tại không đổi. Bật sẽ đổi quyết định:
1. Roll khi vàng còn từ 50 trở lên (giữ lãi tối đa, roll bằng phần vàng thừa).
2. Lên level trước khi có 50 vàng ở các stage đầu (bỏ điều kiện `gold >= 50` ở stage sớm, theo bảng XP rẻ 2, 6, 10).
3. Mốc level của guide metabot thay cho `LEVEL_BY_STAGE` (level 7 quanh 4-1, level 8 quanh 4-5 hoặc 5-1). Đây là `single-source`. Bảng `LEVEL_BY_STAGE_GUIDE` = [0, 2, 4, 6, 7, 8, 9, 9]: lấy level mở đầu của mỗi stage, vì engine không nhận `round`. Bảng đọc level 8 là mở đầu stage 5, và stage 3 là 6 (mốc 3-2, không phải mốc mở đầu 5 của 2-5).
4. Dùng `hitWithin` (xác suất trong toàn bộ ngân sách roll) trong điểm roll. Chưa triển khai: hiện chỉ hiển thị.

Các cách đọc cần người dùng đổi nếu không đúng:
(a) "giai đoạn đầu" là `stage <= 2` trong `earlyLevel`;
(b) bảng mốc mở đầu theo stage trong `guideLevels`;
(c) `earlyLevel` ở stage 2 trở xuống mua XP từ 4 vàng cho tới mục tiêu level, không kiểm tra lãi;
(d) `earlyLevel` phụ thuộc vàng, level và stage. Khi HUD thiếu (I5), các giá trị này là ước lượng, nên quy tắc này dễ sai nhất khi nguồn không đầy đủ.

Các test ghim hành vi hiện tại (`decide.test.js`, mục U9) và các test bật từng quy tắc (`rules.test.js`) đều có trong repo. Invariant chạy cả hai cách: tắt hết là 366/1485/65/35/49, bật cả ba là 363/1484/75/29/49.

## 2. Từ phiên ingest

Format và danh sách trường xem `docs/engine-state.md`, mục 4.

| # | Cần gì | Vì sao | Trạng thái |
| --- | --- | --- | --- |
| I1 | `id` và `star` trên `board` (hiện chỉ có `championName`, `starLevel`) | Đếm bản trên bàn | **mở** |
| I2 | `bench` với `id`, `star`, `sellValue` | Gate bench đầy, bán để nhường chỗ | **mở** |
| I3 | `takenByOthers` cho từng ô shop (số bản người khác đang giữ) | Xác suất gặp tướng chính xác | **mở** |
| I4 | `round`, `phase`, `xp`, `xpToNext` | Lên level và roll đúng thời điểm | **mở** |
| I5 | Đánh dấu giá trị ước lượng trong `missing` (gold, level, stage khi không có HUD), và cho biết tướng shop không rõ cost đang được gán cost 1 mặc định (`standaloneSource.js`) | Tránh khuyến nghị lên level dựa trên vàng bịa; tránh mua/bán sai giá | **mở** |
| I7 | Gửi `freeRolls` (số lượt roll miễn phí còn lại) | Engine đã hỗ trợ nhưng không nguồn nào gửi | **mở** |
| I6 | Tên tướng trong `championName` và `id` của HUD shop khớp nhau | Nếu khác, `copiesOwned` luôn bằng 0 | **mở** |
| I8 | Nguồn gửi `set` và `patch` (phiên bản bản vá đang chạy). Lưu ý: `patch` là nhãn kiểu metabot (16.x), không phải số bản vá của Riot (18.x); cần thống nhất cách đánh số trước khi gửi | Không có nó, engine không biết đang dùng đúng hồ sơ; `TFT_PROFILE_FILE` và `TFT_PATCH` chọn bằng tay | **mở** |

## 3. Quyết định đã tự đưa ra

| Ngày | Quyết định | Commit |
| --- | --- | --- |
| 2026-11-23 | Sửa điểm mua: không mua tướng đã đủ 9 bản; thưởng ghép cặp khi hoàn thành sao | `7ff9485` |
| 2026-11-23 | Tài liệu hoá nhu cầu dữ liệu và hợp đồng giả định | `c5c15e1` |
| 2026-11-23 | Đếm bản từ board và bench, trừ số bản người khác giữ | `afe451c` |
| 2026-11-23 | Chặn mua khi bench đầy; bán để nhường chỗ; log schema 2 | `37cb046` |
| 2026-11-23 | Chỉ bán khi không có lượt mua; giữ bản đang cần trong line | `4766647` |
| 2026-11-23 | Mục tiêu đang có trong shop được mua bất kể priority trên shop; không roll khi mục tiêu đã có trong shop | `0376529` |
| 2026-11-23 | Bỏ qua ô shop không có cost hợp lệ (`thiếu cost`); thêm test bất biến trên 2.000 trạng thái sinh có seed | `744ee3d` |
| 2026-11-23 | Mua món muốn mua có sẵn trước khi roll nếu còn đủ vàng để roll; hỗ trợ lượt roll miễn phí (`freeRolls`, không tốn vàng, không bị phạt) | `ef40fd1` |
| 2026-11-23 | Diễn giải "tối ưu" là tối ưu chất lượng quyết định. Tốc độ không cần sửa: khoảng 70–130 ns mỗi quyết định so với vòng lặp 250 ms | `8cfa5d0` |
| 2026-11-23 | Chọn hành động tốt nhất trong số các hành động vượt ngưỡng của chính nó: mua hoặc bán không còn bị giữ lại bởi roll dưới ngưỡng 0.45 hoặc xp dưới 0.5 | `8cfa5d0` |
| 2026-11-23 | Bán trước khi roll khi việc bán vẫn để đủ vàng roll; sửa văn bản "Mua trước rồi mới roll" để chỉ hiện khi thật sự có roll sau đó | `87987bc` |
| 2026-11-23 | Line tự động (`src/engine/autoline.js`) chỉ bật khi `TFT_AUTO_LINE=1`, mặc định tắt để giữ hành vi hiện tại; chấm điểm theo bàn, không theo toàn bộ tướng sở hữu, để quân bench không khớp vẫn bán được | `8ee5511` |
| 2026-11-23 | Kiểm tra line tự động trên file set thật qua `createApp` (một khung replay, mua tướng cùng tộc với bàn). Chưa chuyển ngưỡng sang `rules.js` vì không đổi hành vi và chưa có gì để tinh chỉnh (xem U8) | `cad25e9` |
| 2026-11-23 | Hiển thị xác suất trong toàn bộ ngân sách roll (`rolls`, `hitWithin`) trong trace và lý do; không đổi điểm, nên không đổi quyết định | `fdabca4` |
| 2026-11-23 | Thêm ba quy tắc U9 sau `TFT_RULES`, mặc định tắt; test ghim hành vi hiện tại và kiểm tra từng quy tắc bật | `eba636a` |
| 2026-11-23 | Đưa bảng dữ liệu vào `profile` (mặc định từ `rules.js`), thêm `TFT_PROFILE_FILE` và `TFT_PATCH` với bản vá chồng lên nhau; mặc định tắt | `7494f0b`, `2f50e6c`, `44e43f9` |
| 2026-11-23 | Hồ sơ candidate Set 18 (bản 16.20, hàng 8 và 9), tắt mặc định, chỉ dùng khi đặt `TFT_PROFILE_FILE` | `63e1724` |

Giới hạn đã biết: `tft_evaluate_state` và các công cụ `tft_rules`, `tft_hit_chance` không dùng `TFT_RULES`, `TFT_PROFILE_FILE`, `TFT_PATCH` và line tự động; chúng đọc bảng mặc định của `rules.js`; đặt priority 0 thủ công không loại được tướng đang có line tự động.
