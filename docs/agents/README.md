# Quy tắc làm việc chung cho các agent

Bộ tài liệu này áp dụng cho mọi agent (Claude, Codex, hoặc người) làm việc trên repo `defu2005/TFT`. Mục tiêu: nhiều agent chạy song song mà không ghi đè công việc của nhau, không phá nhánh, và luôn bàn giao được cho người sau.

## Đọc theo thứ tự

1. [`ownership.md`](ownership.md): ai/cái gì được sở hữu, file nào là "vùng nóng".
2. [`branching.md`](branching.md): đặt tên nhánh, tách từ đâu, khi nào rebase, thứ tự merge.
3. [`claims.md`](claims.md): cách khai báo bắt đầu làm việc trên một vùng.
   Bảng claim nằm trên `master` và chỉ người điều phối ghi. Agent đọc bằng `git show origin/master:docs/agents/claims.md`.
4. [`conflict-protocol.md`](conflict-protocol.md): làm gì khi xung đột hoặc khi hai agent cùng sửa một file.
5. [`handoff.md`](handoff.md): mẫu bàn giao và quy tắc tiếp quản.
6. [`verification.md`](verification.md): lệnh test theo từng vùng và cách ghi kết quả.
7. [`hygiene.md`](hygiene.md): bí mật, file sinh ra, dữ liệu lớn, không commit gì.
8. [`data-contracts.md`](data-contracts.md): dữ liệu nào workstream này cần từ workstream khác, và cách gửi yêu cầu, trả lời qua `requests/` và `responses/`.

## Nguyên tắc cốt lõi

- **Một vùng, một chủ tại một thời điểm.** Chủ được ghi trong `claims.md`.
- **Không sửa vùng của người khác** trừ khi được ghi trong claim hoặc được người điều phối cho phép.
- **Không force-push, không rebase nhánh đã push của người khác, không xóa nhánh của người khác.**
- **Không merge vào `master` khi chưa có người duyệt**, và không tự tạo PR khi chưa được yêu cầu.
- **Mọi thay đổi có bản ghi:** commit message rõ ràng, và handoff khi dừng giữa chừng.
- **Đo trước khi khẳng định.** Ghi phiên bản mã, lệnh chạy, số mẫu và kết quả. Không gọi một con số là "độ chính xác" nếu chưa đối chiếu với nhãn.
- **Khi không chắc, dừng và hỏi.** Tốt hơn là một câu hỏi thay vì một nhánh bị phá.

## Thực trạng cần biết (cập nhật 2026-11-24)

- `master` đã có năm nhánh tích hợp qua PR #1–#4: tài liệu, engine, OCR HUD, mô phỏng `tft-sim/`. Đầu hiện tại: `329f23d`.
- Test trên `master`: 182 Node đạt, `tft-sim` pytest 8 đạt và 1 bỏ qua. `test_hud_ocr.py` cần `TFT_SET18_ART_ZIP` để chạy đủ bộ.
- Roster Set 18 có chủ là `engine` (quyết định 2026-11-24). `data-contracts.md` mục 5 ghi rõ phần còn chưa xác minh.
- Chưa có yêu cầu hay trả lời dữ liệu nào trong `requests/` và `responses/`.
- Mã đường RAM (`probe-ram.py`, `ramSource.js`) vẫn còn trên `master`. Đây là việc của `engine`.

Những thông tin này sẽ lỗi thời. Khi có thay đổi lớn, cập nhật lại mục này.
