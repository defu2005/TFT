# tft-sim

Harness danh gia policy (env-agnostic) va pipeline BC cho bai toan TFT. Trang thai: **giai doan 0** (teacher da sua tren noi dung synthetic; chua co transfer test; chua co noi dung TFT that dung patch).

Ghi chu: toy env trong `src/tft_sim/env.py` chi la test double. Ket qua tren no khong noi gi ve suc manh bot TFT.

## Bang do pham vi (scoreboard) - noi dung TONG HOP, khong phai TFT that

Ty le dong y o day la muc loai+chi so tren hang >=2 hop le, vs random; xem muc BC de biet dinh nghia. Cot: trong sim = action co xuat hien trong sim tong hop; co teacher = scripted_action chon hanh dong do; da hoc = clone dat >= 70% dong y voi teacher tren trang thai clone tu gap; danh gia tren TFT that = chua.

| Quyet dinh | Trong sim | Co teacher | Da hoc (BC) | Ty le dong y (flat / flat+slot) | Danh gia tren TFT that |
|---|---|---|---|---|---|
| Mua tuong tu shop (BUY_SHOP) | co | co | co | 77% / 80% | chua |
| Roll (REROLL) | co | co, hiem (n=845 tren 200 lobby) | co (gan) | 87% / 82% | chua |
| Mua XP (BUY_XP) | co | co | co | 86% / 82% | chua |
| Ban tuong / ban tu board | co | **khong** (scripted khong ban) | - | - | chua |
| Dat tuong len board (FIELD) | co | co | co | 100% / 100% | chua |
| Dat tuong xuong bench (BENCH_BOARD) | co | **khong** | - | - | chua |
| Trang bi (EQUIP) | co | co | co (0 no-op tren noi dung synthetic) | 100% / 100% | chua |
| Chon augment (PICK_AUGMENT) | co | co (dung privileged tier) | chua (59-60%) | 59% / 60% | chua |
| Chon god (PICK_GOD) | co | co | co | 100% / 100% | chua |
| Reroll augment (REROLL_AUGMENT) | co | co, rat hiem (n=42-58) | chua (0%) | 0% / 0% | chua |
| Dinh vi trong tran (positioning) | **mo** (chua co trong 43 action cua TFT_GOAT) | - | - | - | - |
| Nham muc tieu item | **mo** | - | - | - | - |

## Ket qua BC (noi dung synthetic da sua EQUIP, seed test 1000-1199, 200 lobby/bien the)

**Thay the ket qua cu.** Cac so truoc (99.6% / 99.7%, scripted 2.78 vs random 6.23) do teacher bi ket EQUIP; khong dung de ket luan. Ket qua moi: `results/fixed/bc/bc_results.json`.

Tap: train 200-349 (233.919 dong), val 800-849 (77.875 dong). Lobby toan scripted lam nhan. Seat xoay bang shuffle co seed.

| Bien the | Dong y val, moi dong (>=2 hop le) | vs random (diff A-B, CI95) | vs scripted (diff A-B, CI95) | Bat hop le |
|---|---|---|---|---|
| flat | 89.8% (86.0%) | -3.98 [-3.99, -3.96] | +0.08 [-0.17, 0.32] | 0 |
| flat+slot | 90.6% (87.1%) | -3.99 [-4.00, -3.98] | +0.13 [-0.12, 0.36] | 0 |

Doi chung: scripted vs scripted tren noi dung da sua (200 lobby): diff -0.03, CI95 [-0.25, 0.18].

Dong y theo loai (tren trang thai clone tham, chi tinh hang >=2 hop le, vs random, flat / flat+slot):
BUY_SHOP 77% / 80%; BUY_XP 86% / 82%; PASS 45% / 48%; FIELD, EQUIP, PICK_GOD 100%; PICK_AUGMENT 59% / 60%; REROLL 87% / 82%; REROLL_AUGMENT 0% (n=49-58, khong dang tin).

**Chua duoc chung minh:** "vs scripted" o tren nam trong CI nhung CI rong (+-0.25 hang). Xem muc "Do nhay cua metric" ben duoi truoc khi dung bat ky so nao lam bang chung clone = teacher.

## Do nhay cua metric (ladder va ablation)

Seed moi 2000-2199, 200 lobby, A = bien the degraded, B = scripted goc. Script: `scripts/diag_clone.py`. Ket qua: `results/fixed/diag/clone_diag.json`.

| Dieu kien (A) | diff A-B | CI95 |
|---|---|---|
| scripted, 10% hanh dong ngau nhien | -0.45 | [-0.68, -0.21] |
| scripted, 30% ngau nhien | -0.04 | [-0.28, 0.20] |
| scripted, 60% ngau nhien | +2.62 | [2.44, 2.80] |
| scripted, bo mua shop (BUY_SHOP -> PASS) | +3.97 | [3.94, 3.98] |
| clone flat+slot | +0.02 | [-0.22, 0.25] |

Ket luan: metric phat hien duoc teacher bi cat mot phan lon (60% ngau nhien, bo mua) nhung KHONG phat hien duoc mat mat nho (10-30%). Hon nua, 10% ngau nhien cho ket qua **tot hon** scripted co y nghia thong ke. Nghia la scripted khong phai teacher manh, va hieu so hang khong phai thuoc do tot cho viec bat chuoc teacher. Vi vay tieu chi "trong 0.5 hang cua scripted" KHONG chung minh duoc gi o muc chi tiet.

