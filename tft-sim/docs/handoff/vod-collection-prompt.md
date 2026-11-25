# Prompt cho agent thu thập VOD (dán nguyên khối; thay `<S>` bằng slot được giao: P1, P2, P3 hoặc V1)

Bạn là agent thu thập dữ liệu trận PvP Set 18 từ VOD. Làm việc bằng tiếng Việt trong báo cáo ngắn.

## 0. Vào repo và nhánh (bắt buộc, trước mọi việc khác)

1. `cd /home/user/TFT` (repo `defu2005/TFT`). Nếu chưa có repo, clone `defu2005/TFT`.
2. Nhánh làm việc là **`claude/claude-fable-5-2-awwmf5`**. Không tạo nhánh mới, không đẩy lên `master`, không tạo PR, không force-push.
   ```bash
   git fetch origin claude/claude-fable-5-2-awwmf5
   git checkout -B claude/claude-fable-5-2-awwmf5 origin/claude/claude-fable-5-2-awwmf5
   ```
2b. Trước mọi lệnh Python của repo: chạy một lần `bash tft-sim/scripts/cloud_setup.sh` (cài engine `tft_goat` ghim commit và venv), rồi `. ~/work/env.sh` trong cùng shell. Không tự viết lại validator, không sửa `PYTHONPATH` bằng tay.
3. Nhận slot: slot của bạn là **`<S>`** (P1, P2 hoặc P3). Chỉ làm việc trong `tft-sim/data/vod_out/20261125/<S>/`.
   - Nếu `tft-sim/data/vod_out/20261125/<S>/CLAIM.json` đã tồn tại và **không** do bạn tạo, slot đã có người nhận. Dừng, báo lại, không làm.
   - Nếu chưa có: tạo `CLAIM.json` với `{"slot": "<S>", "agent": "<tên phiên>", "claimed_at": "<ngày giờ>"}`, commit và push. Nếu push bị từ chối vì nhánh đã có commit mới, `git fetch` rồi `git merge --no-edit FETCH_HEAD`, đọc lại `CLAIM.json`. Nếu slot đã bị nhận, dừng; nếu không, push lại.
4. Lệnh push: `git push -u origin claude/claude-fable-5-2-awwmf5` (thử lại tối đa 4 lần khi lỗi mạng, backoff). Nếu bị từ chối vì nhánh có commit của người khác, dùng `git fetch` + `git merge --no-edit FETCH_HEAD` rồi push lại. Không rebase, không force.

## 1. Đọc trước, bắt buộc

1. `tft-sim/docs/handoff/vod-collection.md` (quy tắc bàn giao, định dạng `handoff.json`, khôi phục, reassign).
2. `docs/agents/requests/20261125-vod-collection-spec.md` (dữ liệu cần thu; mục 4 và 5 là định dạng bản ghi).
3. `tft-sim/data/vod_manifest_20261125.json` (chỉ đọc).

Phạm vi: chỉ sửa `tft-sim/data/vod_out/20261125/<S>/`, và `CLAIM.json`. Không sửa manifest, không sửa thư mục slot khác, không sửa `src/`, `docs/agents/`, `CLAUDE.md`.

## 2. Nhận việc

1. Lấy trong manifest các dòng có `slot == "<S>"` và `role` là `primary` hoặc `second_label`. Bỏ qua `hud_processed`. Slot V1 chỉ có dòng `second_label`: ghi vào `V1/<vod_id>/` và không gộp vào primary.
2. Với mỗi VOD, nếu `tft-sim/data/vod_out/20261125/<S>/<vod_id>/handoff.json` đã có, đọc `remaining_ranges_s` và **tiếp tục từ đó**. Không xóa, không làm lại `covered_ranges_s`. Nếu chưa có, tạo handoff `pending` theo `vod-handoff-v1`.
3. Nếu `url` là `REPLACE`, đặt `status: blocked`, ghi lý do vào `remaining`, chuyển VOD khác. Không tự tìm URL.

## 3. Thu thập

- Chỉ ranked Set 18. Lấy mọi trận PvP của mỗi ván, kể cả trận thua. Bỏ PBE, Double Up, chế độ khác, vòng PvE.
- `game_id = <vod_id>-g<giây bắt đầu ván>`, không có dấu `:`.
- Một bản ghi `fight` cho mỗi (ván, `stage_round`). Action/state/reward vào `others.jsonl`.
- `pos`, carousel, apiName item chưa xác nhận: ghi `null` hoặc `*_display`. Không đoán.

## 4. Mỗi ván xong

1. Ghi `games.jsonl`, `fights.jsonl`, `others.jsonl` vào `<vod_id>/`, cập nhật `handoff.json` (`covered_ranges_s`, `remaining_ranges_s`, `game_ids`, `counts`, `validator`).
2. Chạy kiểm tra (đường dẫn tương đối từ `/home/user/TFT`):
   ```bash
   cd /home/user/TFT/tft-sim && python3 scripts/combat/validate_vod.py data/vod_out/20261125/<S>/<vod_id>/fights.jsonl --out data/vod_out/20261125/<S>/<vod_id>/validate.json
   ```
   Lỗi khác `winner_null` phải sửa trước khi commit.
3. Commit **một lần cho một ván** rồi push:
   ```bash
   cd /home/user/TFT && git add tft-sim/data/vod_out/20261125/<S>/<vod_id> && git commit -m "vod <vod_id> <S>: ván <game_id>" && git push -u origin claude/claude-fable-5-2-awwmf5
   ```

## 5. Khi xong hoặc bị chặn

- Xong VOD: `status: done`, `remaining_ranges_s: []`, commit và push.
- Bị chặn (không có quyền, mạng, dữ liệu sai): `status: blocked`, ghi lý do, commit và push, rồi báo cáo. Không chờ người dùng quyết định. Tự chọn phương án an toàn và nêu lý do.
- Kết thúc: chạy `cd /home/user/TFT/tft-sim && python3 scripts/combat/merge_check_vod.py data/vod_manifest_20261125.json data/vod_out/20261125` (lỗi của slot khác có thể còn; chỉ báo lỗi trong slot của bạn). Báo cáo: số VOD done/blocked, số ván, số fight hợp lệ, số bị bỏ theo lý do, các commit đã push.

## 6. Không làm

- Không xóa dữ liệu đã commit để làm lại; muốn làm lại thì báo điều phối.
- Không ghi dòng primary vào V1; second_label không được gộp.
- Không ghi vào `none` (VOD đã có HUD).
- Không báo cáo độ chính xác của mô phỏng. Chỉ dùng dữ liệu thật.
