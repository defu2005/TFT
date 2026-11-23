# Kiến trúc tft-coach

Trạng thái: đã có code chạy được trên dữ liệu replay tổng hợp. Chưa kiểm thử với dữ liệu live.

## 1. Phạm vi

App chạy local trên máy người dùng. Mỗi vòng lặp, app đọc trạng thái trận, tính quyết định tốt nhất theo engine, ghi lại quyết định kèm lý do, và cung cấp các khả năng đó cho agent qua MCP. Đọc thông tin realtime trận đấu bằng live client api.

Đã xác minh giấy phép bên thứ 3 từ Riot.

## 2. Thành phần

```
src/
  app.js              cấu hình và lắp ráp (createApp)
  main.js             entry CLI: chạy vòng lặp, in dòng khi quyết định đổi (stderr)
  core/coach.js       vòng lặp, cache trạng thái và quyết định, gọi logger
  engine/decide.js    chấm điểm các hành động; ghi trace nếu được yêu cầu
  engine/reason.js    lý do bằng tiếng Việt, ứng viên, yếu tố
  engine/odds.js      xác suất gặp tướng, lãi theo vàng
  engine/autoline.js  line tự động từ tướng trên bàn và tộc (tắt mặc định, bật bằng TFT_AUTO_LINE=1)
  data/profile.js     hồ sơ mặc định (bảng odds, pool, số tướng theo cost, maxCost) lấy từ rules.js
  data/profileFile.js đọc file hồ sơ set có bản vá chồng lên nhau (tắt mặc định, TFT_PROFILE_FILE)
  data/profiles/      hồ sơ candidate (ví dụ set18.candidate.json), chỉ dùng khi được chọn bằng TFT_PROFILE_FILE

Định dạng file hồ sơ (`TFT_PROFILE_FILE`):
```json
{
  "set": "18",
  "unmodelled": ["ghi chú tính năng set chưa mô hình"],
  "base": { "maxCost": 5, "shopOdds": [null, [1,0,0,0,0], ...], "poolCopies": [0,30,25,18,10,9], "champsPerCost": [0,13,13,13,12,8] },
  "patches": [
    { "version": "16.20", "notes": "...", "shopOdds": { "8": [0.15,0.20,0.32,0.30,0.03] } }
  ]
}
```
`base` có thể bỏ trống; khi đó bảng mặc định của `rules.js` được dùng và được ghi vào caveat. Mỗi hàng odds có `maxCost` phần tử và tổng bằng 1. Bản vá chỉ liệt kê hàng đổi; mọi bản vá có version ≤ `TFT_PATCH` được áp dụng theo thứ tự số. Khóa không rõ làm app báo lỗi. Chỉ `shopOdds`, `poolCopies`, `champsPerCost` và `maxCost` được đọc từ file; các phần khác vẫn là hằng trong code.
  ingest/sources.js   nguồn trạng thái: live hoặc replay
  ingest/liveClient.js đọc Live Client Data tại 127.0.0.1:2999; toState liệt kê trường thiếu
  ingest/capture.js   ghi payload thô ra captures/ (gitignored, có Riot ID); không ra quyết định
  log/decisionLog.js  JSONL, chỉ ghi khi trạng thái hoặc quyết định đổi
  mcp/server.js       MCP qua stdio (stdout chỉ dành cho giao thức)
  mcp/tools.js        các tool MCP
src/data/rules.js     bảng tỉ lệ, số bản, mốc level (chưa xác minh cho Set 18)
src/data/fixtures/    replay tổng hợp, có đánh dấu synthetic
```

## 3. Luồng dữ liệu

1. `coach.tick()` đọc nguồn (live hoặc replay), có timeout 150 ms.
2. `decide(state, out, trace)` chấm điểm và đưa từng ứng viên vào `trace`.
3. `explain(state, out, trace)` tạo lý do một dòng và danh sách ứng viên.
4. Cache được cập nhật. Logger ghi một dòng JSONL nếu `stateHash` hoặc quyết định khác dòng trước.
5. Các tool MCP chỉ đọc cache. Không tool nào gọi nguồn.

