# Đặc tả thu thập dữ liệu từ VOD streamer (Set 18)

Ngày: 2026-11-25. Trạng thái: mở. Người đọc: các agent thu thập VOD.

Đọc phần này trước khi thu bất kỳ dữ liệu nào. Đặc tả mô tả những gì cần ghi, không mô tả thao tác trên màn hình. Nếu một thông tin không đọc được, ghi `null`, không đoán.

## 0. Mục tiêu và giới hạn

- Mục tiêu duy nhất hiện tại: bản ghi **trận combat PvP** (fight-v1). Đây là dữ liệu duy nhất mà bộ chấm điểm `tft-sim/scripts/combat/fidelity.py` đọc được.
- Hai tầng còn lại (snapshot cuối giai đoạn chuẩn bị, sự kiện hành động và phần thưởng) được thu thập theo yêu cầu, nhưng **hiện chưa có gì tiêu thụ**. Chúng chỉ là dữ liệu dự phòng.
- Không tạo định dạng mới cho trận. Không đổi `fight-v1`. Thông tin thêm đi vào các loại bản ghi riêng, liên kết bằng `game_id`.
- Không dùng OCR đối thủ, không dùng PBE, Double Up, chế độ khác, hay vòng PvE (xem mục 7).

## 1. Đọc trước: ràng buộc từ bộ kiểm tra

Các ràng buộc sau đến từ `check_record` (`scripts/combat/fight.py`) và `_validate` (`scripts/combat/fidelity.py`). Bản ghi không đạt sẽ bị bỏ, và điểm không tính được.

| Trường | Ràng buộc |
|---|---|
| `schema` | bằng `"fight-v1"` |
| `label` | `"real"` (file đo lường chỉ chấp nhận `real`) |
| `source` | dạng `"<game_id>:<round>"`, ví dụ `"vod-07:3-2"`. Phần trước `:` là định danh game, bắt buộc để tính khoảng tin cậy theo game |
| `set` | `18` |
| `a`, `b` | mỗi bên có `units` là danh sách |
| `a.units[i].api`, `star` | bắt buộc. `api` phải tồn tại trong danh mục tướng Set 18 (apiName CDragon, ví dụ `DA_Krug18`). `star` là số nguyên |
| `items` | nếu có khóa thì không được là `null`. Item không có trong danh mục chỉ bị đếm, không làm hỏng bản ghi |
| `augments` | nếu có khóa thì không được là `null` |
| `pos` | hoặc có cho mọi unit của bên đó, hoặc `null` cho mọi unit. Không được nửa vời. Bên `a` dùng hàng 0–3, bên `b` dùng hàng 4–7, cột 0–6, không trùng ô |
| `result.winner` | `0` nếu bên `a` thắng round, `1` nếu bên `b` thắng, `null` nếu không đọc được. Bản ghi có `winner = null` bị bỏ khỏi điểm |

Hệ quả: một trận không có người thắng đọc được thì **vẫn được lưu** (để dùng sau), nhưng không tính vào điểm.

## 2. Tầng 1 (bắt buộc): một bản ghi cho mỗi trận PvP

### 2.1 Định danh (ghi cho từng trận)

| Trường | Loại | Quy tắc |
|---|---|---|
| `game_id` | chuỗi | mã cố định của một ván đấu, ví dụ `vod-07-g2`. Mọi round của cùng ván dùng cùng `game_id` |
| `vod_url` | chuỗi | đường dẫn VOD gốc |
| `timestamp_s` | số | giây trong VOD, tại thời điểm bắt đầu combat của round |
| `streamer` | chuỗi | tên kênh, sao chép nguyên văn |
| `patch` | chuỗi hoặc `null` | ví dụ `"18.7"`. Chỉ ghi khi màn hình hoặc phần mô tả VOD cho biết; nếu không thì `null` |
| `stage_round` | chuỗi | ví dụ `"3-2"`, đọc từ thanh trên cùng |
| `side_of_streamer` | `"a"` hoặc `"b"` | quy ước: bên `a` là bàn của streamer. Đây là thứ tự cố định cho mọi trận |
| `source` | chuỗi | `game_id:stage_round`, ví dụ `vod-07-g2:3-2`. Dùng đúng dạng này để validator nhận |
| `label` | chuỗi | luôn `"real"` |
| `schema` | chuỗi | luôn `"fight-v1"` |
| `set` | số | luôn `18` |

### 2.2 Hai bàn lúc bắt đầu combat

Mỗi bên (`a` và `b`) có:

