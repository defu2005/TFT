# Nghiên cứu: dữ liệu combat công khai (2026-11-25)

Mục đích: xác định có thể mô phỏng combat TFT từ dữ liệu công bố hay không, và dữ liệu nào thật sự có.

## 1. Đã có trong repo (đo trực tiếp)

- **Engine Set 17**: `EngineResolver` gọi `run_combat` (tft_goat/engine/simulate.py). Engine tự đặt đội hình theo vai trò (hàm `_lay`, dòng ~250–332), **không nhận vị trí từ bên gọi**. Vị trí đã capture không dùng được nếu không sửa engine.
- **CDragon 18.7** (`data/cdragon/cdragon_18.7_2026-11-23.json.gz`):
  - 91 tướng Set 18, **cả 91 đều có mô tả ability** (`ability.desc`, dạng chuỗi có biến như `@ModifiedDamage@`, `scaleAP`).
  - Chỉ số: armor, attackSpeed, critChance, critMultiplier, damage, hp, initialMana, magicResist, mana, range.
  - Vai trò: 80 tướng không có `role`, 8 ADTank, 2 APTank, 1 APCaster. Trường vai trò gần như trống, nên không đủ để suy đội hình.
- **Set 17**: 69 hàm ability viết tay trong `tft_goat/engine/abilities_set17` (6 file).

## 2. Nguồn công khai bên ngoài (đã tìm, 2026-11-25)

- **Riot TFT match-v1** (developer.riotgames.com/api-details/tft-match-v1): theo kết quả tìm kiếm (không đọc được trang chính thức), participant có `placement`, `level`, `last_round`, `time_eliminated`, `traits` và `units` **của đội hình cuối cùng**. Kết quả tìm kiếm không nêu log combat theo round, sát thương, hay vị trí. **Chưa xác minh** vì trang chính thức không đọc được và schema unit/item chưa thấy đầy đủ.
- **Công thức combat**: hai lần tìm kiếm không thấy trang chính thức của Riot mô tả công thức sát thương TFT. Đây là kết quả của hai tìm kiếm, chưa phải kết luận đã kiểm tra trang wiki cơ chế.
  - Tacter và Metabot (bên thứ ba) nói armor/MR giảm sát thương theo công thức kiểu LoL: giảm = resist / (100 + resist). Chưa kiểm chứng trong TFT.
  - Không tìm thấy công thức tốc độ đánh (attack speed) trong nguồn nào.
- **Ability**: mô tả văn bản (CDragon, wiki) cho biết **hiệu ứng là gì**, không cho logic thực thi. Mỗi ability phải được lập trình tay.

## 3. Kết luận sơ bộ

1. Dữ liệu công bố đủ để **dựng khung** (chỉ số, mô tả ability, cấu trúc đội hình), nhưng **chưa đủ để sao chép logic combat**. Chưa tìm thấy code hay công thức chính thức của Riot; kết luận này dựa trên hai lần tìm kiếm, chưa kiểm wiki.
2. Nếu tự suy logic từ mô tả, cần kiểm bằng dữ liệu thật (cặp bàn + kết quả). Không có dữ liệu này thì không đo được độ trung thực.
3. Log combat theo round không có trong API công khai. Nguồn duy nhất là capture từ app (giả định của người dùng).
4. Set 18: 91 tướng có mô tả ability, nhưng logic phải viết tay. Đo sơ bộ cho Set 17: 69 hàm, 7 hàm ≤2 câu lệnh (khả năng là mẫu chung), còn lại 3–10+ câu. Đây là đếm thô theo số câu lệnh, chưa phân loại thật.

## 4. Chưa xác minh

- Trang wiki TFT (attack speed, mana, damage) chưa được đọc.
- Schema unit/item của match-v1 (cần trang chính thức).
- Công thức sát thương và tốc độ đánh TFT chính thức.
- Giấy phép dùng CDragon (đã nêu trước đó, chưa xác minh).

## 5. Đo sơ bộ v1 (ĐÃ THAY THẾ bởi mục 6; không dùng để kết luận)

Lý do thay thế: v1 không có augment (bug đọc sai trường), chỉ có cặp cùng vòng, và chế độ public tắt cả ability lẫn trang bị nên không tách được hai yếu tố. Lưu ý: bỏ augment chỉ đổi khoảng 2 điểm nên bug augment **không** giải thích khoảng cách v1–v2.

