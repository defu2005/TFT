# Trạng thái engine cần gì, có gì, giả định gì

Tài liệu này liệt kê dữ liệu mà bước quyết định cần, dữ liệu hiện có từ nguồn, và hợp đồng giả định giữa phiên ingest và phiên engine. Trạng thái: **nháp**. Mọi giá trị chưa được xác minh trong game đều ghi rõ.

## 1. Dữ liệu cần, theo quyết định

| Nhóm | Trường | Dùng cho |
| --- | --- | --- |
| Kinh tế | `gold`, `level`, `xp`, `xpToNext`, `hp`, `stage`, `round`, `phase`, `streak`, `freeRolls`, `shop` | mua, lên level, roll, giữ lãi, đánh giá rủi ro |
| Quân | `board`, `bench`, `boardCap` | đếm bản, chỗ trống, bán |
| Cạnh tranh | số bản người khác đang giữ (`takenByOthers`) | xác suất gặp tướng |
| Line | tướng, tộc và mốc của set hiện tại | chọn line tự động |
| Trang bị | túi trang bị, trang bị trên tướng, công thức | ghép trang bị (giai đoạn 4) |
| Lựa chọn | augment, carousel, Wisp | chọn lựa (giai đoạn 4) |
| Vị trí | bàn cờ đối thủ có toạ độ | định vị (giai đoạn 5) |
| Bảng luật set hiện tại | odds shop, số bản theo cost, bảng XP, lãi, sát thương người chơi | mọi tính toán kinh tế |

## 2. Dữ liệu đã có

| Trường | Trạng thái | Nguồn |
| --- | --- | --- |
| `hp` | thật | `TFTEoGStats.json` |
| `shop` | thật khi có file HUD | `captures/hud-live.json` |
| `shop[].price` (vàng trả cho ô) | thật khi HUD đọc được; `null` = không đọc được, không bao giờ mua; vắng = bằng `cost` | HUD (nhánh codex `hud-realtime-handoff`, hợp đồng trong `docs/hud-reader.md`); chưa có frame thật |
| `hudGoldUnknown`, `hudLevelUnknown`, `shopUnknownSlots` | cờ: vàng hoặc cấp chưa xác nhận; ô chưa đọc. Vắng = đã biết | HUD; engine: không mua khi thiếu vàng, không xp/roll khi thiếu vàng hoặc cấp (`ec36ab4`) |
| `gold` / `level` là `null` hoặc vắng, không kèm cờ | coi là chưa biết: coach đặt cờ tương ứng; bản ghi giữ giá trị như nguồn gửi (`null` hoặc vắng); quyết định dùng 0 chỉ sau cờ; không roll, xp, mua vì thiếu vàng, không tính xác suất khi thiếu cấp; MCP `normalizeState` gửi 0 kèm cờ | `src/core/coach.js` (`84408db`); MCP làm việc này trong `normalizeState`. Khóa vắng hẳn cũng được coi là chưa biết (`== null`), có cờ. Test: `src/app.test.js` (`omitted gold and level keys`). Nguồn live (`liveClient.js`) và RAM (`ramSource.js`) không gửi khóa vắng: khi thiếu, live gửi vàng 0 và cấp 1, RAM gửi 0 và 1 khi file không có (không có cờ). Các trường đó vẫn vào `missing`, nên caveat "đang dùng giá trị mặc định" xuất hiện, nhưng quyết định chạy trên 0 và 1: cấp 1 cho xác suất giả. Đây là hành vi có sẵn, chưa sửa.
| `gold`, `level` | thật khi có file HUD; **ước lượng** khi không có | HUD, hoặc công thức trong `standaloneSource.js` |
| `stage` | **ước lượng** từ thời gian trận | `computeStage` |
| `board` (`championName`, `starLevel`) | thật | `boardPieces` trong snapshot |
| `setMismatch` (factors của coach, không phải trạng thái) | tính | `unknownIds` trong `src/engine/autoline.js`, khi line tự động bật |
| `traitOverlay` (factors của coach, không phải trạng thái) | cấu hình | `applyTraitOverlay` trong `src/engine/traitOverlay.js`, khi `TFT_TRAIT_OVERLAY` đặt; `{set, verified, applied}`, kèm caveat khi chưa xác minh |
| `factors.gold`, `factors.level` (factors của explain, không phải trạng thái) | tính | `explain` trong `src/engine/reason.js`: `null` khi `hudGoldUnknown` / `hudLevelUnknown`, không phải số đã dùng |
| `factors.shopKnown` (factors) | tính | `explain` và coach: `false` khi có `shopUnknownSlots` |
| `augments` đã chọn | thật, chỉ là lựa chọn đã có | snapshot |
| bàn cờ đối thủ | có trong snapshot nhưng **chưa được chuyển tiếp** | snapshot |
| `copiesOwned` | chỉ tính quân trên sàn, **thiếu bench** | `standaloneSource.js` |
| `poolCopies`, `champsAtCost` | **chưa có nguồn** | không có |
| mục tiêu và line | nhập tay | MCP `tft_set_target`, `tft_set_line` |
| `rules.js`, `set17.json` | `rules.js` vẫn được engine dùng nhưng **chưa xác minh cho Set 18**; `set17.json` là dữ liệu Set 17 | repo |

