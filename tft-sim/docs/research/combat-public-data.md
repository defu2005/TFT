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

**Chưa làm:** mẫu template, đo đồng thuận template với `none` và `hand`, phạm vi trang bị và trait Set 18 có hiệu ứng.

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
- Đối chiếu chỉ số: HP, giáp, MR, AD, AS khớp ở phần lớn tướng. Lệch: tầm đánh Ashe, Draven, Lux (Blitz 5, CDragon 6; quy ước đo tầm có thể khác), AS Master Yi AP (0,85 so với 0,80).
- Ghép nhãn: số bộ ba `a/b/c` của Blitz và placeholder `@...@` của CDragon không cùng số lượng ở đa số tướng (3/78 trùng). Chưa có cách ghép nhãn tin cậy theo thứ tự.

Kết luận: chưa commit số liệu Blitz vào repo. Lý do: chưa ghép nhãn sát thương được, và tầm đánh/AS cần quy ước riêng. Nếu sau này cần dùng, ghép theo nhãn cần làm bằng tay từng tướng, và lưu ý điều khoản: giấy phép chỉ cho sử dụng cá nhân phi thương mại; robots.txt chặn ClaudeBot/GPTBot, nên không đưa dữ liệu này vào huấn luyện mô hình khi chưa có quyết định khác của người dùng.

### 10c. Đã commit số liệu Blitz Set 18 (2026-11-25)

File: `tft-sim/data/blitz_set18_numbers.json`. Chứa: slug, apiName CDragon (null nếu không ghép duy nhất), tên ability, mana, chỉ số cơ bản, và các bộ ba số `1/2/3 sao` kèm nhãn ngữ cảnh theo quy tắc (magic, physical, true, shield, heal, duration, unlabelled). Không lưu văn bản mô tả.

Hạn chế:
- Biến CDragon Set 18 gần như trống (70/71 tướng ghép được không có biến), nên không kiểm chứng được nhãn bằng CDragon. Nhãn chỉ dựa trên chữ trong mô tả Blitz, chưa kiểm tra tay từng tướng.
- 11/… bộ ba không có nhãn rõ (unlabelled).
- Lux có 10 dạng ghép chung một apiName = null.
- Tầm đánh Ashe, Draven, Lux và AS Master Yi AP lệch so với CDragon; không sửa.
- Nguồn có điều khoản chỉ dùng cá nhân phi thương mại. Người dùng đã chấp nhận rủi ro và cho phép dùng dữ liệu, kể cả cho mô hình.
