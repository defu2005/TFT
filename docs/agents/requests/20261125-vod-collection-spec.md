# Đặc tả thu thập dữ liệu từ VOD streamer (Set 18)

Ngày: 2026-11-25. Trạng thái: mở, bản 2 (sau kiểm tra của advisor). Người đọc: các agent thu thập VOD và người ghép dữ liệu.

Đọc hết trước khi thu bất kỳ dữ liệu nào. Đặc tả mô tả **những gì cần ghi**, không mô tả thao tác trên màn hình. Không đọc được thì ghi `null`. Không bao giờ đoán.

Lưu ý về các mục chưa xác nhận được: đánh dấu rõ `PROVISIONAL` hoặc `CHƯA XÁC NHẬN` và giữ `null` cho đến khi có xác nhận. Không tự chọn quy ước khi chưa có căn cứ.

## 0. Mục tiêu, phạm vi, ranh giới

- **Mục tiêu duy nhất hiện tại:** bản ghi trận combat PvP theo `fight-v1`. Đây là dữ liệu duy nhất bộ chấm điểm `tft-sim/scripts/combat/fidelity.py` đọc được.
- **Các loại khác (game, fight_extra, action, state, gap, reward, round_lobby, scout, calibration):** thu theo yêu cầu, nhưng **chưa có gì tiêu thụ**. Chúng là dự phòng và không được trộn vào file trận.
- **Không đổi `fight-v1`.** Thông tin bổ sung đi vào loại bản ghi riêng, liên kết bằng `game_id`.
- **Ngoài phạm vi:** PBE, Double Up, mọi chế độ khác, vòng PvE (chỉ được gắn nhãn PvE khi thấy rõ), OCR các bàn của đối thủ ngoài khung combat.

## 1. Ràng buộc từ bộ kiểm tra (đọc trước)

Đến từ `check_record` (`scripts/combat/fight.py`) và `_validate` (`scripts/combat/fidelity.py`). Kiểm tra bằng lệnh ở mục 11.

| Trường | Ràng buộc | Ghi chú |
|---|---|---|
| `schema` | `"fight-v1"` | |
| `label` | `"real"` | file có nhãn khác `real` làm `fidelity.score` dừng toàn bộ file |
| `source` | `"<game_id>:<stage_round>"` | ví dụ `twitch-900000001-g3612:3-2`. Phần trước `:` là `game_id` dạng `<vod_id>-g<giây>`. Ingest viết lại thành `<lobby_id>:<stage_round>` trước khi chấm (mục 10.2) |
| `set` | `18` | |
| `a.units[i].api`, `star` | bắt buộc | `api` phải là apiName có trong danh mục tướng Set 18, ví dụ `DA_Krug18` |
| `items` | nếu có khóa thì không được `null` | item không có trong danh mục chỉ bị đếm |
| `augments` | nếu có khóa thì không được `null` | |
| `pos` | có đủ cho mọi unit của bên đó, hoặc `null` cho mọi unit | xem mục 2.4 |
| `result.winner` | `0`, `1`, hoặc `null` | `null` bị bỏ khỏi điểm |

Hệ quả: trận có `winner: null` vẫn được lưu, nhưng bị bỏ khi chấm điểm. Đây là lý do bỏ duy nhất được coi là bình thường.

## 2. Ba giai đoạn của mỗi trường tên

Đây là quy tắc chung cho mọi tên (tướng, item, augment, trait). Không trộn hai giai đoạn trong cùng một trường.

**Giai đoạn A, thu thập (agent làm):** chỉ ghi những gì đọc được trên màn hình, nguyên văn tiếng Anh:
- `api_display`: tên hiển thị của tướng, item hoặc augment, copy đúng chữ.
- `cost`: số vàng của tướng (nếu thấy), để phân biệt tên trùng.
- `traits_display`: danh sách tên trait của tướng (nếu thấy), để phân biệt tên trùng.
- **Không** điền `api` ở giai đoạn này.

**Giai đoạn B, ghép (người ghép chạy sau, không phải agent):** điền `api` từ `tft-sim/src/tft_sim/names18.py`:
- Hàm `resolve(kind, name)` trả về apiName khi chỉ có **một** ứng viên.
- Khi tên trùng, hàm ném `AmbiguousName`. Lúc đó dùng `cost` và `traits_display` để chọn, và ghi lý do chọn vào `field_notes`.
- Nếu vẫn không chọn được, bản ghi đó **giữ ở file chờ xem** (`*_needs_review.jsonl`), không đưa vào file trận.

