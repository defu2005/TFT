# Chiến lược TFT: nguyên tắc, nguồn và khoảng trống của engine

Trạng thái: **nháp**. Tài liệu này chỉ ghi nguyên tắc và số liệu từ nguồn. Không dùng để sửa `rules.js` hay engine ở vòng này.

Nhãn trạng thái (theo `docs/tft-knowledge.md`):
- `verified`: đã mở trang và đọc đúng con số đó.
- `search summary`: chỉ có đoạn tóm tắt từ kết quả tìm kiếm, chưa mở trang.
- `conflict`: hai nguồn khác nhau.
- `pending`: chưa thu thập.

Ngày thu thập: 2026-11-23. Môi trường cho phép `wiki.leagueoflegends.com` và `metabot.gg` (đã đọc bằng `curl`). `esports.gg` và `mobalytics.gg` trả về 403 từ máy chủ đích, nên không đọc được. Công cụ `web-fetch` trong phiên vẫn không phân giải được hai host wiki và metabot, nên toàn bộ trang được đọc bằng `curl`.

## 1. Kinh tế

**Nguyên tắc**
- Lãi: cứ 10 vàng giữ lại được thêm 1 vàng cuối vòng, tối đa 5 vàng (đến 50 vàng). Tính trước thu nhập thụ động.
- Thu nhập thụ động: 5 vàng mỗi đầu giai đoạn chuẩn bị.
- Chuỗi thắng/thua: thêm vàng theo chuỗi. Bảng theo từng bản vá (xem bên dưới).

