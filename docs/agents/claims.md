# Khai báo công việc (claim)

Claim cho biết ai đang làm trên vùng nào. Các agent không chia sẻ bộ nhớ và thường chạy trên nhánh riêng hoặc cloud session riêng, nên claim phải nằm ở một nơi mà mọi agent đọc được **trước khi bắt đầu việc**.

## Kênh chung: nhánh `coordination`

- Claim sống trong `docs/agents/claims.md` trên nhánh **`coordination`**. Nhánh này chỉ chứa file đó, không chứa code.
- Nhánh `coordination` **chỉ được merge, không rebase, không force-push**.
- Mỗi agent phải chạy `git fetch origin coordination` và đọc bảng trước khi bắt đầu bất kỳ việc nào, và trước khi sửa vùng nóng.
- Nhánh `coordination` chưa tồn tại trên remote. Việc tạo và đẩy nhánh này cần người dùng cho phép.

## Cách ghi claim

- **Chỉ thêm dòng mới vào cuối bảng.** Không sửa dòng của người khác. Muốn đóng claim, thêm một dòng mới có trạng thái `xong` cho cùng vùng và cùng nhánh, không sửa dòng cũ.
- Mỗi lần ghi là một commit riêng trên `coordination`, đẩy ngay.
- Vì mọi người đều thêm dòng vào cuối bảng, xung đột sẽ xảy ra ở đúng cuối file. Nếu gặp xung đột, giữ cả hai dòng, sắp theo thời gian ghi.

## Bảng

| Ngày | Vùng / file | Nhánh | Agent | Trạng thái |
|---|---|---|---|---|
| 2026-11-23 | (ví dụ) `src/engine/decide.js` | `codex/hud-realtime-handoff` | codex | đang làm |

Dòng trên chỉ là ví dụ, không có hiệu lực. Xóa khi bảng có dòng thật.

## Quy tắc

- Claim vùng nóng là độc quyền. Agent khác không sửa vùng đó cho đến khi có dòng `xong` cho cùng vùng.
- Claim vùng thường chỉ mang tính thông báo, nhưng vẫn ghi để tránh trùng việc.
- Claim quá 7 ngày không có commit mới trên nhánh tương ứng: người điều phối có thể ghi dòng `giải phóng` và lý do.
- Claim không thay thế việc đọc code. Trước khi sửa, luôn `git fetch` và đọc các commit mới trên `master` và nhánh liên quan.
- Hai claim trùng vùng: claim ghi trước thắng. Người ghi sau dừng và ghi dòng `chờ` kèm tên nhánh đang giữ.

## Nếu không đẩy được `coordination`

Nếu agent không đọc hoặc ghi được nhánh `coordination` (thiếu quyền, offline), dừng việc trên vùng nóng. Ghi trong handoff của nhánh mình rằng claim chưa được xác nhận, và hỏi người điều phối.
