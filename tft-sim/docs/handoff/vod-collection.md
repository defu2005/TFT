# Bàn giao thu thập VOD (nhiều agent chạy song song)

Áp dụng cho lô `2026-11-25-set18-vod`. Đặc tả dữ liệu: `docs/agents/requests/20261125-vod-collection-spec.md`. Prompt để dán cho từng agent: `vod-collection-prompt.md`. Tài liệu này định nghĩa cách các agent không đọc trùng và không ghi chồng.

## 1. Đơn vị công việc và định danh

- **Đơn vị công việc là một VOD.** `vod_id` = `<nền tảng>-<id video>`, ví dụ `twitch-2924500482`. Regex: `^(twitch-\d+|youtube-[A-Za-z0-9_-]+)$`.
- **`game_id` = `<vod_id>-g<số>`**, số là giây bắt đầu của ván trong VOD, ví dụ `twitch-2924500482-g3612`. Không có `:` (vì `fidelity._game()` tách theo `:`).
- **`source` = `<game_id>:<stage_round>`** trong dữ liệu thô. Ingest viết lại thành `<lobby_id>:<stage_round>` trước khi chấm.
- **`fight_key`** = `game_id|stage_round|tên_a|tên_b` (tên đã sắp xếp).
- Mỗi VOD chỉ có một `game_id` cho mỗi ván. Hai streamer cùng lobby có hai `game_id` khác nhau; khu trùng là việc của ingest (mục 6).

## 2. Manifest: chỉ điều phối ghi, agent chỉ đọc

- File: `tft-sim/data/vod_manifest_20261125.json`. Chỉ người điều phối commit file này. Agent không sửa, không đọc nó để quyết định ghi đè.
- Mỗi streamer nằm ở **đúng một slot primary** (`P1`…`P6` và các slot primary khác trong manifest). Kiểm bằng `streamer_multi_slot`.
- **Mở rộng 2026-11-25 (goal ≥1000 ván):** điều phối thêm slot `P4` (wasianiverson), `P5` (souless), `P6` (cambulee) — không trùng streamer P1–P3. Agent thu thập nhận slot qua `CLAIM.json` như cũ.
- `role`:
  - `primary`: ghi dữ liệu thô vào slot của mình.
  - `second_label`: nhãn đối chiếu. Ghi vào slot `V1`, không bao giờ vào đường primary.
  - `hud_processed`: slot `none`. VOD đã có dữ liệu từ HUD, **agent không được ghi gì**.
- URL có giá trị `REPLACE` là chưa có VOD thật. Agent dừng ở VOD đó, ghi `status: blocked` vào handoff và báo lại. Không tự tìm hay đoán URL.

## 3. Phân vùng để các shard rời nhau

- Agent của slot `S` chỉ ghi vào `tft-sim/data/vod_out/20261125/<S>/<vod_id>/`.
- Agent không đọc thư mục slot khác để quyết định việc của mình. Việc chồng khoảng giữa các slot được kiểm ở bước gộp.
- Tất cả agent làm việc trên nhánh `claude/claude-fable-5-2-awwmf5` (phiên không có nhánh giao sẵn; agent tự vào nhánh theo prompt). Không force-push, không tạo PR. Xung đột push được xử lý bằng `git fetch` và `git merge --no-edit FETCH_HEAD`, không rebase.
- Nhận slot bằng `CLAIM.json` trong thư mục slot (xem prompt). Slot đã có `CLAIM.json` của người khác thì không làm.

## 4. Layout đầu ra

```
tft-sim/data/vod_out/20261125/<S>/<vod_id>/
    handoff.json     vod-handoff-v1 (mục 5). Nguồn sự thật về tiến độ.
    games.jsonl      loại game (mục 4 của spec)
    fights.jsonl     loại fight, fight-v1, nhãn real
    others.jsonl     các loại khác (action, state, reward, ...)
```

- **Một bản ghi fight cho mỗi (ván, stage_round)** trong một VOD. `merge_check_vod.py` coi hai dòng cùng `source` là lỗi.
- `others.jsonl` không được trộn vào `fights.jsonl`.

## 5. Bản ghi bàn giao `vod-handoff-v1` (`handoff.json`)

```json
{
  "schema": "vod-handoff-v1",
  "vod_id": "twitch-2924500482",
  "slot": "P1",
  "role": "primary",
  "status": "working",
  "covered_ranges_s": [[210, 1500]],
  "remaining_ranges_s": [[1500, 2940]],
  "game_ids": ["twitch-2924500482-g210"],
  "counts": {"games": 1, "fights": 4, "others": 0},
  "validator": {"ok": 4, "skipped": {}},
  "needs_review": 0,
  "commit": "abc1234",
  "remaining": "tiếp tục từ 1500 s"
}
```

