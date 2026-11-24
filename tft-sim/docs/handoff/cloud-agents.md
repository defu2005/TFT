# Handoff cho agent cloud: thu dữ liệu, huấn luyện, kiểm định (workstream `sim`)

Tài liệu này dành cho các agent cloud chạy song song. Mỗi agent nhận một vai (mục 4) và prompt tương ứng. Đọc hết mục 0–3 trước khi bắt đầu.

## 0. Quy tắc cứng (áp dụng cho mọi agent)

- **Phạm vi:** chỉ sửa `tft-sim/` trên nhánh được giao. Không sửa `src/`, `ingest/`, live coach, `master`, `docs/agents/`, `CLAUDE.md`, `AGENTS.md`.
- **Nhánh:** đẩy lên đúng nhánh mà phiên cloud được giao khi tạo. Tên `claude/sim-<vai>-<mã>` trong prompt chỉ là gợi ý; nếu phiên không có nhánh được giao, dừng và hỏi người dùng. Không tạo PR. Không force-push.
- **Không commit dữ liệu lớn.** File `.npz`, checkpoint `.pt`, log thô: giữ ngoài git, ghi vào thư mục đầu ra được giao (mục 6). Chỉ commit JSON kết quả nhỏ và summary.
- **Không bịa số.** Mọi số báo cáo phải lấy từ file kết quả, kèm đường dẫn file và seed range.
- **Không dùng seed đã dùng** (mục 2). Dùng seed sai là lỗi nghiêm trọng, vì nó làm hỏng kiểm định giữ-lại.
- **Không lộ thông tin cá nhân hoặc bí mật** vào commit, log hay request ra ngoài.
- **Advisor:** nếu có công cụ advisor, gọi tại các điểm quan trọng (theo `CLAUDE.md`). Nếu không có, tiếp tục và ghi rõ trong báo cáo là không có.

## 1. Môi trường

Repo cần có hai thứ:
1. `TFT` (nhánh `claude/claude-fable-5-2-awwmf5`, commit tối thiểu `991ce70`).
2. `tft_goat` (repo `https://github.com/MielPopsssssss/tft_goat`, commit **`d5358e94`**). Đây là repo bên thứ ba. Agent phải có quyền clone; nếu không, dừng và báo người dùng. Không tự thay bằng bản khác.

Cài đặt (Python 3.13 đã kiểm chứng; tối thiểu 3.11):
```bash
cd /path/to/TFT/tft-sim
python -m venv .venv && . .venv/bin/activate
pip install -q numpy pydantic httpx riotwatcher gymnasium pettingzoo
pip install -q torch --index-url https://download.pytorch.org/whl/cpu   # CPU; GPU nếu được giao
export PYTHONPATH=src:/path/to/tft_goat/src
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1   # BẮT BUỘC khi chạy nhiều tiến trình
```
Kiểm tra nhanh trước khi chạy việc thật:
```bash
python -c "import tft_goat, tft_sim, torch; print('ok')"
python scripts/collect_v4.py 150000 150002 /tmp/smoke.npz   # phải báo DONE, rows > 0
```

**Quan trọng:** `OMP_NUM_THREADS=1` khi chạy nhiều tiến trình. Không có nó, torch tranh CPU và chạy chậm gấp nhiều lần (đã đo trên máy có 4 nhân: load 12, tiến trình chạy chậm vài giờ).

## 2. Sổ seed (đã dùng và đã đóng)

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
| 150000–151199 | dữ liệu v4 (train/val/test) | đã dùng |
| 160000–160999 | chơi v4 | đã dùng |
| 170000–170999 | trang bị (xác nhận) | đã dùng |
| 180000–180399 | trang bị dev | đã dùng |
| 190000–191000 | tái hiện valuemax | đã dùng |
| 200000–200399 | định vị | đã dùng |
| 220000–220199 | dev CEM | đã dùng |
| 230000–230999 | giữ-lại CEM | đã dùng |
| **240000–249999** | **giữ-lại mới cho CEM/định vị (chỉ dùng để kiểm định cuối)** | dành riêng |
| **300000 trở đi** | **dữ liệu sinh mới, chia shard (mục 5)** | dành riêng |

Mỗi shard dữ liệu dùng khoảng seed riêng, không chồng lên nhau. Ví dụ: agent 1 dùng 300000–300499, agent 2 dùng 300500–300999.

## 3. Định dạng và kiểm tra dữ liệu

