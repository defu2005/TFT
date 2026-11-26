# 2. Kiến trúc

## Các khối và vai trò

```
 Nguồn VOD (Twitch/YouTube)            Nguồn live (chưa chọn)          CDragon (nội dung game)
        │                                      │                              │
        ▼                                      ▼                              ▼
 pipeline VOD (4 bước)                 bộ thu trạng thái                data/cdragon/*.json.gz
 ingest → validate → merge gate        (ngoài phạm vi nhánh này)
        │                                      │
        └──────────────┬───────────────────────┘
                       ▼
               fight-v1 (bản ghi trận)  ──► usable.reason (bộ lọc chung)
                       │
          ┌────────────┴─────────────┐
          ▼                          ▼
  fidelity.score                  predict_win / boards_of
  (so dự đoán với kết quả,        (BoardUnit, items = len(item_apis))
   chỉ khi có trận thật đạt)             │
                                         ▼
                              engine tft_goat (repo riêng, d5358e9)
                              combat, trang bị, trait, augment, hook item
                                         │
                                         ▼
                         mô hình học chính sách (teacher v4, EngineResolver)
```

## Hai repo, một nhánh làm việc

| Phần | Nằm ở đâu | Quy tắc |
|---|---|---|
| Engine `tft_goat` | Repo riêng, `/root/work/tft_goat`, commit `d5358e9` | **Không sửa** từ nhánh sim. Thắc mắc gửi qua `docs/agents/requests/`. |
| Lớp bọc `tft-sim` | `tft-sim/` trong repo TFT | Nơi làm việc của nhánh `claude/claude-fable-5-2-awwmf5`. |
| Tài liệu tiến độ | `tft-sim/docs/progress/`, bộ này ở `tft-sim/docs/product/` | Cập nhật cuối mỗi phiên (xem `AGENTS.md` gốc). |
| Lộ trình sản phẩm | `origin/claude/nifty-lovelace-252i30:docs/roadmap.md` | Không nằm trong nhánh làm việc. |

## Cấu hình dự đoán (chọn đúng để đọc số)

- **PRIMARY** (đang dùng): `ability=generic`, `items=True`, `augments=True`, `traits=True`; `emblems=False`, `traits_table=False`, `item_alias=False`.
- **SECONDARY** (kiểm tra): PRIMARY cộng `emblems`, `traits_table`, `item_alias`.
- Mỗi con số trong bộ tài liệu phải ghi cấu hình nào đã tạo ra nó.

## Luồng dữ liệu VOD → kết quả chấm

1. Pipeline VOD (`run_vod_pipeline.sh`, 4 bước) sinh bản ghi `fight-v1` từ video.
2. `validate_vod.py` kiểm schema; `check_vod_dir.py` kiểm thư mục.
3. `merge_check_vod.py` là cổng gộp: trạng thái `HANDOFF_STATUS` và chất lượng. Chưa đạt thì không ghi vào `scoring.jsonl`.
4. `usable.reason` từ chối bản ghi thiếu khóa (`items`, `augments`, `frames`, `board` không phân giải được...). Từ chối là kết quả đúng, không phải lỗi.
5. Chỉ bản ghi đạt mới vào `scoring.jsonl`; `fidelity.score` (n=800, seed0=0) so dự đoán với kết quả thật.

Hiện tại bước 3 không có slot nào đạt, nên bước 5 chưa chạy trên dữ liệu thật.

## Ràng buộc kiến trúc quan trọng

- **Khối `_GENERIC_ITEM`** (Health 150, AD 0.15, AP 15, Armor 15, MR 15) được cộng một lần cho mỗi item đếm. Đường combat hiện đang cộng cho cả item có identity. Chú thích `unit.py:14` nói ngược lại. Đang bàn giao cho tác giả (xem [11. Rủi ro](11-rui-ro-cau-hoi-mo.md)).
- **Hook item** khóa theo `TFT_Item_*`. Các item `DA_*` không có hook.
- **`can_ability_crit`** bật khi api chứa `InfinityEdge` hoặc `JeweledGauntlet`.
