# Kế hoạch thu thập và làm sạch dữ liệu (phiên bản 2)

Cập nhật: 2026-11-24. Thay thế phiên bản trước. Quy tắc dữ liệu nằm ở `docs/data-rules.md`. File này nói cách chạy.

## 1. Nguyên tắc chi phí

Chi phí token đến từ hai chỗ. Kế hoạch được thiết kế để tránh cả hai.

- **Vòng thu thập không dùng token.** OCR, hàng đợi, khóa, đĩa và ghi log là mã thường. Chạy bằng script, không bằng một phiên agent đang bật. Một lượt agent luôn tốn token theo kích thước ngữ cảnh.
- **Model chỉ đọc phần OCR không chắc.** Mỗi lượt gọi model tốn token theo ảnh. Nên dùng ba lớp: khớp mẫu icon trước (không tốn token), OCR thứ hai, rồi mới đến model.
- **Batch cho việc không cần trả lời ngay.** Message Batches của Claude giảm chi phí khoảng một nửa so với gọi đồng bộ, và không cần ngữ cảnh lớn. Dùng cho đọc dự phòng và gán nhãn.
- **Prompt cố định được cache.** Đặc tả và hướng dẫn đọc ảnh đặt đầu prompt và giữ nguyên, để tái sử dụng cache.

## 2. Model

Quy tắc của skill `claude-api`: mặc định dùng `claude-opus-5-5`, trừ khi người dùng chỉ định khác. Giá theo triệu token (vào / ra):

| Model | ID | Vào | Ra | Dùng cho |
|---|---|---|---|---|
| Opus 5.5 | `claude-opus-5-5` | $4 | $20 | Đọc dự phòng trên ảnh, gán nhãn mù (mặc định) |
| Sonnet 5.5 | `claude-sonnet-5-5` | $2 | $10 | Pipeline làm sạch, kiểm tra không cần thị giác |
| Haiku 5.5 | `claude-haiku-5-5` | $0,10 | $0,50 | Chỉ khi người dùng chọn để giảm chi phí |

Chọn Haiku cho đọc dự phòng sẽ rẻ hơn Opus khoảng 40 lần ở đầu vào. Đây là quyết định của người dùng, không phải của agent. Trước khi chọn, cần đo độ chính xác của Haiku trên lượt audit, vì lỗi nhãn làm sai chính chỉ số đang đo.

## 3. Vai trò

Chỉ hai hoặc ba vai trò. Không mở nhiều lane như phiên bản trước.

1. **Thu thập (script + một phiên Claude).** Script chạy hàng đợi, OCR, khớp mẫu và đọc dự phòng theo batch. Phiên Claude chỉ được đánh thức khi có batch xong hoặc sau ít nhất 20 phút, kiểm tra trần, ghi checkpoint, rồi khởi động lại script. Phiên này không đọc lại toàn bộ log.
2. **Audit (phiên Claude riêng).** Cứ mỗi N trận, lấy mẫu mù, gán nhãn bằng đọc viên không phải đọc viên đang đo. Ghi tỷ lệ sai tự tin theo từng trường.
3. **Codex (`hud`).** Tiếp tục chiến dịch hiện có trong phân vùng streamer riêng. Phối hợp qua file trong repo, không qua tin nhắn trực tiếp.

## 4. Vòng chạy

Vòng chạy là script. Mỗi batch:

1. Kiểm tra trần chi phí, đĩa, và điều kiện dừng (`docs/data-rules.md` mục 6–7).
2. Lấy nguồn từ hàng đợi đã claim trong `docs/agents/sources/`.
3. Chạy OCR, khớp mẫu icon, rồi đọc dự phòng cho khung không đạt ngưỡng.
4. Ghi log theo mẫu (nén, không ảnh), ledger, và chi phí của batch.
5. Commit checkpoint lên bộ lưu trữ bền.
6. Nếu điều kiện dừng được kích hoạt, ghi lý do và dừng.

## 5. Điều kiện dừng

Không có vòng chạy nào vượt các điều kiện này, kể cả khi mục tiêu là "không dừng":

- trần chi phí ngày, trần đĩa, trần fallback mỗi trận;
- tỷ lệ fallback tăng đột biến;
- lượt audit vượt ngưỡng sai tự tin;
- nguồn lỗi liên tục.

## 6. Lộ trình

Mỗi bước có cổng. Không mở rộng trước khi cổng trước đạt.

**Bước 0: kiểm tra (không tốn token model).**
- Quét mọi nhánh tìm yêu cầu và phản hồi từ `hud`.
- Đo số trường confidence đã có trong bản ghi OCR. Hiện có ngưỡng nội bộ nhưng chưa thấy trường confidence trong bản ghi đầu ra. Cần thêm vào.
- Kiểm tra `run.py` và thêm trần chi phí, trần fallback nếu thiếu. Hiện có kiểm soát bộ nhớ, CPU, đĩa và `status.json`.

**Bước 1: pilot một trận.**
- Chạy toàn bộ chuỗi trên một trận: OCR, khớp mẫu, fallback, làm sạch, audit.
- Đo: chi phí USD và token theo trận, tỷ lệ fallback theo từng trường, tỷ lệ sai tự tin của từng đọc viên.
- Dùng số đo để đặt trần cho bước 2.
- **Cổng 1:** báo cáo pilot đạt. Chi phí dự kiến trong trần. Tỷ lệ sai tự tin của đọc viên dự phòng được đo độc lập.

**Bước 2: chạy có giới hạn.**
- Vài trận, trong phân vùng của từng agent.
- **Cổng 2:** tỷ lệ phủ và tỷ lệ sai tự tin theo từng trường đã có số, cỡ mẫu đã ghi.

**Bước 3: mở rộng.**
- Chỉ sau cổng 2. Thêm streamer, mùa cũ (cần catalog theo set), và phần PBE được gắn nhãn riêng.

**Bước 4: chuyển sang phiên mô hình chuyên trách.**
- Quyết định mô hình học gì. Không thuộc kế hoạch này.

## 7. Quyết định của người dùng

Bốn quyết định không thể thay bằng suy đoán:

1. **Khóa API Anthropic cho vòng chạy.** Script gọi API từng crop tiết kiệm hơn nhiều so với để một phiên agent đọc ảnh. Cần cấp qua `request_credential` hoặc biến môi trường. Phiên này không tự tạo hay lưu khóa.
2. **Trần chi phí USD mỗi ngày.** Con số này quyết định mọi thứ phía trên. Chưa có trần thì không chạy vòng không dừng.
3. **Mô hình đọc dự phòng:** Opus 5.5 (mặc định theo skill, chính xác hơn) hay Haiku 5.5 (rẻ hơn khoảng 40 lần, cần đo trước).
4. **Phân vùng streamer cho từng agent.** Không có phân vùng, hai agent có thể tải trùng VOD.

Thêm một lưu ý: môi trường cloud có giới hạn tài nguyên của phiên. Tài liệu hướng dẫn nói phiên có thể hết hạn mức và chuyển sang máy mới. Vì vậy công việc đang chạy phải được commit và đẩy lên sau mỗi bước, không để trong bộ nhớ phiên.

## 8. Việc đã có và việc còn thiếu

- **Có sẵn:** OCR gán vàng, cấp, shop, giá; hàng đợi VOD với SQLite; kiểm soát bộ nhớ, CPU, đĩa; `status.json`; ngưỡng độ tin cậy nội bộ.
- **Còn thiếu:** trường confidence trong bản ghi; trần chi phí; đọc dự phòng; khớp mẫu icon; catalog theo set; bộ làm sạch; lượt audit tự động; sổ nguồn có claim.