Vòng lặp chạy mỗi 250 ms. Một tick không chạy chồng lên tick trước.

## 4. Bản ghi log

Mỗi dòng JSONL có:

- `schema` (hiện là 2), `ts`, `source` (`engine`), `sourceKind` (`live` hoặc `replay`), `latencyMs`
- `stateHash`, `known` (có shop không, có target không), `state`
- `decision`: `action` (`hold`, `buy`, `xp`, `roll`, `sell`), `slot`, `bench` (ô bench khi bán, -1 nếu không), `score`, `hit`
- `reason`: `text`, `factors`, `caveats`, `candidates` (từng hành động với điểm số và số liệu)

Schema chưa phải chuẩn công khai, có thể thay đổi.

## 5. Tool MCP

| Tool | Việc làm |
| --- | --- |
| `tft_status` | Nguồn, lỗi gần nhất, số lần đọc, trạng thái cache |
| `tft_current_decision` | Quyết định mới nhất kèm lý do và ứng viên |
| `tft_evaluate_state` | Chấm điểm một trạng thái người dùng cung cấp, không ghi log |
| `tft_hit_chance` | Xác suất gặp tướng trong shop |
| `tft_interest` | Lãi theo số vàng |
| `tft_rules` | Bảng luật và tóm tắt Set 17 |
| `tft_recent_decisions` | Các dòng log gần nhất |
| `tft_set_target` | Đặt tướng đang nhắm tới, hoặc xóa |
| `tft_set_line` | Đặt priority cho một tướng trong shop (đưa vào line), hoặc bỏ |

Đăng ký: `.mcp.json` ở gốc repo. Agent khởi chạy `node src/mcp/server.js`.

## 6. Cấu hình

| Biến | Mặc định | Ý nghĩa |
| --- | --- | --- |
| `TFT_SOURCE` | `live` | `live`, `replay` (state tổng hợp) hoặc `capture` (payload thật đã ghi) |
| `TFT_CAPTURE` | (bắt buộc khi `capture`) | file JSONL từ `npm run capture` |
| `TFT_CAPTURE_POLL_MS` | `1000` | chu kỳ đọc khi ghi capture |
| `TFT_REPLAY` | fixture tổng hợp | đường dẫn fixture replay |
| `TFT_LOG` | `logs/decisions.jsonl` | đường dẫn log |
| `TFT_INTERVAL_MS` | `250` | chu kỳ vòng lặp |
| `TFT_AUTO_LINE` | `0` | `1` bật line tự động từ bàn và tộc; cần `TFT_SET_FILE` |
| `TFT_SET_FILE` | (trống) | file dữ liệu set (cùng cấu trúc `src/data/set17.json`) cho line tự động |
| `TFT_PROFILE_FILE` | (trống) | file hồ sơ set (bảng odds, pool, số tướng theo cost, `maxCost`, danh sách bản vá chồng lên nhau). Trống thì dùng `rules.js` |
| `TFT_PATCH` | (trống, cần `TFT_PROFILE_FILE`) | phiên bản bản vá để áp dụng từ file hồ sơ; trống thì lấy bản mới nhất (so số theo thứ tự, 16.9 trước 16.20) |
| `TFT_RULES` | (trống) | danh sách tên, cách nhau bằng dấu phẩy, bật quy tắc U9: `keepInterest`, `earlyLevel`, `guideLevels`. Tên lạ làm app báo lỗi. `tft_evaluate_state` không dùng quy tắc này |

Lưu ý: `TFT_PATCH` phải dùng cùng hệ số với file hồ sơ. Ví dụ file candidate có bản `16.20`; đặt `TFT_PATCH=18.7` sẽ áp dụng bản `16.20` vì 18.7 lớn hơn 16.20 theo so số, và kết quả sẽ không phải của Riot 18.7.


