# Quyền sở hữu và vùng nóng

## Workstream và thư mục sở hữu

Mỗi workstream có một thư mục chính. Agent của workstream đó là chủ tự nhiên của thư mục.

| Workstream | Thư mục / file chính | Ghi chú |
|---|---|---|
| Engine và coach (lõi) | `src/engine/`, `src/core/`, `src/data/rules.js`, `src/main.js`, `src/app.js` | Vùng nóng, xem bên dưới |
| MCP server | `src/mcp/` | Vùng nóng một phần (`tools.js`) |
| Ingest trạng thái | `src/ingest/` | `standaloneSource.js` là vùng nóng |
| OCR HUD Set 18 | `scripts/hud*.py`, `scripts/hud_*.py`, `scripts/hud-campaign/`, `src/data/set18-hud.json` | Workstream codex |
| Mô phỏng và BC | `tft-sim/` | Workstream fable, không chạm `src/` |
| Tài liệu sản phẩm | `docs/` (trừ `docs/agents/`) | Có thể xung đột khi nhiều agent cùng sửa một tài liệu |
| Quy tắc agent | `docs/agents/`, `CLAUDE.md`, `AGENTS.md` | Chỉ sửa qua người điều phối |

## Vùng nóng

Các file sau đã được sửa bởi nhiều nhánh. **Không được sửa khi có claim khác đang giữ chúng.**

- `src/core/coach.js`
- `src/engine/decide.js`
- `src/engine/reason.js`
- `src/ingest/standaloneSource.js` và `standaloneSource.test.js`
- `src/main.js`
- `src/mcp/tools.js`

Ngoài ra, `package.json` và `package-lock.json` là vùng nóng toàn repo. Chỉ thêm dependency khi có claim rõ ràng, và ghi lý do trong commit.

## Quy tắc chung

- Chỉ sửa file trong workstream của mình. Nếu cần sửa file thuộc workstream khác, hỏi người sở hữu hoặc người điều phối trước.
- Thay đổi API dùng chung (ví dụ hàm trong `engine/`, schema log JSONL, tên tool MCP) phải ghi trong commit và cập nhật `docs/architecture.md`.
- Không đổi tên, không xóa, không di chuyển file của workstream khác.
- Tài liệu nằm trong `docs/` được coi là thuộc workstream tạo ra nó. Không viết lại tài liệu của người khác, chỉ thêm ghi chú hoặc mở việc mới.
