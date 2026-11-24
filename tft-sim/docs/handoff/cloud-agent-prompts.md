# Prompt giao việc cho Codex và Cursor (workstream `sim`)

Đọc `docs/handoff/cloud-agents.md` trước khi tạo phiên. File đó có quy tắc, sổ seed và thông số.

## A. Trước khi tạo phiên (người dùng làm một lần)

1. Chọn **nhánh gốc** là `claude/claude-fable-5-2-awwmf5` (chứa `tft-sim/scripts/collect_v4.py`, `cloud_setup.sh`, `merge_v4.py`).
2. Tạo nhánh riêng cho từng phiên, từ nhánh gốc, và đặt tên như sau:
   - DT: `sim-dt`
   - C: `sim-c`
   - R: `sim-r`
   - E: `sim-e` (**tạo sau khi DT đã push**, nhánh gốc của E là `sim-dt`)
3. Cài đặt môi trường cho phiên (mục B).

## B. Cài đặt môi trường

Cả hai dịch vụ đều dùng cùng một lệnh cài đặt:

```bash
bash tft-sim/scripts/cloud_setup.sh
```

**Codex Cloud** (theo tài liệu đã đọc, có xác nhận một phần):
- Tạo môi trường mới, chọn repo `defu2005/TFT`.
- Đặt **Install script** = lệnh trên.
- **Network:** bật "Package managers". Thêm domain nếu cần: `download.pytorch.org`, `github.com`. Lưu ý: agent phase mặc định **không** có internet, nên mọi việc tải về phải nằm trong install script. Các vai DT, C, E chỉ cần máy cục bộ nên không cần thêm.
- Publish môi trường để dùng lại.
- *Chưa xác nhận:* tên chính xác các nút trên giao diện hiện tại có thể khác. Trang "Codex Cloud (Legacy)" nói setup script chạy có internet, agent phase tắt mặc định.

**Cursor Cloud Agents** (theo `cursor.com/docs/cloud-agent/setup`):
- Tạo môi trường mới trong dashboard Cloud Agents, chọn repo `defu2005/TFT`.
- Đặt **install** = lệnh trên. Cursor chạy install khi tạo Build, trước khi agent bắt đầu, và yêu cầu install **idempotent** (script này đã như vậy).
- Vai R cần internet để tra cứu nguồn; Cursor phù hợp hơn Codex cho việc này.
- *Chưa xác nhận:* Cursor có cho chọn nhánh khi tạo phiên hay không. Nếu không, phiên sẽ tự tạo nhánh; khi đó người dùng đổi tên hoặc gửi lại nhánh.

Mỗi lần chạy sim trong phiên, agent tự đặt biến môi trường (mục 1 của `cloud-agents.md`).

---

## Prompt DT (thu dữ liệu, gộp, huấn luyện)