Trùng tên đã biết trong dữ liệu hiện tại (kiểm ngày 2026-11-25):
- `Krug`: `DA_Krug18` (cost 3, trait Riftbeast và Brawler) và `TFT_Krug` (cost 1, không trait). Bản cost 1 không phải tướng Set 18 chơi được theo dữ liệu hiện có, nhưng vẫn xuất hiện trên bàn mô phỏng nên chưa loại.
- `Elder Dragon`, `Murkwolf`, `Razorbeak`: cũng trùng (xem `results/fixed/combat/name_ambiguity18.json`).

Item: một tên có thể có apiName `DA_*` (công thức, không có chỉ số trong CDragon) và `TFT_Item_*` (có chỉ số). Ghi apiName đúng theo client nếu thấy; nếu không biết thì ghi `items_display` và để `api` của item cho người ghép điền (ánh xạ `DA_*` sang `TFT_Item_*` nằm trong `item_alias_map`).

**Lưu ý emblem:** bộ chấm điểm đọc emblem từ **item** có apiName `DA_18_Emblem*` nằm trong `items`. Ví dụ đúng: `DA_18_EmblemBlossom` (tên hiển thị `Blossom Emblem`). Danh sách `emblems` trong bản ghi chỉ dùng để đối chiếu, không dùng để chấm điểm.

## 3. Bản ghi game (một bản cho mỗi lobby, loại `game`)

Thu một lần cho mỗi ván. Đây là nơi chứa bằng chứng về ván và lobby.

| Trường | Kiểu | Quy tắc |
|---|---|---|
| `type` | `"game"` | |
| `game_id` | chuỗi | `<vod_id>-g<giây bắt đầu ván>`, ví dụ `twitch-900000001-g3612`. Không có `:`. Hai streamer cùng lobby có hai `game_id` khác nhau; khử trùng ở ingest (mục 10.2) |
| `vod_url` | chuỗi | đường dẫn VOD gốc. Chỉ nhận `https://www.twitch.tv/videos/<số>`, `https://www.youtube.com/watch?v=<id>` hoặc `https://youtu.be/<id>`; URL khác là lỗi `bad_source_url` khi gộp |
| `vod_start_s`, `vod_end_s` | số hoặc `null` | đoạn ván nằm trong VOD |
| `date_evidence` | `{"text": chuỗi, "frame": chuỗi}` hoặc `null` | ngày nhìn thấy trong VOD (tiêu đề, dòng chat, màn hình); không có thì `null` |
| `streamer` | chuỗi | tên kênh, copy nguyên văn |
| `rank_displayed` | chuỗi hoặc `null` | hạng hiển thị, ví dụ `"Diamond 2"` |
| `region_evidence` | chuỗi hoặc `null` | |
| `patch_evidence` | `{"text": chuỗi, "frame": chuỗi}` hoặc `null` | bằng chứng patch; không có thì `patch: null` |
| `mode_evidence` | `{"text": chuỗi, "frame": chuỗi}` hoặc `null` | chứng minh là ranked Set 18 tiêu chuẩn |
| `client_language` | chuỗi | phải là `"en_US"` (đã đọc tên tiếng Anh) hoặc khác; khác thì **bỏ ván** |
| `resolution` | chuỗi | ví dụ `"1080p"`, đo từ khung hình |
| `lobby_names` | danh sách 8 chuỗi | tên hiển thị của 8 người, copy nguyên văn |
| `final_placement` | số 1–8 hoặc `null` | thứ hạng cuối của streamer |
| `game_start_mechanic` | `{"name": chuỗi, "options": [chuỗi], "picked": chuỗi}` hoặc `null` | cơ chế mở đầu ván nếu có |
| `capture_notes` | chuỗi | ghi bất thường, ví dụ mất hình |

Ví dụ (minh họa, nhãn `fixture`):

```json
{"type": "game", "game_id": "twitch-900000001-g3612", "vod_url": "https://example.invalid/vod/01",
 "vod_start_s": 3600.0, "vod_end_s": 4500.0,
 "date_evidence": null, "streamer": "example_streamer",
 "rank_displayed": "Diamond 2", "region_evidence": null,
 "patch_evidence": null, "mode_evidence": {"text": "Ranked", "frame": "frames/twitch-900000001-g3612_3610000.png"},
 "client_language": "en_US", "resolution": "1080p",
 "lobby_names": ["Name1", "Name2", "Name3", "Name4", "Name5", "Name6", "Name7", "Name8"],
 "final_placement": 2, "game_start_mechanic": null, "capture_notes": ""}
```