## 3. Dữ liệu chưa có

Bench, `xp`, `xpToNext`, `round`, `phase`, `streak`, `freeRolls`, túi trang bị, trang bị trên tướng, offer (augment, carousel, Wisp), vị trí, `sellValue`, số bản người khác.

## 4. Hợp đồng giả định

Mọi trường đều tuỳ chọn. Trường thiếu thì hành động liên quan không được chấm điểm, và trace ghi lý do.

```
round, xp, xpToNext, freeRolls, boardCap    số nguyên
phase     "planning" | "combat" | "carousel"
streak    dương = thắng, âm = thua
shop[i].takenByOthers    số bản gốc người khác giữ
board[]   { id, cost, star, items?, x?, y? }
bench[]   độ dài cố định, ô trống = null: { id, cost, star, priority?, items?, sellValue? }
itemBench[]   mã trang bị
offers    { kind: "augment"|"carousel"|"wisp", options: [{ id }], rerolls? } | null
opponents[]   { hp, level, board: [{ id, star, x, y }] }
```

Quy ước:
- `id` của tướng trên bàn, bench và shop phải trùng nhau.
- Số bản gốc: 1, 3, 9 theo sao 1, 2, 3.
- Độ dài bench cố định, engine không giữ hằng số kích thước bench.
- `bench[].priority` là tuỳ chọn; coach áp dụng line lên cả bench như lên shop.
- `sellValue` do phiên ingest cung cấp. Engine không có bảng hoàn tiền.
- Giá trị ước lượng đưa vào `missing`.

## 5. Trạng thái triển khai

- Đếm bản từ `board` và `bench`, trừ `takenByOthers` khỏi số bản còn lại: **đã làm** (log schema vẫn là 1).
- Chặn mua khi bench đầy, hành động bán để nhường chỗ, chỉ số ô bench trong `out`, log schema 2: **đã làm** (chỉ bán để nhường chỗ; bán để lấy lãi cần `phase` và `round`, chưa làm).
- Lượt roll miễn phí (`freeRolls`): **đã làm**; roll chỉ được khuyến nghị khi có mục tiêu.
- Mua món muốn mua trước khi roll, không roll khi mục tiêu đã có trong shop: **đã làm**.
- Lên level và roll theo `xp` và `round`: **chờ số XP từ người dùng**.
- Xác suất trong toàn bộ ngân sách roll (`hitWithin`): **chỉ hiển thị**, chưa dùng trong điểm (U9 mục 4).
- Quy tắc U9 (`keepInterest`, `earlyLevel`, `guideLevels`): **đã làm nhưng tắt mặc định**, bật bằng `TFT_RULES`. `tft_evaluate_state` không dùng chúng.
- Hồ sơ dữ liệu (`profile`): **đã làm nhưng tắt mặc định**. Bảng mặc định lấy từ `rules.js`; `TFT_PROFILE_FILE` + `TFT_PATCH` đổi bảng theo set và bản vá; file candidate Set 18 chưa được xác nhận (U2). Chưa có nguồn nào gửi `set` và `patch` (I8).
- Chọn line tự động từ bàn và tộc: **đã làm, tắt mặc định** (`TFT_AUTO_LINE=1`, `TFT_SET_FILE`). Chưa có tác dụng trong game vì id của set 17 không khớp id live (xem `docs/needs.md`, U3).

## 6. Lưu ý

- Khi bench đầy, engine vẫn khuyến nghị mua tướng hoàn thành sao (không cần chỗ trên bench). Điều này chưa được đối chiếu với client.
- Mọi logic mới chỉ được kiểm thử trên trạng thái tổng hợp. Hành vi trên game thật không đổi cho đến khi phiên ingest gửi các trường này.
- Không dùng số liệu game từ trí nhớ. Bench size, hoàn tiền khi bán và XP mỗi lần mua phải lấy từ dữ liệu repo hoặc từ người dùng.
- Tài liệu này chỉ có trên nhánh `claude/dazzling-feynman-g7a0b9`. Phiên ingest cần fetch nhánh này để đọc.
