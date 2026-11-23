# Bàn giao

Mỗi khi dừng giữa chừng, đổi người, hoặc hoàn thành một mốc, phải viết bàn giao. Người tiếp quản không có bộ nhớ của bạn, chỉ có repo và tài liệu này.

## Vị trí

- Bàn giao của một nhánh nằm ở `HANDOFF.md` ở gốc nhánh, hoặc ở `docs/handoffs/<tên-nhánh>.md` nếu nhánh có nhiều workstream.
- Mỗi nhánh có một bàn giao đang hiệu lực. Ghi đè bản cũ bằng bản mới, nhưng giữ lịch sử trong git.

## Mẫu

```markdown
# Bàn giao: <tên workstream>

- Nhánh: `<tên-nhánh>`
- Commit gần nhất: `<hash>`
- Agent / người: <ai>
- Ngày: <YYYY-MM-DD>
- Trạng thái: đang chạy / tạm dừng / xong mốc / bị chặn

## Mục tiêu

Một đến ba câu. Mục tiêu đo được là gì.

## Đã xong

- Việc 1, kèm commit hoặc kết quả.

## Kết quả đo (nếu có)

| Thứ đo | Phiên bản | Lệnh | Số mẫu | Kết quả | Ghi chú |
|---|---|---|---|---|---|

Ghi rõ đây là kết quả trên dữ liệu gì (tổng hợp, replay, live), và đã đối chiếu với nhãn chưa.

## Đang chạy

- Tiến trình, PID, đường dẫn log, và cách kiểm tra còn sống.

## Chưa xong / bị chặn

- Việc còn lại, theo thứ tự ưu tiên.
- Điều gì đang chặn và ai có thể gỡ.

## Quyết định đã chốt

- Quyết định và lý do. Người sau không được đảo lại mà không có lý do mới.

## Rủi ro và giả định

- Giả định nào chưa được kiểm chứng.

## Cách tiếp tục

1. Lệnh đầu tiên cần chạy để kiểm tra trạng thái.
2. Lệnh test.
3. File nào cần đọc trước.
```

## Quy tắc tiếp quản

1. Đọc bàn giao, rồi `git log` và `git status` của nhánh.
2. Kiểm tra tiến trình đang chạy theo mục "Đang chạy". Không khởi động trùng nếu tiến trình cũ còn sống.
3. Kiểm tra claim trong `claims.md`.
4. Chạy test trước khi sửa gì.
5. Nếu bàn giao mâu thuẫn với code, tin code và ghi lại sự khác biệt vào bàn giao.

## Không làm

- Không viết bàn giao chỉ bằng "xem commit". Người sau cần biết vì sao và đã thử gì.
- Không ghi "đã kiểm thử" nếu không ghi lệnh và kết quả.
- Không ghi một tỷ lệ là "độ chính xác" nếu chưa đối chiếu với nhãn tay.