## 4. Bản ghi trận (loại `fight`, `fight-v1`, nhãn `real`)

Một bản ghi cho một trận PvP. Thời điểm chụp là **"lúc bắt đầu combat"**: các unit đã khóa vị trí, chưa có đòn đánh đầu tiên. Chọn khung hình đầu tiên đạt điều kiện đó.

### 4.1 Khóa định danh

- `fight_key = game_id + "|" + stage_round + "|" + sorted(hai tên người chơi)`. Trong một VOD, mỗi (ván, `stage_round`) chỉ có **một** bản ghi, và `merge_check_vod.py` coi trùng `source` là lỗi. Hai streamer cùng ván có `game_id` khác nhau nên `fight_key` thô **khác nhau**. Khử trùng là việc của ingest theo `lobby_id` (mục 10.2), giữ một bản và liệt kê nguồn còn lại trong `fight_extra.sources` (mục 5).
- `source`: `game_id:stage_round` (dữ liệu thô); ingest viết lại thành `lobby_id:stage_round`.

### 4.2 Hai bàn

Mỗi bên (`a` và `b`):

- `level`: số nguyên hoặc `null`.
- `augments`: danh sách apiName, theo thứ tự xuất hiện. Thấy rõ không có thì `[]`. Chưa ghép được apiName thì `null` và ghi `augments_display`. Bản ghi có `null` sẽ bị bỏ, nên phải ghép xong mới đưa vào file trận.
- `units`: mỗi phần tử:
  - `api_display`, `cost`, `traits_display` (giai đoạn A) và `api`, `star` (giai đoạn B);
  - `star`: 1, 2 hoặc 3 (số nguyên);
  - `items`: danh sách apiName, tối đa 3, theo thứ tự. Thấy rõ không có item thì `[]`. **Không biết thì bỏ hẳn khóa `items`**, không ghi `null`. Validator bỏ bản ghi có `items: null`;
  - `items_display`: tên hiển thị để đối chiếu;
  - `screen_pos`: xem mục 4.4;
  - `pos`: xem mục 4.4;
  - `frames`: danh sách khung hình nguồn, ví dụ `["frames/twitch-900000001-g3612_3612400.png"]`.

### 4.3 Kết quả

- `result.winner`: `0` nếu bên `a` thắng round, `1` nếu bên `b` thắng, `null` nếu không rõ. Không suy từ HP nếu không chắc chắn.
- Hòa (draw) và bất thường khác: `winner: null` và ghi `result_detail` trong `fight_extra` (mục 5).

### 4.4 Vị trí

Thu vị trí **theo hướng nhìn của chủ bàn**, sau đó suy ra `pos`.

- `screen_pos`: `{"row_from_back": 0..3, "col_from_own_left": 0..6}`.
  - `row_from_back = 0` là hàng sau cùng của chính người đó, `3` là hàng sát đối thủ nhất.
  - `col_from_own_left = 0` là cột ngoài cùng bên trái nhìn từ chỗ người đó đứng.
  - Đây là toạ độ thu trực tiếp trên màn hình; không suy từ tên tướng.
- `pos` (suy ra, **CHƯA XÁC NHẬN**): dựa trên mã engine (`engine/simulate.py`, lưới 8 hàng × 7 cột, bên 1 được xoay 180°). Công thức:
  - bên `a`: `pos = [row_from_back, col_from_own_left]`;
  - bên `b`: `pos = [7 − row_from_back, 6 − col_from_own_left]`.
  - Công thức này khớp với quy ước validator (bên `a` ở hàng 0–3, bên `b` ở hàng 4–7). **Chưa kiểm chứng** trên màn hình game. Đến khi có kiểm chứng, người ghép **không** điền `pos`; mọi `pos` để `null`.
- `fought_at`: `"home"` nếu khung combat hiển thị bàn của streamer ở nửa dưới màn hình, `"away"` nếu hiển thị bàn đối thủ ở nửa dưới, `null` nếu không rõ. Ghi trong `fight_extra`, không đưa vào `fight-v1`.

Vì sao giữ `screen_pos`: nếu sau này kiểm chứng ra quy ước khác, dữ liệu thô vẫn dùng được, không phải thu lại.

### 4.5 Ví dụ đầy đủ (minh họa, nhãn `fixture`; bản thật có `real`)