Số liệu v1 (giữ để đối chiếu): 

Nguồn: 67.122 cặp từ 100 lobby v4 (seed 288000–288099); lấy ngẫu nhiên 500 cặp để phân tích. Mỗi cặp: 20 lần chạy engine đầy đủ và 20 lần ở chế độ public. Kết quả: `results/fixed/combat/study17_288000.json`. Nhãn: **sim**, engine tự sinh, không phải trận thật.

- **A. Tran nhieu**: 83,8% cặp quyết định (≥90% một bên thắng), 5,6% gần tung đồng xu.
- **B. Suc manh don gian**: hồi quy logistic trên tổng cost·sao, số trang bị, cấp, số trait cho độ chính xác 58,7% trên các cặp quyết định. Gần mức đoán. Chỉ số sức mạnh đơn giản gần như không giải thích kết quả trong engine Set 17.
- **C. Public so voi full**: hai chế độ đồng ý về bên thắng ở 72,3% trong 419 cặp quyết định. Chênh lệch xác suất trung bình 0,31.

Đọc kết quả: trong engine, ability và trang bị quyết định phần lớn kết quả, không phải chỉ số. Chế độ public chỉ đúng ở khoảng 3/4 cặp quyết định. Điều này trả lời một phần câu hỏi "chỉ số công khai có đủ không": không đủ để đoán chính xác, nhưng không hoàn toàn vô dụng. Chưa đo độ trung thực với trận thật.

## 6. Đo v2 (sơ bộ, CHƯA XÁC NHẬN)

Kết quả v2 gộp cặp cùng vòng và xuyên vòng trong một tập, nên chưa dùng để kết luận. Mục 7 sẽ tách hai loại và thêm khoảng tin cậy.

Số liệu sơ bộ (`results/fixed/combat/study17_v2_288000.json`, nhãn sim):
- Cặp quyết định: 88,7% (cùng vòng 85,3%, xuyên vòng 92,0%).
- Đồng ý dấu với engine đầy đủ trên cặp quyết định: ability generic 91,2%; không ability (có trang bị) 91,5%; ability viết tay không trang bị 88,4%.
- Logistic trên đặc trưng sức mạnh: 80,5% trên cặp quyết định test (baseline luôn đoán A: 49,3%). Theo tercile chênh lệch: 66,9%, 76,4%, 98,3%.
- Kiểm đối xứng: lệch trung bình 0,0095. Không lệch `items`: 0 trên 129.912 đơn vị.

Chưa biết: số liệu này có đúng cho cặp cùng vòng hay không; sự khác biệt 88,4 và 91,5 có ý nghĩa thống kê hay không; augment có được kiểm riêng chưa (chưa).

Kết luận v1 ("sức mạnh đơn giản gần như không giải thích được") **chưa được xác nhận hay bác bỏ**. Chỉ xem là giả thuyết cần kiểm trên cặp cùng vòng.

## 7. Đo v3 (tách cùng vòng và xuyên vòng, khoảng tin cậy theo lobby) — kết quả chính

Nguồn: `scripts/combat/analyze17_v3.py`. Test 300 cùng vòng + 300 xuyên vòng (lobby id%10<3). Train 300 + 300 (lobby còn lại), chỉ dùng để huấn luyện logistic. Mỗi cặp 20 lần chạy engine. Bảng từng cặp: `results/fixed/combat/pairs_v3_288000.csv`. Kết quả: `results/fixed/combat/study17_v3_288000.json`. Nhãn: **sim**.

**Đồng thuận với engine đầy đủ trên cặp quyết định (CI95 bootstrap theo lobby):**

| Cấu hình | Cùng vòng | Xuyên vòng |
|---|---|---|
| hand, không augment | 98,1% [96,4; 99,6] | 98,6% [97,1; 99,7] |
| hand, seed khác (trần) | 100% | 100% |
| generic (nuke mặc định) | 85,9% [81,1; 90,2] | 96,0% [93,6; 97,9] |
| none (không ability, có trang bị) | 85,6% [81,3; 89,7] | 97,1% [95,1; 98,9] |
| hand, không trang bị | 82,8% [78,2; 87,3] | 93,5% [89,7; 96,3] |
| public (không ability, không trang bị) | 75,0% [69,5; 80,3] | 90,2% [86,6; 93,4] |

