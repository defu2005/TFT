# Tiến độ dự án (cập nhật 2026-11-26)

**Commit:** `4ff53c71` (nhánh `claude/claude-fable-5-2-awwmf5`). **Cập nhật bởi:** agent Claude, phiên 2026-11-26.

**Đã đối chiếu dự đoán với trận thật chưa?** **Chưa.** Không có trận nào đủ điều kiện để chấm điểm.

## Các mảng việc

| Mảng | Trạng thái | Bằng chứng | Việc kế tiếp |
|---|---|---|---|
| Engine combat (`tft_goat`, Set 17 và nền Set 18) | Ổn định nội bộ; chưa đối chiếu trận thật | `results/fixed/combat/` (đối xứng, seed, n) | Trả lời câu hỏi `_GENERIC_ITEM` (xem "Đang chờ") |
| Quy ước item (khối chung `_GENERIC_ITEM`) | Bàn giao, chưa có câu trả lời | `docs/agents/requests/20261126-engine-generic-item-convention.md` | Chờ tác giả `tft_goat` |
| Cấu hình dự đoán PRIMARY, n | Đã chốt n=800 cho bản ghi có item (4,02%) | `docs/model-plan.md` mục 11.28, 11.29 | Không tăng n nữa |
| Mô hình học chính sách (bắt chước giáo viên) | Có kết quả mô phỏng; chưa vượt giáo viên có ý nghĩa | `docs/model-plan.md` mục 10.6–10.10 | Chưa có bước tiếp theo được duyệt |
| Dự đoán thắng/thua Set 18 | Chưa có mô hình học; dùng mô phỏng PRIMARY | `docs/model-plan.md` mục 11.23–11.29 | Cần dữ liệu thật đủ điều kiện |
| Dữ liệu VOD (Twitch/YouTube) | Bị chặn: cổng gộp đỏ, chưa slot nào đạt | `docs/handoff/vod-collection.md` | Sửa lỗi dữ liệu nguồn hoặc đợi dữ liệu mới |
| Item và augment Set 18 | Item: 617/731 không có tác động dưới PRIMARY. Augment: chưa mô hình hóa | `results/fixed/combat/item_effect_classes.json`, `augment_sweep.json` | Đăng ký cấu hình mới nếu muốn mô hình hóa |
| Công cụ và bộ kiểm tra | Xong, selftest PASS | `scripts/combat/selftest*.py` | Chạy lại khi đổi mã |

## Đang chờ ai

- **Tác giả `tft_goat`:** trả lời ba câu hỏi về `_GENERIC_ITEM`.
- **Bạn:** xác nhận việc bàn giao câu hỏi trên là đủ để đóng mục (hoặc để mở tiếp). Quyết định dữ liệu VOD: dùng lại hay bỏ.
- **Agent thu dữ liệu (Codex/Cursor):** chưa có dữ liệu đạt. Cần chạy lại theo `docs/handoff/vod-collection-prompt.md` nếu muốn tiếp tục thu.

## Cấu hình đang dùng

- Cấu hình dự đoán: **PRIMARY** (`ability=generic`, items, augments, traits bật; emblem và alias tắt).
- Số lượt mô phỏng: **n = 800**, seed0 = 0.
- Engine commit: `d5358e9`.

## Thay đổi so với lần trước

- Thêm kiểm tra n=800 trên bàn có item: 16/398 = 4,02%, đạt.
- Đổi mặc định `fidelity.score` từ n=20 sang n=800.
- Phân loại 731 item theo tác động; ghi số liệu vào mục 11.26.
- Thêm file yêu cầu gửi tác giả `tft_goat`.
