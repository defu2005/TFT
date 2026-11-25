# Handoff cho agent cloud (Codex / Cursor): thu dữ liệu, huấn luyện, kiểm định (workstream `sim`)

Dành cho agent chạy trên Codex Cloud hoặc Cursor Cloud Agents. Mỗi phiên nhận một vai (mục 4) và prompt tương ứng ở `cloud-agent-prompts.md`. Đọc mục 0–3 trước khi bắt đầu.

Mỗi phiên chạy trên máy riêng, tạm thời, và **không chia sẻ file với phiên khác**. Vì vậy thu dữ liệu và huấn luyện được gộp trong cùng một phiên (vai DT). Chỉ checkpoint nhỏ và JSON đi giữa các phiên, qua git.

## 0. Quy tắc cứng

- **Phạm vi:** chỉ sửa `tft-sim/` trên nhánh được giao. Không sửa `src/`, `ingest/`, live coach, `master`, `docs/agents/`, `CLAUDE.md`, `AGENTS.md`, hoặc `.cursor/`, `.codex/` ở gốc repo.
- **Nhánh:** commit và push **chỉ** lên nhánh mà người dùng đặt khi tạo phiên. Nếu phiên không có nhánh được giao, dừng và hỏi. Không tạo PR nếu người dùng không yêu cầu. Không force-push.
- **Không commit dữ liệu lớn:** `.npz` giữ ngoài git (thư mục `~/work/data`). Checkpoint `.pt` dưới 1 MB (ước tính ~190 KB) được commit vào `tft-sim/results/checkpoints/`. Chỉ commit JSON kết quả và summary.
- **Không bịa số.** Mọi số báo cáo lấy từ file kết quả, kèm seed range.
- **Không dùng seed đã đóng** (mục 2).
- **Không lộ bí mật** vào commit, log, hay request ra ngoài.

## 1. Môi trường

Cài đặt: Codex dùng `bash tft-sim/scripts/cloud_setup.sh` (xem `cloud-agent-prompts.md` mục B). Cursor dùng lệnh tự chứa trong cùng mục B, vì Build chạy trên nhánh mặc định.

```bash
bash tft-sim/scripts/cloud_setup.sh
```

Script này (đã kiểm thử trên clone sạch của nhánh):
- clone `MielPopsssssss/tft_goat` (công khai, không cần đăng nhập) và ghim commit `d5358e94`;
- tạo venv tại `~/work/venv`, cài numpy, pydantic, httpx, riotwatcher, gymnasium, pettingzoo, pytest, torch CPU;
- kiểm tra nhập được `tft_goat`, `tft_sim`, `torch`.

Script ghi `~/work/env.sh` với đường dẫn tuyệt đối. Trước mỗi lệnh sim, agent chạy `. ~/work/env.sh` (script không giữ được biến môi trường sang shell của agent).

**Bắt buộc `OMP_NUM_THREADS=1`** khi chạy nhiều tiến trình. Không có nó, torch tranh CPU và chạy chậm nhiều lần.

Kiểm tra nhanh (dùng seed thử 900000–900001, không thuộc dữ liệu):
```bash
cd tft-sim && python scripts/collect_v4.py 900000 900002 /tmp/smoke.npz
```
Đã đo: 2 ván ra 5.918 dòng, khoảng 3 giây. Chạy hai lần cho kết quả giống hệt.

## 2. Sổ seed

| Dải seed | Dùng cho | Trạng thái |
|---|---|---|
| 20000–21999 | tinh chỉnh | đã dùng |
| 30000–31999 | giữ-lại cũ | đã dùng |
| 40000–41999 | sàng loại cũ | đã dùng |
| 50000–51999 | BENCH_BOARD | đã dùng |
| 60000–61999 | giữ-lại v3 | đã dùng |
| 70000–71999 | giai đoạn 1 | đã dùng |
| 80000–81199 | dữ liệu clone v2 | đã dùng |
| 90000–91999 | chơi clone v2 | đã dùng |
| 100000–100399 | dev CEM / augment | đã dùng |
| 110000–111999 | giữ-lại augment | đã dùng |
| 120000–120999 | arena engine | đã dùng |
| 130000–130399 | sàng v4 | đã dùng |
| 140000–140999 | giữ-lại trang bị | đã dùng |
| 150000–151199 | dữ liệu v4 | đã dùng |
| 160000–160999 | chơi v4 | đã dùng |
| 170000–170999 | trang bị (xác nhận) | đã dùng |
| 180000–180399 | trang bị dev | đã dùng |
| 190000–191000 | tái hiện valuemax | đã dùng |
| 200000–200399 | định vị | đã dùng |
| 220000–220199 | dev CEM | đã dùng (dev, được tái dùng) |
| 230000–230999 | giữ-lại CEM cũ | đã dùng |
| 900000–900099 | kiểm thử cài đặt (không phải dữ liệu) | dành cho smoke |
| **300000–301999** | **dữ liệu DT: train 300000–301499, val 301500–301599, test 301600–301999** | **đã dùng một phần (DT, chế độ rút gọn): 300000–300499 và 301500–301999. 300500–301499 chưa dùng, để dành** |
| **240000–240999** | **kiểm định cuối CEM (vai C)** | **đã dùng (C, 2026-11-24)** |
| **241000–241999** | **kiểm định cuối clone (vai E)** | dành riêng, chưa dùng (E) |
| **242000–249999** | **dự trữ cho vai P (định vị)** | dành riêng |