```
Bạn là agent DT cho dự án TFT (workstream sim). Nhánh được giao: sim-dt.

Bước 0 (bắt buộc): kiểm tra file tft-sim/scripts/collect_v4.py và tft-sim/docs/handoff/cloud-agents.md có trong repo. Nếu thiếu, dừng và báo "nhánh sai", không làm gì thêm.

Đọc trước: tft-sim/docs/handoff/cloud-agents.md (mục 0–6). Đó là nguồn chuẩn.

Môi trường: đã cài bằng bash tft-sim/scripts/cloud_setup.sh. Trước mỗi lệnh sim, chạy:
  . ~/work/venv/bin/activate
  export PYTHONPATH="$PWD/tft-sim/src:$HOME/work/tft_goat/src"
  export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
Nếu lệnh cài đặt chưa chạy hoặc `import tft_goat` lỗi, chạy lại bash tft-sim/scripts/cloud_setup.sh; nếu vẫn lỗi, dừng và báo log.

Các bước:
1. Thu 4 shard song song (từ thư mục tft-sim):
   mkdir -p ~/work/data
   python scripts/collect_v4.py 300000 300500 ~/work/data/s1.npz &
   python scripts/collect_v4.py 300500 301000 ~/work/data/s2.npz &
   python scripts/collect_v4.py 301000 301500 ~/work/data/s3.npz &
   python scripts/collect_v4.py 301500 302000 ~/work/data/s4.npz &
   wait
   Mỗi tiến trình phải in DONE. Ghi thời gian và RAM đỉnh.
2. Kiểm tra tái lập: chạy lại python scripts/collect_v4.py 300000 300002 ~/work/data/check.npz. Lọc s1.npz theo seed 300000–300001 và so sánh action và số dòng với check.npz (phải giống hệt). Nếu khác, dừng và báo.
3. Gộp và chia:
   python scripts/merge_v4.py ~/work/data/split ~/work/data/s1.npz ~/work/data/s2.npz ~/work/data/s3.npz ~/work/data/s4.npz
   In ra số dòng train/val/test. Nếu shard nào bị LOAI, dừng và báo.
4. Huấn luyện clone v5:
   python scripts/bc_v4.py ~/work/data/split v5
   Ghi kết quả vào results/fixed/real/bc_v5.json và checkpoint ~/work/data/split/clone_v5_seed0.pt.
   Huấn luyện mất khoảng 20 phút mỗi seed. Sau 10 phút đầu, báo thời gian thực tế.
5. Lưu checkpoint vào repo: mkdir -p tft-sim/results/checkpoints && cp ~/work/data/split/clone_v5_seed0.pt tft-sim/results/checkpoints/ (kiểm tra dung lượng dưới 1 MB; nếu lớn hơn, dừng và báo).
6. Viết tft-sim/results/fixed/real/shard_summary.json gồm: seeds, số dòng từng shard và từng tập, sha256 của s1–s4 và split/*.npz, commit_tft (git rev-parse HEAD), commit_tft_goat (git -C ~/work/tft_goat rev-parse HEAD), ram_peak_mb, wall_seconds, check_results (kết quả 5 kiểm tra trong mục 3 của cloud-agents.md).
7. Commit các file: results/fixed/real/bc_v5.json, results/fixed/real/shard_summary.json, results/checkpoints/clone_v5_seed0.pt. KHÔNG commit .npz. Push lên sim-dt.

Ràng buộc: không dùng seed ngoài 300000–301999; không sửa src/, ingest/, master; không tạo PR.

Báo cáo cuối (ngắn):
- số dòng train/val/test;
- bảng accuracy overall của 3 seed (min–max) và theo loại trên tập test;
- kết quả kiểm tra tái lập;
- RAM đỉnh, thời gian thu và huấn luyện;
- tên nhánh và commit hash.
```

## Prompt C (CEM trang bị, nhiều thế hệ hơn)

```
Bạn là agent C cho dự án TFT (workstream sim). Nhánh được giao: sim-c.

Bước 0: kiểm tra tft-sim/scripts/cem_item.py có trong repo. Nếu thiếu, dừng và báo "nhánh sai".

Đọc trước: tft-sim/docs/handoff/cloud-agents.md (mục 0, 2, 5).

Môi trường: đã cài bằng bash tft-sim/scripts/cloud_setup.sh. Trước mỗi lệnh sim, chạy:
  . ~/work/venv/bin/activate
  export PYTHONPATH="$PWD/tft-sim/src:$HOME/work/tft_goat/src"
  export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1

Các bước (từ thư mục tft-sim):
1. Chạy CEM với 6 thế hệ, 12 ứng viên, dev 220000–220199, giữ-lại 240000–240999:
   python scripts/cem_item.py 6 12 220000 220200 results/fixed/real/cem_item_v2.json 240000 241000
   Chạy trong nền và ghi log ra file. Ước tính khoảng 1,5 giờ. Nếu gần hết thời gian phiên, giảm số thế hệ và ghi lại đã giảm bao nhiêu.
2. Đọc file JSON. Báo: best_fit và mean_fit từng thế hệ, trọng số cuối, held_mean_A_minus_B và held_ci95.
3. Lưu ý: script đã tự so sánh chính sách học được với mặc định trên 240000–240999. Chưa có so sánh với valuemax. Chạy thêm: python scripts/item_target_probe.py valuemax default 240000 241000 (đây là hiệu valuemax trừ default, số âm nghĩa là valuemax tốt hơn). Báo CI95 của hiệu. Lưu ý: lệnh trên so valuemax với default, chưa so chính sách CEM học được với valuemax. Nếu không có cách chạy trực tiếp trọng số w với scripts có sẵn, báo "chưa so sánh được CEM với valuemax" và không tự viết mã so sánh mới trong phiên.
4. Kết luận rõ một trong ba: học được vượt valuemax (CI95 nằm hoàn toàn dưới 0), ngang valuemax (CI95 chứa 0), hoặc kém valuemax (CI95 nằm hoàn toàn trên 0).

Ràng buộc: không dùng seed 230000–230999 (đã dùng) hay 241000+ (dành cho E); không sửa src/, ingest/, master; không tạo PR; không chọn tham số trên 240000–240999 rồi báo lại như kết quả giữ-lại.

Commit: results/fixed/real/cem_item_v2.json và các JSON so sánh. Push lên sim-c.

Báo cáo cuối: bảng thế hệ, trọng số cuối, hiệu trên 240000–240999 kèm CI95, so sánh valuemax, kết luận, nhánh và commit hash.
```

