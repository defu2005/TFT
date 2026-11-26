# Tiến độ (dev) · cập nhật 2026-11-26

**Nhánh:** `claude/claude-fable-5-2-awwmf5`. Hash: xem `git log -1`. Bản cho người không chuyên: [STATUS-cho-nguoi-dung.md](STATUS-cho-nguoi-dung.md).

**Đã đối chiếu dự đoán với trận thật?** Chưa. Không có trận nào đủ điều kiện.

## Mảng việc

| Mảng | Trạng thái | Bằng chứng | Kế tiếp |
|---|---|---|---|
| Engine combat (`tft_goat` d5358e9) | Ổn định nội bộ | `results/fixed/combat/` | Trả lời `_GENERIC_ITEM` |
| Bộ dự đoán PRIMARY | n=800, bàn có item 16/398 = 4,02% (đạt) | `model-plan` 11.28 | Không tăng n |
| Lệch bên (mirror) | +0,0075, SE 0,0059, ngưỡng 0,01 | `mirror_check.json` | — |
| Item | 617/731 không có tác động dưới PRIMARY | `item_effect_classes.json` | Mô hình hóa nếu có cấu hình mới |
| Augment | 0/252 đổi xác suất (1 bàn, 1 seed, n=200, không item) | `augment_sweep.json` | Điều tra sâu |
| Học chính sách (Set 17 mô phỏng) | Clone ≈ teacher v4 (luật viết tay). Chưa vượt teacher | `model-plan` 10.6–10.10 | Chưa duyệt bước tiếp |
| Dữ liệu VOD fight-v1 | Cổng đỏ, chưa slot nào đạt. Lô 2026-11-25 đang thu (P1–P10, V1). PR #6 (P4) đã merge 25/11 | `vod-collection.md` | Chờ bản ghi đạt cổng |
| Roadmap Phase 1–6 | P2 xong; P3 bị chặn (chưa chốt nguồn live); P4 chưa bắt đầu; P5 đang làm (mô phỏng); P6 chưa | `nifty` `docs/roadmap.md` | Chốt nguồn live |
| Đường RAM | Không đóng. Người dùng sẽ tự phát triển. Rủi ro: chính sách Riot từ 6/10/2026 chặn app chưa duyệt. Mâu thuẫn Vanguard/OpenProcess mở | `data-sources.md`, trang hỗ trợ Riot | Người dùng quyết khi phát triển |
| Roster Set 18 | Chủ `engine`, advisor quyết (ủy quyền người dùng). `set18.json` trên master | roadmap mục 3 | — |
| Thứ tự tích hợp PR | Đã thực hiện, PR #1–#4 merge 24/11 | GitHub API | — |

## Đang chờ ai

- **Tác giả `tft_goat`:** trả lời `_GENERIC_ITEM` (đã gửi `docs/agents/requests/20261126-engine-generic-item-convention.md`).
- **Người dùng:** chọn nguồn live; cấp khóa Riot API nếu làm Phase 2 Set 18; gửi ảnh EoG (mục 6); xác nhận lại số liệu blitz đã commit; xác nhận lô VOD 2026-11-25 (người duyệt chưa rõ trong tài liệu).
- **Set 19 đang PBE:** cửa sổ thu bản ghi Set 18 thật đang đóng dần.

## Cấu hình đang dùng

PRIMARY (`ability=generic`, items, augments, traits; emblem và alias tắt). n=800, seed0=0. Engine `d5358e9`.

## Thay đổi lần này

- Thêm bộ tài liệu product (`docs/product/`).
- Chốt trạng thái RAM: không đóng (sửa lỗi phiên trước).
- Truy vết và sửa quyết định roadmap ghi sai (`sessions/2026-11-26-truy-vet-quyet-dinh-roadmap.md`).
- Sửa bảng quyết định roadmap (nhánh nifty, `ba387bf9`).
- Tách STATUS thành bản dev và bản người dùng.