Không chồng dải. Không dùng 230000–230999 hay 240000+ để huấn luyện.

## 3. Định dạng và kiểm tra

`scripts/collect_v4.py lo hi out.npz` ghi các mảng:
- `uni3`: float32, `(N, 185)`; `mask`: bool, `(N, 43)`; `action`: int64 trong `[0, 42]`; `seed`, `seat`, `step`.

`scripts/merge_v4.py out_dir shard...` kiểm tra từng shard (shape, action, mask hợp lệ, không NaN), loại shard lỗi, rồi chia theo seed thành `train.npz`, `val.npz`, `test.npz` theo mục 2.

Đo thực tế (máy 4 nhân, 15 GB): 300 ván mất 4 phút 41 giây một nhân, tạo 886.111 dòng (khoảng 2.950 dòng mỗi ván), đỉnh RAM tiến trình 1,7 GB. 2.000 ván ≈ 6 triệu dòng ≈ 4,4 GB `uni3` (chưa nén). **Cần máy có RAM tối thiểu 16 GB** (gộp tạm thời nhân đôi bộ nhớ). Nếu ít hơn, giảm số ván và báo lại.

Kiểm tra bắt buộc trước khi báo xong:
1. `uni3.shape[1] == 185`, `mask.shape[1] == 43`, action trong `[0, 42]`, không NaN/inf.
2. `mask[i, action[i]]` là True với mọi dòng.
3. Mọi seed nằm đúng dải được giao (mục 2).
4. Chạy lại `collect_v4.py` trên 2 seed đầu, so sánh `action` và số dòng phải giống hệt.
5. Ghi summary: số dòng, số ván, sha256 của từng file, RAM đỉnh, thời gian.

## 4. Các vai

| Vai | Số phiên | Việc | Phụ thuộc | Đầu ra (commit) |
|---|---|---|---|---|
| **DT — thu + huấn luyện** | 1 | Thu 2.000 ván (4 tiến trình song song), gộp, huấn luyện clone v5, đánh giá test | không | `bc_v5.json`, `shard_summary.json`, `clone_v5_seed0.pt` |
| **C — trang bị (CEM)** | 1 | CEM 6 thế hệ, 12 ứng viên, dev 200 ván, kiểm định cuối 240000–240999 | không | `cem_item_v2.json` |
| **R — nghiên cứu Set 18** | 1 | Bổ sung `set18-sources.md` từ nguồn công khai | không | `set18-sources.md` |
| **E — kiểm định clone v5** | 1 | Chơi clone v5 vs v4, v3, scripted trên 241000–241999 | **DT xong** (cần checkpoint) | `play_v5_*.json` |
| P — định vị | — | chưa giao | — | — |

**Thứ tự chạy:**
1. Ngay bây giờ: DT, C, R song song.
2. Khi DT đã commit checkpoint: E, và chọn nhánh E là nhánh DT (để E có `clone_v5_seed0.pt`).

## 5. Thông số chạy

- **DT:** 4 tiến trình song song, mỗi tiến trình 500 ván:
  `300000–300499`, `300500–300999`, `301000–301499`, `301500–301999`. Shard cuối chứa cả val và test; `merge_v4.py` tự tách.
- **C:** `python scripts/cem_item.py 6 12 220000 220200 results/fixed/real/cem_item_v2.json 240000 241000` (Pool(4)). Ước tính khoảng 1,5 giờ, vì mỗi ứng viên chạy 200 ván dev. Nếu hết giờ, giảm số thế hệ và báo lại.
- **E:** `python scripts/play_v4.py <mode> <ckpt> 241000 242000 v5` với mode trong `v4null`, `clone_v4`, `clone_v3`, `clone_scr`. Đã đặt `torch.set_num_threads(1)`. Tối đa 4 tiến trình song song.

Đo thực tế (máy 4 nhân, 16 GB, mạng bật): gộp 350 ván (1,03 triệu dòng) mất 15 giây, đỉnh RAM 1,5 GB; huấn luyện 3 seed × 40 epoch trên 886.111 dòng train mất 630 giây, đỉnh RAM 2,4 GB; test 147.991 dòng. Ngoại suy cho 1.500 ván train (~4,4 triệu dòng): huấn luyện khoảng 55 phút, RAM đỉnh khoảng 8–10 GB, gộp khoảng 6–7 GB. Bước thu 2.000 ván: khoảng 15 phút với 2 tiến trình.

## 6. Đầu ra và đóng gói

- Raw `.npz`: ở `~/work/data`, không commit, không đưa ra ngoài phiên.
- Checkpoint (`~190 KB`) và JSON: commit lên nhánh được giao.
- Dữ liệu thô chỉ rời máy khi người dùng yêu cầu rõ.


## Dang chay / bi chan (cap nhat 2026-11-25)

- **DT:** chap nhan clone v5 o che do rut gon (500 van train, seed 300000–300499; val + test 301500–301999). Seed 300500–301499 de danh, khong dung. Khong chay lai tren may cung.
- **R:** snapshot CDragon trong repo la trang thai truoc 18.7 (chuoi version 16.23). Du lieu Set 18 trong mo phong khong khop 18.7. Can lay file dung ban 18.7 truoc khi dung cho Set 18. Set 17 (E) khong bi chan boi viec nay.
- **E:** nhanh `codex/sim-e` da tao tu `codex/sim-dt` @ 01d2339. Checkpoint da kiem tra nap duoc (smoke 900000–900002, 0 luot khong hop le).
- **C:** xong. CEM tren 240000–240999 (xem README).
