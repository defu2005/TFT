# 10. Nhật ký quyết định

Ghi theo thứ tự thời gian. Cột "Nguồn" chỉ tới nơi ghi quyết định. Nếu không tìm được nguồn, dòng bị bỏ.

| Ngày | Quyết định | Nguồn | Ai quyết |
|---|---|---|---|
| 2026-11-23 | Dùng snapshot CDragon làm bảng xác minh | Yêu cầu của người dùng trong phiên | Người dùng |
| 2026-11-26 | Chủ roster Set 18 là nhánh `engine` (giữ hiệu lực) | `roadmap.md`, mục 3 | Advisor quyết, người dùng ủy quyền |
| 2026-11-24 | Thứ tự tích hợp PR #1 → #2 → #3 → #4 (đã thực hiện) | PR #1–#4 merge 15:09–15:11 UTC; người merge chưa xác minh | Đã thực hiện |
| 2026-11-26 | Đường RAM không đóng; người dùng sẽ phát triển sau | Lời người dùng trong phiên | Người dùng |
| 2026-11-26 | Mục 6 (ảnh EoG) không phải quyết định, là việc chờ người dùng | `roadmap.md` | Advisor |
| 2026-11-24 | Dừng mở rộng chiến dịch OCR VOD của `hud` (không áp cho lô fight-v1) | `roadmap.md`, mục 5 | Advisor quyết, người dùng ủy quyền (2026-11-26) |
| 2026-11-24 | Dùng VOD streamer cho huấn luyện; rủi ro pháp lý chưa kiểm | `roadmap.md`, bổ sung | Người dùng đã nhận thức và quyết định |
| 2026-11-25 | Mở lô VOD `2026-11-25-set18-vod` (goal ≥1000 ván) để thu `fight-v1` | `vod-collection.md` | Người dùng yêu cầu trong phiên |
| 2026-11-25 | Không chuyển các đánh giá cũ sang nội dung đã alias; đường ghi bản ghi thật dùng nội dung đã alias | `model-plan.md` 10.12 | Theo advisor, ghi trong mục 10.12 |
| 2026-11-25 | Kế hoạch Set 18 Phase 0–4, lý do là Set 19 đang PBE | `model-plan.md` mục 11 | Theo advisor, ghi trong mục 11 |
| 2026-11-25 | Đóng thí nghiệm mask (10.6), giải đấu v2 (10.9), dropout (10.10) | `model-plan.md` 10.6–10.10 | Đăng ký trước, chạy theo đăng ký |
| 2026-11-26 | Augment không đổi xác suất dưới bàn cân bằng (0/252) | `results/fixed/combat/augment_sweep.json` | Số liệu |
| 2026-11-26 | Phân loại item: 617/731 không có tác động dưới PRIMARY | `item_effect_classes.json` | Số liệu |
| 2026-11-26 | n=400 không đạt cho bàn có item (5,03%) | `adaptive_n_items_check.json` | Số liệu |
| 2026-11-26 | Chọn n=800 cho bàn có item (16/398 = 4,02%) | `model-plan.md` 11.28 | Người dùng để advisor quyết; advisor chọn đăng ký n=800 |
| 2026-11-26 | Gửi ba câu hỏi `_GENERIC_ITEM` cho tác giả engine | `docs/agents/requests/20261126-…md` | Agent. Người dùng chưa xác nhận đóng hay mở. |
| 2026-11-26 | Bộ tài liệu tiến độ và quy tắc cuối phiên | `AGENTS.md`, `docs/progress/` | Người dùng yêu cầu |

## Chưa xác nhận

- **Roadmap nhánh nifty:** dòng Lịch sử "đóng nhánh RAM" và quyết định 1 cần đối chiếu với ý định (xem [3](03-lo-trinh.md)).
- **Bàn giao `_GENERIC_ITEM`:** advisor xác nhận bàn giao là chấp nhận được. Người dùng chưa xác nhận.


## Đính chính (những điều đã nói sai)

| Đã nói | Sự thật | Sửa ở |
|---|---|---|
| "generic_items luôn 0" | Sai. Khối chung được cộng cho item đếm. | [5](05-engine-set18.md) |
| "65/776 item không có hiệu ứng" | Sai phạm vi. Đúng là 617/731 (bỏ 45 twin). | [5](05-engine-set18.md) |
| "+0,015 là mô hình vượt teacher" | Sai. Đây là kiểm công bằng harness (v4 − v4_null). | [4](04-mo-hinh.md) |
| Hash commit `4ff53c71` trong STATUS | Sai, lỗi thời. Đã bỏ hash. | `progress/STATUS.md` |
| "Blitz không được lưu theo quy tắc" | Không tìm thấy quy tắc đó trong `docs/`. Có ghi nhận người dùng cho phép. | [6](06-du-lieu.md) |
