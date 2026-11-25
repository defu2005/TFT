# Dữ liệu cần có (workstream sim)

## Đầu vào thật cho mô hình
- HP của mình theo thời gian
- Stage/round, timer, streak
- Bàn và bàn chờ, kèm sao
- Trang bị và augment, kèm tier
- Kết quả combat từng round
- Thứ hạng cuối mỗi trận
- HP của 7 đối thủ
- Log của set thứ hai

## Nội dung game
- Kỹ năng tướng Set 18
- Odds cửa hàng và bảng XP theo cấp Set 18
- Trang bị và augment Set 18
- Cơ chế Wisp và Lux
- Tướng, trait, cost Set 18 (có licence)

## Đánh giá
- Cặp (bàn, kết quả round) từ trận thật, nhiều trận
- Khối seed mới cho mỗi lần đánh giá

## Bản ghi trận (fight-v1)
Mỗi round có cả hai bên, mỗi bên gồm:
- Cấp, augment đã chọn.
- Tướng: apiName, sao, trang bị (apiName), vị trí (hàng, cột) nếu đọc được.
- Kết quả combat của round: bên thắng.
Schema và kiểm tra: `scripts/combat/fight.py`.