Số cặp quyết định: 85% cùng vòng, 92% xuyên vòng. Tỷ lệ A thắng trong cặp quyết định: 51% cùng vòng.

**Kiểm tra ghép cặp (cùng vòng, 256 cặp quyết định, bootstrap theo lobby):**
- Trang bị so với ability (none − hand_noitems): +0,027 [−0,041; +0,097]. **Không phân biệt được** ở cùng vòng. Xuyên vòng: +0,036 [0,000; +0,077]. Vì vậy không kết luận "trang bị quan trọng hơn ability".
- generic − none (cùng vòng): +0,004 [−0,043; +0,046]. Trung bình không khác, nhưng |p_generic − p_none| trung bình là 0,158 và 13,7% cặp đổi bên thắng (chênh > 0,5). Nuke mặc định **có thay đổi kết quả từng trận**, chỉ là các chiều triệt tiêu khi lấy trung bình. Không được kết luận nuke mặc định "không tạo khác biệt".
- Augment: bỏ augment đổi khoảng 2 điểm đồng thuận (98%). Không giải thích được khoảng cách v1–v2.
- v1 `public` 72% được tái lập ở đây: public 75% (cùng vòng).

**Hồi quy logistic (sức mạnh đơn giản):**
- Huấn luyện chỉ trên cặp cùng vòng: **66,4%** [59,1; 73,3] trên cặp quyết định cùng vòng (baseline luôn đoán A: 50,8%).
- Huấn luyện trên cả cùng vòng và xuyên vòng: 68,0%. Không khác biệt đáng kể so với chỉ cùng vòng.
- Xuyên vòng: 92,0% (baseline 47,8%). Không nên trộn vào con số chính.
- Tổng hợp v2 (80,5%) bị thổi phồng bởi cặp xuyên vòng.

**Đọc kết quả (cho cặp cùng vòng, dạng thực tế):**
- Bỏ trang bị và bỏ ability đều làm giảm đồng thuận, nhưng khi so cặp với nhau không khác biệt rõ ở cùng vòng.
- Nuke mặc định đổi kết quả một số trận riêng lẻ (13,7% cặp), nhưng không thiên về một chiều.
- Augment đóng góp nhỏ (khoảng 2 điểm).
- Sức mạnh đơn giản giải thích được một phần cho cặp cùng vòng: 66% (CI 59–73), so với baseline 51%.

**Giới hạn**: chỉ là engine tự đối chiếu với bot v4; 256 cặp quyết định cùng vòng; ngưỡng quyết định 0,9 theo 20 lần chạy; chưa đo với trận thật.

## 8. Phạm vi và chặn im lặng (sau v3)

**Đã làm trong wrapper (`scripts/combat/fight.py`):**
- Tên tướng lạ: `predict_win` báo lỗi, không còn bỏ qua im lặng.
- `coverage()`: mỗi dự đoán kèm số unit, trang bị không rõ, trang bị có hook combat, augment có hook (registry Set 17).
- Vị trí: ben a hàng 0–3, ben b hàng 4–7 (khung tuyệt đối). Sai nửa lưới bị từ chối.
- CLI `scripts/combat/fight_cli.py`.

**Phát hiện mới:**
- **Augment Set 18 không có hook.** Set 18 có 594 augment, nhưng `AUGMENT_REGISTRY` chỉ có Set 17. Augment Set 18 được truyền nhưng không làm gì.
- **Biến ability Set 18 gần như trống**: 10/91 tướng có `variables`, 3/91 có biến damage. Set 17: 74/88 và 62/88. `default_damage` rơi về `ad × 2` cho phần lớn tướng Set 18. Template dựa trên biến sẽ không có số cho khoảng 81 tướng Set 18.
- **Vai trò Set 18**: 11/91 tướng có `role` (Set 17: 74/88). Định vị và nhắm mục tiêu dùng vai trò, nên Set 18 sẽ rơi về mặc định.
- **Tên trong roster nifty** (`data/hud-audit/roster_solutions_by_round.json`, 115 tên, 17 vòng): 113 khớp duy nhất với tướng Set 18. 2 khớp nhiều nghĩa (Krug: `TFT_Krug` và `DA_Krug18`, cần chọn). Đây là kiểm định định dạng một bên, không phải trận đấu.

