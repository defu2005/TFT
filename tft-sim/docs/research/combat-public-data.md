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

Lý do thay thế: v1 không có augment (bug đọc sai trường), chỉ có cặp cùng vòng, và chế độ public tắt cả ability lẫn trang bị nên không tách được hai yếu tố.

Số liệu v1 (giữ để đối chiếu): 

Nguồn: 67.122 cặp từ 100 lobby v4 (seed 288000–288099); lấy ngẫu nhiên 500 cặp để phân tích. Mỗi cặp: 20 lần chạy engine đầy đủ và 20 lần ở chế độ public. Kết quả: `results/fixed/combat/study17_288000.json`. Nhãn: **sim**, engine tự sinh, không phải trận thật.

- **A. Tran nhieu**: 83,8% cặp quyết định (≥90% một bên thắng), 5,6% gần tung đồng xu.
- **B. Suc manh don gian**: hồi quy logistic trên tổng cost·sao, số trang bị, cấp, số trait cho độ chính xác 58,7% trên các cặp quyết định. Gần mức đoán. Chỉ số sức mạnh đơn giản gần như không giải thích kết quả trong engine Set 17.
- **C. Public so voi full**: hai chế độ đồng ý về bên thắng ở 72,3% trong 419 cặp quyết định. Chênh lệch xác suất trung bình 0,31.

Đọc kết quả: trong engine, ability và trang bị quyết định phần lớn kết quả, không phải chỉ số. Chế độ public chỉ đúng ở khoảng 3/4 cặp quyết định. Điều này trả lời một phần câu hỏi "chỉ số công khai có đủ không": không đủ để đoán chính xác, nhưng không hoàn toàn vô dụng. Chưa đo độ trung thực với trận thật.

## 6. Đo v2 trên cặp bàn Set 17 (engine, không phải trận thật)

Nguồn: `scripts/combat/study17.py` v2. 67.122 cặp cùng vòng và 4.000 cặp xuyên vòng từ 100 lobby v4 (seed 288000–288099). Lobby chia theo `id % 10`: 30% giữ lại làm test. Test: 600 cặp (300 cùng vòng, 300 xuyên vòng). Mỗi cặp 20 lần chạy engine cho mỗi cấu hình. Kết quả: `results/fixed/combat/study17_v2_288000.json`. Nhãn: **sim**.

**Kiểm tra:**
- Lệch `items` so với `len(item_apis)`: 0 trên 129.912 đơn vị.
- Đối xứng: |p(a,b) + p(b,a) − 1| trung bình = 0,0095.
- Quyết định (một bên ≥90%): 88,7% cặp test; cùng vòng 85,3%, xuyên vòng 92,0%.

**Cấu hình (đồng ý dấu với engine đầy đủ, trên cặp quyết định):**
- Ability generic (mọi tướng dùng nuke mặc định): **91,2%**.
- Không ability (có trang bị): **91,5%**.
- Ability viết tay, không trang bị: **88,4%**.

Đọc: bỏ ability làm mất khoảng 8 điểm; bỏ trang bị làm mất khoảng 12 điểm. Ability generic và không ability gần như nhau, nên nuke mặc định gần như không khác so với không ability ở mức thắng/thua.

**Hồi quy logistic (đặc trưng: tổng cost·sao, số trang bị, cấp, số trait; nhãn mềm = p engine đầy đủ; huấn luyện trên lobby train):**
- Độ chính xác trên cặp quyết định test: **80,5%**. Baseline luôn đoán A: 49,3%.
- Theo tercile độ chênh sức mạnh: 66,9% (thấp nhất), 76,4%, 98,3% (cao nhất).

**Đính chính**: kết luận v1 "sức mạnh đơn giản gần như không giải thích được" là sai. Nó xuất phát từ bug thiếu augment và thiếu cặp xuyên vòng. Với dữ liệu v2, sức mạnh đơn giản giải thích được phần lớn kết quả, đặc biệt khi chênh lệch lớn.

**Giới hạn**:
- Chỉ là mô phỏng engine Set 17, bot v4. Chưa đo với trận thật.
- Test chỉ có khoảng 30 lobby, nên khoảng tin cậy chưa tính.
- Nhãn là xác suất ước lượng từ 20 lần chạy, có nhiễu.
