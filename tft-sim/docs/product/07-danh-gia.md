# 7. Đánh giá

## Nguyên tắc

1. **Đăng ký trước.** Quy tắc, ngưỡng và n được ghi vào plan trước khi chạy. Không đổi sau khi có kết quả.
2. **Tách mô phỏng với trận thật.** Mô phỏng chỉ kiểm tính nhất quán. Chỉ trận thật đạt cổng mới chứng minh độ đúng.
3. **Kiểm đối xứng và seed.** Kết quả không được phụ thuộc vào bên nào là A, hay seed cụ thể.

## Chấm điểm dự đoán

- `fidelity.score`: so dự đoán với kết quả thật trên `scoring.jsonl`.
- `MIN_GAMES = 30`, `BOOT = 2000` (số lần bootstrap).
- `predict_win`: hòa không tính cho p_a.
- Mặc định **n = 800, seed0 = 0**. Lịch sử: 20 → 400 (mục 11.26) → 800 (mục 11.28).
- Kết quả thiếu dữ liệu được gắn **inconclusive**, không được coi là đạt.

## Kết quả kiểm tra nội bộ (mô phỏng, không phải trận thật)

| Kiểm tra | Cấu hình | Kết quả | Ngưỡng | Đạt? |
|---|---|---|---|---|
| Đảo bên (mirror) | PRIMARY | lệch +0,0075 (SE 0,0059) | 0,01 | Đạt |
| Tỷ lệ đảo, không item | n=400 | 13/319 = 4,08% | 5% | Đạt |
| Tỷ lệ đảo, có item | n=400 | 20/398 = 5,03% | 5% | **Không đạt** |
| Tỷ lệ đảo, có item | n=800 | 16/398 = 4,02% | 5% | Đạt |

Ghi chú về mẫu số: với mẫu số thay thế, n=400 cho 20/344 = 5,81% và n=800 cho 16/346 = 4,62%. Kết luận không đổi về hướng; phải ghi rõ mẫu số đang dùng. Kết luận không đổi về hướng, nhưng phải ghi rõ mẫu số nào đang dùng.

## Phải đọc kỹ: quyết định n=800 được đưa ra sau khi thấy n=400 không đạt

- n=400 trên bàn có item **không đạt** (5,03%).
- Sau đó nhánh chọn n=800 (mục 11.28), trước khi chạy. Advisor đã chọn phương án này khi được hỏi.
- Đây là **lần thử thứ hai** trên cùng dữ liệu. Nó không phải thí nghiệm mới hoàn toàn. Khi báo cáo, phải nói rõ điều này.
- Nếu muốn kết luận chắc hơn, cần một bộ cặp bàn mới, đăng ký trước, không dùng bộ cũ.

## Chi phí

Một luồng, 20 cặp bàn không item: n=400 khoảng 2,71 giây/cặp; n=800 khoảng 5,57 giây/cặp.

## Ngưỡng cho trận thật (chưa áp dụng)

Chưa có ngưỡng nào được đăng ký cho đánh giá trên trận thật. Trước khi có dữ liệu đạt, không đặt ngưỡng vì không có gì để đo.

## Selftest

Các bài kiểm tự động trong `scripts/combat/selftest_*.py` phải PASS trước mọi báo cáo. Selftest PASS không chứng minh engine đúng; nó chỉ chứng minh các bài kiểm tra chạy đúng.
