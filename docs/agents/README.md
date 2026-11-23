# Quy tắc làm việc chung cho các agent

Bộ tài liệu này áp dụng cho mọi agent (Claude, Codex, hoặc người) làm việc trên repo `defu2005/TFT`. Mục tiêu: nhiều agent chạy song song mà không ghi đè công việc của nhau, không phá nhánh, và luôn bàn giao được cho người sau.

## Đọc theo thứ tự

1. [`ownership.md`](ownership.md): ai/cái gì được sở hữu, file nào là "vùng nóng".
2. [`branching.md`](branching.md): đặt tên nhánh, tách từ đâu, khi nào rebase, thứ tự merge.
3. [`claims.md`](claims.md): cách khai báo bắt đầu làm việc trên một vùng.
4. [`conflict-protocol.md`](conflict-protocol.md): làm gì khi xung đột hoặc khi hai agent cùng sửa một file.
5. [`handoff.md`](handoff.md): mẫu bàn giao và quy tắc tiếp quản.
6. [`verification.md`](verification.md): lệnh test theo từng vùng và cách ghi kết quả.
7. [`hygiene.md`](hygiene.md): bí mật, file sinh ra, dữ liệu lớn, không commit gì.

## Nguyên tắc cốt lõi

- **Một vùng, một chủ tại một thời điểm.** Chủ được ghi trong `claims.md`.
- **Không sửa vùng của người khác** trừ khi được ghi trong claim hoặc được người điều phối cho phép.
- **Không force-push, không rebase nhánh đã push của người khác, không xóa nhánh của người khác.**
- **Không merge vào `master` khi chưa có người duyệt**, và không tự tạo PR khi chưa được yêu cầu.
- **Mọi thay đổi có bản ghi:** commit message rõ ràng, và handoff khi dừng giữa chừng.
- **Đo trước khi khẳng định.** Ghi phiên bản mã, lệnh chạy, số mẫu và kết quả. Không gọi một con số là "độ chính xác" nếu chưa đối chiếu với nhãn.
- **Khi không chắc, dừng và hỏi.** Tốt hơn là một câu hỏi thay vì một nhánh bị phá.

## Thực trạng cần biết (tại thời điểm viết)

- `master` (`f3284c7`) có engine, MCP server, 39 test và replay tổng hợp.
- Ba nhánh chưa merge, mỗi nhánh một workstream:
  - `codex/hud-realtime-handoff`: OCR HUD Set 18 và chiến dịch kiểm thử VOD. Tách từ `3e09f8a`.
  - `claude/dazzling-feynman-g7a0b9`: tài liệu và logic coach. Tách từ `f3284c7`.
  - `claude/claude-fable-5-2-awwmf5`: mô phỏng `tft-sim/`. Tách từ `3e09f8a`.
- Hai nhánh `codex` và `fable` tách từ commit cũ hơn master, thiếu commit cấu hình `f3284c7`. Cần rebase trước khi merge.
- Bảy file trong `src/` bị sửa bởi cả `codex` và `dazzling`. Đây là nguồn xung đột chính. Xem `ownership.md`.

Những thông tin này sẽ lỗi thời. Khi có thay đổi lớn, cập nhật lại mục này.