```json
{"schema": "fight-v1", "type": "fight", "set": 18, "label": "fixture",
 "source": "twitch-900000001-g3612:3-2", "fight_key": "twitch-900000001-g3612|3-2|NameA|NameB",
 "patch": null, "side_of_streamer": "a",
 "a": {"level": 6, "augments": ["DA_18_BlossomTraitAugment"], "augments_display": ["Blossom's Call"],
       "units": [{"api_display": "Krug", "cost": 3, "traits_display": ["Riftbeast", "Brawler"],
                  "api": "DA_Krug18", "star": 2,
                  "items": ["DA_HandOfJustice", "DA_18_EmblemBlossom"], "items_display": ["Hand of Justice", "Blossom Emblem"],
                  "screen_pos": {"row_from_back": 3, "col_from_own_left": 3}, "pos": null,
                  "frames": ["frames/twitch-900000001-g3612_3612400.png"]}]},
 "b": {"level": 6, "augments": [], "augments_display": [],
       "units": [{"api_display": "Krug", "cost": 1, "traits_display": [],
                  "api": "TFT_Krug", "star": 1, "items": [], "items_display": [],
                  "screen_pos": {"row_from_back": 3, "col_from_own_left": 2}, "pos": null,
                  "frames": ["frames/twitch-900000001-g3612_3612400.png"]}]},
 "result": {"winner": 0}}
```

Lưu ý ví dụ:
- Bên `a` có một unit, bên `b` có một unit. Đây là đủ cho ví dụ, không phải dấu hiệu đúng quy mô thật.
- `Krug` ở bên `b` được ghép thành `TFT_Krug` vì ví dụ giả định cost 1 không trait. Trong thực tế, nếu không có căn cứ để chọn thì phải để vào `needs_review`.
- `DA_18_EmblemBlossom` nằm trong `items`, đúng cách bộ chấm điểm đọc emblem.

Khi đã ghép xong, bản ghi trên phải qua `validate_vod.py` với nhãn `real` (mục 11). Ví dụ bản ghi trận đã được kiểm: `check_record` với nhãn `fixture`, và `validate_vod.py` với nhãn `real` (kết quả: 1 hợp lệ, 0 bị bỏ). Các loại khác (game, action, state, reward, ...) chưa có bộ kiểm tra riêng; chúng là mẫu cấu trúc.

## 5. Phần mở rộng của trận (loại `fight_extra`, không đưa vào `fight-v1`)

Một bản ghi cho mỗi `fight_key`.

| Trường | Kiểu | Quy tắc |
|---|---|---|
| `type` | `"fight_extra"` | |
| `fight_key` | chuỗi | khóa liên kết với bản ghi `fight` |
| `sources` | danh sách `{"streamer": chuỗi, "vod_url": chuỗi, "timestamp_s": số}` | mọi nguồn đã thấy trận này |
| `fought_at` | `"home"`, `"away"`, `null` | mục 4.4 |
| `result_detail` | `"win"`, `"loss"`, `"draw"`, `null` | |
| `summoned_units` | danh sách `{"api_display": chuỗi, "side": "a"|"b"}` | thấy rõ triệu hồi thì ghi; không thấy thì `null` |
| `stacked_stats` | danh sách `{"api_display": chuỗi, "stat": chuỗi, "value": số}` hoặc `null` | chỉ số cộng dồn hiển thị trên unit |
| `board_size_vs_level` | `{"a": {"units": int, "level": int}, "b": {...}}` | để kiểm tra giới hạn số unit theo cấp |
| `damage_taken` | `{"a": [...], "b": [...]}` hoặc `null` | chỉ khi thấy rõ |
| `opponent_flags` | `{"ghost": bool|null, "copied": bool|null}` | đối thủ là bản ghost hoặc bản sao; `null` nếu không biết |
| `frames` | danh sách | khung hình chính của trận |

Ví dụ:

```json
{"type": "fight_extra", "fight_key": "twitch-900000001-g3612|3-2|NameA|NameB",
 "sources": [{"streamer": "example_streamer", "vod_url": "https://example.invalid/vod/01", "timestamp_s": 3612.4}],
 "fought_at": "home", "result_detail": "win", "summoned_units": null, "stacked_stats": null,
 "board_size_vs_level": {"a": {"units": 1, "level": 6}, "b": {"units": 1, "level": 6}},
 "damage_taken": null, "opponent_flags": {"ghost": false, "copied": null},
 "frames": ["frames/twitch-900000001-g3612_3612400.png"]}
```

## 6. Sự kiện theo từng hành động (loại `action`)

Một bản ghi cho **mỗi hành động** của streamer. Dùng đúng tên hành động của engine (`tft_goat/env/actions.py`):

