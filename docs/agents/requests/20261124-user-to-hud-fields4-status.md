# Yêu cầu: lỗi đã biết của bộ đọc trường (fields4) trên trận 01 mùa 18

dataset: `fields4.jsonl` (23.082 mẫu, 0,1 s, 311,8–2619,9 s) của trận `01-boxbox` đọc bằng bộ đọc trường v4. File nằm ở ổ scratch của phiên, chưa commit. Không đưa MP4 hay khung hình vào git.
fields: mỗi dòng gồm `t`, `stage`, `timer`, `gold`, `level`, `xp`, `streak`, `raw`. Chưa có `hudDetected` đáng tin, chưa có cờ thanh HUD.
schema: không đổi. Bộ đọc nằm ở `fields4.py` (bản sao của `fields3.py` với 3 chỉnh sửa).
status: mở. Lỗi dưới đây cần `hud` xử lý trước khi dùng dữ liệu làm nhãn.

## Độ phủ (toàn trận)

stage 97,0%, timer 95,5%, gold 69,5%, level 67,8%, xp 52,6%, streak 70,9%. Độ phủ không phải độ chính xác.

## Lỗi đã biết, có bằng chứng

1. **Thanh HUD bị che, vẫn đọc ra giá trị sai.** Tại 1493,9 s, bảng chọn augment che HUD nhưng bộ đọc vẫn trả level 7 và gold 2. Cần bộ phát hiện thanh HUD đáy. Thử so màu dải đáy không phân tách được (1493,9 có số liệu giống các khung có HUD).
2. **Lệch một mẫu giữa pipeline và ảnh đơn.** Tại 398,4 s, ảnh đơn đọc timer 20 (đúng theo mắt), pipeline đọc 19 ở cùng thời điểm. Cần kiểm tra cách `ffmpeg -ss` / `fps=10` lấy khung trước khi tin các trường theo thời gian.
3. **Timer bị đọc nhầm chevron.** Hộp timer giai đoạn 1 cũ (x 722–745) chứa chevron ở x≈743, đọc thành "17" khi đúng là 1 (375,7 s). Đã sửa thành x 722–743, nhưng cần kiểm tra trên các giai đoạn khác.
4. **Gold 0 bị bỏ.** Tại 2558,6 s, hộp gold đọc chuỗi rỗng dù đúng là 0. Hộp gold chưa đáng tin.
5. **XP mất ký tự.** "0/10" và "8/10" đọc thành "0" (mất "/10" và chữ số đầu). Bộ đọc trả null, đúng nguyên tắc null-over-guess, nhưng độ phủ XP thấp.
6. **Hệ số XP chưa xác minh.** Cấp 8 = 68 (đã xác nhận bằng mắt ở 1405,7 s). Cấp 5, 6, 7 (20, 36, 56) chưa kiểm chứng.
7. **Ô shop không khớp m01.** Tại 431,5 s, m01 ghi Rakan ở ô 3 (cost 1), mắt thấy ô trống và gold 0→2. Không giải thích được bằng quy tắc "mất ô = mua".
8. **Chưa có dữ liệu:** HP, bàn và hàng chờ (định danh tướng), trait, augment, item, hành động, kết quả vòng, thứ hạng, đội hình cuối.

## Kiểm thử

- Nhãn mắt 20 khung (dùng để gỡ lỗi): không có giá trị sai trong stage, timer, level, gold, xp, streak sau sửa.
- Nhãn mù 10 khung (đọc trước khi xem bộ đọc): stage 10/10, timer 10/10, level 6/6 (+1 dương giả ở 1493,9), gold 5/5 (+1 null), xp 4/4 (+2 null), streak 6/6.
- Chưa đo độ chính xác 100%. Chưa có nhãn mù đủ cỡ để ước lượng sai số.

## Việc cần `hud` làm

A. Thêm bộ phát hiện thanh HUD đáy và cờ `hudBarVisible` cho từng mẫu.
B. Kiểm tra lệch một mẫu giữa pipeline và ảnh đơn (so 398,4 s và 434,6 s).
C. Xác minh hệ số XP cho cấp 5, 6, 7 trên mỗi cấp một khung.
D. Sửa hộp gold để đọc được 0.
E. Giải thích ô Rakan tại 431,5 s trên m01.

## Lưu ý

- Không commit `fields4.jsonl`, ảnh đơn hay MP4. Chỉ dùng bảng tóm tắt trong yêu cầu này.
- Nhãn mắt không chứa tên người chơi thật hoặc Riot ID.
