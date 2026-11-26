# 10. Nhật ký quyết định

Ghi theo thứ tự thời gian. Mỗi dòng có lý do. Quyết định đã rút lại vẫn được giữ, kèm dòng đính chính.

| Ngày | Quyết định | Lý do | Ai quyết |
|---|---|---|---|
| 2026-11-23 | Snapshot CDragon làm bảng xác minh nội dung | Cần nguồn nội dung đối chiếu được | Người dùng |
| 2026-11-24 | Roster Set 18 do nhánh `engine` sở hữu | Tách trách nhiệm | Người dùng |
| 2026-11-26 | Dùng cấu hình PRIMARY cho dự đoán | Cấu hình tối thiểu có item và augment, không alias | Advisor, theo mục 11 |
| 2026-11-26 | Augment không đổi p dưới bàn cân bằng (0/252) | Kết quả đo | Số liệu |
| 2026-11-26 | Tách 617/731 item không có tác động | Cần biết phần nào của engine thực sự có hiệu lực | Số liệu |
| 2026-11-26 | Đăng ký n=400 cho bàn không item | Đạt 4,08% | Advisor |
| 2026-11-26 | n=400 cho bàn có item **không đạt** (5,03%) | Kết quả đo | Số liệu |
| 2026-11-26 | Chọn n=800 cho bàn có item (đạt 4,02%) | Người dùng yêu cầu chọn giữa hai hướng, để advisor quyết; advisor chọn đăng ký n=800 | Advisor, theo ủy quyền của người dùng |
| 2026-11-26 | Gửi ba câu hỏi `_GENERIC_ITEM` cho tác giả engine | Mâu thuẫn giữa chú thích và đường combat | Agent, chấp nhận khi advisor xác nhận bàn giao |
| 2026-11-26 | Dữ liệu VOD: cổng đỏ, không dùng | Không slot nào đạt | Số liệu |
| 2026-11-26 | Tài liệu tiến độ và quy tắc cuối phiên | Người không chuyên cần đọc được tiến độ | Người dùng |

## Chưa được xác nhận

- **Bàn giao `_GENERIC_ITEM`:** advisor xác nhận bàn giao là chấp nhận được. Người dùng chưa xác nhận đóng hay mở. Mục vẫn để mở.
- **Lệnh /goal "làm hết những gì advisor liệt kê":** đã đặt rồi xóa. Không còn hiệu lực.

## Các đính chính (những điều đã nói sai và đã sửa)

| Nói sai | Sự thật | Sửa ở đâu |
|---|---|---|
| "generic_items luôn 0" | Sai. Khối chung được cộng. | 05 |
| "65/776 item không có hiệu ứng" | Sai phạm vi. Đúng là 617/731 (bỏ 45 twin). | 05 |
| "+0,015 là mô hình vượt giáo viên" | Sai. Đây là kiểm công bằng harness. | 04 |
| Hash commit `4ff53c71` trong STATUS | Sai. Hash được ghi tự động và không khớp HEAD. Đã bỏ. | `progress/STATUS.md` |
| Tên file `tieu-do` | Đổi thành `tien-do` (theo quy ước tiếng Việt không dấu của nhánh). | Chưa làm, ghi để theo dõi |
| "n=400 đạt" cho bàn có item | Sai. Chỉ bàn không item đạt ở n=400. | 07 |

## Việc người dùng đã yêu cầu nhưng chưa xong

- Tên file `tieu-do` chưa đổi (xem ghi chú trên).
