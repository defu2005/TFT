# Trạng thái Set 18 (sim, chưa kiểm chứng với trận thật)

Cập nhật: 2026-11-25. Mọi con số là của sim/engine, không phải trận thật. Repo chưa có bản ghi trận Set 18 thật nào.

## Trạng thái tổng quát
- Dự đoán Set 18 dùng ability generic (ability viết tay bị chặn cho Set 18). Cấu hình này chưa được đo so với trận thật.
- Đường đo thật (`scripts/combat/fidelity.py`) đã sẵn sàng: bỏ qua bản ghi hỏng có lý do, tách tên item lạ, chặn bản ghi sim. Đã có selftest.
- Phase 4 đã khóa quy tắc đạt/không đạt (mục 11.7 của `docs/model-plan.md`). Đang chờ dữ liệu người dùng cung cấp.

## Ability
- Template ability Set 18: không làm. Cổng (mục 11.2): template 17,1% đảo chiều, generic_novars 15,9%, hiệu +1,1 điểm, CI95 [-0,7; +3,0]. Không đạt.
- Phủ template Set 18: 1/91 tướng (mục 9 của `docs/research/combat-public-data.md`).
- Số liệu ability Blitz: 74 mục, 58 căn chỉnh được (mục 10). Chưa nối vào Set 18 vì chưa có bản ghi thật để chấm.

## Trait (36 trait trong CDragon)
- 11 trait có ánh xạ stat (`generic_stat_applied`), 25 trait không có ánh xạ stat (`no_stat_mapping`). Nguồn: `results/fixed/combat/coverage_items_traits.json`.
- Vanguard `MaxHealthShield` và Spellweaver `APPerCast` bị bỏ trong đường Set 18 (`_SET18_BAD_KEYS` trong `fight.py`). Selftest mục 9 và mục 10e.
- 25 trait chưa ánh xạ: danh sách và thứ tự ở mục 11.5.

## Emblem
- CDragon có 23 mục emblem: 21 emblem có trait (gồm một bản augment của Flora Fatalis), 2 Phantom không có trait.
- Engine trước đây không cộng điểm trait từ emblem (`env/traits.py::active_traits` chỉ đếm tướng). Đã thêm `emblems=True` trong `fight.py` (mặc định tắt). Selftest mục 10 PASS.
- Độ nhạy (mục 11.5): 108/1000 cặp đổi tier, 31 cặp đổi tier ở trait có ánh xạ stat, |Δp| trung bình 0,026 ở nhóm đó. Mẫu bị bão hòa (876/1000 là cặp quyết định), nên chưa kết luận được.

## Item
- setData có 776 item Set 18 (505 `DA_*`, 271 `TFT_Item_*`). Đã alias 37 cặp DA/TFT_Item cùng công thức (mục 8b).
- Trong mẫu sim `pairs18_sample.jsonl`: 0 slot item không rõ tên. 40,6% slot có hiệu ứng rỗng, 91,8% trong số đó là emblem. Đây là cơ cấu item của sim, không phải tần suất thật.
- Tên item phía client của Set 18 (`DA_*` hay `TFT_Item_*`) chưa biết. Bản ghi thật có thể dùng tên nào cũng được; tên lạ được đếm trong `unknown_items`.

## Augment
- 594 augment Set 18. 70 cái trùng id với hook của Set 17 (`AUGMENT_REGISTRY`).
- Trong mẫu sim: 1008/3616 slot augment (27,9%) chạy hook Set 17. Đọc mẫu cho thấy có khác biệt về cơ chế (mục 11.8). Chưa có công tắc để bỏ hook; đề xuất thêm `augment_hooks` cho Set 18.

## Quy ước engine đã xác định
- Trang bị: hiệu ứng riêng của item cộng thêm bonus generic theo số item (`_GENERIC_ITEM`). Cộng gộp là quy ước của engine; `fight.py` tái tạo đúng (mục 8).
- Biến số của generic ability: bỏ biến số làm đổi ~12% cặp, nhưng tỷ lệ đảo chiều so với hand gần như bằng nhau (mục 11.1).

## Dữ liệu và tái lập
- Mẫu sim Set 18: `data/sim/pairs18_sample.jsonl.gz` (1000 cặp, nhãn `sim`, 10 lobby).
- Bộ dry-run cho đường thật: `tests/fixtures/set18_dryrun.jsonl` (8 bản ghi, source `dryrun-*`, mặc định bị bỏ).
- Yêu cầu dữ liệu từ người dùng: `docs/agents/requests/20261125-sim-to-hud-state-fields.md`. Bản ghi là từng fight, không phải bảng cuối game.

## Lệnh tái lập
Môi trường cần `PYTHONPATH` trỏ tới engine và `tft-sim/src`, và cần `httpx`:

```bash
pip install httpx numpy pandas
export PYTHONPATH=/root/work/tft_goat/src:/home/user/TFT/tft-sim/src
cd /home/user/TFT/tft-sim/scripts/combat
python3 selftest.py
python3 emblem_sensitivity.py ../../data/sim/pairs18_sample.jsonl.gz ../../results/fixed/combat/emblem_sensitivity.json
python3 fidelity.py ../../tests/fixtures/set18_dryrun.jsonl generic 1 5 0
```

Lưu ý: `emblem_sensitivity.py` đọc file `.jsonl`, không đọc `.gz`. Cần giải nén trước: `gunzip -k ../../data/sim/pairs18_sample.jsonl.gz`.