**Hệ quả:** trước khi viết template cho Set 18, cần nguồn số liệu ability khác (mô tả đầy đủ có số, hoặc dữ liệu tay). Template chỉ dựa trên biến CDragon sẽ không đo được Set 18. Đây là điểm dừng hợp lý cho đến khi quyết định nguồn dữ liệu.

**Độ phủ trang bị và trait (đo hành vi engine, 2026-11-25).** Script: `tft-sim/scripts/combat/coverage_items_traits.py`; kết quả: `tft-sim/results/fixed/combat/coverage_items_traits.json` và `coverage_setdata_denominators.json`. Đây là độ phủ tĩnh theo hành vi: không có tần suất sử dụng, không có kích thước hiệu ứng, và Set 18 chưa có trận thật để đo.

Phân loại item theo hai phép thử: (a) có nằm trong bảng hook của engine (`ITEM_COMBAT_START`, `ITEM_ON_ATTACK`, `ITEM_HP_THRESHOLD`, ...) hay không; (b) có làm đổi chỉ số đơn vị sau `_build_team` khi gắn trang bị hay không.

Mẫu số lấy từ `setData` của từng set (mutator TFTSet17 và TFTSet18):

| Nhóm | Set 17 | Set 18 |
|---|---|---|
| Tổng item trong setData | 687 | 776 |
| Có hiệu ứng riêng (stat hoặc hook, theo apiName) | 212 (31%) | 157 (20%) |
| Chỉ hook, không stat | 0 | 0 |
| Không có hiệu ứng riêng (vẫn nhận bonus chung nếu được đếm) | 475 | 619 |

**Bonus chung của engine (quan trọng):** `build_unit` áp hiệu ứng riêng của từng item có trong `item_apis`, và áp thêm `_GENERIC_ITEM` (+150 máu, +15% AD, +15 AP, +15 giáp, +15 kháng phép) cho mỗi lần đếm `items`. Môi trường (`env/actions.py`) tăng `items` cùng lúc với việc thêm `item_apis`, nên engine luôn cộng cả hai. `fight.py` tái hiện đúng hành vi này; đây là thuộc tính của engine, không phải lỗi của wrapper. Hệ quả: mọi item được đếm, kể cả emblem và `DA_*` rỗng, đều nhận bonus chung. Đây là sai lệch đã biết khi dùng các item không có hiệu ứng riêng, và là rủi ro độ trung thực khi so với trận thật.

**Cảnh báo về con số 20%:** con số này tính theo apiName đúng như engine nhận. Nó không phản ánh việc item Set 18 có tác dụng hay không, vì phần lớn công thức ghép có apiName `DA_*` mà CDragon để trống `effects`, trong khi item cùng tên `TFT_Item_*` có đầy đủ hiệu ứng.

Phân nhóm Set 18 (theo tên và thành phần):
- 271 item `TFT_Item_*` (cổ điển): 148 có stat hoặc hook, 123 không tác dụng.
- 55 công thức `DA_*` có thành phần (craftable):
  - 16 là emblem (chỉ cộng trait; engine không xử lý emblem).
  - 39 craftable không phải emblem: 36 có item cùng tên `TFT_Item_*` có hiệu ứng (27 stat+hook, 9 stat; gồm Infinity Edge và Jeweled Gauntlet, hai mục này có stat ngay trên apiName `DA_*`), 1 có item cùng tên nhưng không tác dụng, 2 không có item cùng tên.
  - Ví dụ: `DA_Bloodthirster` có `effects` rỗng, `TFT_Item_Bloodthirster` có AD, AP, hút máu, kháng phép...
  - Chưa biết client thật gửi apiName nào cho item Set 18 khi chụp dữ liệu. Đây là điểm cần làm rõ trong hợp đồng capture, không phải lỗi của engine.