Script `scripts/collect_v4.py lo hi out.npz` sinh các mảng:
- `uni3`: float32, shape `(N, 185)`. 185 = 179 (uni2) + 6 cờ augment.
- `mask`: bool, shape `(N, 43)`.
- `action`: int64, giá trị trong `[0, 42]`.
- `seed`, `seat`, `step`: int64.

**Kiểm tra bắt buộc trước khi báo DONE:**
1. `uni3.shape[1] == 185`, `mask.shape[1] == 43`, `action` trong `[0, 42]`, không có NaN/inf trong `uni3`.
2. `mask[i, action[i]]` là True với mọi dòng (hành động phải hợp lệ).
3. `seed` nằm đúng trong dải được giao.
4. Chạy lại đúng 2 seed đầu một lần nữa, so sánh: số dòng và `action` phải giống hệt (tái lập).
5. Ghi summary: số dòng, số ván, `sha256` của file, thời gian chạy, RAM đỉnh.

Kích thước: 1,18 triệu dòng ≈ 0,9 GB mảng `uni3` không nén. **Mỗi lần chạy không quá 500 ván** (khoảng 1,5 triệu dòng) để giữ RAM đỉnh dưới 3 GB. Nếu máy có ít RAM hơn, giảm xuống 250 ván.

## 4. Các vai

| Vai | Số agent | Việc | Đầu vào | Đầu ra |
|---|---|---|---|---|
| **D — thu dữ liệu** | nhiều (chia shard) | Sinh `uni3` cho một dải seed | dải seed, commit `991ce70` | `.npz` (ngoài git) + summary JSON (trong git) |
| **T — huấn luyện** | 1 | Gộp shard, huấn luyện clone v5, đánh giá trên test | các `.npz` | checkpoint (ngoài git), `bc_v5.json` (trong git) |
| **E — kiểm định** | 1–2 | Chơi clone/luật trên seed giữ-lại mới | checkpoint, luật | `play_v5_*.json` (trong git) |
| **C — trang bị** | 1 | Học luật/tham số trang bị bằng CEM, nhiều thế hệ hơn | seed dev/giữ-lại | `cem_*.json` (trong git) |
| **R — nghiên cứu Set 18** | 1 | Tìm bảng odds, XP, tướng Set 18 từ nguồn công khai | danh sách nguồn | `docs/handoff/set18-sources.md` (trong git) |

Vai **P — định vị (lớp con môi trường)** là việc phát triển mã, giao sau khi D/T/E chạy được. Không giao vai này trước.

## 5. Kế hoạch chia shard và sử dụng máy

- Mục tiêu tạm: **5.000 ván** cho một bộ cấu hình (mục 4 README của dự án), tương đương 10 shard 500 ván.
- Phân shard: `300000–300499`, `300500–300999`, ..., `304500–304999`.
- Mỗi máy chạy **một** tiến trình thu dữ liệu nếu có ít nhân; máy nhiều nhân chạy một tiến trình cho mỗi nhóm 2 nhân, không hơn số nhân.
- Ước tính (đo trên máy 4 nhân, cần đo lại trên máy thuê): khoảng 1 ván mỗi giây mỗi nhân, khoảng 3.000 dòng mỗi ván.
- Thứ tự: D sinh toàn bộ shard → T gộp và huấn luyện → E kiểm định. Không chạy T trước khi D xong, vì T cần đủ dữ liệu.

## 6. Thư mục đầu ra và đóng gói

- Dữ liệu lớn: `/data/sim/<ngày>/<shard>/` (đường dẫn người dùng cung cấp; nếu chưa có, ghi `TBD` và báo lại).
- Summary JSON: `tft-sim/results/fixed/real/shard_<seed_lo>.json` (commit lên nhánh).
- Mỗi kết quả JSON có: `seeds`, `rows`, `sha256`, `commit_tft`, `commit_tft_goat`, `ram_peak_mb`, `wall_seconds`.

---

# Prompt cho từng vai

Mỗi khối dưới đây là một prompt độc lập, dán nguyên văn cho agent. Thay các giá trị trong `<ngoặc>`.

## Prompt D — thu dữ liệu một shard

