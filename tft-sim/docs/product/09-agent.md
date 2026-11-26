# 9. Làm việc với agent

## Ai làm gì

| Agent | Việc | Đầu vào |
|---|---|---|
| Agent Claude (phiên này) | Engine sim, kiểm công cụ, tài liệu, phân tích | Repo, `docs/` |
| Agent thu dữ liệu (Codex, Cursor) | Thu VOD streamer Twitch/YouTube theo prompt | `docs/handoff/vod-collection-prompt.md` |
| Tác giả `tft_goat` | Trả lời câu hỏi về engine | `docs/agents/requests/` |

Người dùng là người quyết định cuối. Agent không tự chọn hướng khi người dùng đã yêu cầu chọn.

## Bàn giao

Mỗi việc giao cho agent có một file handoff. Trạng thái: `pending`, `working`, `done`, `blocked`, `stale`. Agent phải cập nhật trạng thái khi làm xong. Trạng thái không hợp lệ bị cổng từ chối.

| File | Dùng cho |
|---|---|
| `docs/handoff/cloud-agent-prompts.md` | Prompt cho agent đám mây |
| `docs/handoff/cloud-agents.md` | Phân công và trạng thái agent |
| `docs/handoff/set18-sources.md` | Nguồn dữ liệu Set 18 |
| `docs/handoff/vod-collection-prompt.md` | Prompt thu VOD |
| `docs/handoff/vod-collection.md` | Trạng thái thu VOD |

Mục tiêu là hai agent không thu trùng một video. Cách phân slot hiện tại xem `vod-collection.md` (chưa xác minh lại trong bộ tài liệu này).

## Nhánh

- Mọi agent làm việc trên một nhánh riêng, không đẩy lên nhánh khác khi chưa được phép.
- Không tạo pull request nếu người dùng không yêu cầu.

## Quy tắc cuối phiên (từ `AGENTS.md` gốc)

1. Cập nhật `docs/progress/STATUS.md` (ghi đè, không quá một màn hình).
2. Tạo file phiên mới trong `docs/progress/sessions/` (không sửa file cũ).
3. Commit theo cụm.
4. Push lên nhánh làm việc.

## Quy tắc khi báo cáo agent

- Không nói "đã hỏi advisor" nếu chưa gọi thật.
- Không nói "đã đạt" nếu cổng chưa đạt.
- Ghi rõ số liệu là mô phỏng hay trận thật.

## Prompt nào đang chờ

- Prompt thu VOD đã được viết lại để chỉ dùng Twitch và YouTube.
- Chưa có prompt nào cho việc thu live. Nguồn live chưa chốt.
