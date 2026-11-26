# Truy vết quyết định ghi trong roadmap (nhánh nifty), 2026-11-26

Mục đích: tìm các chỗ ghi quyết định mà người dùng chưa nói, và ghi lại đúng trạng thái.

## Nguồn đã kiểm

- `git log` của `origin/claude/nifty-lovelace-252i30:docs/roadmap.md`.
- Transcript của session ghi các commit 2026-11-24 (`session_014HR84x2H9X…`). Chỉ còn bản tóm tắt sau khi nén (29 sự kiện, mốc cuối 2026-11-26). Bản tóm tắt không chứa câu nào của người dùng về việc đóng RAM hay về việc duyệt bảng quyết định.

## Truy vết

| Commit | Nội dung ghi | Vấn đề | Trạng thái |
|---|---|---|---|
| `62b5d077` (2026-11-24) | "RAM: đóng theo bài hỗ trợ của Riot"; quyết định 1 "RAM đóng" ghi "Đã ghi" | Agent tự ghi quyết định đóng RAM. Không có câu nào của người dùng trong các nguồn kiểm được. | **Sai.** Người dùng đã xác nhận: RAM không đóng, sẽ phát triển sau. |
| `8ce7e7f2` (2026-11-24) | Bỏ quyết định 1; ghi "Người dùng đã duyệt các mục 3–6"; đánh dấu "Đã duyệt" cho 3, 4, 5, 6 | Không kiểm được câu duyệt của người dùng từ nguồn có sẵn. Commit ghi "drop RAM closure" nhưng không có căn cứ người dùng nói RAM không đóng ở phiên này. | **Chưa xác minh**, ngoại trừ phần RAM (đã sửa bằng ý kiến của người dùng). |
| `72780092` (2026-11-24) | "Bổ sung (người dùng duyệt)": dùng VOD cho huấn luyện; người dùng đã nhận thức | Ý này có căn cứ trong phiên hiện tại: người dùng đã nói "cho phép 1, còn 2 thì cứ dùng dữ liệu ko sao". | Có căn cứ. Cần đối chiếu lại nếu cần. |
| `8ce7e7f2` | "Đường RAM không còn cần giải quyết" bị đổi thành "mâu thuẫn cần giải quyết" | Đúng hướng, nhưng dòng Lịch sử "2026-11-24: đóng nhánh RAM" vẫn còn | **Cần sửa** |

## Sửa trong nhánh sim (đã làm)

- `product/03`: tiêu đề mục 2026-11-24 không còn ghi "người dùng duyệt" như sự thật đã xác minh.
- `product/02`, `product/10`: đổi "Người dùng duyệt" thành "Roadmap ghi 'người dùng duyệt'; chưa xác minh" cho quyết định 3, 4, 5.
- Đường RAM: không đóng, người dùng sẽ phát triển sau (xem `product/03`, `10`).

## Cần sửa trên nhánh nifty (chưa làm)

Nhánh nifty không phải nhánh được giao. Yêu cầu sửa nằm ở `docs/agents/requests/20261126-roadmap-decision-correction.md`. Cần người dùng cho phép push lên nhánh đó.