```
Bạn là agent thu dữ liệu cho dự án TFT (workstream sim). Làm đúng quy tắc sau.

Nhiệm vụ: sinh dữ liệu clone v4 cho seed [LO]–[HI-1] (tối đa 500 ván), dùng teacher v4 trên EngineResolver.

Nguồn: repo TFT, nhánh claude/claude-fable-5-2-awwmf5, commit 991ce70 hoặc mới hơn; repo tft_goat, commit d5358e94.
Đọc trước: tft-sim/docs/handoff/cloud-agents.md (mục 0, 1, 3, 5, 6). Đó là nguồn chuẩn.

Các bước:
1. Thiết lập môi trường theo mục 1 của tài liệu. Dừng và báo nếu không clone được tft_goat.
2. Chạy: python scripts/collect_v4.py [LO] [HI] /data/sim/[NGÀY]/shard_[LO].npz  (OMP_NUM_THREADS=1).
3. Kiểm tra theo mục 3 (năm điều). Nếu một điều không đạt, không báo DONE; báo lỗi kèm log.
4. Viết tft-sim/results/fixed/real/shard_[LO].json với các trường: seeds, rows, sha256, commit_tft, commit_tft_goat, ram_peak_mb, wall_seconds, check_results.
5. Commit chỉ file JSON trên nhánh claude/sim-d-[LO]. Không commit .npz. Đẩy: git push -u origin claude/sim-d-[LO].

Ràng buộc: không sửa src/, ingest/, master; không tạo PR; không dùng seed ngoài [LO]–[HI-1]; không chạy quá 500 ván.

Báo cáo cuối (ngắn): số dòng, số ván, sha256, kết quả 5 kiểm tra, RAM đỉnh, thời gian, đường dẫn file .npz, tên nhánh, commit hash.
```

## Prompt T — gộp và huấn luyện clone v5

```
Bạn là agent huấn luyện cho dự án TFT (workstream sim). Làm đúng quy tắc sau.

Nhiệm vụ: gộp các shard uni3 đã thu, huấn luyện clone v5 (3 seed, 40 epoch), đánh giá trên tập test.

Đọc trước: tft-sim/docs/handoff/cloud-agents.md (mục 0, 3, 6).
Đầu vào: danh sách file .npz do vai D tạo, đường dẫn [THƯ MỤC] (do người dùng cung cấp).

Các bước:
1. Kiểm tra mọi shard: shape, action trong [0,42], mask hợp lệ (mục 3). Loại shard lỗi và ghi lại.
2. Gộp train/val/test theo seed: test là các seed đã nằm trong dải riêng [TEST_LO]–[TEST_HI] (chọn trước, không thuộc train). Ghi số dòng từng tập.
3. Chạy: python scripts/bc_v4.py [THƯ MỤC_GỘP]  (sửa tên file đầu ra thành bc_v5.json nếu cần, không ghi đè bc_v4).
4. Báo số: overall và theo loại trên 3 seed (lấy min–max). Không báo số của một seed duy nhất.
5. Commit tft-sim/results/fixed/real/bc_v5.json trên nhánh claude/sim-t-[MÃ]. Không commit checkpoint hay .npz.

Ràng buộc: không dùng seed giữ-lại 240000+ để huấn luyện; không sửa src/, ingest/; không tạo PR.

Báo cáo cuối: số dòng từng tập, số shard bị loại (nếu có), bảng accuracy 3 seed, đường dẫn checkpoint, commit hash.
```

## Prompt E — kiểm định trên seed giữ-lại mới

```
Bạn là agent kiểm định cho dự án TFT (workstream sim). Làm đúng quy tắc sau.

Nhiệm vụ: chơi clone v5 với các đối thủ trên seed giữ-lại mới [LO]–[HI-1] (dải 240000+, chưa dùng).

Đọc trước: tft-sim/docs/handoff/cloud-agents.md (mục 0, 2, 3).
Đầu vào: checkpoint clone v5 seed 0 (từ vai T, đường dẫn [CKPT]).

Các phép (mỗi phép 1000 ván, cùng dải seed):
- null: v4 vs v4 (kỳ vọng CI chứa 0).
- clone vs v4 (kỳ vọng CI chứa 0 nếu clone bắt chước v4).
- clone vs v3 (kỳ vọng xấu hơn 0 nếu v4 tốt hơn v3).
- clone vs scripted goc.

Chạy bằng scripts/play_v4.py (đã đặt torch.set_num_threads(1)). Mỗi tiến trình một phép. Tối đa 4 tiến trình song song.
Tính CI95 bằng bootstrap 2000 lần (cùng cách với các bảng trong README).

Ràng buộc: seed giữ-lại không được dùng để chọn tham số; không chạy lại với seed khác để "tìm" kết quả tốt; không sửa src/, ingest/; không tạo PR.

Báo cáo cuối: bảng 4 phép (hiệu, CI95, n), kết luận rõ là đạt/không đạt từng tiêu chí, commit JSON trên nhánh claude/sim-e-[MÃ].
```