| Tên engine | Chỉ số | Ý nghĩa |
|---|---|---|
| `PASS` | 0 | không làm gì |
| `REROLL` | 1 | làm mới cửa hàng |
| `BUY_XP` | 2 | mua XP |
| `BUY_SHOP` | 3–7 (slot 0–4) | mua tướng ở slot cửa hàng |
| `SELL_BENCH` | 8–16 (slot 0–8) | bán tướng trên bench |
| `FIELD_BENCH` | 17–25 (slot 0–8) | đưa tướng từ bench lên bàn |
| `BENCH_BOARD` | 26–34 (slot 0–8) | đưa tướng từ bàn xuống bench |
| `EQUIP` | 35 | ghép trang bị vào tướng |
| `PICK_AUGMENT` | 36–38 (lựa chọn 0–2) | chọn augment |
| `REROLL_AUGMENT` | 42 | làm mới lựa chọn augment |
| `PICK_GOD` | 39–41 (lựa chọn 0–2) | chọn trong vòng quà ba lựa chọn (carousel). **Ánh xạ carousel → PICK_GOD là tên của engine, CHƯA XÁC NHẬN** |

Lưu ý quan trọng:
- Các tên trên là tên trong `env/actions.py`. Không đặt tên khác như `BUY`, `SELL`, `FIELD` cho cùng hành động.
- Hành động không thuộc engine (ví dụ quan sát một bảng khác) dùng loại riêng, không gắn tên engine.

Mỗi bản ghi:

| Trường | Kiểu | Quy tắc |
|---|---|---|
| `type` | `"action"` | |
| `game_id` | chuỗi | |
| `seq` | số nguyên | tăng dần **trong mỗi game**, không reset giữa các round |
| `timestamp_s` | số | |
| `stage_round` | chuỗi | |
| `action` | chuỗi | tên engine ở bảng trên |
| `index` | số nguyên hoặc `null` | slot hoặc lựa chọn |
| `payload` | object | chi tiết theo hành động, ví dụ `{"api_display": ..., "cost": ...}` |
| `state_before` | object (mục 7) | trạng thái ngay trước hành động |
| `state_after` | object (mục 7) | trạng thái ngay sau hành động |
| `frames` | danh sách | khung hình trước và sau |
| `field_status` | object | `observed`, `inferred` hoặc `unseen` cho từng trường quan trọng |
| `field_confidence` | object | số 0–1 do agent tự ước lượng, cho từng trường |

Ví dụ:

```json
{"type": "action", "game_id": "twitch-900000001-g3612", "seq": 14, "timestamp_s": 3570.2, "stage_round": "2-5",
 "action": "BUY_SHOP", "index": 2,
 "payload": {"api_display": "Krug", "cost": 3},
 "state_before": {"gold": 12, "level": 6, "xp": "10/40", "hp": 60, "streak": 2},
 "state_after": {"gold": 9, "level": 6, "xp": "10/40", "hp": 60, "streak": 2},
 "frames": ["frames/twitch-900000001-g3612_3570200.png"],
 "field_status": {"action": "observed", "payload.cost": "observed"},
 "field_confidence": {"action": 0.95, "payload.cost": 0.9}}
```

## 7. Trạng thái (state)

Mẫu cấu trúc, **không phải JSON hợp lệ** (có ký hiệu `int|null`), chỉ để tham chiếu. Dùng chung cho `state_before`, `state_after`, và bản ghi `state` (mục 7.1). Trường nào không đọc được thì `null`.

```json
{"gold": int|null, "level": int|null, "xp": "a/b"|null, "hp": int|null, "streak": int|null,
 "lock": true|false|null,
 "board": [{"api_display": chuỗi, "api": chuỗi|null, "star": int, "items_display": [chuỗi], "items": [chuỗi]|null}],
 "bench": [giống board],
 "item_bench": [chuỗi display]|null,
 "shop": [{"slot": 0..4, "api_display": chuỗi|null, "cost": int|null}]|null}
```

- `lock`: trạng thái khóa cửa hàng (`true` đang khóa, `false` không khóa, `null` không thấy).
- `board`: tối đa theo cấp (không phải phần này của mục thu thập; dùng để đối chiếu với `board_size_vs_level`).

### 7.1 Bản ghi snapshot cuối giai đoạn chuẩn bị (loại `state`)

Một bản ghi cho mỗi round, ngay trước khi combat bắt đầu.

