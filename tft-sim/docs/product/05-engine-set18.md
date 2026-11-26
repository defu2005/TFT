# 5. Engine Set 18

Engine là repo `tft_goat` (commit `d5358e9`). Nhánh sim không sửa engine; mọi thiếu sót ghi lại ở đây và trong `docs/agents/requests/`.

## Đã mô hình hóa (trong cấu hình PRIMARY)

- **Tướng:** 91 tướng Set 18 từ snapshot CDragon (`data/cdragon/cdragon_18.7_2026-11-23.json.gz`). Tên file ghi "18.7" nhưng **số patch thật chưa xác minh**.
- **Trait:** bật (`traits=True`). Có kiểm tra bậc trait (`selftest_trait_tiers.py`).
- **Trang bị:** bật. 113 item đổi chỉ số, 1 item có proc, dưới PRIMARY. Khối chung `_GENERIC_ITEM` áp cho mọi item đếm (xem dưới).
- **Augment:** bật về mặt cờ. Quét 252 augment: **0/252 đổi xác suất**, trên một bàn cân bằng, một seed, n=200, không item (`augment_sweep.json`). Nghĩa là hiện tại augment không tạo khác biệt đo được trong combat mô phỏng.
- **Crit:** `can_ability_crit` bật cho item có `InfinityEdge` hoặc `JeweledGauntlet`.

## Chưa mô hình hóa (dưới PRIMARY)

- **Ability riêng từng tướng:** `ability=generic`. Mỗi tướng không có kỹ năng riêng. Số Blitz (74 trang, 58 căn chỉnh được với mô tả CDragon) đã có trong `data/blitz_set18_numbers.json` nhưng **chưa nối vào Set 18** vì chưa có bản ghi thật để chấm.
- **Emblem:** tắt.
- **Alias item:** tắt trong PRIMARY. SECONDARY bật alias cho item có thành phần và `DA_Component_*` (`src/tft_sim/item_alias.py`). 41 ứng viên Radiant/Artifact chỉ được đếm, chưa alias.
- **617 trên 731 item không có tác động nào** trong mô hình. Trong số này 324 không có hiệu ứng trong nội dung; 293 có hiệu ứng nhưng khóa không được `_apply_effects` nhận.
- **Hook proc cho `DA_*`:** không có. Hook chỉ khóa theo `TFT_Item_*`, trừ khi có alias SECONDARY.
- **Độ phủ item Set 18:** 40,6% slot có hiệu ứng rỗng; 91,8% trong số đó là emblem (`docs/research/combat-public-data.md` mục 12).
- **Template ability Set 18:** không đạt cổng (17,1% so với 15,9% generic, CI [−0,0066; +0,0297]). Set 18 không làm template (`combat-public-data.md` mục 12).
- **Vị trí (positioning):** chưa có trong nhánh sim.

## Quy ước chưa xác nhận: `_GENERIC_ITEM`

Đây là điểm có ảnh hưởng lớn nhất tới số combat có item.

- Chú thích `unit.py:14` nói khối chung chỉ cho item **không có identity**.
- Đường combat thực tế (`simulate.py:318-321`, `generic_items=bu.items`) cộng khối chung cho **mọi** item, kể cả item có identity.
- Env (`actions.py:212-224`) luôn làm `items == len(item_apis)`.

Nhánh sim giữ nguyên `items=len` và không đổi cấu hình đông lạnh. Ba câu hỏi đã gửi tác giả: `docs/agents/requests/20261126-engine-generic-item-convention.md`. **Chưa có trả lời.**

Hai hướng: (a) giữ hành vi hiện tại, khối chung áp cho mọi item; (b) khối chung chỉ cho phần không có identity. Chưa chọn. Nếu (b), 617 item PRIMARY sẽ không có tác động nào, và mọi số có item phải đo lại.

## Đã đính chính (đừng tin các bản cũ)

- "generic_items luôn 0": **sai**.
- "65/776 item không có hiệu ứng": **sai phạm vi**. Số đúng: 617/731 dưới PRIMARY (đã bỏ 45 twin trong 776).

## Câu hỏi mở cho engine

1. Quy ước `_GENERIC_ITEM` (a hay b).
2. `composition`, `DA_Component_*`, `DA_Artifact*`, `*Radiant` không có chỉ số: có nằm trong phạm vi engine không?
3. Hook proc khóa `TFT_Item_*` có phải thiết kế chủ đích không?
4. Có kế hoạch để `DA_*` có identity dùng được trong bảng hook (ví dụ qua alias) không?
