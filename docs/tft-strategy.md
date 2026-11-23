# Chiến lược TFT: nguyên tắc, nguồn và khoảng trống của engine

Trạng thái: **nháp**. Tài liệu này ghi nguyên tắc và số liệu từ nguồn. Vòng này không đổi bảng mặc định trong `rules.js`. Chỉ thêm ba quy tắc U9 tắt mặc định, bật bằng `TFT_RULES` (`keepInterest`, `earlyLevel`, `guideLevels`). `guideLevels` dùng bảng mốc level của metabot (mục 2).

Nhãn trạng thái (theo `docs/tft-knowledge.md`):
- `verified`: đã mở trang và đọc đúng con số đó.
- `search summary`: chỉ có đoạn tóm tắt từ kết quả tìm kiếm, chưa mở trang.
- `conflict`: hai nguồn khác nhau.
- `single-source`: chỉ một nguồn đã mở trang, chưa đối chiếu.
- `pending`: chưa thu thập.

Ngày thu thập: 2026-11-23. Môi trường cho phép `wiki.leagueoflegends.com` và `metabot.gg` (đã đọc bằng `curl`). `esports.gg` và `mobalytics.gg` trả về 403 từ máy chủ đích, nên không đọc được. Công cụ `web-fetch` trong phiên vẫn không phân giải được hai host wiki và metabot, nên toàn bộ trang được đọc bằng `curl`.

Ngày đăng và ngày cập nhật của các trang metabot (lấy từ thẻ meta của trang):

| Trang | Đăng | Cập nhật |
| --- | --- | --- |
| Economy: gold, interest, streaks (`tft-economy-gold-interest-streaks-explained`) | 2026-07-25 | 2026-10-15 |
| When to roll vs level up, shop odds (`tft-when-to-roll-vs-level-up-shop-odds`) | 2026-07-25 | 2026-10-15 |
| Star levels, champion pool (`tft-star-levels-champion-pool-explained`) | 2026-07-28 | 2026-10-15 |
| Set 18 leveling guide (`tft-set-18-leveling-guide-when-to-roll`) | 2026-10-24 | 2026-10-24 |

## 1. Kinh tế

**Nguyên tắc**
- Lãi: cứ 10 vàng giữ lại được thêm 1 vàng cuối vòng, tối đa 5 vàng (đến 50 vàng). `verified` (wiki và metabot).
- Thu nhập thụ động: 5 vàng mỗi đầu giai đoạn chuẩn bị. `verified` (wiki).
- Chuỗi thắng/thua: thêm vàng theo chuỗi. **conflict**, xem bảng dưới.

| Nguồn | 2–3 liên tiếp | 3–4 liên tiếp | 4 liên tiếp | 5 liên tiếp | 5+ liên tiếp | 6+ liên tiếp |
| --- | --- | --- | --- | --- | --- | --- |
| Wiki TFT:Gold, mục Income (trang hiện tại) | — | +1 | — | +2 | — | +3 |
| Metabot, economy guide, "Typical streak bonuses" (`single-source`) | +1 | — | +2 | — | +3 (5+) | — |
| Wiki TFT:Gold, ghi chú V10.8 (lịch sử, đã thay thế) | +1 (2–3) | — | +2 (4) | — | +3 (5+) | — |

Ghi chú: mục Income của wiki và bảng "Typical streak bonuses" của metabot khác nhau. Metabot ghi bảng này là "typical", không phải quy tắc chính thức. Mục lịch sử bản vá mới nhất trên trang wiki là V10.12 (bán lại tướng 1 sao và 1 vàng), không đề cập chuỗi. Chưa biết giá trị nào áp dụng cho Set 18, nên trạng thái là `conflict`.

