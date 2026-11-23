# Cần gì để tiếp tục

File này ghi mọi thứ engine cần từ người dùng hoặc phiên ingest, và các quyết định đã tự đưa ra khi người dùng vắng mặt. Mỗi mục có trạng thái: **mở**, **đã có**, hoặc **đã quyết**.

## 1. Từ người dùng

| # | Cần gì | Vì sao | Mở khóa | Trạng thái |
| --- | --- | --- | --- | --- |
| U1 | Bảng XP theo level (xp mỗi lần mua, xp để lên từng level) | Quyết định lên level và thời điểm lên level | Bước 3 của quyết định XP | **mở** |
| U2 | Dùng bảng odds nào: `rules.js` (chưa xác minh, lệch nguồn Set 17 ở level 8, 9) hay nguồn khác | Xác suất gặp tướng, quyết định roll | Mọi tính toán hit chance | **mở** |
| U3 | File dữ liệu của set hiện tại (tướng, tộc, mốc, cost) | Chọn line tự động, thay `tft_set_line` nhập tay | Giai đoạn 3 | **mở** |
| U4 | Xác nhận: mua tướng hoàn thành sao khi bench đầy có hợp lệ trong client không | Engine đang khuyến nghị lượt này | Quy tắc gate bench đầy | **mở** |

## 2. Từ phiên ingest

Format và danh sách trường xem `docs/engine-state.md`, mục 4.

| # | Cần gì | Vì sao | Trạng thái |
| --- | --- | --- | --- |
| I1 | `id` và `star` trên `board` (hiện chỉ có `championName`, `starLevel`) | Đếm bản trên bàn | **mở** |
| I2 | `bench` với `id`, `star`, `sellValue` | Gate bench đầy, bán để nhường chỗ | **mở** |
| I3 | `takenByOthers` cho từng ô shop (số bản người khác đang giữ) | Xác suất gặp tướng chính xác | **mở** |
| I4 | `round`, `phase`, `xp`, `xpToNext` | Lên level và roll đúng thời điểm | **mở** |
| I5 | Đánh dấu giá trị ước lượng trong `missing` (gold, level, stage khi không có HUD) | Tránh khuyến nghị lên level dựa trên vàng bịa | **mở** |
| I6 | Tên tướng trong `championName` và `id` của HUD shop khớp nhau | Nếu khác, `copiesOwned` luôn bằng 0 | **mở** |

## 3. Quyết định đã tự đưa ra

| Ngày | Quyết định | Commit |
| --- | --- | --- |
| 2026-11-23 | Sửa điểm mua: không mua tướng đã đủ 9 bản; thưởng ghép cặp khi hoàn thành sao | `7ff9485` |
| 2026-11-23 | Tài liệu hoá nhu cầu dữ liệu và hợp đồng giả định | `c5c15e1` |
| 2026-11-23 | Đếm bản từ board và bench, trừ số bản người khác giữ | `afe451c` |
| 2026-11-23 | Chặn mua khi bench đầy; bán để nhường chỗ; log schema 2 | `37cb046` |
| 2026-11-23 | Chỉ bán khi không có lượt mua; giữ bản đang cần trong line | `4766647` |
| 2026-11-23 | Mục tiêu đang có trong shop được mua bất kể priority trên shop; không roll khi mục tiêu đã có trong shop | `0376529` |
| 2026-11-23 | Bỏ qua ô shop không có cost hợp lệ (`thiếu cost`); thêm test bất biến trên 2.000 trạng thái sinh có seed | `744ee3d` |
| 2026-11-23 | Mua món muốn mua có sẵn trước khi roll nếu còn đủ vàng để roll; hỗ trợ lượt roll miễn phí (`freeRolls`, không tốn vàng, không bị phạt) | (commit này) |

## 4. Mở cho người dùng, phát sinh từ vòng này

| # | Câu hỏi | Trạng thái |
| --- | --- | --- |
| U5 | Lượt roll miễn phí có được cộng dồn sang stage sau không? | **mở** |
| U6 | Roll miễn phí chỉ được khuyến nghị khi đã đặt mục tiêu (`tft_set_target`). Đây có phải là điều muốn không? | **mở** |