```json
{"type": "state", "game_id": "twitch-900000001-g3612", "stage_round": "3-2", "timestamp_s": 3610.0,
 "state": {"gold": 24, "level": 6, "xp": "20/40", "hp": 54, "streak": -1, "lock": false,
           "board": [], "bench": [], "item_bench": null,
           "shop": [{"slot": 0, "api_display": "Krug", "cost": 3}]},
 "other_players_hp": {"NameB": 42},
 "frames": ["frames/twitch-900000001-g3612_3610000.png"],
 "field_status": {"state.gold": "observed"}, "field_confidence": {"state.gold": 0.95}}
```

## 8. Các loại sự kiện khác

### 8.1 Làm mới cửa hàng (loại `shop_refresh`)

Ghi mỗi lần cửa hàng thay đổi: đầu round, sau `REROLL`, và khi bị làm mới khác.

```json
{"type": "shop_refresh", "game_id": "twitch-900000001-g3612", "stage_round": "3-2", "timestamp_s": 3601.0,
 "cause": "round_start|reroll|other", "shop": [{"slot": 0, "api_display": "Krug", "cost": 3}],
 "lock": false, "frames": ["frames/twitch-900000001-g3612_3601000.png"]}
```

### 8.2 Khoảng mất hình (loại `gap`)

Ghi khi khung hình bị che hoặc streamer rời màn hình. Không suy hành động trong khoảng này.

```json
{"type": "gap", "game_id": "twitch-900000001-g3612", "t_from": 3640.0, "t_to": 3652.5,
 "reason": "tab_away|covered|overlay|unknown", "note": "chuỗi hoặc null"}
```

### 8.3 Phần thưởng (loại `reward`)

Ghi đủ mọi lựa chọn được đưa ra và lựa chọn đã chọn:

- `reward_type`: `carousel` (ánh xạ tới `PICK_GOD`, CHƯA XÁC NHẬN), `augment`, `pve_orb`, `other`.
- `offered`: danh sách `{"api_display": chuỗi, "api": chuỗi|null}`.
- `picked`: một phần tử của `offered` hoặc `null`.
- `inventory_delta`: thay đổi kho sau khi chọn: `{"gold": int, "items": [...], "units": [...]}`.

Ví dụ phần thưởng PvE kiểu orb:

```json
{"type": "reward", "game_id": "twitch-900000001-g3612", "stage_round": "2-1", "timestamp_s": 3300.0,
 "reward_type": "pve_orb", "offered": null, "picked": null,
 "orb_contents": [{"kind": "item|gold|unit|other", "api_display": chuỗi|null, "value": int|null}],
 "inventory_delta": {"gold": 0, "items": ["Hand of Justice"], "units": []},
 "frames": ["frames/twitch-900000001-g3612_3300000.png"]}
```

Ví dụ augment (mọi lần đề nghị và làm mới):

```json
{"type": "reward", "game_id": "twitch-900000001-g3612", "stage_round": "2-1", "timestamp_s": 3450.0,
 "reward_type": "augment", "offered": [{"api_display": "Blossom's Call", "api": "DA_18_BlossomTraitAugment"}],
 "picked": {"api_display": "Blossom's Call", "api": "DA_18_BlossomTraitAugment"},
 "inventory_delta": {"gold": 0, "items": [], "units": []}, "frames": ["frames/twitch-900000001-g3612_3450000.png"]}
```

### 8.4 Thu nhập vàng theo round (loại `income`)

```json
{"type": "income", "game_id": "twitch-900000001-g3612", "stage_round": "3-2", "timestamp_s": 3608.0,
 "base": int|null, "interest": int|null, "streak_bonus": int|null, "round_result_bonus": int|null,
 "other": int|null, "total": int|null, "frames": ["frames/twitch-900000001-g3612_3608000.png"]}
```

### 8.5 Trạng thái cả lobby theo round (loại `round_lobby`)

Mỗi round một bản ghi, cho cả 8 người chơi:

```json
{"type": "round_lobby", "game_id": "twitch-900000001-g3612", "stage_round": "3-2", "timestamp_s": 3612.0,
 "players": [{"name": "NameA", "hp": 54, "alive": true}, {"name": "NameB", "hp": 42, "alive": true}],
 "pairings": [["NameA", "NameB"]], "eliminated": [], "frames": ["frames/twitch-900000001-g3612_3612000.png"]}
```

### 8.6 Xem bàn người khác (loại `scout`)

Khi streamer xem bàn của người khác:

