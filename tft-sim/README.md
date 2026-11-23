# tft-sim

Harness danh gia policy (env-agnostic) va pipeline BC cho bai toan TFT. Trang thai: **giai doan 0**.

Ghi chu: toy env trong `src/tft_sim/env.py` chi la test double. Ket qua tren no khong noi gi ve suc manh bot TFT.

## Bang do pham vi (scoreboard) - noi dung TONG HOP, khong phai TFT that

Cot: trong sim = action co xuat hien trong sim tong hop; co teacher = scripted_action chon hanh dong do; da hoc = clone dat >= 70% dong y voi teacher tren trang thai clone tu gap; danh gia tren TFT that = chua.

| Quyet dinh | Trong sim | Co teacher | Da hoc (BC) | Ty le dong y (flat / flat+slot) | Danh gia tren TFT that |
|---|---|---|---|---|---|
| Mua tuong tu shop (BUY_SHOP) | co | co | co | 74% / 82% | chua |
| Roll (REROLL) | co | co, rat hiem (n=3) | chua du du lieu | - | chua |
| Mua XP (BUY_XP) | co | co | co (gan nguong) | 71% / 77% | chua |
| Ban tuong / ban tu board | co | **khong** (scripted khong ban) | - | - | chua |
| Dat tuong len board (FIELD) | co | co | co | 100% / 100% | chua |
| Dat tuong xuong bench (BENCH_BOARD) | co | **khong** | - | - | chua |
| Trang bi (EQUIP) | co | co | co | 100% / 100% | chua |
| Chon augment (PICK_AUGMENT) | co | co | chua (59-60%) | 59% / 60% | chua |
| Chon god (PICK_GOD) | co | co | co | 100% / 100% | chua |
| Reroll augment (REROLL_AUGMENT) | co | co, rat hiem (n=37-51) | chua (0%) | 0% / 0% | chua |
| Dinh vi trong tran (positioning) | **mo** (chua co trong 43 action cua TFT_GOAT) | - | - | - | - |
| Nham muc tieu item | **mo** | - | - | - | - |

## Ket qua BC (synthetic, seed test 1000-1199, 200 lobby/bien the)

Tap: train 200-349 (150 lobby, 2.02M dong), val 800-849. Lobby toan scripted lam nhan. Seat xoay bang shuffle co seed.

| Bien the | Dong y val voi teacher | vs random (diff A-B, CI95) | vs scripted (diff A-B, CI95) | Bat hop le |
|---|---|---|---|---|
| flat | 99.6% | -3.40 [-3.51, -3.28] | +0.22 [-0.02, 0.47] | 0 |
| flat+slot | 99.7% | -3.39 [-3.51, -3.27] | +0.07 [-0.17, 0.29] | 0 |

Doi chung: scripted vs scripted (200 lobby): diff +0.07, CI95 [-0.15, 0.29], chua 0.
Tieu chi qua: 0 hanh dong bat hop le, thang random ro rang, va trong khoang 0.5 hang cua scripted. **Dat ca hai bien the, tren noi dung tong hop.**
Luu y: "vs scripted" ghi lai hieu so hang trung binh, khong phai ty le dong y. Bien the flat+slot dong y tot hon nhung khong cai thien ro ret ve hieu so. Cac loai co dong y thap (REROLL_AUGMENT, PICK_AUGMENT) ghi nhan ro, chua duoc giai quyet.
File: `results/bc/bc_results.json`, model `results/bc/bc_flat.pt`, `results/bc/bc_flat+slot.pt`.

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

- Ty le dong y 99.6% / 99.7% bi thoi phong boi EQUIP: 82% quyet dinh cua teacher la EQUIP, va hau het la hanh dong khong co tac dung. `_equip` khong tieu thu thanh phan khi cap khong co cong thuc (44.952 / 45.015 lan goi `combine` tra ve None), nhung mask van cho EQUIP hop le. Teacher bi ket trong vong lap EQUIP den gioi han 50 buoc moi phase. Day la mismatch giua mask va hieu ung trong TFT_GOAT, khong phai loi cua tft-sim.
- Nguong "da hoc" 70% duoc dat sau khi da xem so lieu, nen khong duoc coi la tieu chi trung lap.
- Ket qua theo loai (BUY_SHOP 74-82%, BUY_XP 71-77%, PICK_AUGMENT ~60%, REROLL_AUGMENT 0%) la phan co y nghia. Ket qua vs scripted can doc cung canh bao nay.
- Nghien cuu theo patch: xem `docs/knowledge/`. Thiet ke: `docs/PATCH_MODEL.md`. Transfer test chua chay.
