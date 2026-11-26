# 9. Làm việc với agent

## Ai làm gì

| Agent | Việc | Đọc trước |
|---|---|---|
| Agent Claude (phiên trò chuyện) | Engine sim, kiểm công cụ, tài liệu, phân tích | `AGENTS.md`, `docs/progress/STATUS.md` |
| Agent Codex/Cursor, workstream `sim` (vai DT, C, R, E) | Thu dữ liệu, huấn luyện, kiểm định theo seed đã đóng | `docs/handoff/cloud-agents.md`, `cloud-agent-prompts.md` |
| Agent Codex/Cursor, thu VOD (slot P1–P10, V1) | Thu bản ghi trận từ VOD Twitch/YouTube | `docs/handoff/vod-collection.md`, `vod-collection-prompt.md` |
| Tác giả `tft_goat` | Trả lời câu hỏi về engine | `docs/agents/requests/` |

Người dùng quyết định cuối. Agent không tự chọn hướng khi người dùng đã yêu cầu chọn.

## Hai luồng agent, đừng nhầm

**Luồng sim (cloud-agents.md):** mỗi phiên là một vai, chạy trên máy riêng, **không chia sẻ file**. Thu dữ liệu và huấn luyện gộp trong một phiên (vai DT). Chỉ checkpoint nhỏ và JSON đi giữa các phiên qua git.
- Nhánh gốc: `claude/claude-fable-5-2-awwmf5`. Nhánh mỗi phiên: `codex/sim-dt`, `codex/sim-c`, `cursor/sim-r`, `codex/sim-e` (E tạo sau khi DT đã push).
- Không commit `.npz`. Checkpoint `.pt` dưới 1 MB được commit vào `results/checkpoints/`.
- Không dùng seed đã đóng. Không bịa số.

**Luồng VOD (vod-collection.md):** lô `2026-11-25-set18-vod`, mục tiêu ≥1000 ván.
- Manifest `data/vod_manifest_20261125.json`: chỉ người điều phối commit. Agent không sửa.
- Mỗi streamer ở đúng một slot primary. Dòng `REPLACE` là chưa có VOD thật: ghi `blocked`, không đoán URL.
- Nhận slot bằng `CLAIM.json` (có `slot`, `agent`, `claimed_at`). Slot đã có `CLAIM.json` của người khác thì dừng.
- Vai `primary` ghi dữ liệu thô. `second_label` ghi vào V1 để đối chiếu. `hud_processed` không được ghi gì.
- Chỉ Twitch (`twitch.tv/videos/<số>`) và YouTube (`watch?v=` hoặc `youtu.be/`). URL khác bị `bad_source_url`.

## Nhánh và push

- Chỉ đẩy lên nhánh được giao khi tạo phiên. Không tạo PR nếu người dùng không yêu cầu. Không force-push.
- Khi push bị từ chối vì commit của người khác: `git fetch`, `git merge --no-edit FETCH_HEAD`, rồi push lại. Không rebase.

## Quy tắc cuối phiên (`AGENTS.md` gốc)

1. Cập nhật `docs/progress/STATUS.md` (ghi đè, không quá một màn hình).
2. Tạo file phiên mới trong `docs/progress/sessions/` (không sửa file cũ).
3. Commit theo cụm. Không ghi hash commit vào STATUS (sẽ lỗi thời).
4. Push lên nhánh làm việc.

## Quy tắc khi báo cáo

- Không nói "đã hỏi advisor" nếu chưa gọi thật.
- Không nói "đạt" nếu cổng chưa đạt.
- Ghi rõ số liệu là mô phỏng hay trận thật.

## Chưa có

- Chưa có prompt nào cho thu live. Nguồn live chưa chốt.
- Chưa có khóa API Riot. Phase 2 của kế hoạch Set 18 cần khóa này, do người dùng cấp.
