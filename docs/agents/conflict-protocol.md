# Xử lý xung đột

## Loại xung đột và cách xử lý

### 1. Xung đột khi rebase hoặc merge

1. Dừng. Không chọn "ours" hoặc "theirs" mà không đọc.
2. Đọc cả hai phía. Xác định mỗi bên muốn đạt điều gì.
3. Nếu hai thay đổi bổ trợ nhau: gộp cả hai.
4. Nếu hai thay đổi mâu thuẫn về hành vi: không tự quyết. Ghi lại xung đột trong handoff và hỏi người điều phối.
5. Sau khi giải quyết, chạy test của vùng bị ảnh hưởng (xem `verification.md`) và ghi kết quả vào commit message.

### 2. Hai agent sửa cùng vùng nóng

- Nếu có claim, claim đầu tiên thắng. Agent sau dừng và thông báo.
- Nếu không có claim: người sửa sau phải rebase lên commit của người trước, đọc diff, và không ghi đè thay đổi đã có. Nếu thay đổi không tương thích, ghi vào handoff và hỏi người điều phối.

### 3. Thay đổi API dùng chung

Khi đổi chữ ký hàm, schema JSONL, hoặc tên tool MCP:

- Liệt kê tất cả nơi gọi trong repo (`grep -rn`).
- Cập nhật cả nơi gọi trong cùng commit, hoặc tách thành hai commit: thêm API mới, rồi chuyển caller, rồi xóa API cũ.
- Cập nhật `docs/architecture.md` nếu là API công khai (MCP tool, log schema).

### 4. Sai khác về số liệu hoặc kết quả

Khi hai nhánh báo cáo số khác nhau cho cùng một thứ (ví dụ số tướng theo cost, kết quả kiểm định):

- Không chọn số "đẹp" hơn.
- Ghi cả hai, nguồn của mỗi số, và phiên bản dữ liệu.
- Đưa vào mục "chưa giải quyết" trong handoff, không tự kết luận.

## Khi nào dừng và hỏi

Dừng và hỏi người điều phối khi:

- Xung đột đụng vào `src/core/coach.js`, `src/engine/decide.js` hoặc `src/engine/reason.js` và bạn không chắc hành vi nào đúng.
- Cần xóa hoặc đổi tên file của workstream khác.
- Test đỏ sau merge mà nguyên nhân nằm ở nhánh khác.
- Có thay đổi bí mật, credential, hoặc đường dẫn tuyệt đối trong repo.

## Khi test đỏ sau merge

1. Xác định commit gây đỏ bằng `git bisect` hoặc đọc log.
2. Nếu lỗi nằm trong thay đổi của mình, sửa ngay trên nhánh của mình.
3. Nếu lỗi nằm trong thay đổi của người khác, không tự sửa. Ghi lại test nào đỏ, commit nào, và thông báo.
4. Không tắt, bỏ qua hoặc xóa test để có màu xanh.