## Prompt C — CEM trang bị nhiều thế hệ

```
Bạn là agent học trang bị cho dự án TFT (workstream sim). Làm đúng quy tắc sau.

Nhiệm vụ: chạy scripts/cem_item.py với nhiều thế hệ hơn bản hiện có (bản cũ: 3 thế hệ, 8 ứng viên, 200 ván).
Cấu hình đề xuất: 8 thế hệ, 16 ứng viên, 300 ván dev mỗi ứng viên. Dev cố định 220000–220299 (hoặc dải dev mới chưa dùng do người dùng chỉ định). Giữ-lại: 240000–240999.

Đọc trước: tft-sim/docs/handoff/cloud-agents.md (mục 0, 2), tft-sim/scripts/cem_item.py.

Các bước:
1. Đảm bảo dev không chồng giữ-lại (mục 2). Nếu chỉnh dải, ghi rõ trong JSON.
2. Chạy bằng 4 nhân (Pool(4)); OMP_NUM_THREADS=1.
3. Ghi log từng thế hệ (best, mean fitness) vào JSON.
4. Kiểm định trọng số cuối trên giữ-lại 240000–240999 so với mặc định, và so với luật valuemax (cùng seed). Báo CI95.
5. Commit JSON trên nhánh claude/sim-c-[MÃ]. Không commit log thô lớn.

Kết luận cần nêu rõ: học được vượt valuemax không (CI95 của khác biệt có nằm hoàn toàn dưới 0 không). Nếu không, nói rõ là ngang hoặc kém.

Ràng buộc: không sửa src/, ingest/; không tạo PR; không dùng 230000–230999 (đã dùng).
```

## Prompt R — nghiên cứu bảng Set 18

```
Bạn là agent nghiên cứu dữ liệu cho dự án TFT (workstream sim). Làm đúng quy tắc sau.

Nhiệm vụ: thu thập bảng cho Set 18 (bản 18.7 nếu có, ghi rõ nếu không):
1. Tỉ lệ cửa hàng theo cấp 1–10 (5 con số cho cost 1–5 mỗi cấp).
2. Kinh nghiệm để lên cấp theo cấp (bảng đầy đủ).
3. Số lượng bản mỗi tướng trong pool theo cost (nếu có).
4. Danh sách tướng và tộc, đánh dấu tướng đổi tộc ở các bản 18.x.
5. Các cơ chế đặc thù mùa (tóm tắt, không suy diễn).

Nguồn ưu tiên (chính thức trước): trang tin và ghi chú bản vá của Riot (teamfighttactics.leagueoflegends.com), wiki Riot. Nguồn cộng đồng (seemeta, esports.gg, mobalytics, op.gg) chỉ dùng để đối chiếu và phải ghi rõ là cộng đồng.

Quy tắc:
- Không bịa số. Nếu không tìm được một ô, ghi "không có nguồn".
- Mọi số phải kèm URL nguồn và trích ngắn (một câu) chứng minh số đó.
- Không truy cập domain bị chặn; nếu một domain báo ENOTFOUND, ghi lại và dùng nguồn khác, không đổi cấu hình mạng.
- Ghi rõ bản vá và ngày truy cập cho từng số.

Đầu ra: tft-sim/docs/handoff/set18-sources.md (bảng có cột: đại lượng, cấp/mục, giá trị, bản vá, nguồn, loại nguồn chính thức/cộng đồng, trạng thái đối chiếu). Commit lên nhánh claude/sim-r-[MÃ].

Báo cáo: những gì tìm được, những gì thiếu, những gì mâu thuẫn giữa các nguồn.
```

---

# Điều người dùng cần làm trước khi giao

1. **Quyền truy cập repo `MielPopsssssss/tft_goat`** cho các agent cloud. Quy tắc phạm vi hiện chỉ cho `defu2005/tft`; cần bổ sung repo này hoặc cung cấp tarball tại commit `d5358e94`.
2. **Nơi lưu `.npz`** (ví dụ bucket hoặc ổ chung). Chưa có nơi này thì agent D không thể bàn giao dữ liệu.
3. **Cho phép domain** cho R (nếu cần truy cập các trang nguồn). Hoặc chấp nhận để R làm việc chỉ với nguồn công khai đã được phép.
4. **Số agent và cấu hình máy** (nhân, RAM). Dùng để chia shard ở mục 5.
