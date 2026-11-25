# Bàn giao: sim (mô phỏng và học chính sách)

- Nhánh: `claude/claude-fable-5-2-awwmf5`
- Commit gần nhất: xem `git log -1` (commit ghi trong nhánh)
- Agent / người: Claude (phiên sim), người điều phối: user
- Ngày: 2026-11-25
- Trạng thái: bị chặn (chờ dữ liệu trạng thái từ `hud`)

## Mục tiêu

Mô hình học chính sách có đo được trên đầu vào thật. Mục tiêu đo: tỷ lệ đồng ý của `decide.js` trên trận giữ lại, chia theo VOD.

## Đã xong

- Clone v5 khớp teacher v4; kiểm định E trên 241000–241999 (xem `tft-sim/README.md`).
- Valuemax vs mặc định: −1,016 [−1,113; −0,913], seed 250000–250999 (lặp lại; xem README).
- Kế hoạch mô hình: `tft-sim/docs/model-plan.md`.
- Thống kê log schema 2 và đếm hành động sơ bộ (mục "Kết quả đo").
- Đường dẫn máy cụ thể trong 5 script đã thay (`diag_*`, `engine_arena.py`, `run_fixed_pipeline.sh`).

## Kết quả đo (log schema 2, `hud` nhánh `claude/hud-data-set18` @ `1b4c468`)

| Thứ đo | Phiên bản | Lệnh | Số mẫu | Kết quả | Ghi chú |
|---|---|---|---|---|---|
| Đếm giao dịch vàng giảm | `1b4c468` | script đếm trong phiên, không lưu trong repo | 2.803 | mua ứng viên 71%, không rõ 21,5%, làm mới ứng viên 5,8%, XP 1,3% | Phân loại thô, chưa kiểm bằng nhãn tay |
| Odds cấp 7 | `1b4c468` | như trên | 70 cửa hàng | xem `docs/agents/requests/20261125-sim-to-engine-set18-odds-xp.md` | Có thiên lệch: ô đã mua, cạn pool, OCR |
| Odds cấp 8 | `1b4c468` | như trên | 208 cửa hàng | khớp bảng Riot (15/20/32/30/3), lệch `rules.js` ở bậc 4 | Cùng nguồn thiên lệch |

Đây là dữ liệu replay từ VOD, chưa đối chiếu với nhãn mù.

## Đang chạy

Không có tiến trình nào.

## Chưa xong / bị chặn

1. **Chặn:** harness Phase 4 (đo đồng ý `decide.js`). `decide.js` cần `hp`, `stage`, `board`, `bench`; log hiện không có HP, bàn, bàn chờ. Gỡ bởi `hud` (`docs/agents/requests/20261125-sim-to-hud-state-fields.md`).
2. Cấp trống ở 9 file VOD (`docs/agents/requests/20261125-sim-to-hud-level-null-vods.md`). Gỡ bởi `hud`.
3. Không dùng `scripts/replay-real-match.js` (nhánh `claude/dazzling-feynman-g7a0b9`) làm baseline: script đọc `captures/extracted-live.jsonl` (không có trong repo), tự sinh vàng theo mốc thời gian và cửa hàng cố định. Đây là mô phỏng, không phải replay log. Ghi nhận để `engine` xử lý. Script cũng chứa một tên người chơi cụ thể trong mã, cần xem lại theo `hygiene.md`.
4. Chờ `engine` trả lời về odds (xem yêu cầu trên).
5. Dữ liệu sim không dùng nhãn thật. Mọi mô hình học trên đây là bắt chước teacher trong môi trường mô phỏng.

## Yêu cầu dữ liệu

- Yêu cầu tôi đã gửi (trên nhánh này):
  - `docs/agents/requests/20261125-sim-to-hud-state-fields.md` — mở
  - `docs/agents/requests/20261125-sim-to-hud-level-null-vods.md` — mở
  - `docs/agents/requests/20261125-sim-to-engine-set18-odds-xp.md` — mở
- Yêu cầu gửi cho tôi đang chờ: không có (quét `docs/agents/requests/` trên các nhánh; không thấy yêu cầu nào hướng `sim`).
- Dữ liệu tôi đã giao: checkpoint `tft-sim/results/checkpoints/clone_v5_seed0.pt` (commit `01d2339`, nhánh `codex/sim-dt`), kết quả E trên `codex/sim-e` (`ff95d66`).