Chan doan clone (tren cung seed 2000-2199):
- 0 hanh dong bat hop le; 243.7 buoc/game (scripted 225.7).
- 0 phase cham gioi han MAX_PLANNING_STEPS = 50 (scripted cung 0). Clone khong bi lap den gioi han.
- Ma tran nham o muc loai (teacher -> clone): BUY_SHOP, FIELD, EQUIP, PICK_GOD, PICK_AUGMENT luon khop loai. Loai khop nhung chi so khac nhau nen dong y theo chi so thap hon. PASS khi teacher noi PASS: clone chon PASS 69%, BUY_XP 24%, REROLL 7%. Sai lech nay la cho chinh cua rule gold >= 54 trong teacher.
- PICK_AUGMENT va REROLL_AUGMENT dung tier augment trong state privileged cua teacher, khong co trong observation. Day la khoang trong quan sat, khong phai ket qua hoc.

## Trang thai cong viec

- Test cua tft-sim: 9 pass (chay tren toy env, co loai tru seat). Toy env chi kiem chung harness.
- Adapter TFT_GOAT (`adapter_tftgoat.py`): **chua kiem thu**.
- TFT_GOAT, pytest (bo qua test co tai mang): 193 pass, 2 fail. Nguyen nhan da xac dinh: `data/cdragon/` chua ban CommunityDragon `latest` (tai 2026-11-23, patch 18.7) bi luu duoi ten `cdragon_17.4.json`. File da duoc doi ten thanh `cdragon_latest_fetched-2026-11-23.json`, sha256 `caed07e9b1602557b8bce09ed2c80a29d67a1d3fa83c676d85592a52b11c3a9e`.
- Snapshot dung patch 17.4 cua CommunityDragon: `https://raw.communitydragon.org/17.4/cdragon/tft/en_us.json` tra ve 404. Cac bien the 17.1, 17.2, 17.3, 17.4.1 cung 404. Chua co nguon 17.x nao duoc chap nhan.
- Gate 0 tren **noi dung tong hop** (`build_sample_content`, khong phai TFT that): **dat**. 200/200 ban hoan thanh, 0 crash, replay cung seed giong het, scripted 2.78 so voi random 6.23, CI95 hieu so [-3.55, -3.34]. Ket qua: `results/gate0_synthetic_200.json`. Script: `scripts/gate0_tftgoat.py`.
- Gate 0 tren noi dung TFT that (Set 17 patch 17.4): **chua chay**, vi chua co snapshot dung patch.

## Nguon du lieu TFT that (da tim, chua dung de chay gate)

- Riot DDragon chinh thuc cho TFT, repo cong dong `InFinity54/TFT_DDragon`: commit `cb44ecd9` ("Added patch 17.4", 2026-06-13) co `data/en_US/champion.json` va `trait.json`. Dem tuong `TFT17_*` theo cost trong commit nay: cost1=14, cost2=13, cost3=14, cost4=14, cost5=9 (kem 2 muc cost 0). Trait.json khong co breakpoint, nen KHONG kiem duoc `Anima (3,6)` tu nguon nay.
- So voi bang xac minh trong test (15/13/13/14/10) va CDragon 18.7 (16/13/14/14/10): ba nguon khac nhau. Chua quyet dinh nguon nao dung.
- CommunityDragon: `https://raw.communitydragon.org/<so-patch>/` co thu muc theo so patch LoL (10.x, 11.x...), khong co `17.4/cdragon/tft/en_us.json`.

## Canh bao ket qua BC (cap nhat)

- **Da xu ly tren noi dung synthetic** (`src/tft_sim/content.py`): moi cap cong thuc deu co, `diag_equip.py` cho 0 EQUIP khong tieu thu tren 901 hanh dong. Noi dung TFT that (CDragon 18.7, 3 game) van con ~4% EQUIP khong tieu thu; chua sua.
- Muc ben duoi chi con de tham khao lich su.

- Ty le dong y 99.6% / 99.7% bi thoi phong boi EQUIP: 82% quyet dinh cua teacher la EQUIP, va hau het la hanh dong khong co tac dung. `_equip` khong tieu thu thanh phan khi cap khong co cong thuc (44.952 / 45.015 lan goi `combine` tra ve None), nhung mask van cho EQUIP hop le. Teacher bi ket trong vong lap EQUIP den gioi han 50 buoc moi phase. Day la mismatch giua mask va hieu ung trong TFT_GOAT, khong phai loi cua tft-sim.
- Nguong "da hoc" 70% duoc dat sau khi da xem so lieu, nen khong duoc coi la tieu chi trung lap.
- Ket qua theo loai (BUY_SHOP 74-82%, BUY_XP 71-77%, PICK_AUGMENT ~60%, REROLL_AUGMENT 0%) la phan co y nghia. Ket qua vs scripted can doc cung canh bao nay.
- Nghien cuu theo patch: xem `docs/knowledge/`. Thiet ke: `docs/PATCH_MODEL.md`. Transfer test chua chay.