- `level` (số nguyên hoặc `null`). Cấp của người chơi bên đó, đọc khi combat bắt đầu.
- `augments`: danh sách apiName augment đã chọn, theo thứ tự xuất hiện. Nếu thấy rõ là không có augment thì ghi `[]`. Nếu không đọc được apiName thì ghi `null` cho `augments`, và ghi tên hiển thị vào `augments_display`. Validator bỏ bản ghi có `augments: null`, nên bản ghi đó chỉ dùng được sau khi có apiName.
- `units`: danh sách, mỗi phần tử:
  - `api`: apiName CDragon, ví dụ `DA_Krug18`. **Không** dùng tên hiển thị. Nếu chỉ đọc được tên hiển thị, ghi vào `api_display` và để `api` là `null`; bản ghi đó bị validator bỏ, nên phải sửa khi có apiName.
  - `star`: 1, 2 hoặc 3.
  - `pos`: `[hàng, cột]` theo quy ước ở 2.4, hoặc `null`.
  - `items`: danh sách apiName item, theo thứ tự, tối đa 3. Thấy rõ là không có item thì ghi `[]`. Không biết thì **bỏ hẳn khóa `items`**, không ghi `null` (validator bỏ bản ghi có `items: null`).
  - `items_display`: tên hiển thị của item, để đối chiếu.
  - `emblems`: danh sách trait emblem đang gắn (nếu thấy), ghi tên trait.
  - `evidence`: đoạn thời gian (giây) trong VOD mà mọi thông tin của unit này được đọc.

### 2.3 Đếm trait trên bảng (đối chiếu)

Với mỗi bên, ghi số trait hiển thị trên panel trait và mức đạt được, ví dụ `{"Defender": 2, "Brawler": 2, "Spellweaver": 2}`. Đây là **đối chiếu**, không dùng để chấm điểm. Ghi `null` nếu panel không đọc được.

### 2.4 Quy ước tọa độ (phải xác nhận trước khi dùng)

Validator yêu cầu bên `a` ở hàng 0–3, bên `b` ở hàng 4–7, cột 0–6. **Chưa xác nhận** quy ước này khớp với hướng hiển thị của game:
- Đến khi có xác nhận, ghi `pos: null` cho mọi unit. Đừng tự chọn hướng.
- Khi có xác nhận, mô tả trong mục này: hàng nào là hàng trước, bàn đối thủ có được lật gương không (mirror), và cách đọc cột.

### 2.5 Kết quả

- `result.winner`: `0` nếu bên `a` thắng round, `1` nếu bên `b` thắng, `null` nếu không rõ.
- `players_hp_before`: `{"a": int|null, "b": int|null}` (HP người chơi trước round).
- `players_hp_after`: `{"a": int|null, "b": int|null}` (HP sau round).
- `survivors`: số unit còn sống mỗi bên, nếu thấy rõ, ghi `{"a": int|null, "b": int|null}`.
- `evidence_result`: đoạn thời gian trong VOD cho kết quả.

Không suy kết quả từ HP nếu không chắc. Nếu HP thay đổi nhưng không rõ bên nào thắng, ghi `winner: null`.

### 2.6 Ví dụ đầy đủ (Tầng 1)

Các giá trị dưới đây là minh họa, không phải dữ liệu thật. Ví dụ dùng nhãn `"fixture"` để chạy qua validator; bản thật phải có `"real"`.

```json
{
  "schema": "fight-v1",
  "set": 18,
  "label": "fixture",
  "source": "vod-07-g2:3-2",
  "game_id": "vod-07-g2",
  "vod_url": "https://example.invalid/vod/07",
  "timestamp_s": 1234.5,
  "streamer": "example_streamer",
  "patch": null,
  "stage_round": "3-2",
  "side_of_streamer": "a",
  "a": {
    "level": 6,
    "augments": ["DA_Augment_Example"],
    "augments_display": ["Example Augment"],
    "units": [
      {"api": "DA_Krug18", "star": 2, "pos": null,
       "items": ["DA_HandOfJustice"], "items_display": ["Hand of Justice"],
       "emblems": [], "evidence": [1230.0, 1234.5]}
    ],
    "trait_counts": {"Defender": 2, "Brawler": 2, "Spellweaver": 2}
  },
  "b": {
    "level": 6,
    "augments": [],
    "augments_display": [],
    "units": [
      {"api": "DA_Krug18", "star": 1, "pos": null,
       "items_display": null, "emblems": null, "evidence": [1230.0, 1234.5]}
    ],
    "trait_counts": null
  },
  "players_hp_before": {"a": 60, "b": 42},
  "players_hp_after": {"a": 52, "b": 42},
  "survivors": {"a": 1, "b": 0},
  "result": {"winner": 0},
  "evidence_result": [1240.0, 1241.0]
}
```