```json
{"type": "scout", "game_id": "twitch-900000001-g3612", "timestamp_s": 3590.0, "target_name": "NameC",
 "board": [{"api_display": "Krug", "star": 1, "items_display": []}], "frames": ["frames/twitch-900000001-g3612_3590000.png"]}
```

### 8.7 Chụp hiệu chuẩn (loại `calibration`)

Mỗi khi streamer mở bảng chỉ số của một tướng hoặc tooltip của một trait:

```json
{"type": "calibration", "kind": "unit_stat_panel", "game_id": "twitch-900000001-g3612", "timestamp_s": 3600.0,
 "unit_api_display": "Krug", "unit_star": 2, "unit_cost": 3,
 "active_traits": {"Defender": 2, "Brawler": 2, "Spellweaver": 2},
 "items_display": ["Hand of Justice"],
 "numbers": {"Armor": 40, "Max HP": 1100, "AP": 100},
 "frames": ["frames/twitch-900000001-g3612_3600000.png"]}
```

Quy tắc: mỗi lần chụp chỉ ghi **một** tướng với **một** tổ hợp trait và item cố định. Không gộp các tổ hợp khác nhau. Bản ghi này dùng để giải quyết các giả định còn mở trong `docs/model-plan.md` mục 11.17 (Defender 25 là phần thêm hay tổng, Brawler áp phần trăm lên gì, Spellweaver là tổng hay cộng thêm).

## 9. Bằng chứng, độ tin cậy, quy tắc chung

1. **Khung hình:** mọi bản ghi phải có `frames` trỏ đến khung hình đã lưu (tên file gồm `vod_id` và mili-giây). Không có khung hình thì bản ghi đó không đáng tin.
2. **Trạng thái trường:** `field_status` với ba giá trị `observed` (thấy rõ), `inferred` (suy từ nguồn khác, ghi lý do trong `field_notes`), `unseen` (không thấy).
3. **Độ tin cậy:** `field_confidence` là số 0–1 do agent tự ước lượng cho từng trường quan trọng. Đây là tín hiệu thô, không thay thế kiểm tra chéo.
4. **Không đoán:** không dùng `0` để thay `null`; không dùng `[]` để thay "không biết". `[]` chỉ dùng khi đã thấy rõ là không có.
5. **Tên copy nguyên văn** từ client tiếng Anh. Không dịch. Không tự chuẩn hóa. Tên hiển thị đi vào trường `*_display`.
6. **Thứ tự thời gian:** mọi bản ghi có `timestamp_s` (giây trong VOD). `seq` của hành động tăng dần trong mỗi game.

## 10. Lấy mẫu, khử trùng, kiểm tra chéo

### 10.1 Lấy mẫu

- Chỉ ranked Set 18 tiêu chuẩn. Loại PBE, Double Up, mọi chế độ khác, vòng PvE (khi thấy rõ là PvE).
- Lấy **mọi trận PvP** của mỗi ván, không chỉ đoạn nổi bật. **Giữ cả trận thua.**
- Ưu tiên lấy **trọn ván**, trải đều giữa nhiều streamer, không để một người chiếm phần lớn.
- Mục tiêu theo số **ván** (không phải số trận combat): khoảng **137 ván** để ước lượng chênh lệch ±0,10, và khoảng **545 ván** để ±0,05. Mỗi trận combat một bản ghi `fight`; khi tính khoảng tin cậy, các trận cùng ván được gom theo `lobby_id` **sau khi khử trùng ở ingest** (mục 10.2), không theo `game_id` thô.

### 10.2 Khử trùng

Việc này thuộc bước **ingest**, chạy sau khi gộp (`merge_check_vod.py`): `tft-sim/scripts/combat/ingest_vod.py` (kiểm thử `selftest_ingest_vod.py`).

- `lobby_id` = `sha1` của 8 tên lobby đã chuẩn hóa (NFC, casefold, bỏ khoảng trắng đầu cuối, sắp xếp), lấy 12 ký tự đầu. Hai VOD cùng lobby có cùng `lobby_id` dù `game_id` khác nhau.
- Với mỗi (`lobby_id`, `stage_round`, cặp người chơi): giữ **một** bản ghi `fight`, ưu tiên khung hình rõ hơn. Các nguồn còn lại ghi vào `fight_extra.sources`.
- Viết lại `source` thành `lobby_id:stage_round`. Đây là khóa dùng cho cụm ván (mục 10.1).
- `merge_check_vod.py` báo WARN `shared_lobby_needs_ingest` và `duplicate_fight_key_needs_ingest` để ingest biết cần khử trùng ở đâu.
- Lobby thiếu tên: WARN `incomplete_lobby`, ingest giữ lại trong `held.jsonl`. Tên placeholder (`unknown_*`, `unk_*`) là lỗi `placeholder_name`. Ván không có fight là lỗi `game_without_fights`.

