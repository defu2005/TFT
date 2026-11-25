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