Lưu ý với ví dụ: `augments: []` ở bên `b` nghĩa là đã thấy rõ không có augment. Với unit thứ hai của `b`, khóa `items` bị bỏ vì không biết item (không ghi `null`). Mỗi trường có ý nghĩa riêng.

## 3. Tầng 2: snapshot cuối giai đoạn chuẩn bị (dự phòng, chưa có gì tiêu thụ)

Ghi một bản cho mỗi round, tại thời điểm hết giai đoạn chuẩn bị, trước khi combat bắt đầu.

| Trường | Loại | Quy tắc |
|---|---|---|
| `game_id`, `stage_round`, `timestamp_s` | như Tầng 1 | khóa liên kết |
| `gold` | số nguyên hoặc `null` | vàng hiện có |
| `level` | số nguyên hoặc `null` | cấp |
| `xp` | chuỗi hoặc `null` | ví dụ `"12/40"` |
| `hp` | số nguyên hoặc `null` | HP người chơi |
| `streak` | số nguyên hoặc `null` | chuỗi thắng/thua, ghi dấu (+ thắng, - thua) |
| `board` | danh sách | như 2.2 (api, star, items) |
| `bench` | danh sách | như 2.2, cùng cấu trúc |
| `item_bench` | danh sách apiName hoặc `null` | item trên thanh item |
| `shop` | danh sách apiName hoặc `null` | 5 tướng trong cửa hàng, theo thứ tự ô |
| `other_players_hp` | object | HP từng người nếu có, ghi tên hiển thị kèm `null` nếu không đọc được |
| `evidence` | `[giây_bắt_đầu, giây_kết_thúc]` | đoạn đọc |

Ghi chú: ở tầng này, `hp` và `board` cần độ phân giải đủ để nhận diện tướng; nếu không, ghi `null` cho trường đó.

## 4. Tầng 3: sự kiện hành động và phần thưởng (dự phòng, chưa có gì tiêu thụ)

Mỗi sự kiện là một dòng JSON với các trường chung:
`game_id`, `stage_round`, `timestamp_s`, `type`, `payload`, `evidence`.

Loại sự kiện, lấy từ các lớp action của engine (`tft_goat/env/actions.py`) để tên khớp:

- `BUY`: payload `{"slot": int, "api": apiName|null, "cost": int|null}`
- `SELL`: payload `{"source": "board"|"bench", "api": apiName|null, "star": int|null}`
- `REROLL`: payload `{"cost": int|null}`
- `BUY_XP`: payload `{"cost": int|null, "level_after": int|null}`
- `MOVE` (field/bench): payload `{"api": apiName|null, "from": "bench"|"board", "to": "bench"|"board"}`
- `EQUIP`: payload `{"item_api": apiName|null, "target_api": apiName|null}`
- `PICK_AUGMENT`: payload `{"offered": [apiName|null, ...], "picked": apiName|null}`. `offered` là ba lựa chọn theo thứ tự hiển thị.
- `REROLL_AUGMENT`: payload `{"offered_before": [...], "offered_after": [...]}`
- `REWARD_CAROUSEL`: payload `{"offered": [apiName|null, ...], "picked": apiName|null}`
- `REWARD_PVE`: payload `{"kind": "item"|"gold"|"orb"|"other", "value": apiName|int|null}`
- `SET18_MECHANIC`: payload `{"name": chuỗi, "detail": chuỗi}`, dùng cho cơ chế đặc thù của Set 18 chưa có loại riêng.

**Quy tắc**: ghi sự kiện khi thấy thao tác rõ, không suy diễn từ kết quả. Nếu không rõ, ghi `null` trong payload, không ghi loại khác để thay thế.

## 5. Chụp hiệu chuẩn (calibration captures)

Mỗi khi streamer mở bảng chỉ số của một tướng hoặc tooltip của một trait, ghi lại:

- `kind`: `"unit_stat_panel"` hoặc `"trait_tooltip"`
- `timestamp_s`, `game_id`, `stage_round`
- `unit_api` (nếu là bảng tướng), `unit_star`
- `active_traits`: danh sách trait đang kích hoạt kèm mức (ví dụ `{"Defender": 2, ...}`)
- `items` (apiName) của tướng đó
- `numbers`: các số đọc được, ghi tên chỉ số đúng như hiển thị, ví dụ `{"Armor": 40, "Max HP": 1100, "AP": 100}`
- `evidence`: đoạn thời gian