### 10.3 Kiểm tra chéo (ngưỡng tạm thời, do người viết đặt; **PROVISIONAL**)

- Mẫu kiểm tra chéo: ngẫu nhiên **10%** số trận, tối thiểu **30 trận**, tối thiểu **20 ván** khác nhau.
- Hai agent gán nhãn độc lập và so khớp theo từng trường.
- Ngưỡng đồng ý (tỉ lệ trùng khớp):
  - `api`, `star`, `result.winner`: **≥ 0,95**;
  - `items`, `augments`: **≥ 0,90**;
  - `screen_pos`: **≥ 0,90**;
  - dưới ngưỡng ở bất kỳ trường nào thì gán lại cả lô và kiểm tra lại.
- Đây là ngưỡng khởi điểm. Sau lô đầu tiên, người ghép điều chỉnh và ghi lý do vào tài liệu. Không đổi ngưỡng sau khi xem kết quả để làm lô đó đạt.

## 11. Chạy kiểm tra và bàn giao

### 11.1 Lệnh kiểm tra cho collector

Chạy trên file **trận** (`fight`) của từng VOD (mục 11.2):

```bash
cd tft-sim
python3 scripts/combat/validate_vod.py data/vod_out/20261125/<S>/<vod_id>/fights.jsonl --out data/vod_out/20261125/<S>/<vod_id>/validate.json
```

- Lệnh in số bản ghi hợp lệ, số bị bỏ, và lý do từng loại. Ví dụ dòng: `winner_null`, `items_null`, `augments_null`, `tuong_la:<api>`, `star_khong_hop_le`, `source_sin_game`, `label_khong_phai_real:<nhãn>`, `schema:<lỗi>`.
- Thoát với mã 0 khi không có dòng bị bỏ; mã 1 khi có. `winner_null` là lý do bỏ **bình thường** (giữ lại để kiểm tra sau). Mọi lý do khác phải được sửa trước khi bàn giao.
- File chứa dòng `label` khác `real` làm `fidelity.score` từ chối toàn bộ file. Không trộn nhãn.

### 11.2 Bàn giao

- Thư mục bàn giao: `tft-sim/data/vod_out/20261125/<S>/<vod_id>/` với `<S>` là slot (P1, P2, P3, V1). Layout và quy tắc khôi phục, reassign, khử trùng nằm trong `tft-sim/docs/handoff/vod-collection.md`.
- Mỗi VOD có: `handoff.json` (`vod-handoff-v1`), `games.jsonl`, `fights.jsonl`, `others.jsonl`. Tên file cố định, không ghép thêm tên streamer.
- `others.jsonl` chứa mọi loại khác (action, state, shop_refresh, gap, reward, income, round_lobby, scout, calibration). Không trộn vào `fights.jsonl`.
- Trận có `winner: null` vẫn ghi vào `fights.jsonl`. Validator và bộ chấm bỏ chúng; số lượng ghi vào `needs_review` trong `handoff.json`.
- Mỗi lô: người ghép chạy `merge_check_vod.py` (thoát 0 khi không có ERR), sau đó ingest khử trùng (mục 10.2), rồi mới chạy chấm điểm. Báo cáo lô gồm số ván, số trận hợp lệ, số bị bỏ theo lý do, số `needs_review`, và kết quả kiểm tra chéo (mục 10.3).

## 12. Việc còn mở (không được tự giải quyết)

- **Quy ước `pos`** (mục 4.4): chưa kiểm chứng trên màn hình. Đến khi có, mọi `pos` là `null`.
- **Ánh xạ carousel → `PICK_GOD`**: là tên của engine, chưa xác nhận.
- **Apiname item client gửi** (`DA_*` hay `TFT_Item_*`): chưa biết. Ghi `items_display` và để người ghép quyết định theo `item_alias_map`.
- **Augment, thứ tự hiển thị:** chưa chắc; ghi theo thứ tự xuất hiện.
- **Ba giả định trait** (Defender 25 hay 37, phần trăm Brawler, tổng hay cộng thêm của Spellweaver): chỉ giải quyết qua `calibration` (mục 8.7).
- **Quan sát tầng action, state, reward:** chưa có gì tiêu thụ. Chỉ thu để sau.
