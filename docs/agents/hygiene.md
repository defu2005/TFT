# Vệ sinh repo

## Không bao giờ commit

- Bí mật: `.env`, file credential, token, API key, cookie, URL đã ký.
- Dữ liệu cá nhân: Riot ID, tên người chơi, email. Thư mục `captures/` đã nằm trong `.gitignore`, giữ như vậy.
- File sinh ra: log lớn, cache, `node_modules/`, `__pycache__/`, báo cáo chạy dài.
- Video và media: MP4, HLS, ảnh HUD hàng loạt. Giữ trong `scratch/` hoặc `/tmp`, không trong repo.
- Đường dẫn tuyệt đối máy cụ thể (`/workspace/...`, `/root/...`) trong code hoặc tài liệu. Dùng đường dẫn tương đối hoặc biến môi trường.

**Ngoại lệ:** `HANDOFF.md` và `docs/handoffs/*` có thể nêu đường dẫn scratch (`/workspace/scratch/...`, `/tmp/...`) để chỉ nơi một tiến trình đang chạy hoặc nơi lưu kết quả tạm. Chỉ dùng cho vị trí tạm, không dùng cho code, cấu hình hoặc đường dẫn cài đặt.

Nếu vô tình stage file thuộc danh sách trên, `git reset` file đó trước khi commit. Không `git add -A` khi chưa xem `git status`.

## Commit file dữ liệu

- Dữ liệu nhỏ, cần cho test (fixture): được commit, nhưng phải ghi rõ là tổng hợp hay thật.
- Dữ liệu thật lớn: không commit. Ghi checksum và cách lấy lại trong tài liệu.
- Mỗi nguồn dữ liệu thật phải có ghi chú về giấy phép hoặc điều khoản sử dụng (xem `docs/data-sources.md`).

## Tài liệu

- Tài liệu sống trong `docs/` hoặc trong thư mục workstream. Không tạo file ghi chú tạm trong gốc repo.
- Không dán log dài vào tài liệu. Đưa vào file riêng và link.
- Không copy nội dung từ nguồn bên ngoài mà không ghi nguồn và điều khoản.

## Công cụ và môi trường

- Không cài dependency toàn cục rồi giả định nó có trong repo. Khai báo trong `package.json` hoặc tài liệu cài đặt.
- Không phụ thuộc vào trạng thái máy cụ thể (cổng, đường dẫn, phiên bản OS). Ghi cách tái tạo.

## Khi phát hiện vi phạm

- Đã push mà có bí mật: báo người điều phối ngay. Không tự xóa lịch sử. Người điều phối quyết định cách xử lý và xoay khóa.
- Đã commit file lớn hoặc bí mật nhưng **chưa push**: sửa bằng `git commit --amend` (nếu là commit cuối) hoặc `git reset --soft HEAD~1` rồi commit lại. Không dùng cách tạo commit mới để xóa, vì blob cũ vẫn nằm trong lịch sử và sẽ bị đẩy lên cùng các commit sau.
- Đã push: xem mục trên, báo người điều phối. Không tự viết lại lịch sử nhánh đã push.