Bản ghi này dùng để giải quyết các giả định còn mở (xem `docs/model-plan.md`, mục 11.17): Defender 25 là phần thêm hay tổng; Brawler phần trăm áp lên gì; Spellweaver là tổng hay cộng thêm. Mỗi lần chụp chỉ ghi một tướng với một tổ hợp trait và item cố định. **Đừng gộp** các tổ hợp khác nhau.

## 6. Quy tắc áp dụng cho mọi trường

1. **Đánh dấu nguồn của từng giá trị**: `observed` (thấy rõ trên màn hình), `inferred` (suy từ thông tin khác), hoặc `unseen` (không thấy). Ghi trạng thái trong một khóa riêng `field_status` ở cấp bản ghi, ví dụ `{"a.units[0].api": "observed", "result.winner": "inferred"}`. **Không** bọc giá trị thành object: validator yêu cầu `winner` là 0, 1 hoặc `null`, và `api` là chuỗi. Nếu là `inferred`, ghi lý do vào `field_notes` cùng khóa đó.
2. **Không đoán**. Không đọc được thì `null`, không dùng `0`, không dùng danh sách rỗng để thay cho "không biết". Danh sách rỗng chỉ dùng khi đã thấy rõ là không có.
3. **Mọi bản ghi có `evidence`**: một đoạn thời gian `[bắt_đầu, kết_thúc]` trong VOD.
4. **Tên copy nguyên văn từ client tiếng Anh**. Không tự dịch, không tự chuẩn hóa. Tên hiển thị đi vào trường `*_display`.
5. **Không tự chọn apiName** khi tên trùng. Ví dụ `Krug` có hai bản (`DA_Krug18` cost 3 và `TFT_Krug` cost 1). Nếu thấy tên trùng, ghi thêm `cost` và `traits` để phân biệt; nếu không phân biệt được thì `api: null` và ghi tên hiển thị.
6. **Item cần đúng bản**: nếu client hiển thị một tên item có nhiều apiName, ghi tên hiển thị và để `items: null` cho đến khi xác định được.

## 7. Lấy mẫu

- **Chỉ** ranked Set 18 tiêu chuẩn. **Loại**: PBE, Double Up, mọi chế độ khác, vòng PvE (chỉ loại PvE khi xác nhận được đó là vòng PvE).
- Lấy **mọi trận PvP của mỗi ván**, không chỉ các đoạn nổi bật, và giữ cả các trận thua.
- Ưu tiên **lấy trọn ván**, và trải đều trên nhiều streamer, tránh một người chiếm phần lớn dữ liệu.
- Mục tiêu tối thiểu: khoảng **137 ván** (để ước lượng chênh lệch ±0,10) và khoảng **545 ván** (để ±0,05). Đây là số ván, không phải số trận combat. Mỗi trận combat một bản ghi, nhiều trận cùng ván được chấm theo cụm ván.
- Ghi `game_id` cố định để cụm không bị vỡ.

## 8. Chấp nhận

1. Mọi bản ghi phải qua `check_record` (không lỗi) với nhãn `real`. Bản ghi không qua thì sửa, không bỏ qua.
2. Lấy ngẫu nhiên khoảng 10% bản ghi và để hai agent cùng gán nhãn độc lập. Báo tỷ lệ đồng ý theo từng trường (`api`, `star`, `items`, `pos`, `winner`).
3. Chưa có tỷ lệ đồng ý trên ngưỡng đã thống nhất thì không coi là dữ liệu sạch. Ngưỡng do người nhận quyết định trước khi bắt đầu.

## 9. Bàn giao

- File JSONL, một bản ghi trên mỗi dòng, mã hóa UTF-8.
- Tên file: `YYYYMMDD-<streamer>-<game_id>.jsonl`.
- Mỗi file một streamer. Không trộn label.
- Ghi kèm một file `README` ngắn: danh sách `game_id`, số bản ghi qua và không qua validator, số trận bị loại và lý do.
- Để tầng 2 và 3 ở file riêng (`*_snapshots.jsonl`, `*_events.jsonl`). Không trộn vào file trận.

## 10. Việc chưa có

- Quy ước tọa độ hàng/cột (mục 2.4) chưa xác nhận. Đến khi có, mọi `pos` là `null`.
- Chưa biết client ghi apiName nào cho item Set 18 (`DA_*` hay `TFT_Item_*`). Ghi cả hai dạng nếu thấy, và ghi `items_display`.
- Chưa có thứ tự hiển thị augment chắc chắn; ghi theo thứ tự xuất hiện.
- Các trường tầng 2 và 3 chưa có gì đọc. Chúng là dự phòng.
