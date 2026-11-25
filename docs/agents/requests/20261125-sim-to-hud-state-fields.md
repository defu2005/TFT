# Yêu cầu: dữ liệu HUD theo thứ tự mở khóa cho mô hình

dataset: các đoạn VOD Set 18 đã có log OCR (nhánh `claude/hud-data-set18` @ `1b4c468`, 23 file, 174.492 mẫu, schema 2, 7 VOD). Cùng khóa `VOD-startSec`, cùng lịch 4 Hz.
fields: theo thứ tự ưu tiên dưới đây. Mỗi trường kèm `confidence` và `src`. Không đọc được thì ghi `null`, không ghi 0.
  1. `stage` (đã có trong `fields4`, do hud xử lý) và `hp` (0–100) của người chơi mình.
  2. `placement` (thứ hạng cuối 1–8), một số cho mỗi trận, kèm nguồn đọc (màn kết thúc hoặc bảng cuối). Hiện chỉ có 1 trận nháp (streamer 2/8, `docs/agents/responses/20261124-hud-match01-result.md`).
  3. `board` (tướng trên bàn, `{champion_api, star}`, `src: template`) và `bench` (cùng cấu trúc). Lưu ý nhánh hud ghi tên tướng trên bàn không đọc được ở 720p: cần xác nhận độ phân giải hoặc icon matching trước khi cam kết lịch.
  4. Kết quả combat từng round (thắng/thua; sát thương nếu có).
  5. `items` và `augments` (kèm tier nếu đọc được).
  6. `hp` đối thủ: hiện chỉ có 6 mẫu nhãn bằng mắt (`data/hud-audit/hp_labels_6.jsonl`, nhánh nifty). Chờ hud xác nhận nguồn trước khi yêu cầu đầy đủ. Không yêu cầu OCR đối thủ lúc này.
  7. Log của set thứ hai (ràng buộc chính: mọi dữ liệu hiện tại là Set 18).
schema: hudSchema 3 (tăng phiên bản theo data-contracts mục 3). Schema 2 giữ nguyên để đọc file cũ.
why: mô hình thích ứng nhiều mùa cần dữ liệu đến dần theo từng loại. Mỗi loại mở khóa một bước đo khác (`tft-sim/docs/model-plan.md` mục 10). Thứ tự trên theo thứ tự mở khóa, không theo độ tiện làm. Hiện không trường nào trong schema 2 đủ để chạy `decide.js`: nó coi `hp` và `stage` thiếu là 0.
unblocks: harness đo tỷ lệ đồng ý của `decide.js` (Phase 4); thí nghiệm mask của sim (`model-plan.md` 10.6); tiêu chí placement của sim.; bàn (3) và kết quả round (4) còn dùng để kiểm độ trung thực của simulator (nhân nhóm `tft-sim`, xem model-plan 10.8)
deadline:
status: mở

## Bản ghi trận fight-v1 (bổ sung 2026-11-25, yêu cầu mở rộng)

Mỗi round có ít nhất một cặp (bàn, bàn đối thủ, kết quả). Định dạng dùng chung với `tft-sim/scripts/combat/fight.py`, schema `fight-v1`:

```
{"schema": "fight-v1", "set": 18, "label": "real", "source": "<vod>:<round>", "patch": "<chuoi patch hoac null>",
 "a": {"level": int, "augments": [apiName...], "units": [{"api": apiName, "star": 1|2|3, "items": [apiName...], "pos": [row, col] | null}]},
 "b": {...cùng cấu trúc...},
 "result": {"winner": 0 | 1 | null}}
```

- `patch`: chuỗi patch của trận (ví dụ `"16.23"` hoặc `"18.x"` nếu biết). Không biết thì ghi `null`; bản ghi vẫn được nhận. `fidelity.py` báo số trận theo patch (`per_patch`) để thấy trận đến từ patch nào.
- `api`: apiName CDragon (ví dụ `DA_Krug18`, Krug của Set 18; `TFT_Krug` là một bản cost 1 không trait, không phải tướng Set 18 chơi được theo dữ liệu hiện có, nhưng vẫn xuất hiện trên bàn mô phỏng, nên chưa được coi là không chơi được; xem names18 báo trùng). Không dùng tên hiển thị. Nếu chỉ đọc được tên hiển thị, ghi tên và đánh dấu; không đoán.
- `pos`: hoặc có đủ cho mọi unit của bên đó (hàng 0–3 cho bên a, 4–7 cho bên b, cột 0–6, không trùng ô), hoặc `null` cho mọi unit. Không ghi nửa vời.
- `result.winner`: 0 nếu bên a thắng round, 1 nếu bên b, `null` nếu không đọc được. Không suy từ HP nếu không chắc.
- Trường chưa đọc được: `null`, không ghi 0.

Ví dụ một round (các giá trị là minh họa, không phải dữ liệu thật):

```
{"schema": "fight-v1", "set": 18, "label": "real", "source": "vod-XX:3-2",
 "a": {"level": 6, "augments": [], "units": [{"api": "DA_Krug18", "star": 2, "items": [], "pos": null}]},
 "b": {"level": null, "augments": null, "units": [{"api": null, "star": 1, "items": null, "pos": null}]},
 "result": {"winner": null}}
```

Thứ tự ưu tiên: (a) bàn của người được quay, (b) bàn đối thủ khi có trong khung combat, (c) kết quả round. Mục (b) là điều kiện để dự đoán combat; không có (b) thì (a) vẫn có ích cho mô hình kinh tế.

## Ghi chú

- Level null ở 9 VOD: xem `20261125-sim-to-hud-level-null-vods.md`.
- `timer`, `gold`, `level`, `xp`, `streak` không yêu cầu ở đây: đã có trong `fields4`.


## Ghi chú apiName trang bị Set 18 (2026-11-25)

- Với Set 18, cùng một tên trang bị có thể có hai apiName: `DA_*` (công thức ghép, `effects` rỗng trong CDragon) và `TFT_Item_*` (có hiệu ứng). Chưa biết client gửi apiName nào trong dữ liệu chụp thật.
- Đề nghị: bản ghi trận phải ghi đúng apiName client gửi, và kèm trường tên hiển thị để đối chiếu. Chưa quyết định ánh xạ nào được dùng trong mô phỏng.


## Danh sách tên Set 18 (bổ sung 2026-11-25)
- File: `tft-sim/data/set18_names.json` (91 tướng, 776 item gồm cả `DA_*` và `TFT_Item_*` có twin, 594 augment, 36 trait). Dùng `api` làm khóa; tên hiển thị là `name`.
- Trường `twin_tft_item` cho biết item `DA_*` tương ứng với `TFT_Item_*` nào (37 cặp alias). Tên phía client Set 18 vẫn chưa biết; nếu client ghi `TFT_Item_*` thì đối chiếu qua trường này.
- Định dạng dữ liệu giả định: JSONL fight-v1 (mỗi dòng là một fight), `source` dạng `game:round`, `api` lấy từ file tên.
