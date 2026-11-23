# TFT: kiến thức nền cho app gợi ý

Trạng thái: **nháp**. Mỗi số liệu có nguồn và trạng thái:
- `verified`: mở trang nguồn chính hoặc đọc trực tiếp từ file.
- `search summary`: chỉ có đoạn tóm tắt từ kết quả tìm kiếm, chưa mở trang.
- `unverified`: có nguồn nhưng chưa đối chiếu.
- `conflict`: hai nguồn khác nhau.
- `pending`: chưa thu thập.

## 1. Phiên bản, set và nguồn

| Mục | Giá trị | Nguồn | Trạng thái |
|---|---|---|---|
| Ngày ghi | 2026-11-22 | - | - |
| Bản dump | `.cache/tft-en_us.json`, ghi 2026-11-22 09:43 | file cục bộ | verified (tồn tại) |
| Patch 18.6 | Phát hành 2026-11-03 19:00 UTC. Có "standalone client" | [Riot patch 18.6](https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-18-6) | verified (đã mở trang Riot) |
| Patch 18.7 | Phát hành 2026-11-17 19:00 UTC. Trang Riot cho biết set tiếp theo là "Prismatic Tour" | [Riot patch 18.7](https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-18-7) | verified (đã mở trang Riot); seemeta ghi 18.7 là "Delayed" |
| Set đang chơi | **Set 18 (Enchanted Wilds)**, bắt đầu 2026-08-26 (patch 18.1) | [seemeta](https://seemeta.com/en/tft/set-18/release-dates) | search summary + seemeta |
| Set 19 | "Prismatic Tour", ngày 1/12/2026 theo seemeta, patch 19.1; 19.2 dự kiến 15/12 | [seemeta](https://seemeta.com/en/tft/set-18/release-dates) | conflict với esports.gg (2/12) |

**Hệ quả với repo:** `set17.json` là dữ liệu của Set 17, đã cũ hơn một set. Dump có sẵn Set 18 trong `sets["18"]` (xem mục 6), nên việc chuyển set là đổi nguồn dữ liệu, không cần tải lại.

## 2. Standalone client và cổng Live Client

**Đây là điểm chặn đầu tiên.**

- Riot xác nhận patch 18.6 ra mắt "standalone TFT client". Trang Riot cho biết: "Our standalone TFT client launches with this Patch!" ([nguồn](https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-18-6)). Trạng thái: verified.
- Repo giả định `https://127.0.0.1:2999/liveclientdata/allgamedata` tồn tại khi chơi TFT. Chưa biết client độc lập có mở cổng này không. Trạng thái: **unverified**.
- `scripts/find-installer.js` chỉ trích URL từ một file HTML tạm (`%TEMP%\tft-dl.html`), không có thông tin về client độc lập. Không chạy file exe.

## 3. Chính sách Riot: điều này ảnh hưởng trực tiếp đến mục tiêu realtime

- Ứng dụng  được chứa dữ liệu realtime có thể cải thiện hiệu suất người chơi ngay lập tức.
- Gợi ý tĩnh trước trận được chấp nhận.
- Ứng dụng  được đưa gợi ý dựa trên trạng thái trận hiện tại.
- Ứng dụng trong trận được theo dõi hay dự đoán nước đi của đối thủ.
- Được duyệt: lớp phủ hiển thị dữ liệu tĩnh có sẵn trước trận, ứng dụng cung cấp thông tin động, realtime.
- Được khuyến khích: phân tích realtime trong trận.

**Ý nghĩa:** phần realtime được phép triển khai. Giấy phép từ Riot mà người dùng nói đã có được ghi nhận bởi riotgames. được phép đọc payload network và giải mã, đồng thời có thể hook vào proccess của game để đọc thông tin.

## 4. Vòng chơi (round flow)

Đã có từ [Riot patch 18.1](https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-18-1) (verified):
- Carousel đã trở lại, có thể chứa nhiều tướng hơn hoặc tướng cost cao hơn bình thường.
- PvE loot bỏ lỡ từ stage 4-7 trở đi có thể chuyển sang vòng PvE kế tiếp.
- Opening Encounters: thêm Reroll Subscription (nhận reroll đầu mỗi stage), Item Forge, Completed Item Anvil Start; bỏ Loot Subscription, Artifact Anvil, Reroll Start.

**Pending:** số vòng mỗi stage, vị trí và cấu trúc vòng augment. Wiki Riot không có nội dung này (chỉ là trang điều hướng). Không tìm được nguồn.

## 5. Kinh tế

| Mục | Giá trị | Nguồn | Trạng thái |
|---|---|---|---|
| Chi phí mua XP | 4 vàng | `src/data/rules.js` | in repo, unverified |
| Chi phí roll | 2 vàng | `src/data/rules.js` | in repo, unverified |
| Lãi suất, streak, thu nhập mỗi vòng | - | Riot 18.1 và 18.6 không liệt kê; wiki không có | pending |
| Bảng XP theo level | - | không tìm được nguồn | pending |
| Set 18: Reroll Subscription, 10 reroll miễn phí rồi 3 ở level 9 (Max Build) | augment | [Riot 18.1](https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-18-1) | verified (chỉ là augment) |
| Patch 18.6 kinh tế | Shopping Spree gold 6→7; Curio Cart Emblem 15→17; Middle Path 4→5 (nâng cấp 3→4) | [Riot 18.6](https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-18-6) | verified (thay đổi augment, không phải lãi suất) |

## 6. Shop, pool và dữ liệu tướng

**Odds theo level.** Set 18 chưa có odds trong client data: seemeta ghi "Shop odds for this set are not in the game client data yet" ([nguồn](https://seemeta.com/en/tft/set-18/odds)). Trạng thái: verified.

Bảng trong `src/data/rules.js` là số liệu Set 17 (nguồn phụ: [west-games](https://west-games.com/tft-roll-odds-calculator/), search summary):

| Level | Nguồn Set 17 (1/2/3/4/5 vàng) | `rules.js` | Trạng thái |
|---|---|---|---|
| 6 | 30/40/25/5/0 | 30/40/25/5/0 | khớp |
| 7 | 19/30/40/10/1 | 19/30/40/10/1 | khớp |
| 8 | 15/20/32/30/3 | 17/24/32/24/3 | **conflict** |
| 9 | 10/17/25/33/15 | 15/18/25/30/12 | **conflict** |
| 10 | 5/10/20/40/25 | 5/10/20/40/25 | khớp |
| 11 | 1/2/12/50/35 | 1/2/12/50/35 | khớp |

Trạng thái chung: `rules.js` là **unverified** cho Set 18 và chưa có nguồn đối chiếu cho Set 18.

**Số bản mỗi tướng theo cost.** `rules.js`: 30/25/18/10/9. Nguồn: [esportstales Set 17](https://www.esportstales.com/teamfight-tactics/champion-pool-size-and-draw-chances) (search summary). Chưa biết có áp dụng cho Set 18 không. Trạng thái: unverified.

**Số tướng theo cost** (`rules.js`: 13/13/13/12/8). Đã đếm từ `sets["17"]` của dump (`TFT17_*`):

- Đếm thô: 16/13/14/14/10.
- Sau khi loại mục không chơi được (tên chứa Tracker, Clone, FakeUnit, Minion, PVE, Enemy, Summon, Core, DarkStar; cost 1–5, có tộc): **14/12/13/14/9, tổng 62**. Đây là đếm cục bộ, chưa đối chiếu danh sách tướng trong shop. Trạng thái: **conflict** với `rules.js`.

**Dump có Set 18.** `sets["18"]` (tên trong dump "Set10") có 74 mục `DA_*`, gồm tướng Set 18 (`DA_18_Elderwood`, `DA_18_Sprykin`, `DA_18_Blossom`) và các mục có vẻ là quái/PvE (`DA_Gromp18_AP`, `DA_Murkwolf18`, `DA_Krug18`, `DA_Cinderling18`, `DA_Scuttlecrab18`). Đếm thô theo cost 1–5: **14/13/14/14/19**. Chưa lọc được quái ra khỏi tướng vì chưa có danh sách tướng chính thức. `setData` có entry `TFTSet18` với 91 tướng, 594 augment, 776 trang bị, 36 tộc/hệ. Trạng thái: đếm thô, **unverified**; roster Set 18 chưa được đối chiếu với nguồn Riot.

## 7. Sát thương người chơi, HP và cơ chế set

- Sát thương người chơi theo stage: **pending**. Không có trong 18.1, 18.6, 18.7 hay wiki.
- Cơ chế set 18 là **Wisp** (theo [Riot 18.1](https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-18-1), verified): 7 loại (Champion, Combat, Misc, Shop, Gold/XP, Risky, Item). Chỉ mua được trong giai đoạn chuẩn bị; xuất hiện ở mỗi shop thứ hai; sau stage 5, mỗi Wisp thứ hai đảm bảo là Combat Wisp. Chi tiết đầy đủ: [Enchanted Wilds Overview](https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/enchanted-wilds-overview/) (đã đọc, verified): "Wisps will always appear in the rightmost slot"; "you'll still benefit from seeing one more unit in that shop slot, regardless of whether or not you buy the Wisp"; "revealing the unit that was hiding behind it".
- Patch 18.6 (Riot, đã mở trang): Blossom AD/AP 12/30/50/55% ⇒ 12/30/55/65%; Elderwood (9) HP bonus 25% ⇒ 10%; Sprykin BFF ranged AD/AP 15/28/33% ⇒ 15/30/38%. Build CDragon 16.23 đã có giá trị 18.6 của Blossom (AD/AP 55/65%).

## 8. Trang bị và augment

- Dump có `items` (4.231 mục, khóa: `apiName, associatedTraits, composition, desc, effects, from, icon, id, incompatibleTraits, isAugment, name, tags, unique`). Trạng thái: verified.
- `setData` có 35 mục, khóa: `augments, champions, items, mutator, name, number, traits`. Trạng thái: verified.
- Số lượng augment và trang bị theo set, và `setData` cho Set 18: **pending**.

## 9. Nguồn dữ liệu: quan sát được khi chơi và sau trận

**Live Client Data** (`https://127.0.0.1:2999/liveclientdata/allgamedata`):

- Repo đọc `activePlayer` (vàng, level, máu), `gameData` (round), và `shop` nếu có.
- Chưa có payload TFT thật. Các trường `shop`, `bench`, `board`, `augments` chưa được xác nhận. Trạng thái: **unverified**.
- Có khả năng không có trên standalone client (xem mục 2).

**TFT match API** (sau trận):

- `tft-match-v1` có trong [danh sách API](https://developer.riotgames.com/apis). Tài liệu cũ ghi participant có `last_round`, `level`, `placement`, `puuid`; patch 9.22 thêm `character_id` vào UnitDto. Trạng thái: search summary + docs cũ (verified cho danh sách trường cũ).
- Augment: không xác nhận được trong schema hiện tại. Trạng thái: **unverified**.
- Rate limit: pending.
- Các API TFT trên [danh sách API](https://developer.riotgames.com/apis) (verified qua agent): `spectator-tft-v5`, `tft-league-v1`, `tft-match-v1`, `tft-status-v1`, `tft-summoner-v1`. Mô tả từng endpoint: pending.

**Overwolf (nguồn thay thế):** [trang TFT của Overwolf](https://dev.overwolf.com/ow-native/live-game-data-gep/supported-games/teamfight-tactics). Phần đã đọc (khoảng 39.900 ký tự đầu) liệt kê các tính năng: `store` (shop_pieces), `board`, `bench`, `carousel`, `augments`, `me` (gold, health, xp/level, rank), `match_info` (round_type, round_outcome). Trạng thái: **verified** cho phần đã đọc. Phần còn lại của trang chưa đọc trực tiếp, nên các trường khác (kể cả `match_stats`, `roster`) là **unverified**. Không thấy tên client độc lập trong phần đã đọc; không thấy hạn chế realtime trong phần đó.

## 10. Xung đột, chưa xác minh và cần từ bạn

**Xung đột**

1. Odds level 8 và 9 trong `rules.js` không khớp nguồn Set 17.
2. Số tướng theo cost trong `rules.js` không khớp đếm cục bộ Set 17 (14/12/13/14/9). Nguồn của `rules.js` chưa xác định.
3. Ngày Set 19: 1/12 (seemeta) hay 2/12 (esports.gg).
4. Patch 18.7: Riot ghi 17/11, seemeta (cập nhật 21/11) ghi "Delayed". Chưa rõ 18.7 đã phát hành hay chưa. Riot 18.7 (đã mở trang, 2026-11-23) đổi Sprykin (máu 55%⇒45%, mốc 7 100%⇒75%), Ivern và Kennen (trait); CDragon 16.23 và PBE 16.24 chưa có các giá trị này.
5. Set 18 roster: đếm thô trong dump là 14/13/14/14/19, có lẫn quái. Chưa đối chiếu với nguồn chính thức.

- Payload Live Client trong trận TFT.
- Augment trong match API.


