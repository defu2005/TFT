# Yêu cầu: commit log OCR theo mẫu từ chiến dịch VOD

dataset: log OCR theo từng mẫu (4 Hz) của các trận trong chiến dịch VOD, đã chạy xong, gồm 26 trận đầy đủ đã kiểm tra ranh giới và các chương còn lại.
fields: mỗi dòng JSON là một mẫu. Tối thiểu gồm `mediaTimeMs`, `frame`, `hudSchema`, `gold`, `level`, `shop` (5 ô: `id`, `cost`, `price`, và cờ chưa xác định), `shopUnknownSlots`, `hudGoldUnknown`, `hudLevelUnknown`, `deadlineMissed`, `captureLatencyMs`, `recognitionLatencyMs`. Mỗi file trận có một dòng đầu (header) gồm: ID VOD, URL nguồn công khai, mùa, patch nếu biết, độ phân giải, phiên bản OCR (commit), mã băm profile dùng, mã băm catalog `set18-hud.json`.
schema: `hudSchema` hiện tại (2). Nếu thay đổi, ghi phiên bản mới vào header.
why: dữ liệu huấn luyện cần nhãn trạng thái theo thời gian. Log theo mẫu là nguồn chính để suy hành động (mua, roll, lên cấp) từ các mẫu liên tiếp, và để làm sạch nhiễu nhãn.
unblocks: bước làm sạch dữ liệu và bước suy hành động. Không bắt đầu được nếu log chỉ nằm trên ổ scratch của máy cloud.
deadline: không có.
status: mở

## Việc cần làm (hud)

1. **Ước tính dung lượng trước** (tổng MB của log nén, theo từng trận). Ghi vào phản hồi.
2. **Định dạng:** JSON Lines nén gzip, `.jsonl.gz`. Không kèm ảnh, không kèm khung hình, không kèm URL media đã ký, không kèm MP4.
3. **Vị trí:** nếu tổng dung lượng vài chục MB trở xuống, commit vào nhánh của `hud` tại `data/hud-logs/`. Nếu lớn hơn, đề xuất nơi lưu bền khác (release asset hoặc kho ngoài) và không commit vào git.
4. **Manifest:** tạo `docs/agents/contracts/hud-logs.md` trên nhánh của `hud`, gồm danh sách file, số mẫu, số mẫu bị bỏ, `sha256` của từng file, phiên bản OCR và commit đã giao.
5. **Phản hồi:** tạo `docs/agents/responses/20261124-user-to-hud-vod-sample-logs.md` trên nhánh của `hud`, ghi `status: nhận` rồi `status: đã giao` kèm `commit:`, `path:`, `schema:`.
6. **Không đưa vào log** bất kỳ thông tin nhận dạng cá nhân nào, và không copy nội dung từ nguồn mà không có ghi chú giấy phép.

## Lưu ý cho bên nhận dữ liệu

- Log của Set 18 là dữ liệu có chủ. Bên tiêu thụ chỉ dùng cho huấn luyện và làm sạch trong phạm vi đã được người dùng phê duyệt.
- Các mẫu phải kèm mùa và patch để lọc về sau.