- 10 thành phần `DA_Component_*`: không tác dụng (đúng bản chất).
- 440 mục `DA_*` còn lại: 7 có stat (Flow, Marksmen's Gale, Stand Alone và các mục khác), 7 emblem không craftable, 426 không tác dụng. Các mục này có tên và mô tả giống augment Set 18 (ví dụ Aftershock: "sau 8 giây, choáng mọi địch 1,5 giây"; Bark Armor: "tướng nhận 150 khiên trong 10 giây"), nhưng apiName không nằm trong danh sách 594 augment của setData. Chưa xác định chắc phân loại; đây là mục chưa rõ.
- Lưu ý về `build_real_set18_clean` (nội dung dùng trong môi trường mô phỏng): hàm này bỏ toàn bộ `TFT_Item_*` và giữ 505 mục `DA_*`, 667 item. Khi dùng nội dung này, 36 craftable có twin hiệu ứng chỉ nhận bonus chung của engine, không nhận hiệu ứng riêng.
- Hook: 0 mục `DA_*` nằm trong bảng hook của engine. Các hook của item cổ điển được tính trong bảng dùng chung với Set 17.

Đếm hiệu quả theo tên (ghép craftable `DA_*` với item cùng tên `TFT_Item_*`): 191/776 item có tác dụng trong engine (157 theo apiName + 34 craftable qua item cùng tên). Vẫn chỉ khoảng một phần tư, và phần lớn là item cổ điển.

Trait (36 trait Set 18; 44 trait Set 17):
- Set 18: 11 trait có bonus chỉ số được áp dụng khi kích hoạt. Kiểm tra mô tả và biến cho thấy 9 ánh xạ đúng (Sprykin, Hunter, Monolith, Attuned, Blackthorn, Fae, Lunar, Thornmaiden, Blossom). 2 ánh xạ sai âm thầm: Vanguard (`MaxHealthShield` là khiên theo phần trăm máu tối đa, đang bị áp thành +máu tối đa), Spellweaver (`APPerCast` là AP cộng dồn theo mỗi lần thi triển, đang bị áp một lần như AP cố định). 25 không có ánh xạ chỉ số (Elderwood, Avatar, Ravager, Bounty Seeker, Solar, Adaptor, Coven, Eclipse, Old Growth, Primal, Greenfather, Invoker, Rapidfire, Juggernaut, Inferno, Rival, Brawler, Executioner, Apex Predator, Riftbeast, Caustic, Defender, Flora Fatalis, Summoner, Emerald Aspect).
- Set 17 để so sánh: 27 áp dụng được, 15 không ánh xạ, 1 có ánh xạ nhưng không đổi chỉ số, 1 không có effect.
- Tên trait Set 18 xuất hiện trong mã engine ngoài `trait_effects.py`: 1/36. Chỉ là dấu hiệu tham chiếu, không chứng minh có logic riêng.

Hệ quả: với Set 18, engine chỉ mô hình hóa được một phần nhỏ trang bị và trait có ý nghĩa trong combat. Trait "không ánh xạ" và emblem có thể làm sai số lớn, nhưng chưa đo được mức ảnh hưởng vì không có trận thật. Không dùng các con số này để kết luận về độ chính xác dự đoán Set 18.

### 8b. Alias item Set 18 (2026-11-25)

`tft-sim/src/tft_sim/item_alias.py`: với craftable `DA_*` rỗng có item cùng tên `TFT_Item_*` có hiệu ứng, copy hiệu ứng và đăng ký hook của twin cho `DA_*`. Có 37 alias. Đã kiểm: đơn vị với DA và với twin cho chỉ số giống hệt, cả khi có và không có bonus chung. Giả định: hiệu ứng của twin là hiệu ứng Set 18 thật. Chưa chạy đo độ lệch trận; `coverage()` chưa báo số alias.

### 8c. Đo tác động của alias lên cặp sim Set 18 (2026-11-25)

Mẫu: 1000 cặp cùng vòng lấy ngẫu nhiên từ 6839 cặp của 10 lobby (seed 288100–288109), ability `generic`, 20 seed mỗi cặp. Cặp sim do env sinh ra; các bàn này có `DA_*` trong trang bị (9072 bản ghi unit có item `DA_*`), nên alias có tác dụng.

- Cặp quyết định (p_tắt ≥ 0,9 hoặc ≤ 0,1): 846/1000. Trên các cặp này, tỷ lệ đảo chiều khi bật alias là 10,1% [6,7; 13,9] (bootstrap theo lobby, 10 lobby).
- Chênh lệch trung bình |p_on − p_off| trên mọi cặp: 0,117.

Đọc kết quả: alias thay đổi kết quả sim đáng kể trên Set 18. Đây là khác biệt giữa hai cách mô phỏng cùng một engine, không phải độ đúng so với thật. Mẫu chỉ 10 lobby và chưa có nhãn thật, nên chưa biết hướng nào đúng.

Script: `scripts/combat/alias18.py` (thu thập và chấm điểm), `scripts/combat/alias18_report.py` (báo cáo). Kết quả: `results/fixed/combat/alias18_report.json`.

Ghi chú về mục 7: `hand_noitems` bỏ cả hiệu ứng riêng và bonus chung của item, nên so sánh "có item / không item" là so sánh gộp hai lớp.

## 9. Template từ mô tả + biến (Set 17), đo trên 2000 cặp cùng vòng từ cả 100 lobby

Template: `scripts/combat/templates.py`. Quy tắc cố định trước khi đo: loại sát thương từ tag mô tả, giá trị từ biến `damage`, tỷ lệ AP/AD từ `scaleAP`/`scaleAD`, choáng nếu có `stun` và biến `duration`. Tướng không áp dụng được dùng `default_ability`.

Phủ: Set 17 61/88 tướng (69%). Set 18 1/91 (1%).

Kết quả (sim, cặp quyết định 1.675/2.000, bootstrap theo lobby). Chỉ số là đồng thuận với engine viết tay (hand):

| Cấu hình | Đồng thuận | |p − p_hand| TB |
|---|---|---|
| template | 82,9% | 0,209 |
| generic (nuke mặc định) | 83,4% | 0,206 |
| none | 81,6% | 0,221 |

Hiệu theo cặp:
- template − none: +1,3 điểm [−0,7; +3,4]. Không khác 0.
- template − generic: −0,5 điểm [−1,1; +0,1]. Không khác 0.
- generic − none: +1,8 điểm [−0,2; +3,8]. Không khác 0.

**Đọc kết quả**: template theo mô tả không cải thiện đồng thuận so với nuke mặc định ở Set 17, và không khác biệt rõ với không ability. Đồng thời phủ Set 18 chỉ 1%, nên con đường template không đủ cho Set 18 khi dữ liệu biến trống. Không có căn cứ để tiếp tục mở rộng template cho Set 18 trên nguồn hiện có.

Giới hạn: tham chiếu là engine viết tay, không phải trận thật; mỗi tướng chỉ có một template đơn giản (sát thương đơn mục tiêu, choáng); chưa thử template hồi máu, khiên, nhiều mục tiêu.

## 10. Nguồn số liệu ability Set 18 (blitz.gg): không thu thập

Đã kiểm tra blitz.gg (2026-11-25). Trang tướng có chỉ số và số ability theo sao (ví dụ Alune: 58/88/500 sát thương phép), nên về mặt nội dung đây là nguồn có số. Nhưng không dùng để thu thập:

- Điều khoản sử dụng (`/legal/terms-of-service`): giấy phép chỉ cho "personal, non-commercial entertainment use"; cấm sao chép, sửa đổi, dùng cho mục đích thương mại, dịch ngược.
- `robots.txt`: chặn `ClaudeBot` và `GPTBot` (`Disallow: /`) với ghi chú "training crawlers".
- Đã thu thập tự động 30/74 trang trước khi dừng (danh sách đầu vào chỉ lấy được 74 slug, không phải 91). Dừng và xóa dữ liệu thô, không ghi file nào vào repo.

Hệ quả: không dùng số liệu blitz.gg cho template Set 18 trừ khi có quyết định cấp phép của người dùng. Ngay cả khi có, kết quả mục 9 cho thấy template số liệu chưa cải thiện đồng thuận so với nuke mặc định ở Set 17, nên số liệu không tự mở khóa một predictor Set 18 trung thực.

Chặn thật sự của Set 18 vẫn là: 0/594 augment có hook, logic ability viết tay chưa có, chưa có bản ghi trận thật có kết quả, và chưa xác nhận vị trí tướng trên dữ liệu thật.

Việc cần người dùng quyết: (a) xác nhận giấy phép CDragon (nguồn mô tả và biến đang dùng); (b) nếu muốn số liệu Set 18, cần nguồn có giấy phép rõ ràng, hoặc chấp nhận rủi ro điều khoản blitz.gg cho mục đích nghiên cứu nội bộ.

### 10b. Cập nhật (2026-11-25): đã thu thập để kiểm tra, chưa commit số liệu

Đính chính mục 10 ở trên: sau khi người dùng chấp nhận rủi ro điều khoản, đã crawl lại 74 trang blitz.gg Set 18 (patch 18.7) và lưu văn bản thô trong scratchpad, không vào repo. Kết quả kiểm tra:

- Parse được 74/74 trang; chỉ số cơ bản và khối ability có mặt ở 72/74 (2 trang không có chỉ số).
- Ghép với CDragon 18.7 theo tên: 71 khớp duy nhất. 3 tên trùng nhiều bản (Elder Dragon, Krug, Murkwolf) và 10 trang Lux (các dạng Lux) chưa ghép được: 10 trang Lux đều rơi vào bản Lux duy nhất của CDragon.
- Đối chiếu chỉ số: HP, giáp, MR, AS khớp ở phần lớn tướng (AD không được so sánh trong script này). Lệch: tầm đánh Ashe, Draven, Lux (Blitz 5, CDragon 6; quy ước đo tầm có thể khác), AS Master Yi AP (0,85 so với 0,80).
- Ghép nhãn: số bộ ba `a/b/c` của Blitz và placeholder `@...@` của CDragon không cùng số lượng ở đa số tướng (3/78 trùng). Chưa có cách ghép nhãn tin cậy theo thứ tự.

Kết luận: chưa commit số liệu Blitz vào repo. Lý do: chưa ghép nhãn sát thương được, và tầm đánh/AS cần quy ước riêng. Nếu sau này cần dùng, ghép theo nhãn cần làm bằng tay từng tướng, và lưu ý điều khoản: giấy phép chỉ cho sử dụng cá nhân phi thương mại; robots.txt chặn ClaudeBot/GPTBot, nên không đưa dữ liệu này vào huấn luyện mô hình khi chưa có quyết định khác của người dùng.

### 10c. Số liệu Blitz Set 18 đã commit (2026-11-25, sửa lần 2)

File: `tft-sim/data/blitz_set18_numbers.json`. 74 trang Blitz (patch 18.7).

- Ghép CDragon 18.7 theo tên: 71 tướng có apiName duy nhất. Elder Dragon, Krug và Murkwolf trùng tên nên apiName = null. Mười dạng Lux ghép riêng từng dạng.
- Căn chỉnh văn bản với mô tả CDragon (placeholder `@...@`): 58/74 tướng khớp. Tổng cộng 270 dòng có nhãn từ căn chỉnh, và 35 bộ ba thô không căn chỉnh được (nhãn `unaligned`).
- 16 tướng chưa căn chỉnh = 13 lệch văn bản (Akali-AD, Alistar, Amumu, Cinderling, Elise, Gnar, Khazix, Kog'Maw-AP, Master Yi-AP, Ornn, Rengar, Teemo, Xayah) + 3 không ghép được apiName.
- Nhãn lấy từ tên placeholder, ưu tiên: duration > shield > magic > physical > heal (`HealthCalc`, `Heal*`) > percent > other. Đã đọc tay câu mô tả của 13 tướng (Fiddlesticks, Hecarim, Kobuko, Lillia, Maokai, Reksai, Scuttlecrab, Sett, Taric, Vi, Yorick, Shen, Camille) cho các dòng heal/shield; `HealthCalc2` của Yorick là HP của tướng triệu hồi (nhãn `summon_hp`). Các tướng còn lại, kể cả Malphite, Ivern, Kennen, Rakan, Rammus, Sejuani, Sentinel, Diana, Ornn, chưa đọc tay.
- Giá trị là số hiển thị trong tooltip (đã tính sẵn), không phải hệ số thô. Chưa xác nhận được gốc tỷ lệ AP/AD: kiểm tra Caitlyn (base AD 50, số 220/330/535) không đủ để kết luận. Vì vậy `templates.py` không được nhân lại theo AP/AD khi dùng các số này.
- Biến CDragon Set 18 gần như trống (70/71 tướng không có biến), nên không đối chiếu được số bằng biến.
- Tầm đánh Ashe, Draven, Lux và AS Master Yi-AP lệch so với CDragon. Số giữ nguyên theo Blitz.
- Điều khoản Blitz: chỉ dùng cá nhân phi thương mại. Người dùng đã chấp nhận rủi ro và cho phép dùng dữ liệu, kể cả cho mô hình.