**Nguồn**
- Riot wiki, TFT:Gold, [wiki.leagueoflegends.com/en-us/TFT:Gold](https://wiki.leagueoflegends.com/en-us/TFT:Gold): `verified` cho lãi (1 per 10, tối đa 5) và thu nhập thụ động (5 mỗi planning phase). Trang không ghi rõ set; có mục Enchanted Wilds (Set 18) trong menu.
- Riot wiki, cùng trang: chuỗi thắng/thua đã thay đổi qua nhiều bản vá (ví dụ "Streak gold changed to 2-3(1g), 4(2g), 5+(3g)"). Bảng chuỗi hiện tại: `pending`, vì chỉ đọc được lịch sử thay đổi.
- Metabot, [metabot.gg](https://metabot.gg/en/TFT/guides/tft-when-to-roll-vs-level-up-shop-odds): `verified` (đọc bằng `curl`) cho "Interest cap 1 per 10 held, up to 50"; trang không ghi set.

**Hiện tại engine làm gì**
- Lãi chỉ là chi phí cơ hội: `interestLoss * 0.35` bị trừ khỏi điểm mua, không được tính là thu nhập.
- Không có thu nhập thụ động hay chuỗi thắng/thua trong trạng thái; `streak` đã được nêu trong hợp đồng nhưng không nguồn nào gửi.

**Khoảng trống**
- Engine không biết thu nhập tương lai, nên không thể đánh giá việc giữ vàng để lên level hay roll sau này.
- Chưa có chuỗi thắng/thua: không phân biệt được thắng liên tiếp (giữ lãi) với thua liên tiếp (chi tiêu).

## 2. Lên level và XP

**Nguyên tắc**
- Mua XP: 4 vàng = 4 XP.
- Mỗi vòng nhận 2 XP miễn phí.
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

Nguồn: Riot wiki, TFT:Experience, [wiki.leagueoflegends.com/en-us/TFT:Experience](https://wiki.leagueoflegends.com/en-us/TFT:Experience): `verified` cho số trong bảng và "4 gold = 4 XP", "2 XP free at end of round". Trang không ghi set; **conflict** với các đoạn tìm kiếm cho Set 14 (ví dụ 7→8 = 48, 8→9 = 76). Bảng này là nguồn tốt nhất hiện có, nhưng cần xác nhận set trước khi dùng cho Set 18.

**Hiện tại engine làm gì**
- Chỉ lên level khi `gold >= 50` và `level < LEVEL_BY_STAGE[stage]` (mục tiêu 2/4/6/8/8/9/9 theo stage). Không dùng bảng XP.
- Điểm XP là `(wanted - level) * 1.1` (hoặc 0.6 khi HP thấp), và chỉ mua khi điểm > 0.5.

**Khoảng trống**
- Không có XP hiện tại và XP cần cho level tiếp theo, nên không biết còn bao nhiêu XP để lên level.
- Mục tiêu level theo stage là số tự đặt (`rules.js`), không có nguồn.
- Điều kiện `gold >= 50` loại bỏ việc lên level sớm ở các vòng đầu, dù bảng wiki cho thấy các bước đầu rất rẻ (2, 6, 10 XP).

## 3. Roll: khi nào, mức level nào

**Nguyên tắc**
- Tỉ lệ shop theo level là điểm mấu chốt. Bảng sau lấy từ metabot: `verified` (đã mở trang bằng `curl` và đọc đúng bảng), nhưng trang không ghi set nên chưa biết áp dụng cho set nào:

| Level | 1 vàng | 2 vàng | 3 vàng | 4 vàng | 5 vàng |
| --- | --- | --- | --- | --- | --- |
| 4 | 55% | 30% | 15% | 0% | 0% |
| 5 | 45% | 33% | 20% | 2% | 0% |
| 6 | 30% | 40% | 25% | 5% | 0% |
| 7 | 19% | 30% | 40% | 10% | 1% |
| 8 | 15% | 20% | 32% | 30% | 3% |
| 9 | 10% | 17% | 25% | 33% | 15% |

- Mốc: 3 vàng đạt đỉnh ở level 7; 4 vàng tăng mạnh ở level 8; 5 vàng thực tế từ level 9.
- Khuyến nghị chung của metabot: giữ vàng và lên level theo lịch (thường đạt level 7 ở 4-1, level 8 ở 5-1); chỉ roll mạnh khi máu thấp hoặc bàn đã đủ mạnh.

**Hiện tại engine làm gì**
- `SHOP_ODDS` trong `rules.js`: khớp metabot ở level 4–7, nhưng **level 8 và 9 không khớp** (`rules.js` level 8: 17/24/32/24/3; level 9: 15/18/25/30/12; metabot: 15/20/32/30/3 và 10/17/25/33/15). Bảng `docs/tft-knowledge.md` cũng ghi cùng xung đột này với Set 17.
- Roll chỉ được khuyến nghị khi có mục tiêu (`tft_set_target`), tính xác suất gặp một tướng trong một shop.
- Điều kiện roll: 12 vàng (2 khi máu ≤ 30 hoặc khi có lượt miễn phí, 0 với lượt miễn phí). Không xét lượt roll nhiều lần.

**Khoảng trống**
- Chỉ tính một shop, không tính xác suất gặp trong nhiều lượt roll (chuỗi roll).
- Không có chiến lược "slow roll" (giữ vàng để roll tại level cụ thể) ngoài điểm số một lần.
- Bảng odds lệch ở level 8, 9 (xem U2).

## 4. Máu (HP) và sát thương người chơi

- Không có nguồn `verified` nào trong vòng này. Đoạn tìm kiếm mô tả: người thua chịu sát thương bằng giá trị theo giai đoạn cộng thêm 1 cho mỗi đơn vị địch còn sống. Các con số khác nhau giữa các bản vá (ví dụ giai đoạn 4 là 6, 7 hoặc 8 tùy nguồn).
- Trạng thái: `search summary` + **conflict**. Không đưa số nào vào engine.
- Hiện tại engine chỉ có một ngưỡng: HP ≤ 30 là "khẩn cấp", và khi đó đổi sang chế độ roll. Không dùng sát thương để dự đoán máu sau vòng.
- Khoảng trống: cần bảng sát thương theo giai đoạn của set hiện tại (`pending`).

## 5. Số bản trong pool và tướng cùng cost

- Đoạn tìm kiếm cho thấy số bản mỗi tướng theo cost thay đổi theo set: một nguồn ghi 30/25/18/10/9 (Set 12), nguồn khác ghi 22/20/17/10 (không rõ set). `rules.js` dùng 30/25/18/10/9.
- Trạng thái: `search summary` + **conflict**. Không đổi `rules.js` trong vòng này.
- Hiện tại: `POOL_COPIES` và `CHAMPS_PER_COST` là số tự đặt cho Set 17 (xem `docs/tft-knowledge.md`). Số tướng theo cost chưa khớp với danh sách set.

## 6. Mua khi đang đánh và khi bench đầy (U4)

- Chưa tìm được nguồn xác nhận việc mua tướng hoàn thành sao khi bench đầy. Trạng thái: `pending`.
- Engine hiện chặn mua khi bench đầy, trừ trường hợp hoàn thành sao (`owned % 3 === 2`), và đề xuất lượt này. Xem U4 trong `docs/needs.md`.

## 7. Bench, ghép cặp, bán

- Chưa có nguồn đã mở trang cho nguyên tắc bán và ghép cặp trong vòng này. Trạng thái: `pending`.
- Hiện tại engine chỉ bán để nhường chỗ cho lượt mua bị chặn, và không bán tướng trong line hoặc tướng mục tiêu.

## 8. Thay đổi Set 19

- Ngày Set 19: một nguồn ghi 2/12 (`search summary`), `docs/tft-knowledge.md` ghi xung đột giữa 1/12 và 2/12. Trạng thái: **conflict**.
- Đoạn tìm kiếm mô tả Set 19 có tướng cost 7 và hệ thống mở khóa tướng theo điều kiện: `search summary`.
- Kiểm tra trên engine: `decide` nhận tướng cost 7 không báo lỗi và mua được với xác suất 0 (điểm chỉ dựa vào priority). Schema MCP giới hạn cost từ 1 đến 5 nên không xảy ra qua MCP, nhưng nguồn live có thể gửi cost 7. **Khoảng trống**: engine chưa kiểm tra miền cost.

## 9. Bảng khoảng trống, xếp theo mức ảnh hưởng đến quyết định mua, roll, lên level

| # | Khoảng trống | Ảnh hưởng | Trường cần | Trạng thái nguồn |
| --- | --- | --- | --- | --- |
| G1 | Bảng odds level 8, 9 trong `rules.js` không khớp nguồn | Trực tiếp: xác suất roll và điểm mua | không cần trường mới | `conflict` (U2) |
| G2 | Không có XP hiện tại và XP cần để lên level | Trực tiếp: quyết định lên level | `xp`, `xpToNext` (I4) | wiki `verified`, thiếu set |
| G3 | Lên level bị khóa bởi `gold >= 50` | Trực tiếp: bỏ lỡ lên level sớm | cần `xp` (I4) | `verified` (bảng wiki) |
| G4 | Không có thu nhập thụ động và chuỗi thắng/thua | Gián tiếp: giữ vàng hay chi tiêu | `streak`, `round` (I4) | wiki `verified` cho thụ động; chuỗi `pending` |
| G5 | Không xét nhiều lượt roll, chỉ một shop | Trực tiếp: điểm roll | không cần trường mới | ý tưởng từ nguyên tắc, chưa kiểm chứng |
| G6 | Không có sát thương người chơi theo giai đoạn | Gián tiếp: quyết định ổn định máu | `stage`, số tướng địch sống | `conflict` |
| G7 | Số bản pool và số tướng theo cost chưa khớp set | Trực tiếp: xác suất gặp | `takenByOthers` (I3) | `conflict` |
| G8 | Không kiểm tra miền cost | Gián tiếp: dữ liệu live lỗi có thể mua nhầm | không cần | đã xác nhận bằng chạy thử |
| G9 | Chưa có quy tắc bán và ghép cặp | Gián tiếp | bench, sellValue (I2) | `pending` |
| G10 | Chưa rõ mua hoàn thành sao khi bench đầy | Trực tiếp: lượt mua bị chặn/cho phép | U4 | `pending` |

## 10. Mâu thuẫn giữa các nguồn

1. Bảng odds level 8: metabot và Set 17 (`docs/tft-knowledge.md`) đều 15/20/32/30/3; `rules.js` 17/24/32/24/3.
2. Bảng odds level 9: metabot và Set 17 đều 10/17/25/33/15; `rules.js` 15/18/25/30/12.
3. Bảng XP (wiki) ghi 7→8 = 60, 8→9 = 68; đoạn tìm kiếm Set 14 ghi 7→8 = 48, 8→9 = 76.
4. Sát thương người chơi giai đoạn 4: 6, 7 hoặc 8 tùy nguồn.
5. Ngày Set 19: 1/12 (seemeta) và 2/12 (esports.gg và đoạn tìm kiếm gần đây).
6. Số bản pool: 30/25/18/10/9 (Set 12) và 22/20/17/10 (không rõ set).