- `status`: `pending` | `working` | `done` | `blocked` | `stale`. Chỉ agent của slot đó được đặt `done` hoặc `working`. `stale` do điều phối đặt khi reassign.
- `covered_ranges_s` là các khoảng **đã xử lý xong** (đã commit). `remaining_ranges_s` là phần còn lại của `candidate_ranges_s` trong manifest. Hai danh sách không được chồng nhau trong cùng handoff (`overlap_within_slot`).
- Tiến độ chỉ đọc từ `handoff.json`, **không** đọc trường `status` trong manifest.
- `needs_review`: số fight để sang `*_needs_review` (xem spec 11.1).

## 6. Quy trình của agent

1. Đọc manifest, lấy các dòng `slot == <S>` và `role in (primary, second_label)`, bỏ qua `hud_processed`.
2. Với mỗi VOD: nếu `handoff.json` đã có, đọc `remaining_ranges_s` và **tiếp tục từ đó**. Không xóa và không làm lại `covered_ranges_s`. Nếu chưa có, tạo handoff `pending`.
3. Xử lý từng ván xong thì: ghi `games.jsonl`, `fights.jsonl`, `others.jsonl`, cập nhật `handoff.json`, chạy `validate_vod.py` trên `fights.jsonl`, rồi **commit và push** thư mục VOD. Một ván một commit.
4. Khi hết VOD: đặt `status: done`, `remaining_ranges_s: []`, commit và push lần cuối.
5. Lệnh kiểm tra:
   ```bash
   cd tft-sim
   python3 scripts/combat/validate_vod.py data/vod_out/20261125/<S>/<vod_id>/fights.jsonl --out /tmp/x.json
   ```
   Lỗi khác `winner_null` phải sửa trước khi commit.

### Khôi phục khi restart

- Agent mới đọc `handoff.json` của mọi VOD thuộc slot, tiếp tục theo `remaining_ranges_s`.
- Không bao giờ xóa dữ liệu đã commit để làm lại. Muốn làm lại thì điều phối đặt `stale` và cấp slot mới.

### Reassign

- Điều phối sửa manifest (đổi `slot`) và `git mv` thư mục từ `<S_cũ>/<vod_id>` sang `<S_mới>/<vod_id>` trong **một commit**. Agent mới tiếp tục từ `handoff.json`.
- Thư mục cũ không được để lại. Nếu còn, `overlap_across_slots` sẽ bắt. Ca này đã có trong selftest (`tai_phan_cong`).

## 7. Second label

- Ghi vào `V1/<vod_id>/` đúng layout mục 4. Không đưa vào gộp primary (`merge_check_vod.py` chỉ dùng các handoff primary để gộp, các khoảng second chỉ dùng để đối chiếu).
- Đối chiếu nhãn (spec 10.3) là việc của người ghép, không phải của agent thu thập.

## 8. Gộp và khử trùng

- Gộp kiểm lỗi: `python3 scripts/combat/merge_check_vod.py data/vod_manifest_20261125.json data/vod_out/20261125 --report data/vod_out/20261125-merge.json`. Thoát 0 khi không có ERR.
- Các mã WARN:
  - `shared_lobby_needs_ingest`: cùng lobby ở hai VOD, bắt buộc khử trùng khi ingest.
  - `duplicate_fight_key_needs_ingest`: cùng (lobby, stage, cặp) ở hai VOD, giữ một bản.
  - `lobby_partial_overlap`: hai lobby chung 4–7 tên, kiểm tay.
- **Khử trùng ingest chưa được cài đặt.** Đặc tả ở spec 10.2: khóa lobby = sha1 của 8 tên đã chuẩn hóa (NFC, casefold, bỏ khoảng trắng), giữ một fight cho mỗi (lobby, stage, cặp), viết lại `source` thành `<lobby_id>:<stage>`, và gộp cluster theo `lobby_id` khi tính khoảng tin cậy (spec 10.1). Chỉ khi có script ingest thì mới được chấm điểm.

## 9. Không làm

- Không ghi vào thư mục slot khác, không ghi vào `none`, không sửa `vod_manifest_20261125.json`.
- Không tự quyết định `pos`, carousel, apiName item chưa xác nhận (spec mục 12). Ghi `null` hoặc `*_display`.
- Không báo cáo độ chính xác từ mẫu mô phỏng. Chỉ dùng dữ liệu thật.