**Nguồn**
- Riot wiki, TFT:Gold, [wiki.leagueoflegends.com/en-us/TFT:Gold](https://wiki.leagueoflegends.com/en-us/TFT:Gold): `verified` cho lãi và thu nhập thụ động. Trang không ghi rõ set; có mục Enchanted Wilds (Set 18) trong menu.
- Metabot, economy guide, [metabot.gg](https://metabot.gg/en/TFT/guides/tft-economy-gold-interest-streaks-explained): `single-source` cho bảng chuỗi và lãi tối đa 50 vàng.

**Hiện tại engine làm gì**
- Lãi chỉ là chi phí cơ hội: `interestLoss * 0.35` bị trừ khỏi điểm mua, không được tính là thu nhập.
- Không có thu nhập thụ động hay chuỗi thắng/thua trong trạng thái; `streak` đã được nêu trong hợp đồng nhưng không nguồn nào gửi.

**Khoảng trống**
- Engine không biết thu nhập tương lai, nên không thể đánh giá việc giữ vàng để lên level hay roll sau này.
- Chưa có chuỗi thắng/thua: không phân biệt được thắng liên tiếp (giữ lãi) với thua liên tiếp (chi tiêu).

## 2. Lên level và XP

**Nguyên tắc**
- Mua XP: 4 vàng = 4 XP. `verified` (wiki).
- Mỗi vòng nhận 2 XP miễn phí. `verified` (wiki).
- Bảng XP cần để lên level (riêng cho từng bước, theo bản wiki):

| Level hiện tại | XP cần (theo bảng wiki) |
| --- | --- |
| 1 → 2 | (mở đầu, sau wave đầu) |
| 2 → 3 | 2 |
| 3 → 4 | 6 |
| 4 → 5 | 10 |
| 5 → 6 | 20 |
| 6 → 7 | 36 |
| 7 → 8 | 60 |
| 8 → 9 | 68 |
| 9 → 10 | 68 |

Nguồn: Riot wiki, TFT:Experience, [wiki.leagueoflegends.com/en-us/TFT:Experience](https://wiki.leagueoflegends.com/en-us/TFT:Experience): `verified` cho số trong bảng, "4 gold = 4 XP" và "2 XP free at end of round". Trang đã lưu không có mục lịch sử bản vá, nên không xác định được bảng nào áp dụng cho Set 18. Kiểm tra chuỗi chính xác "48 XP", "76 XP", "84 XP": không có trong trang này; "60 XP" và "68 XP" có trong bảng. Trạng thái: **conflict** với đoạn tìm kiếm, cần xác nhận set (U1).

**Mục tiêu level theo stage**
- Metabot, Set 18 leveling guide (`single-source`, đăng 2026-10-24): "level 4 ở 2-1, 5 ở 2-5, 6 ở 3-2, 7 ở 4-1, 8 ở 4-5 hoặc 5-1 khi rolldown, 9 ở 5-5". Trang ghi số liệu theo patch 16.20.
- Trang Set 18 leveling của metabot (`single-source`, một site): chỉ có câu về level 8 (4-cost 30%), level 9 (4-cost 33%, 5-cost 15%) và level 10 (4-cost 40%, 5-cost 25%) trên patch 16.20. Không có bảng đầy đủ và không nói về level 11. Level 8 và 9 khớp bảng Set 17 và bảng metabot, lệch `rules.js`; level 10 khớp `rules.js`.
- `LEVEL_BY_STAGE` trong `rules.js` đặt level 8 ở stage 4 (xem G11). Đây là điểm lệch với metabot.

**Hiện tại engine làm gì**
- Chỉ lên level khi `gold >= 50` và `level < LEVEL_BY_STAGE[stage]` (mục tiêu 2/4/6/8/8/9/9 theo stage). Không dùng bảng XP.
- Điểm XP là `(wanted - level) * 1.1` (hoặc 0.6 khi HP thấp), và chỉ mua khi điểm > 0.5.

**Khoảng trống**
- `guideLevels` (bật bằng `TFT_RULES`) dùng mốc level của metabot thay `LEVEL_BY_STAGE`. Mốc stage 3 là 6, là mốc 3-2, không phải mốc mở đầu; xem comment trong `rules.js`.
- Không có XP hiện tại và XP cần cho level tiếp theo, nên không biết còn bao nhiêu XP để lên level.
- Điều kiện `gold >= 50` loại bỏ việc lên level sớm ở các vòng đầu, dù bảng wiki cho thấy các bước đầu rất rẻ (2, 6, 10 XP).

## 3. Roll: khi nào, mức level nào

**Nguyên tắc**
- Tỉ lệ shop theo level là điểm mấu chốt. Bảng sau lấy từ metabot, `single-source`. Trang ghi rõ: "Approximate shop odds by level... use them as a map, not a precise contract" (xấp xỉ, dùng như bản đồ, không phải hợp đồng chính xác). Trang không ghi set:

| Level | 1 vàng | 2 vàng | 3 vàng | 4 vàng | 5 vàng |
| --- | --- | --- | --- | --- | --- |
| 4 | 55% | 30% | 15% | 0% | 0% |
| 5 | 45% | 33% | 20% | 2% | 0% |
| 6 | 30% | 40% | 25% | 5% | 0% |
| 7 | 19% | 30% | 40% | 10% | 1% |
| 8 | 15% | 20% | 32% | 30% | 3% |
| 9 | 10% | 17% | 25% | 33% | 15% |

- Mốc: 3 vàng đạt đỉnh ở level 7; 4 vàng tăng mạnh ở level 8; 5 vàng thực tế từ level 9.
- Khuyến nghị chung của metabot (guide cùng trang, `single-source`): giữ vàng và lên level theo lịch (thường đạt level 7 quanh 4-1, level 8 quanh 5-1); chỉ roll mạnh khi máu thấp hoặc bàn đã đủ mạnh.

**Hiện tại engine làm gì**
- `SHOP_ODDS` trong `rules.js`: khớp metabot ở level 4–7, nhưng **level 8 và 9 không khớp** (`rules.js` level 8: 17/24/32/24/3; level 9: 15/18/25/30/12; metabot: 15/20/32/30/3 và 10/17/25/33/15). Riêng ô 4 vàng ở level 8: `rules.js` 24%, metabot 30%. Số 24% của `rules.js` khớp con số Set 14 trong đoạn tìm kiếm. Bảng `docs/tft-knowledge.md` cũng ghi cùng xung đột này với Set 17.
- Roll chỉ được khuyến nghị khi có mục tiêu (`tft_set_target`), tính xác suất gặp một tướng trong một shop.
- Điều kiện roll: 12 vàng; 2 khi HP ≤ 30; 0 khi có lượt miễn phí (`freeRolls`).

**Khoảng trống**
- Điểm roll chỉ tính một shop. Từ `fdabca4`, trace và lý do hiển thị xác suất trong toàn bộ ngân sách roll (`rolls`, `hitWithin`), nhưng điểm roll không dùng con số này. Đưa nó vào điểm sẽ đổi quyết định, nên chờ U9 (G5).
- Không có chiến lược "slow roll" (giữ vàng để roll tại level cụ thể) ngoài điểm số một lần. Quy tắc U9 `keepInterest` là một phần liên quan (giữ 50 vàng trước khi roll), nhưng vẫn tắt mặc định (xem U9).
- Bảng odds lệch ở level 8, 9 (xem U2).

## 4. Máu (HP) và sát thương người chơi

- Không có nguồn `verified` nào trong vòng này. Đoạn tìm kiếm mô tả: người thua chịu sát thương bằng giá trị theo giai đoạn cộng thêm 1 cho mỗi đơn vị địch còn sống. Các con số khác nhau giữa các bản vá (ví dụ giai đoạn 4 là 6, 7 hoặc 8 tùy nguồn).
- Trạng thái: `search summary` + **conflict**. Không đưa số nào vào engine.
- Hiện tại engine chỉ có một ngưỡng: HP ≤ 30 là "khẩn cấp", và khi đó đổi sang chế độ roll. Không dùng sát thương để dự đoán máu sau vòng.
- Khoảng trống: cần bảng sát thương theo giai đoạn của set hiện tại (`pending`).

## 5. Số bản trong pool và tướng cùng cost

- Số bản mỗi tướng theo cost: đoạn tìm kiếm cho thấy Set 12 tăng 22/20/17 lên 30/25/18. `rules.js` dùng 30/25/18/10/9, khớp con số mới và nguồn mà `docs/tft-knowledge.md` đã dẫn. **Đây không phải xung đột**: con số 22/20/17 là bản cũ, đã được thay bằng bản mới trong cùng nguồn.
- Điều chưa kiểm chứng là số bản có đúng cho Set 18 hay Set 19 không. Trạng thái: `search summary`.
- `CHAMPS_PER_COST` chưa khớp danh sách tướng của set (xem G7).
- Không đổi `rules.js` trong vòng này.

## 6. Mua khi đang đánh và khi bench đầy (U4)

- Chưa tìm được nguồn xác nhận việc mua tướng hoàn thành sao khi bench đầy. Trạng thái: `pending`.
- Engine hiện chặn mua khi bench đầy, trừ trường hợp hoàn thành sao (`owned % 3 === 2`), và đề xuất lượt này. Xem U4 trong `docs/needs.md`.

## 7. Bench, ghép cặp, bán

- Chưa có nguồn đã mở trang cho nguyên tắc bán và ghép cặp trong vòng này. Trạng thái: `pending`.
- Hiện tại engine chỉ bán để nhường chỗ cho lượt mua bị chặn, và không bán tướng trong line hoặc tướng mục tiêu.

## 8. Thay đổi Set 19

- Ngày Set 19: một nguồn ghi 2/12 (`search summary`), `docs/tft-knowledge.md` ghi xung đột giữa 1/12 và 2/12. Trạng thái: **conflict**.
- Đoạn tìm kiếm mô tả Set 19 có tướng cost 7 và hệ thống mở khóa tướng theo điều kiện: `search summary`.
- Không giới hạn cost về 1–5 ở lớp nhận dữ liệu: làm vậy sẽ làm mất tướng cost 7 của Set 19.
- Kiểm tra trên engine: `decide` nhận tướng cost 7 không báo lỗi và cho hit 0 vì `rules.js` không có dòng odds hay pool cho cost trên 5. Mua vẫn dựa vào priority. Khoảng trống thật là `rules.js` thiếu dòng odds và pool cho cost 6 trở lên (G8).

## 9. Bảng khoảng trống, xếp theo mức ảnh hưởng đến quyết định mua, roll, lên level

| # | Khoảng trống | Ảnh hưởng | Trường cần | Trạng thái nguồn |
| --- | --- | --- | --- | --- |
| G1 | Bảng odds level 8, 9 trong `rules.js` không khớp nguồn | Trực tiếp: xác suất roll và điểm mua | không cần trường mới | `conflict` (U2) |
| G2 | Không có XP hiện tại và XP cần để lên level | Trực tiếp: quyết định lên level | `xp`, `xpToNext` (I4) | wiki `verified`, thiếu set |
| G3 | Lên level bị khóa bởi `gold >= 50` (quy tắc U9 `earlyLevel` mở ở stage ≤ 2) | Trực tiếp: bỏ lỡ lên level sớm | cần `xp` (I4) | `verified` (bảng wiki) |
| G4 | Không có thu nhập thụ động và chuỗi thắng/thua | Gián tiếp: giữ vàng hay chi tiêu | `streak`, `round` (I4) | thụ động `verified`; chuỗi `conflict` |
| G5 | Điểm roll chỉ tính một shop; xác suất nhiều lượt (`hitWithin`) chỉ hiển thị, chưa dùng trong điểm | Trực tiếp: điểm roll | không cần trường mới | hiển thị ở `fdabca4`; dùng trong điểm chờ U9 |
| G6 | Không có sát thương người chơi theo giai đoạn | Gián tiếp: quyết định ổn định máu | `stage`, số tướng địch sống | `conflict` |
| G7 | `CHAMPS_PER_COST` chưa khớp danh sách tướng của set; số bản pool chưa xác nhận cho Set 18/19 | Trực tiếp: xác suất gặp | `takenByOthers` (I3) | `search summary` |
| G8 | `rules.js` không có dòng odds hay pool cho cost trên 5; engine nhận cost 7 và cho hit 0 | Gián tiếp: tướng cost cao không bao giờ được tính xác suất | không cần trường mới | đã xác nhận bằng chạy thử |
| G9 | Chưa có quy tắc bán và ghép cặp | Gián tiếp | bench, sellValue (I2) | `pending` |
| G10 | Chưa rõ mua hoàn thành sao khi bench đầy | Trực tiếp: lượt mua bị chặn/cho phép | U4 | `pending` |
| G11 | `LEVEL_BY_STAGE` đặt level 8 ở stage 4 (quy tắc U9 `guideLevels`); metabot đặt level 8 quanh 4-5 hoặc 5-1 (Set 18 guide) | Trực tiếp: thời điểm lên level | `stage`, `round` (I4) | `single-source` (metabot, patch 16.20) |

## 10. Mâu thuẫn giữa các nguồn

1. Bảng odds level 8: metabot và Set 17 (`docs/tft-knowledge.md`) đều 15/20/32/30/3; `rules.js` 17/24/32/24/3.
2. Bảng odds level 9: metabot và Set 17 đều 10/17/25/33/15; `rules.js` 15/18/25/30/12.
3. Bảng XP (wiki) ghi 7→8 = 60, 8→9 = 68; đoạn tìm kiếm Set 14 ghi 7→8 = 48, 8→9 = 76.
4. Sát thương người chơi giai đoạn 4: 6, 7 hoặc 8 tùy nguồn.
5. Ngày Set 19: 1/12 (seemeta) và 2/12 (esports.gg và đoạn tìm kiếm gần đây).
6. Chuỗi thắng/thua: mục Income của wiki ghi 3–4 +1, 5 +2, 6+ +3. Metabot ghi "Typical streak bonuses" (bảng "thường gặp"): 2–3 +1, 4 +2, 5+ +3. Ghi chú V10.8 của wiki là lịch sử đã bị thay thế, không phải nguồn hiện hành.

Lưu ý chung: lịch sử bản vá của wiki TFT:Gold chỉ đến V10.x, nên không xác định được ngày của mục Income. Trang TFT:Experience đã lưu không có mục lịch sử bản vá, nên không xác định được ngày của bảng XP. Vì vậy chuỗi thắng/thua và U1 vẫn mở, cần người dùng xác nhận.
