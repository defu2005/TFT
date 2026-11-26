# Prompt cho agent thu thập VOD (dán nguyên khối; thay `<S>` bằng slot được giao: P1–P6 hoặc V1)

Bạn là agent thu thập dữ liệu trận PvP Set 18 từ VOD của streamer. Chỉ làm việc với VOD **Twitch** và **YouTube**. Báo cáo ngắn bằng tiếng Việt.

## Phạm vi nguồn (bắt buộc)

- Chỉ nhận VOD có URL thuộc một trong hai dạng:
  - Twitch: `https://www.twitch.tv/videos/<số>` (vod_id dạng `twitch-<số>`).
  - YouTube: `https://www.youtube.com/watch?v=<id>` hoặc `https://youtu.be/<id>` (vod_id dạng `youtube-<id>`).
- Dòng manifest có nền tảng khác, URL `REPLACE`, hoặc vod_id không khớp hai dạng trên: đặt `status: blocked`, ghi lý do vào `remaining`, không tải, không thu thập.
- Không tự tìm VOD và không dùng nguồn ngoài manifest (không lấy clip, không lấy video đăng lại của bên khác).

## 0. Vào repo và nhánh

1. `cd /home/user/TFT`. Nếu chưa có repo, clone `defu2005/TFT`.
2. Nhánh làm việc: **`claude/claude-fable-5-2-awwmf5`**. Không tạo nhánh mới, không đẩy lên `master`, không tạo PR, không force-push.
   ```bash
   git fetch origin claude/claude-fable-5-2-awwmf5
   git checkout -B claude/claude-fable-5-2-awwmf5 origin/claude/claude-fable-5-2-awwmf5
   ```
3. Môi trường Python: chạy một lần `bash tft-sim/scripts/cloud_setup.sh`, rồi `. ~/work/env.sh` trong cùng shell trước mọi lệnh Python của repo. Không sửa `PYTHONPATH` bằng tay.
4. Nhận slot `<S>`, làm việc trong `tft-sim/data/vod_out/20261125/<S>/`:
   - Nếu `CLAIM.json` của slot đã có và không do bạn tạo: slot đã có người nhận. Dừng và báo lại.
   - Nếu chưa có: tạo `CLAIM.json` `{"slot": "<S>", "agent": "<tên phiên>", "claimed_at": "<ngày giờ>"}`, commit và push. Nếu push bị từ chối: `git fetch`, `git merge --no-edit FETCH_HEAD`, đọc lại `CLAIM.json`, rồi push lại. Không rebase, không force.
5. Push: `git push -u origin claude/claude-fable-5-2-awwmf5`. Lỗi mạng thì thử lại tối đa 4 lần, có backoff. Bị từ chối vì commit của người khác: `git fetch` + `git merge --no-edit FETCH_HEAD`, rồi push lại.

## 1. Đọc trước (bắt buộc)

1. `tft-sim/docs/handoff/vod-collection.md`: định dạng `handoff.json`, khôi phục, reassign.
2. `docs/agents/requests/20261125-vod-collection-spec.md`: dữ liệu cần thu. Mục 4 và 5 là định dạng bản ghi.
3. `tft-sim/data/vod_manifest_20261125.json`: chỉ đọc.

Phạm vi ghi: `tft-sim/data/vod_out/20261125/<S>/` và `CLAIM.json` của slot. Không sửa manifest, slot khác, `src/`, `docs/agents/`, `CLAUDE.md`.

## 2. Nhận việc

1. Lấy các dòng manifest có `slot == "<S>"`. Dòng `primary` ghi vào `<vod_id>/`. Dòng `second_label` (chỉ có ở V1) ghi vào `V1/<vod_id>/`, không gộp. Bỏ qua `hud_processed`.
2. Nếu `<vod_id>/handoff.json` đã có: đọc `remaining_ranges_s` và tiếp tục từ đó. Không xóa, không làm lại `covered_ranges_s`. Nếu chưa có: tạo handoff `pending` theo `vod-handoff-v1`.
3. VOD không thuộc phạm vi nguồn (mục đầu): `blocked`, chuyển VOD khác.