## Prompt R (nghiên cứu Set 18)

```
Bạn là agent R cho dự án TFT (workstream sim). Nhánh được giao: sim-r.

Bước 0: kiểm tra tft-sim/docs/handoff/set18-sources.md có trong repo. Nếu thiếu, dừng và báo "nhánh sai".

Đọc trước: tft-sim/docs/handoff/set18-sources.md. Ghi rõ những ô còn thiếu hoặc mâu thuẫn.

Mục tiêu:
1. XP cấp 2→3, 3→4, 4→5, 5→6, 6→7 cho Set 18.
2. Dòng cấp 7 của tỉ lệ cửa hàng: đối chiếu hai nguồn (19/30/40/10/1 và 16/30/43/10/1), ghi nguồn nào tin được hơn và vì sao.
3. Tướng và tộc Set 18 bản 18.7: xác nhận Ivern, Kennen, Kruggs và các thay đổi khác.

Nguồn ưu tiên: trang Riot chính thức (teamfighttactics.leagueoflegends.com). Nguồn cộng đồng chỉ để đối chiếu, và phải ghi rõ là cộng đồng.

Quy tắc:
- Không bịa số. Ô nào không có nguồn thì ghi "không có nguồn".
- Mỗi số kèm URL và một câu trích chứng minh.
- Không vượt qua chặn truy cập (403, chặn bot, yêu cầu JavaScript). Ghi lại và chuyển sang nguồn khác.
- Không sửa src/, ingest/, src/data/set18.json.

Đầu ra: cập nhật tft-sim/docs/handoff/set18-sources.md. Commit lên sim-r. Không tạo PR.

Báo cáo cuối: đã tìm được gì, còn thiếu gì, mâu thuẫn giữa các nguồn, nhánh và commit hash.
```

## Prompt E (kiểm định clone v5, chỉ sau khi DT xong)

```
Bạn là agent E cho dự án TFT (workstream sim). Nhánh được giao: sim-e. Nhánh gốc của phiên này là sim-dt (đã có checkpoint).

Bước 0: kiểm tra tft-sim/results/checkpoints/clone_v5_seed0.pt có trong repo. Nếu thiếu, dừng và báo "DT chưa xong".

Đọc trước: tft-sim/docs/handoff/cloud-agents.md (mục 0, 2, 5).

Môi trường: đã cài bằng bash tft-sim/scripts/cloud_setup.sh. Trước mỗi lệnh sim, chạy:
  . ~/work/venv/bin/activate
  export PYTHONPATH="$PWD/tft-sim/src:$HOME/work/tft_goat/src"
  export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1

Các phép (mỗi phép 1000 ván, seed 241000–241999, chưa dùng). Từ thư mục tft-sim, checkpoint là results/checkpoints/clone_v5_seed0.pt:
- python scripts/play_v4.py v4null results/checkpoints/clone_v5_seed0.pt 241000 242000 v5
- python scripts/play_v4.py clone_v4 results/checkpoints/clone_v5_seed0.pt 241000 242000 v5
- python scripts/play_v4.py clone_v3 results/checkpoints/clone_v5_seed0.pt 241000 242000 v5
- python scripts/play_v4.py clone_scr results/checkpoints/clone_v5_seed0.pt 241000 242000 v5
Tối đa 4 tiến trình song song. Mỗi tiến trình ghi results/fixed/real/play_v5_<mode>.json.

Lưu ý: v4null là kiểm tra âm (v4 với v4, kỳ vọng CI chứa 0). Các phép còn lại: clone_v4 kỳ vọng CI chứa 0 nếu clone bắt chước được v4; clone_v3 và clone_scr kỳ vọng hiệu âm nếu clone tốt hơn.

Tính CI95 bằng bootstrap 2000 lần trên per_lobby_diff_A_minus_B (cùng cách với README).

Ràng buộc: không chọn tham số hay checkpoint trên 241000–241999; không chạy lại với seed khác để tìm kết quả đẹp; không sửa src/, ingest/; không tạo PR.

Báo cáo cuối: bảng 4 phép (hiệu, CI95, n, số lượt đi không hợp lệ nếu có), kết luận đạt/không đạt từng tiêu chí, nhánh và commit hash.
```

---

## Ghi chú cho người dùng

- Phiên DT và phiên C, R có thể chạy song song ngay. Phiên E phải đợi DT push xong.
- Nếu một dịch vụ không cho chọn nhánh khi tạo phiên, dán tên nhánh vào prompt và yêu cầu agent đổi nhánh ngay đầu phiên (bước 0 kiểm tra nhánh).
- Vai P (định vị) chưa giao. Chỉ giao khi C và E đã có kết quả.
</content>
