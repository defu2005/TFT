# Yêu cầu tới tác giả `tft_goat`: quy ước khối item chung `_GENERIC_ITEM`

Ngày: 2026-11-26. Người gửi: nhánh `claude/claude-fable-5-2-awwmf5` (tft-sim). Commit engine tham chiếu: `d5358e9`.

## Câu hỏi

Khối `_GENERIC_ITEM` được cộng cho mọi "item" đếm trong `BoardUnit.items`, kể cả item đã có identity trong `item_apis`. Quy ước đúng là gì?

- (a) Khối chung cho **mọi** item đếm được (hiện tại: `items == len(item_apis)` nên mỗi item có identity cũng nhận khối chung, cộng với hiệu ứng thật của nó).
- (b) Khối chung chỉ cho phần **không có identity**: `items - len(item_apis)`.

## Mâu thuẫn trong mã

- `src/tft_goat/engine/unit.py:14` ghi: "Bonus generique d'un objet « moyen » quand l'identite n'est pas connue (board env = compteur)." Theo chú thích, khối chung dành cho item không có identity.
- `src/tft_goat/engine/unit.py:126` áp hiệu ứng thật cho `item_apis`; `unit.py:129-130` cộng khối chung `generic_items` lần nữa.
- `src/tft_goat/env/actions.py:212-224` (`_equip`): item thật được thêm vào `item_apis` và `items += 1` cùng lúc. Trong env, `items == len(item_apis)` luôn đúng.
- `src/tft_goat/engine/simulate.py:318-321` (`_build_team`): truyền `generic_items=bu.items`. Vì vậy đường combat của engine cộng khối chung cho mọi item có identity.
- `src/tft_goat/surrogate/dataset.py:92`: `BoardUnit(..., items=len(u.items))` không kèm `item_apis`. Đây là trường hợp "identity không biết" mà chú thích mô tả.
- `src/tft_goat/surrogate/dataset.py:48`: `items=int(it), item_apis=item_apis`, tức là cả hai cùng có mặt.

Kết luận của chúng tôi: đường combat hiện tại (a) là hành vi thực tế tại `d5358e9`, còn chú thích nói (b). Chúng tôi không tự chọn.

## Hệ quả đo được (dữ liệu nội dung Set 18, không VOD)

Trên 731 api item mà `names18` xuất ra (bỏ 45 twin alias), đo bằng `build_unit` một unit cố định, có và không có item, không tính khối chung (`scripts/combat/check_item_effects.py`, kết quả `results/fixed/combat/item_effect_classes.json`):

- Dưới PRIMARY (không alias): 113 item đổi chỉ số, 1 item có proc, **617 item không có tác động nào** trong mô hình (324 không có hiệu ứng trong nội dung; 293 có hiệu ứng nhưng khóa không được `_apply_effects` nhận). Với 617 item này, khối chung là toàn bộ tác động.
- Dưới SECONDARY (có alias): 127 item đổi chỉ số, 28 có proc, 576 không có tác động.
- Nếu chọn (b), cấu hình record của chúng tôi sẽ không còn khối chung nào, và 617 item PRIMARY sẽ không có tác động. Câu hỏi phụ: bổ sung hiệu ứng cho các lớp `composition`, `DA_Component_*`, `DA_Artifact*`, `*Radiant` không có chỉ số có nằm trong phạm vi của engine không?

## Câu hỏi phụ

1. Hook proc (`ITEM_ON_ATTACK`, `ITEM_ON_CAST`, `ITEM_ON_DAMAGED`, `ITEM_HP_THRESHOLD`, `ITEM_REVIVE`, `ITEM_COMBAT_START`, `ITEM_ON_TICK` trong `simulate.py`) khóa theo `TFT_Item_*`, còn `DA_*` không có hook. Đây có phải thiết kế chủ đích?
2. Có kế hoạch nào để `DA_*` có identity dùng được trong bảng hook không (ví dụ qua alias)?

## Không có gì được thay đổi bên phía chúng tôi chờ câu trả lời

Giữ `items=len` trong `fight.boards_of`. Không đổi cấu hình đông lạnh vì lý do này.
