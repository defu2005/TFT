# 2. Kiến trúc

## Sơ đồ

```
 VOD Twitch/YouTube ──► pipeline VOD (run_vod_pipeline.sh)
                          1 cổng gộp (merge_check_vod)  ── đỏ thì DỪNG
                          2 ingest + khử trùng (usable.reason, scoring.jsonl)
                          3 validate fights.jsonl (thông tin)
                          4 validate scoring.jsonl (dừng nếu có bản ghi lỗi)
                                   │
                                   ▼
                     scoring.jsonl ──► fidelity.score (n=800, seed0=0)
                                          ▲
                                          │ predict_win / boards_of
                                          │ (BoardUnit, items = len(item_apis))
                                          │
 CDragon (data/cdragon) ──► tft_goat engine (repo riêng, d5358e9)
                                          ▲
                                          │
 Dữ liệu live (CHƯA CHỐT NGUỒN) ──────────┘  (đường găng sản phẩm)

 Engine Set 17 (EngineResolver) ──► teacher v4 ──► mô hình học chính sách
                                                   (nhánh riêng, không đi qua
                                                    fight-v1 hay fidelity)
```

Hai nhánh đi qua engine nhưng **không** nối với nhau: bộ dự đoán combat (chấm bằng trận thật) và mô hình học chính sách (chấm bằng mô phỏng, hiện chỉ Set 17).

## Repo và nhánh

| Phần | Nằm ở đâu | Quy tắc |
|---|---|---|
| Engine `tft_goat` | Repo riêng, `/root/work/tft_goat`, commit `d5358e9` | Không sửa từ nhánh sim. Thắc mắc gửi qua `docs/agents/requests/`. |
| Lớp bọc `tft-sim` | `tft-sim/` trong repo TFT | Nhánh làm việc `claude/claude-fable-5-2-awwmf5`. |
| Tài liệu tiến độ | `tft-sim/docs/progress/` | Cập nhật cuối mỗi phiên (`AGENTS.md` gốc). |
| Lộ trình sản phẩm | `origin/claude/nifty-lovelace-252i30:docs/roadmap.md` | Không nằm trong nhánh sim. |
| Nhánh `hud` | Đọc HUD/OCR | Ngoài phạm vi nhánh sim. |
| Nhánh `engine` | Chủ roster Set 18 (`src/data/set18.json`) | Roster do advisor quyết, người dùng ủy quyền (2026-11-26); `set18.json` có trên `master`. |

## Cấu hình dự đoán

- **PRIMARY** (đang dùng): `ability=generic`, `items=True`, `augments=True`, `traits=True`; `emblems=False`, `traits_table=False`, `item_alias=False`.
- **SECONDARY** (kiểm tra): PRIMARY cộng `emblems`, `traits_table`, `item_alias`.
- Mỗi con số trong bộ tài liệu phải ghi cấu hình đã tạo ra nó.

## Alias item (chỉ SECONDARY)

`src/tft_sim/item_alias.py` ánh xạ `DA_*` sang `TFT_Item_*` cho item có thành phần (craftable) và `DA_Component_*`. Áp dụng qua id trong `fight.boards_of`, không qua nội dung hay hook. `DA_Component_TearOfTheGoddess` không có twin nên không alias. 41 ứng viên Radiant/Artifact chỉ được **đếm** (`check_alias_candidates.py`), chưa alias.

## Luồng VOD → chấm điểm

Đúng thứ tự trong `scripts/combat/run_vod_pipeline.sh`:

1. Cổng gộp (`merge_check_vod.py`). Đỏ thì dừng.
2. Ingest và khử trùng (`ingest_vod.py`): bản ghi qua `usable.reason`; bản ghi đạt vào `scoring.jsonl`.
3. `validate_vod.py` trên `fights.jsonl` (chỉ để biết, fight bị bỏ là bình thường).
4. `validate_vod.py` trên `scoring.jsonl` (dừng nếu có bản ghi không qua scorer).

`fidelity.score` chỉ đọc `scoring.jsonl`. Hiện tại bước 1 chưa có slot nào đạt.

## Ràng buộc kiến trúc quan trọng

- **Khối `_GENERIC_ITEM`** (Health 150, AD 0.15, AP 15, Armor 15, MR 15) được cộng một lần cho mỗi item đếm. Đường combat hiện cộng cả cho item có identity (`simulate.py:321`); chú thích `unit.py:14` nói ngược lại. Đang chờ tác giả engine (xem [11](11-rui-ro-cau-hoi-mo.md)).
- **Hook item** khóa theo `TFT_Item_*`. Item `DA_*` không có hook (trừ khi qua alias SECONDARY).
- **`can_ability_crit`** bật khi api chứa `InfinityEdge` hoặc `JeweledGauntlet`.
- **Vị trí (positioning):** `BoardUnit` (`tft_goat/env/state.py:19`) không có trường vị trí. Chỉ engine `Unit` có `pos=(0,0)`. Mọi kết quả sim giả định vị trí do engine tự quyết.
