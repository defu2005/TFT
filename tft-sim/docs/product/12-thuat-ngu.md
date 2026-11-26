# 12. Thuật ngữ

| Thuật ngữ | Nghĩa |
|---|---|
| advisor | Mô hình reviewer mạnh hơn được gọi để góp ý. Ghi nhận là "đã hỏi" chỉ khi thật sự đã gọi. |
| augment | Lựa chọn tăng sức mạnh trong ván (Set 18). |
| BoardUnit | Một unit trên bàn, gồm tướng, sao, items, item_apis, augments. |
| CDragon | Nguồn dữ liệu nội dung game (tướng, item, trait). Dùng làm bảng xác minh. |
| cổng gộp (merge gate) | Kiểm tra VOD trước khi ghi vào `scoring.jsonl`. |
| `DA_*` | Tiền tố tên item trong CDragon, không có hook proc trong engine. |
| đăng ký trước | Quy tắc ghi trước khi chạy thí nghiệm. |
| engine | Mô phỏng trận TFT, repo `tft_goat`. |
| `EngineResolver` | Bộ giải combat của engine, dùng cho Set 17 trong mô hình học. |
| `fidelity.score` | Hàm chấm điểm dự đoán với trận thật. |
| `fight-v1` | Định dạng một bản ghi trận. |
| HUD | Giao diện trong game, nguồn dữ liệu live đề xuất. |
| `HANDOFF_STATUS` | Trạng thái bàn giao: pending, working, done, blocked, stale. |
| inconclusive | Kết quả không đủ dữ liệu để kết luận. |
| item_alias | Bật alias item (twin, Radiant/Artifact). Tắt trong PRIMARY. |
| mirror | Kiểm đảo bên A và B để đo thiên lệch. |
| MIN_GAMES | Số ván tối thiểu để chấm điểm (30). |
| mô phỏng | Dữ liệu sinh từ engine, không phải trận thật. |
| n | Số lượt mô phỏng cho mỗi xác suất. |
| PRIMARY | Cấu hình dự đoán chính. |
| `predict_win` | Ước lượng xác suất thắng cho một cặp bàn. |
| SECONDARY | Cấu hình kiểm tra, PRIMARY cộng emblem, traits_table, item_alias. |
| seed | Số khởi tạo ngẫu nhiên của mô phỏng. |
| Set 17, Set 18, Set 19 | Các set TFT. Set 18 là set đang chạy; Set 19 đang PBE. |
| teacher (giáo viên) | Chính sách scripted (v4) mà mô hình học bắt chước. |
| `_GENERIC_ITEM` | Khối chỉ số chung cộng cho item đếm được. Quy ước đang mở. |
| twin | Item trùng lặp alias; 45 cái trong 776. |
| `usable.reason` | Bộ lọc chung từ chối bản ghi thiếu dữ liệu. |
| VOD | Video xem lại trận (Twitch/YouTube). |
| v4_null | Biến thể đối chứng của v4, dùng để kiểm harness. |
