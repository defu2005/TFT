# Cần gì để tiếp tục

File này ghi mọi thứ engine cần từ người dùng hoặc phiên ingest, và các quyết định đã tự đưa ra khi người dùng vắng mặt. Mỗi mục có trạng thái: **mở**, **đã có**, hoặc **đã quyết**.

## 1. Từ người dùng

| # | Cần gì | Vì sao | Mở khóa | Trạng thái |
| --- | --- | --- | --- | --- |
| U1 | Bảng XP theo level (xp mỗi lần mua, xp để lên từng level) | Quyết định lên level và thời điểm lên level | Bước 3 của quyết định XP | **mở** |
| U2 | Dùng bảng odds nào: `rules.js` (chưa xác minh, lệch nguồn Set 17 ở level 8, 9) hay nguồn khác | Xác suất gặp tướng, quyết định roll | Mọi tính toán hit chance | **mở** |
| U3 | File dữ liệu của set hiện tại (tướng, tộc, mốc, cost) | Chọn line tự động, thay `tft_set_line` nhập tay | Giai đoạn 3 | **mở** |
| U4 | Xác nhận: mua tướng hoàn thành sao khi bench đầy có hợp lệ trong client không | Engine đang khuyến nghị lượt này | Quy tắc gate bench đầy | **mở** |
| U5 | Lượt roll miễn phí có cộng dồn sang stage sau không? | Quy tắc tính roll miễn phí | Giá trị `freeRolls` | **mở** |
| U6 | Roll miễn phí chỉ được khuyến nghị khi đã đặt mục tiêu (`tft_set_target`). Có đúng ý không? | Hành vi roll miễn phí | Khuyến nghị roll | **mở** |

## 2. Từ phiên ingest

Format và danh sách trường xem `docs/engine-state.md`, mục 4.

| # | Cần gì | Vì sao | Trạng thái |
| --- | --- | --- | --- |
| I1 | `id` và `star` trên `board` (hiện chỉ có `championName`, `starLevel`) | Đếm bản trên bàn | **mở** |
| I2 | `bench` với `id`, `star`, `sellValue` | Gate bench đầy, bán để nhường chỗ | **mở** |
| I3 | `takenByOthers` cho từng ô shop (số bản người khác đang giữ) | Xác suất gặp tướng chính xác | **mở** |
| I4 | `round`, `phase`, `xp`, `xpToNext` | Lên level và roll đúng thời điểm | **mở** |
| I5 | Đánh dấu giá trị ước lượng trong `missing` (gold, level, stage khi không có HUD), và cho biết tướng shop không rõ cost đang được gán cost 1 mặc định (`standaloneSource.js`) | Tránh khuyến nghị lên level dựa trên vàng bịa; tránh mua/bán sai giá | **mở** |
| I7 | Gửi `freeRolls` (số lượt roll miễn phí còn lại) | Engine đã hỗ trợ nhưng không nguồn nào gửi | **mở** |
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
| 2026-11-23 | Mua món muốn mua có sẵn trước khi roll nếu còn đủ vàng để roll; hỗ trợ lượt roll miễn phí (`freeRolls`, không tốn vàng, không bị phạt) | `ef40fd1` |
| 2026-11-23 | Diễn giải "tối ưu" là tối ưu chất lượng quyết định. Tốc độ không cần sửa: khoảng 70–130 ns mỗi quyết định so với vòng lặp 250 ms | `8cfa5d0` |
| 2026-11-23 | Chọn hành động tốt nhất trong số các hành động vượt ngưỡng của chính nó: mua hoặc bán không còn bị giữ lại bởi roll dưới ngưỡng 0.45 hoặc xp dưới 0.5
| 2026-11-23 | Bán trước khi roll khi việc bán vẫn để đủ vàng roll; sửa văn bản "Mua trước rồi mới roll" để chỉ hiện khi thật sự có roll sau đó | `87987bc` |
