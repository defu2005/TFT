# Dự án đang ở đâu? (bản cho người không chuyên) · 26/11/2026

## Dự án này làm gì?

Giúp bạn trả lời: "trong trận này, bên nào có khả năng thắng cao hơn, và nên làm gì tiếp". Hiện tại, phần đang làm là **tính xác suất thắng bằng cách mô phỏng trận đánh** và **thử dạy máy chơi bằng cách bắt chước một luật chơi viết tay**.

## Hiện đang ở đâu?

**Chưa có bằng chứng nào rằng dự đoán đúng trên trận thật.** Mọi con số hiện có đều đến từ mô phỏng, không phải trận đấu thật. Đây là điểm quan trọng nhất.

Điều đã làm được:
- **Mô phỏng trận đánh:** máy tính chạy được hàng trăm trận giả và đo kết quả. Kiểm tra cho thấy kết quả ổn định, không nghiêng về bên nào (chênh lệch dưới 1%).
- **Trang bị và tướng:** phần lớn trang bị trong Set 18 **chưa có tác dụng** trong mô phỏng (617 trên 731 món). Đây là khoảng trống lớn nhất.
- **Phép kiểm tra "dạy máy":** máy bắt chước được luật viết tay, nhưng **chưa giỏi hơn** luật đó.
- **Thu thập dữ liệu:** đã xem 1.026 ván từ video của streamer. Nhưng **chưa ván nào đủ chất lượng** để dùng chấm điểm.

## Có đúng tiến độ không?

Kế hoạch có 6 bước. Hiện:
- Bước 1 (củng cố) và bước 2 (gộp các nhánh làm việc): **xong phần lớn**. Bước 2 đã hoàn tất ngày 24/11.
- Bước 3 (đọc trạng thái trận trực tiếp): **bị chặn**. Chưa chọn được cách đọc dữ liệu trận đang diễn ra.
- Bước 4 (kiểm tra trên dữ liệu thật): **chưa bắt đầu**, vì cần bước 3.
- Bước 5 (nghiên cứu, như hiện tại): đang làm, chỉ trên mô phỏng.
- Bước 6 (đóng gói cho người dùng): chưa bắt đầu.

Nói ngắn: **đang chậm ở khâu có dữ liệu thật**. Phần mô phỏng đã khá chắc, nhưng chưa thể nói là dự đoán đúng.

## Độ khả quan

- **Khả quan:** phần mô phỏng và cách kiểm tra đã chắc. Khi có dữ liệu thật, có thể đo ngay.
- **Đáng lo:** chưa chọn được nguồn dữ liệu trận trực tiếp. Chính sách của Riot cũng đang thay đổi, nên đường đọc bộ nhớ trò chơi có rủi ro. Bạn đã nói sẽ tự phát triển phần này sau.
- **Cửa sổ thời gian:** Set 19 đang thử trên máy chủ thử nghiệm (PBE). Khi Set 19 ra mắt chính thức, việc thu trận Set 18 sẽ khó hơn.

## Cần gì để tiếp tục?

Theo thứ tự ưu tiên:
1. **Chọn nguồn dữ liệu trận trực tiếp.** Cách nào đọc được: vàng, cấp, máu, giai đoạn, cửa hàng. Đây là việc quan trọng nhất.
2. **Một số trận thật đã được ghi lại** (ảnh chụp màn hình hoặc video đủ rõ). Hiện mới có một phần.
3. **Quyết định về dữ liệu video streamer:** dùng lại sau khi sửa lỗi chất lượng, hay bỏ.
4. **Khóa Riot API** (nếu muốn dùng API chính thức cho Set 18).
5. **Ảnh chụp giữa trận** bạn đã hẹn gửi (3–5 ảnh, đã che tên).
6. **Xác nhận** việc dùng số liệu blitz.gg đã lưu trong dự án.

## Đầu ra mong muốn

Một công cụ cho bạn biết: trong một tình huống cụ thể, bên nào có khả năng thắng cao hơn, và độ tin cậy của con số đó. Trước khi nói là "đúng", cần đo trên trận thật ít nhất vài chục ván.