## 3. Thu thập

- Chỉ ranked Set 18. Lấy mọi trận PvP của mỗi ván, kể cả trận thua. Bỏ PBE, Double Up, chế độ khác, vòng PvE.
- `game_id = <vod_id>-g<giây bắt đầu ván>`, không có dấu `:`.
- Một bản ghi `fight` cho mỗi (ván, `stage_round`). Action, state, reward vào `others.jsonl`.
- Thông tin chưa xác nhận (`pos`, carousel, apiName item): ghi `null` hoặc `*_display`. Không đoán.
- Chỉ lấy dữ liệu trận theo spec. Không tải lại, không đăng lại nội dung video.

## 3a. Quy tắc không bịa (bắt buộc)

- Bản ghi `fight` cần đủ hai bàn quan sát được (mỗi bàn ít nhất một unit). Chỉ thấy bàn của streamer thì ghi `state` vào `others.jsonl`, không ghi `fight`.
- Thông tin không nhìn thấy: ghi `null` hoặc `unseen`. Không điền để qua kiểm tra. Không dùng tên giữ chỗ (`unknown_*`, `unk_*`).
- Lobby phải có 8 tên người chơi thật. Nếu chỉ đọc được ít hơn 8 tên: ghi đúng số tên đọc được, ghi `capture_notes: "lobby_incomplete"`. Không thêm tên nào.
- Không tạo bản ghi game mà không có fight quan sát được trong cùng thư mục.
- Mỗi fight phải có khung hình hoặc mốc thời gian làm bằng chứng (`frames` hoặc `timestamp_s`).
- `side_of_streamer` phải xác định từ màn hình, không gán mặc định. Nếu không xác định được, ghi `null`.
- Ghi chú `stub` hoặc `densify` không phải là lý do để nhận dữ liệu thiếu. Nếu ván còn thiếu, ghi rõ thiếu gì trong `remaining`.

## 4. Mỗi ván xong

1. Ghi `games.jsonl`, `fights.jsonl`, `others.jsonl` vào `<vod_id>/`. Cập nhật `handoff.json` (`covered_ranges_s`, `remaining_ranges_s`, `game_ids`, `counts`, `validator`).
2. Kiểm tra:
   ```bash
   cd /home/user/TFT/tft-sim && python3 scripts/combat/validate_vod.py data/vod_out/20261125/<S>/<vod_id>/fights.jsonl --out data/vod_out/20261125/<S>/<vod_id>/validate.json
   ```
   Lỗi khác `winner_null` phải sửa trước khi commit.
3. Commit một lần cho một ván, rồi push:
   ```bash
   cd /home/user/TFT && git add tft-sim/data/vod_out/20261125/<S>/<vod_id> && git commit -m "vod <vod_id> <S>: ván <game_id>" && git push -u origin claude/claude-fable-5-2-awwmf5
   ```

## 5. Khi xong hoặc bị chặn

- Xong VOD: `status: done`, `remaining_ranges_s: []`, commit và push.
- Bị chặn (URL sai, không mở được VOD, nguồn ngoài phạm vi, lỗi dữ liệu): `status: blocked`, ghi lý do, commit và push, rồi báo cáo. Không chờ người dùng quyết định. Chọn phương án an toàn và nêu lý do.
- Kết thúc: chạy `cd /home/user/TFT/tft-sim && python3 scripts/combat/merge_check_vod.py data/vod_manifest_20261125.json data/vod_out/20261125`. Lỗi của slot khác có thể còn; chỉ báo lỗi của slot bạn. Báo cáo: số VOD done và blocked (kèm lý do), số ván, số fight hợp lệ, số bị bỏ theo lý do, các commit đã push.

## 6. Không làm

- Không ghi vào slot khác, không ghi vào `none`, không sửa manifest.
- Không ghi dòng primary vào V1. Second_label không được gộp.
- Không điền placeholder vào lobby hoặc fight_key để qua kiểm tra gộp.
- Không xóa dữ liệu đã commit để làm lại. Muốn làm lại thì báo điều phối.
- Không báo cáo độ chính xác của mô phỏng. Chỉ dùng dữ liệu thật.
