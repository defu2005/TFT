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
| `gold`, `level` | thật khi có file HUD; **ước lượng** khi không có | HUD, hoặc công thức trong `standaloneSource.js` |
| `stage` | **ước lượng** từ thời gian trận | `computeStage` |
| `board` (`championName`, `starLevel`) | thật | `boardPieces` trong snapshot |
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
- Lên level và roll theo `xp` và `round`: **chờ số XP từ người dùng**.
- Chọn line tự động từ dữ liệu set: **chưa có dữ liệu set hiện tại**.

## 6. Lưu ý

- Mọi logic mới chỉ được kiểm thử trên trạng thái tổng hợp. Hành vi trên game thật không đổi cho đến khi phiên ingest gửi các trường này.
- Không dùng số liệu game từ trí nhớ. Bench size, hoàn tiền khi bán và XP mỗi lần mua phải lấy từ dữ liệu repo hoặc từ người dùng.
- Tài liệu này chỉ có trên nhánh `claude/dazzling-feynman-g7a0b9`. Phiên ingest cần fetch nhánh này để đọc.
