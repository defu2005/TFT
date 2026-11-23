# Quy tắc nhánh

## Đặt tên

- Nhánh agent: `claude/<mô-tả>-<hậu-tố-ngẫu-nhiên>` hoặc `codex/<mô-tả>`.
- Nhánh tài liệu hoặc quy tắc: `docs/<mô-tả>`.
- Mô tả bằng chữ thường, dùng `-`, ngắn gọn, nói rõ workstream. Ví dụ: `codex/hud-realtime-handoff`.
- Không dùng nhánh tên chung chung như `main-work` hoặc `fix`.

## Tách nhánh

- **Luôn tách từ `master` mới nhất.** Chạy `git fetch origin && git checkout -b <nhánh> origin/master` trước khi bắt đầu.
- Nếu nhánh cần một thay đổi chưa có trên master, không tách từ nhánh khác. Hãy yêu cầu merge thay đổi đó vào master trước, hoặc ghi rõ phụ thuộc trong handoff.
- Không tách từ nhánh đã có công việc chưa merge của người khác.

## Commit

- Mỗi commit làm một việc. Message tiếng Việt hoặc tiếng Anh, nhất quán trong một nhánh.
- Dòng đầu tối đa khoảng 72 ký tự. Nội dung ghi rõ vì sao, không chỉ là gì.
- Kết thúc commit bằng dòng attribution theo yêu cầu của người dùng.
- Không commit file bí mật, file sinh ra, hay dữ liệu lớn (xem `hygiene.md`).

## Đẩy và đồng bộ

- Đẩy bằng `git push -u origin <nhánh>`. Thử lại tối đa 4 lần khi lỗi mạng.
- Nếu push bị từ chối vì remote có commit mới:
  1. Dừng. Không force-push.
  2. `git fetch origin <nhánh>`, rồi kiểm tra commit lạ là của ai (đọc log).
  3. Nếu là công việc của chính mình ở phiên trước, merge hoặc rebase lên và đẩy lại.
  4. Nếu là của người khác, hỏi người điều phối.
- Không force-push lên nhánh có người khác đang làm, và không force-push lên `master` trong mọi trường hợp.

## Rebase và merge

- Rebase nhánh của mình lên `master` mới nhất **trước khi** yêu cầu merge, và chỉ khi nhánh chưa được người khác dùng làm nền.
- Nhánh đã có người khác tách từ nó thì dùng `merge`, không rebase.
- Xung đột khi rebase: xử lý theo `conflict-protocol.md`.

## Thứ tự merge được khuyến nghị

Đây là thứ tự đề xuất, không phải lệnh. Người điều phối quyết định cuối.

1. Nhánh tài liệu và quy tắc (không chạm `src/`).
2. Nhánh mô phỏng `tft-sim/` (không chạm `src/`, nhưng cần rebase để có commit cấu hình trên master).
3. Nhánh đã rebase lên master có thay đổi `src/` nhỏ nhất.
4. Nhánh còn lại, sau khi giải quyết xung đột trên bảy file vùng nóng.

## Dọn nhánh

- Không xóa nhánh của người khác. Chỉ xóa nhánh mình tạo, và chỉ sau khi đã merge hoặc người điều phối đồng ý.
- Nhánh đã merge: đánh dấu trong handoff, không xóa ngay.
