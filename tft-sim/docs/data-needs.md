# Dữ liệu cần có (workstream sim)

Chỉ liệt kê những gì còn thiếu hoặc cần cập nhật. Trạng thái: có / một phần / thiếu.

## Đầu vào thật cho mô hình (từ `hud`)
- HP của mình theo thời gian — thiếu
- Stage/round, timer, streak — một phần (đã yêu cầu trong `fields4`)
- Bàn và bàn chờ kèm sao — thiếu (720p không đọc được, cần xác nhận 1080p hoặc icon)
- Trang bị và augment, kèm tier — thiếu
- Kết quả combat từng round — thiếu
- Thứ hạng cuối mỗi trận — thiếu (chỉ có 1 trận nháp)
- HP của 7 đối thủ — thiếu nguồn (6 mẫu nhãn mắt, chưa xác nhận)
- Log của set thứ hai — thiếu

## Nội dung game (cho simulator)
- Kỹ năng tướng Set 18 — thiếu (~91 tướng cần viết logic)
- Odds cửa hàng và bảng XP theo cấp Set 18 — lệch `rules.js` ở cấp 7–8, chờ `engine`
- Trang bị và augment Set 18 — thiếu
- Cơ chế Wisp và Lux — chưa mô hình
- CDragon snapshot: licence chưa xác minh; nhãn "18.7" sai

## Đánh giá
- Cặp (bàn, kết quả round) từ trận thật, nhiều trận — thiếu (điều kiện cổng cho độ trung thực)
- Khối seed mới cho mỗi lần đánh giá — dự trữ 280000–283999 đang dùng cho giải đấu v2
