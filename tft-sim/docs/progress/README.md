# Đọc bộ tài liệu tiến độ

**Mở `STATUS.md` trước.** Đó là trang tóm tắt, cập nhật mỗi lần có agent làm xong việc. Mọi thứ khác là chi tiết để tra cứu.

## Thứ tự đọc

1. `STATUS.md`: dự án đang ở đâu, cái gì đang chờ ai.
2. `sessions/`: mỗi phiên làm việc một file, theo ngày. Đọc file mới nhất để biết việc vừa làm.
3. `../model-plan.md`: hồ sơ kỹ thuật đầy đủ, dài. Chỉ mở khi cần chi tiết một quyết định.
4. `../product/README.md`: bộ tài liệu product (tổng quan, kiến trúc, lộ trình, rủi ro, nhật ký quyết định).

## Thuật ngữ

| Thuật ngữ | Nghĩa |
|---|---|
| Engine | Phần mô phỏng trận TFT (`tft_goat`), đóng vai trò "luật chơi" để chạy thử. |
| Mô hình | Thành phần học từ dữ liệu để đưa ra quyết định (học chính sách). Hiện clone đầy đủ ngang giáo viên; chưa có mô hình nào vượt giáo viên một cách có ý nghĩa. Con số +0,015 là kiểm công bằng của harness (v4 − v4_null), không phải kết quả mô hình. |
| Dự đoán thắng/thua | Xác suất bên A thắng một cặp bàn, tính bằng mô phỏng engine (không phải mô hình học, không phải trận thật). |
| PRIMARY | Cấu hình dự đoán đang dùng (xem `STATUS.md`). |
| n | Số lượt mô phỏng cho mỗi xác suất. Hiện n = 800. |
| Tỷ lệ đảo | Tỷ lệ cặp mà dự đoán đổi bên thắng khi đổi seed. Dùng để kiểm độ ổn định. |
| Seed | Số khởi tạo ngẫu nhiên của mô phỏng. Đổi seed để kiểm độ ổn định. |
| Cổng gộp VOD | Kiểm tra dữ liệu VOD trước khi dùng. Hiện đỏ. |
| `fight-v1` | Định dạng một bản ghi trận: hai bàn tại một round, kết quả. |
| Dữ liệu `real` | Dữ liệu thật đã qua cổng, đủ điều kiện để chấm điểm. Hiện chưa có. |
| Mô phỏng | Dữ liệu sinh từ engine, không phải trận thật. Mọi con số hiện có đều là mô phỏng. |
| Bàn giao | Câu hỏi đã gửi cho người ngoài (ví dụ tác giả `tft_goat`), chưa có trả lời. |
| Đăng ký trước | Quy tắc được ghi vào plan trước khi chạy thí nghiệm, không đổi sau khi có kết quả. |

## Mục lục `model-plan.md` (còn hiệu lực hay không)

- Mục 1–4, 7–9: nền tảng và cập nhật cũ. Còn đúng về mặt lịch sử.
- Mục 5 và 6: đã bị thay bởi mục 10.
- Mục 10: khả thi mô hình thích ứng; các thí nghiệm 10.6–10.10 là bằng chứng mô phỏng.
- Mục 11.1–11.20: kế hoạch Set 18 và các phát hiện cũ. Một số con số đã được đính chính trong các mục sau.
- Mục 11.21–11.23: dữ liệu VOD và kết luận không cần dữ liệu.
- Mục 11.24–11.29: kiểm tra nội bộ và quyết định mới nhất. **11.25 và 11.26 có phần n đã bị thay bởi 11.28; 11.29 là bản chốt.**

## Quy tắc khi thêm tài liệu

- `STATUS.md`: ghi đè mỗi lần, không quá một màn hình.
- `sessions/`: mỗi phiên một file mới, không sửa file cũ.
- Không dùng phần trăm hoàn thành. Dùng: xong, đang làm, bị chặn, chưa bắt đầu, đã bỏ.
- Tách rõ "mô phỏng" với "trận thật" ở mọi dòng.
