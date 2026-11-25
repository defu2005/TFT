# tft-sim

Harness danh gia policy (env-agnostic) va pipeline BC cho bai toan TFT. Trang thai: giai doan 1 va 2 dong tren HeuristicResolver; giai doan 3 mo lai tren **EngineResolver** (san chinh tu nay). Chua co bang chung nao tu TFT that.

Ghi chu: toy env trong `src/tft_sim/env.py` chi la test double. Ket qua tren no khong noi gi ve suc manh bot TFT.

## Bang do pham vi (scoreboard) - noi dung TONG HOP, khong phai TFT that

Ty le dong y o day la muc loai+chi so tren hang >=2 hop le, vs random; xem muc BC de biet dinh nghia. Cot: trong sim = action co xuat hien trong sim tong hop; co teacher = scripted_action chon hanh dong do; da hoc = clone dat >= 70% dong y voi teacher tren trang thai clone tu gap; danh gia tren TFT that = chua.

| Quyet dinh | Trong sim | Co teacher | Da hoc (BC) | Ty le dong y (flat / flat+slot) | Danh gia tren TFT that |
|---|---|---|---|---|---|
| Mua tuong tu shop (BUY_SHOP) | co | co | co | 77% / 80% | chua |
| Roll (REROLL) | co | co, hiem | co (gan) | 87% / 82% (vs random, n=84 / 308; val n chua tach) | chua |
| Mua XP (BUY_XP) | co | co | co | 86% / 82% | chua |
| Ban tuong / ban tu board | co | co (teacher v4 co quy tac ban, `make_swap_rule(sell=True)`) | - | - | chua |
| Dat tuong len board (FIELD) | co | co | co | 100% / 100% | chua |
| Dat tuong xuong bench (BENCH_BOARD) | co | co (teacher v4: doi unit board yeu nhat khi bench manh hon) | - | - | chua |
| Trang bi (EQUIP) | co | co | co (0 no-op tren noi dung synthetic) | 100% / 100% | chua |
| Chon augment (PICK_AUGMENT) | co | co (dung privileged tier) | **co, khi co tier trong feature** (99,9% val, closed loop 99,99%) | 99,9% (co tier) | chua |
| Chon god (PICK_GOD) | co | co | co | 100% / 100% | chua |
| Reroll augment (REROLL_AUGMENT) | co | co, rat hiem (n=42-58) | **co, khi co tier** (96% val n=23, closed loop 97% n=524) | 96% (co tier, it mau) | chua |
| Dinh vi trong tran (positioning) | **mo** (env khong co hanh dong dinh vi); engine: mac dinh theo vai tro tot hon xao (+1,0) va dao nguoc (+2,0) | - | - | - | - |
| Nham muc tieu item | **mo** | - | - | - | - |

## Engine (EngineResolver): san chinh cho giai doan 3

Engine (`tft_goat.engine.resolver`) mo phong tung tick, co ability, item, augment (Set 17 only), dinh vi theo vai tro. Khong co quyen dieu khien dinh vi cua nguoi choi. Chay ~1 lobby/giay. Set 18 khong danh gia duoc tren engine.

| Phep (engine) | Seed | Hieu A-B | CI 95% |
|---|---|---|---|
| null: v3 vs v3 | 120000-120999 | +0,007 | [-0,10, +0,11] |
| v3 vs scripted goc | 120000-120999 | -1,93 | [-2,03, -1,84] |
| v3 vs hybrid | dev 100000-100399 | -0,80 | [-0,97, -0,62] |
| augment (registry truoc) vs v3, dev | dev 100000-100399 | -0,77 | [-0,94, -0,61] |
| augment vs v3, giu-lai | 110000-111999 | -0,814 | [-0,889, -0,740] |
| null: v3 vs v3, giu-lai augment | 110000-111999 | -0,0005 | [-0,074, +0,073] |

Ghi chu:
- Heuristic: v3 vs hybrid -1,88 (giu-lai 60000-61999). Engine: -0,80. Muc chenh cho thay so heuristic phong dai hon engine.
- Quy tac augment la **sua teacher trong mo phong, phan anh do phu cai dat**. Trong `env/combat.py`, `augment_power` (heuristic) va `AUGMENT_REGISTRY` (engine, 89 augment) chi tinh augment co trong registry. `env/actions.py` `_pick_augment` ap dung bonus chung theo tier (`_TIER_POWER`: silver 0,7, gold 1,0, prismatic 1,4) cho moi augment, nen augment ngoai registry van co tac dung, nhung chi la bonus chung, khong phai hieu ung that. Vi vay ket qua o day la cai dat cua chung toi, khong phai kien thuc TFT.
- Endgame (ap luc HP): khong phat hien o +-0,17 (endgame_dev H20/40/60).
- Dinh vi va item: mo. Engine tu xep vi tri, EQUIP khong chon unit nhan item. Giai doan 4 can sua engine hoac env.
- God (PICK_GOD): chua do duoc. `diag_aug.py` dem god bang `god_offer` (sai), ket qua 0 khong hop le.
- Clone (uni2, huan luyen tren heuristic) vs v3 tren engine, seed 120000-120999: -0,086 [-0,19, +0,02]. CI chua 0: clone ngang v3 tren engine, khong phai chi tren heuristic. Nguon: `engine_arena.py clone`, log scratchpad.

## Giai doan 2 tren engine: clone v4 (v3 + augment, uni3) - ung vien dong bang

- **Quy tac teacher v4** = `make_aug_rule()`: v3 (swap value) + chon augment uu tien augment co trong `AUGMENT_REGISTRY`, roi moi den tier. Chon tren dev 100000-100399 (-0,77 [-0,94, -0,61] so v3).
- **Dac trung uni3 (185 chieu)** = uni2 (179) + 3 co "co augment o slot" + 3 co "augment o slot nam trong registry" (`src/tft_sim/features_v4.py`).
- **Du lieu:** teacher v4 tren EngineResolver, ca 8 ghe. Train 150000-150399 (1,18 trieu dong), val 150400-150499 (297 nghin), test 151000-151199 (590 nghin). Script: `scripts/collect_v4.py`. File .npz khong commit (o scratchpad).
- **BC (40 epoch, 3 seed):** test 99,5-99,7% tong; PICK_AUGMENT 99,6-99,9%; REROLL 94,6-98,6%; BENCH_BOARD 95,9-97,1%. Script: `scripts/bc_v4.py` (checkpoint seed 0 o scratchpad).

**Choi tren engine, seed 160000-160999 (chua dung):**

| Phep | Hieu A-B | CI 95% |
|---|---|---|
| null: v4 vs v4 | -0,011 | [-0,12, +0,09] |
| clone v4 vs v4 | -0,031 | [-0,14, +0,08] |
| clone v4 vs v3 | -0,82 | [-0,92, -0,71] |
| clone v4 vs scripted goc | -2,30 | [-2,39, -2,21] |

Dat tieu chi cua advisor: clone vs v4 co CI chua 0, va clone vs v3 gan -0,8 (dung bang gia tri augment). Ghi chu: v4 chi la ung vien dong bang, chua sang loc nhieu theo loai va chua chon quy tac god; PICK_GOD van la teacher cu. Script choi: `scripts/play_v4.py` (chay 1 luong torch de tranh tranh chap CPU).

## Sang nhieu theo loai tren v4 (engine), seed 130000-130399 (dev, 400 lobby moi loai)

Quy tac: voi xac suat 0,1 chon ngau nhien mot hanh dong hop le cua loai do, nguoc lai v4. A = v4 + nhieu, B = v4. Duong = nhieu lam xau di.

| Loai | A-B | CI 95% |
|---|---|---|
| null (v4 vs v4) | +0,092 | [-0,08, +0,26] |
| PASS | +1,271 | [+1,11, +1,42] |
| REROLL | +1,331 | [+1,17, +1,49] |
| SELL_BENCH | +0,349 | [+0,17, +0,52] |
| EQUIP | +0,099 | [-0,07, +0,27] |
| PICK_AUGMENT | +0,091 | [-0,08, +0,27] |
| PICK_GOD | +0,085 | [-0,09, +0,27] |
| REROLL_AUGMENT | +0,070 | [-0,11, +0,24] |
| BUY_SHOP | -0,004 | [-0,18, +0,18] |
| BENCH_BOARD | -0,059 | [-0,22, +0,11] |
| BUY_XP | -0,098 | [-0,27, +0,07] |
| FIELD | -0,133 | [-0,31, +0,04] |

**Ket luan:** khong loai nao co nhieu thang voi CI ca 99,5% loai 0. Theo tieu chi cua advisor, **v4 dong bang**, khong can lap lai tren 140000-141999. Ghi chu: PASS, REROLL, SELL_BENCH cho thay teacher da dung o do la ro; cac loai con lai khong co y nghia thong ke o n=400.

## Trang bi tren engine: don bay that, chua biet dich toi uu (giai doan 4)

Mac dinh cua env: thanh pham (2 thanh phan) duoc trao cho unit dat nhat (cost cao nhat) trong board con slot (`_equip` trong `env/actions.py`). Khong co hanh dong chon unit nhan item. Thu nghiem: thay luat chon dich, cung chinh sach v4, ghe nhom A dung luat moi, ghe nhom B mac dinh, cung lobby; hieu A-B so voi null.

| Luat (ghe A) | Seed | Hieu so voi mac dinh | CI 95% | n |
|---|---|---|---|---|
| unit re nhat | 130000-130399 | -0,19 | [-0,45, +0,06] | 400 |
| ngau nhien | 130000-130399 | -0,18 | [-0,42, +0,07] | 400 |
| unit re nhat | 170000-170999 (chua dung) | -0,21 | [-0,36, -0,07] | 1000 |
| ngau nhien | 170000-170999 (chua dung) | -0,23 | [-0,38, -0,09] | 1000 |

**Dau cua so (da sua):** hieu so la A-B, A la nhom dung luat thay the. Thu hang thap hon la tot hon, nen **am = nhom A xep tot hon**. Ban truoc ghi nguoc dau.

**Kiem chung dau (doi chung):** nhom A khong bao gio ghep item (`none`), seed 180000-180199: A-B = +3,99 (A xep rat xau). Dau dung: am = A tot hon.

**Luat ung vien (toi da hai, theo advisor):**
- `spread`: unit it item nhat; hoa thi gia tri cao nhat (gia tri = cost x 3^(sao-1)).
- `valuemax`: unit gia tri cao nhat.

| Hieu A-B (ghe A = luat, ghe B = ngau nhien) | Seed | Hieu so | CI 95% | n |
|---|---|---|---|---|
| null: ngau nhien vs ngau nhien | 140000-140999 | -0,015 | [-0,12, +0,09] | 1000 |
| spread vs ngau nhien | 140000-140999 (giu-lai) | -0,70 | [-0,80, -0,59] | 1000 |
| valuemax vs ngau nhien | 140000-140999 (giu-lai) | -0,80 | [-0,91, -0,70] | 1000 |
| valuemax vs mac dinh (cost cao nhat) | 140000-140999 (giu-lai) | **-1,09** | [-1,19, -0,99] | 1000 |
| spread vs ngau nhien | 180000-180399 (dev) | -0,76 | [-0,92, -0,59] | 400 |
| valuemax vs ngau nhien | 180000-180399 (dev) | -0,87 | [-1,03, -0,71] | 400 |

**Ket luan:** luat `valuemax` (dua item cho unit co gia tri cao nhat) tot hon mac dinh cua env khoang 1,1 thu hang tren seed giu-lai, va tot hon ngau nhien khoang 0,8. Chon cho `valuemax` duoc dong bang cho giai doan 4 trong engine nay.

**Gioi han:**
- Day la so trong engine (Set 17, mo phong item don gian), chua phai TFT that.
- Chua do co che (item tap trung hay trai deu) vi chua ghi log tong item theo ghe; buoc nay chua lam.
- Gia tri 1,1 lon hon nhieu so voi cac luat dau (cheapest/ngau nhien vs mac dinh ~0,2). Can kiem tra them truoc khi tin manh (vi du tren seed moi, va luat khac cung loai).
- Lan chay 400 lobby dau (130000) khong dung de ket luan do CI chua 0; do la cau hinh cu, da bo sung seed moi.

## Dinh vi trong tran (giai doan 4): don bay that trong engine (do bang probe)

Engine dat vi tri theo vai tro (`_frontline_score`: tank truoc, carry sau), va env khong co hanh dong dinh vi. De do, `scripts/pos_probe.py` patch `_build_team` va `rounds._fight`: nhom A doi vi tri sau mac dinh, nhom B giu mac dinh, cung lobby, cung chinh sach v4. Am = A tot hon.

| Nhom A | Seed | A-B | CI 95% | n |
|---|---|---|---|---|
| null (mac dinh vs mac dinh) | 200000-200399 | -0,04 | [-0,20, +0,13] | 400 |
| xao ngau nhien (cac o giu nguyen) | 200000-200399 | +1,00 | [+0,85, +1,16] | 400 |
| carry ra truoc, tank sau | 200000-200399 | +1,98 | [+1,84, +2,12] | 400 |

**Ket luan:** mac dinh theo vai tro tot hon nhieu so voi ngau nhien va so voi dao nguoc. Vi tri la don bay that trong engine. Chua biet mot chinh sach dinh vi hoc duoc co vuot mac dinh hay khong; buoc do can them dau vao dinh vi cho clone/teacher.

## Tai hien valuemax (seed moi) va co che trang bi

- Tren seed moi 190000-190999 (chua dung): valuemax vs mac dinh **-1,06** [-1,16, -0,95]; spread vs mac dinh -0,95 [-1,06, -0,85]; null +0,015 [-0,09, +0,12]. Hieu ung duoc tai hien.
- Co che (200 lobby, seed 190000-190199, `scripts/item_mechanism.py`): ghe valuemax dat item len unit co gia tri trung binh 5,10, so voi 2,98 cua mac dinh (dem cac lan gan co gia tri). Ty le item roi vao unit da co item: 23,8% so voi 20,1%. Vay co che la chon dung carry (unit 2-3 sao, gia tri cao), it hon la don item vao mot unit.

## Chinh sach hoc duoc dau tien: CEM chon dich trang bi (engine)

`scripts/cem_item.py`: diem unit = w . [cost, sao, items, gia tri, la tank]; chon unit diem cao nhat. CEM 3 the he x 8 ung vien x 200 lobby (tinh chinh 220000-220199, co dinh moi the he). Giu lai 230000-230999 (chua dung), so voi mac dinh.

- Trong so cuoi (trung binh elite): cost 0,04; sao -0,19; items 0,04; gia tri 0,30; tank **1,41**.
- Giu lai: A-B = **-1,05** [-1,15, -0,95] (n = 1000). Null (mac dinh vs mac dinh) ~ 0 (xem muc tren).
- So voi luat heuristic `valuemax`: -1,06 (190000) va -1,09 (140000). **Chinh sach hoc duoc ngang luat heuristic, khong vuot.** Tin hieu chinh nam o vai tro tank, khong chi gia tri.

Gioi han: CEM chi 3 the he, 200 lobby moi ung vien; chua thu voi nhieu the he hon hoac kien truc lon hon.

## Set 17 va Set 18 (luu y cho nhanh `sim` va cac workstream khac)

- Mo phong nay chay tren noi dung **Set 17** (block trong CDragon). Tro choi dang chay la Set 18 (patch 18.7). Ket qua o day la cho Set 17, khong phai cho Set 18.
- Bang odds Set 17 lech so voi Set 18 o cap 8-9 (xem `docs/needs.md` U2 tren nhanh `claude/dazzling-feynman-g7a0b9`). Tren Set 18 chi co phep chay DA-only (muc Set 18 o tren).
- Hop dong du lieu: snapshot CDragon dung patch cho mo phong la viec cua `sim`; dang chan Gate 0 tren noi dung that. Chua co snapshot Set 18 day du.

## Yeu cau du lieu (ghi trong handoff, chuyen cho nguoi dung)

- Odds va XP Set 18 theo cap, nguon chinh thuc hoac ban chup client. Can de chay Set 18 khong lech Set 17.
- Ban chup shop that (`captures/`), neu can cho giai doan 6.
- Nguon du lieu TFT that cho giai doan 6 va xac nhan dieu khoan API Riot.

## Dinh chinh (noi dung that, buoc 4)

- **Rut lai nhan "134 EQUIP no-op" tren CDragon.** Chan doan truoc so sanh so thanh phan truoc va sau ca buoc env, nen tron lan cap thanh phan cuoi vong (PvE). Chan doan truc tiep (bao `_equip`, `scripts/diag_equip_real.py`): **134/134 EQUIP tieu thu dung 2 thanh phan.** Khong can dan xuat noi dung moi cho EQUIP tren CDragon.
- Tren CDragon 18.7 Set 17: 10 thanh phan co so, 55/55 cap co cong thuc (`scripts/diag_real_items.py`). 622 item co so khac khong bao gio duoc cap (env chi cap thanh phan co trong cong thuc hoan chinh).
- Kich thuoc block (nhan that): flat 168 (synthetic 126, khac do trait 44 so 2), uni 85 (giong synthetic). Flat khong chuyen duoc giua noi dung; uni chuyen duoc ve chieu.

## Noi dung that: CDragon latest (18.7) (buoc 4)

Nguon: `cdragon_latest_fetched-2026-11-23.json` (18.7). Nhan: "CDragon latest (18.7), Set 17 block" (TFTSet17) va "Set 18 roster" (TFTSet18, cung file). Dung `tft_sim/real_content.py`.

**Dieu chinh EQUIP:**
- Set 17: 10 thanh phan co so, 55/55 cap co cong thuc. 134/134 EQUIP tieu thu dung 2 thanh phan (`scripts/diag_equip_real.py`). Khong can sua noi dung.
- Set 18: roster CDragon 18.7 tron hai ho thanh phan: `DA_Component_*` (Set 18) va `TFT_Item_*` (con sot tu Set 17). Ban goc co 20 thanh phan, 116/210 cap thieu cong thuc, 34.433/34.456 EQUIP la no-op. **Cach sua ban dau (them cong thuc placeholder `it_placeholder_<x>_<y>`, AD 0.1) bi RUT LAI**: do la noi dung bia, khong phai du lieu that. Cach dung (`build_real_set18_clean`, `scripts/diag_real_items.py`): loai item co thanh phan `TFT_Item_*` va item co so `TFT_Item_*`; chi giu thanh phan `DA_*`. Ket qua: 10 thanh phan, 55/55 cap co cong thuc that, 135/135 EQUIP tieu thu dung 2 thanh phan, khong placeholder.
- Cac ket qua Set 18 TRUOC khi sua (2,8 trieu dong test, 98% la EQUIP) va ket qua dung placeholder **KHONG dung**; da luu thanh `s18_old_eqbug_*` va `s18fp_*`.
- Bo chuan hoa: cot hang (sd < 1e-6) bi chia cho ~0. Cot `gods` hang tren synthetic nhung co do lech chuan ~0,5 tren noi dung that, gay z ~ 1e6 va sap REROLL xuong 0%. Da sua trong `bc_train.train` (sd = 1 cho cot hang). Ket qua 67% o ban cu la **artifact cua bo chuan hoa, da rut lai**.

**Thu thap:** Set 17: train 40000-40399, val 40400-40499, test 41000-41199 (614k / 154k / 306k dong). Set 18 (DA-only): train 40000-40399 (591k), test 41000-41199 (295k).
Toc do: ~9 lobby/s tren noi dung that (scripted). Chay tuan tu: chay song song gay het bo nho.

**Chuyen giao (uni 85 chieu, epoch 40, 5 seed, exact, >=2 hop le):**

| dieu kien (5 seed, min-max) | overall | BUY_SHOP | BUY_XP | PASS | REROLL | PICK_AUGMENT | REROLL_AUGMENT |
|---|---|---|---|---|---|---|---|
| synthetic -> Set 17 | 90.0 (89.4-91.0) | 88.8 | 94.8 | 80.5 | 82.0 | 92.2 | 33.8 |
| Set 17 -> Set 17 | 99.95 | 99.8 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 |
| Set 17 -> Set 18 (DA-only roster) | 99.3 (98.5-99.9) | 99.7 | 99.7 | 97.9 | 100.0 | 100.0 | 100.0 |
| Set 18 -> Set 18 (DA-only) | 99.95 | 99.7 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 |

Ten hang: "Set 17 -> Set 18" nghia la huan luyen tren Set 17, kiem tra tren Set 18 (DA-only). Ket qua file: `results/fixed/real/transfer_real.json`.

Doc ket qua:
- **Synthetic chuyen sang Set 17 o muc ~90%** (sau khi sua bo chuan hoa), nhung REROLL_AUGMENT chi ~34% va PASS/REROLL ~80%. Synthetic 8 tuong va 2 trait khong phu duoc phan phoi that, nen hanh vi kho chuyen nhat la REROLL_AUGMENT va PASS.
- **Trong noi dung that, metric bao hoa** (~100%). Quyet dinh teacher gan nhu ham xac dinh cua dac trung; chi 1,5% dong test co dac trung trung voi train (khong phai ro ri lon). Vi vay phep so "Set 17 -> Set 18" (99,3%) **khong phan biet duoc** nhieu: no chi cho biet universal cua Set 17 gan nhu du cho roster Set 18 duoi cung quy tac.
- Rut lai: "Set 18 tuong duong" khong duoc chung minh tren TFT that; day chi la teacher scripted tren ban dung tuong ung voi CDragon 18.7.

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

Chan doan clone (tren cung seed 2000-2199). **Luu y pham vi: moi 8 ghe deu la clone** (`diag_run` dung cung policy cho moi ghe), nen day khong phai do tren lobby A/B. Ma tran o muc loai, khong phai hanh dong chinh xac.
- 0 hanh dong bat hop le; 243.7 buoc/game (scripted 225.7).
- 0 phase cham gioi han MAX_PLANNING_STEPS = 50 (scripted cung 0). Clone khong bi lap den gioi han.
- Ma tran nham o muc loai (teacher -> clone): BUY_SHOP, FIELD, EQUIP, PICK_GOD, PICK_AUGMENT luon khop loai. Loai khop nhung chi so khac nhau nen dong y theo chi so thap hon. PASS khi teacher noi PASS: clone chon PASS 69%, BUY_XP 24%, REROLL 7%. Sai lech nay la cho chinh cua rule gold >= 54 trong teacher.
- Kiem tra cong gold (`encoding.py`): gold la scalar THO trong observation (vi tri 0, khong clip). Teacher khong bao gio mua XP hay roll duoi 54 gold, va khong bao gio PASS khi du 54 gold (val: 0 / 21.181 BUY_XP duoi 54; 0 / 13.505 PASS tren 54). Clone dong y PASS 100% o gold < 40, 92% o 40-49, nhung chi 71% o 50-53 (8.707 dong). Loi tap trung dung o nguong 54: day la boundary fit (3 epoch, chuan hoa) va phan bo lech, KHONG phai thieu feature.
- PICK_AUGMENT va REROLL_AUGMENT dung tier augment trong state privileged cua teacher, khong co trong observation. Day la khoang trong quan sat, khong phai ket qua hoc.

### Lap lai va co che (fresh seeds 3000-3199, eps=0.1 = A, scripted = B)

| Eps | diff A-B | CI95 |
|---|---|---|
| 0.05 | -0.22 | [-0.44, 0.04] |
| 0.10 | -0.18 | [-0.43, 0.06] |
| 0.20 | -0.30 | [-0.54, -0.07] |

Ca 4 do (2000-2199 va 3000-3199) deu co dau am: ngau nhien lam tot hon scripted khoang 0.2-0.4 hang. Do lon nho, chua co y nghia thuc te. Ket luan: **scripted la teacher yeu**, khong phai bang chung ngau nhien "that" co the chuyen thanh teacher.

Co che (eps=0.1 so voi scripted): ngau nhien nang ban board nhieu hon (FIELD 14.057 so voi 8.432; BENCH_BOARD 5.497 so voi 0; SELL_BENCH 3.073 so voi 0), level som hon mot chut o vong 2-3 (3.08 so voi 3.00), ban lam gold duoi 54 (XP/REROLL 786 lan, scripted 0). Chenh lech board va HP nho (~0.1 don vi). Khong tim thay co che lon duy nhat.

Ung vien teacher (1 wrapper, seed 4000-4199): scripted, nhung PASS -> BUY_XP khi gold >= 40. Ket qua: diff +0.18, CI95 [-0.05, 0.43]. **Khong tot hon scripted; giu scripted lam teacher.**

### Transfer A -> B (ket qua)

**Noi dung B**: `src/tft_sim/content_b.py`. Cung 8 tuong, cung thu tu, cung so chieu flat (126) va aux (20). Hoan vi co dinh seed 1234 tren cost va tuple trait giua cac tuong (cung multiset). Patch rieng `synth-fullrecipe-B`. Kiem tra: `diag_equip_b.py` 898 EQUIP, 0 khong tieu thu.

**Du lieu**: A train 200-349, A val 800-849 (cu). B train 5000-5149, B val 7000-7049, B test 6000-6199 (moi). Diag seed 2000-2199, 3000-3199, 4000-4199 khong trung.

**Bien the**: flat (day du); flat+slot (flat + aux); universal = scalars + opponents + gods + aux (82 chieu, bo shop, bench, board, traits). Epoch 10 la mac dinh cua lan chay dau, KHONG duoc chon tu val. Universal van tang o epoch 40 (93.7 -> 95.5 -> 98.2), nen can chon epoch tren A val hoac B val (chua lam).

**Tieu chi (viet truoc khi chay)**: metric = dong y exact action tren hang >= 2 hop le, rieng BUY_SHOP.
- L = flat, A -> B.  T = universal, A -> B.  U = bien the tot nhat, B -> B.
- Void neu U - L < 0.05. Pass neu T >= L + 0.8 (U - L).
- Kiem soat: cac loai khac, A -> A (val) so voi A -> B (test). Dich chuyen > 2 diem phai dieu tra.

**Ket qua BUY_SHOP** (`results/fixed/transfer/transfer_results.json`):

| Bien the | A -> A (val) | A -> B (test) | B -> B (test) |
|---|---|---|---|
| flat | 81.5% | 80.0% | 82.6% |
| flat+slot | 93.3% | 92.9% | 94.0% |
| universal | 93.5% | 94.0% | 93.8% |

- L = 80.0%, U = 94.0% (flat+slot, B->B), gap = 13.9 diem, CI bootstrap theo lobby cho U-L [13.6, 14.3].
- T = 94.0%, nguong = 91.2%, CI T-L [13.6, 14.3].
- Ket qua "Pass" tren seed 0 da RUT LAI (xem bang seed ben duoi): khac biet flat/slot la do feature, khong phai do chuyen giao.

**Kiem tra void (buoc truoc)**: mo hinh khong noi dung (scalars + opponents + gods, khong slot) dat 81.2% BUY_SHOP tren A val (`results/fixed/transfer/content_free_check.txt`), cung muc flat. Tuc la: quyet dinh mua khong doc duoc tu scalar/opponent; can block slot. Khoang cach 12 diem > 5, nen khong void.

**Kiem soat (cac loai khac, A -> A vs A -> B, bien the flat)**: BUY_XP -7.9 diem, REROLL -10.7 diem, cac loai con lai < 1.5 diem. Voi universal:
- BUY_XP: 98.7% -> 98.4% (khong doi). Flat giam 8 diem vi dung dinh danh tuong.
- REROLL: 89.9% -> 86.3%, giam 3.6 diem, CI bootstrap [-6.5, -0.7] (`results/fixed/transfer/reroll_control_check.txt`). **Vuot nguong 2 diem va CI khong chua 0. Nguyen nhan CHUA ro.** Loai nay chi ~1% hang (n=845 A val, n=2546 B test); khong anh huong ket luan BUY_SHOP. Phan bo nhan cua A va B gan nhu giong nhau (BUY_SHOP 22.0% vs 22.1%, BUY_XP 37.2% vs 37.4%), nen khong phai do lech nhan chung.

**Dieu can nho**: ket qua chi tren 8 tuong, 2 trait, 1 set synthetic. Pass chung minh model doc duoc luat mua tu feature slot (cost, trait chung), khong chi nho danh tinh tuong. Chua chung minh tren TFT that.

### Lap lai co seed: penalty = B->B minus A->B (5 seed torch, epoch 10/20/40)

**Tuyen bo "Pass" o tren da bi rut lai.** Phep so sanh cu (flat vs slot vs universal, 1 seed) bi nhieu boi khac biet ve feature: flat va slot khac nhau o khoi slot, khong chi o du lieu huan luyen. Ket qua seed ben duoi thay the no.

Moi o: trung binh [min, max] qua 5 seed. Nguon: `results/fixed/transfer/transfer_seeds.json`, bang `transfer_seeds_table.md`. Ghi chu: `train()` co tham so `seed` (mac dinh 0); lan chay dau bi trung seed, da sua.

| bien the | epoch | BUY_SHOP A->B | BUY_SHOP B->B | penalty BUY_SHOP | penalty BUY_XP | penalty REROLL | penalty overall | BUY_SHOP A->A (val) |
|---|---|---|---|---|---|---|---|---|
| flat | 10 | 80.4 [79.5, 81.2] | 82.4 [82.1, 82.6] | 2.0 [0.9, 2.9] | 6.1 [3.1, 10.4] | 4.7 [-2.9, 22.6] | 2.7 [2.0, 4.1] | 81.5 [81.3, 81.7] |
| flat | 20 | 79.8 [79.4, 80.5] | 85.0 [83.9, 85.8] | 5.3 [3.4, 6.1] | 4.6 [2.8, 6.0] | 2.5 [-0.2, 6.8] | 2.9 [2.4, 3.2] | 81.5 [80.8, 82.0] |
| flat | 40 | 79.1 [78.7, 79.4] | 88.9 [88.3, 89.2] | 9.7 [8.9, 10.4] | 3.5 [2.5, 4.2] | -0.1 [-2.1, 1.6] | 3.6 [3.3, 4.0] | 82.7 [81.7, 83.3] |
| flat+slot | 10 | 92.9 [92.8, 93.1] | 94.1 [94.0, 94.2] | 1.1 [1.1, 1.2] | 3.0 [0.0, 7.0] | 12.1 [-5.1, 23.5] | 1.7 [1.1, 2.7] | 93.2 [92.8, 93.4] |
| flat+slot | 20 | 94.2 [93.7, 94.6] | 95.7 [95.3, 96.1] | 1.4 [1.1, 2.0] | 2.8 [1.4, 3.8] | 9.2 [0.2, 17.4] | 1.7 [1.4, 1.9] | 94.8 [94.5, 95.0] |
| flat+slot | 40 | 96.2 [95.9, 96.7] | 97.9 [97.7, 98.2] | 1.7 [1.2, 2.3] | 1.7 [-0.1, 3.1] | 0.5 [-5.2, 11.3] | 1.5 [1.3, 1.7] | 97.3 [96.9, 97.7] |
| universal | 10 | 93.7 [93.3, 94.0] | 93.8 [93.5, 93.9] | 0.1 [-0.3, 0.6] | -0.4 [-1.3, 0.2] | 2.9 [0.2, 6.4] | 0.1 [-0.0, 0.3] | 93.2 [92.9, 93.5] |
| universal | 20 | 95.5 [94.7, 95.9] | 95.7 [94.9, 96.3] | 0.2 [-0.0, 0.4] | 0.1 [-0.2, 0.5] | 1.1 [-3.8, 5.0] | 0.0 [-0.1, 0.1] | 95.1 [94.3, 95.4] |
| universal | 40 | 98.2 [97.5, 98.6] | 98.1 [97.7, 98.6] | -0.1 [-0.4, 0.3] | -0.0 [-0.2, 0.1] | 0.4 [-1.8, 2.8] | -0.0 [-0.1, 0.1] | 98.0 [97.2, 98.6] |

Doc ket qua:
- **universal**: penalty BUY_SHOP ~0 o ca 3 muc epoch (khoang -0.1 den 0.2). A->A va B->B gan bang nhau. Day la ket qua ky vong vi khoi slot duoc xay tu cac dau vao cua chinh teacher (owned, trait chung), nen dieu nay chi cho thay cai dat khong lam hong suy luan tren 8 tuong, KHONG phai bang chung model tong quat hoa.
- **flat**: penalty tang theo epoch (2.0 -> 5.3 -> 9.7), nhung do B->B tang (82.4 -> 88.9) trong khi A->B gan nhu khong doi (80.4 -> 79.1). Dung cho thay model hoc danh tinh tuong: moi bang chung la B->B tang, khong phai A->B giam.
- **flat+slot**: penalty 1.1 den 1.7, nho nhung khac 0.
- **REROLL**: khong on dinh. Penalty universal 6.4 diem o seed 0 khong lap lai; o epoch 40 khoang la [-1.8, 2.8] chua 0. Nen KHONG can thi nghiem bo cot aux.
- **BUY_XP**: flat giam 3.5-6.1 diem o ca 3 epoch, do lech co he thong o nguong gold 54 (xem muc tren). Universal ~0.

### Mo: ung vien teacher

- Da thu 1 wrapper (PASS -> BUY_XP khi gold >= 40), seed 4000-4199: +0.18 [-0.05, 0.43]. Khong tot hon scripted; giu scripted.
- Nguyen nhan chenh lech teacher-ngau nhien CHUA XAC DINH. Ngau nhien nang FIELD, BENCH_BOARD va SELL_BENCH (teacher khong lam BENCH_BOARD/SELL), roi FIELD lai. Co the la hoan doi bang board ma teacher khong bao gio thuc hien. Ghi "mot ung vien da thu, nguyen nhan mo".

## Do phan giai placement (2000 lobby, seed 20000-21999, noi dung A)

Script: `scripts/big_eval.py`. Ket qua: `results/fixed/big_eval/big_eval.json`. Hieu = A - scripted, CI95 theo lobby.

| Dieu kien (A) | diff | CI95 | illegal |
|---|---|---|---|
| universal, 40 epoch, closed loop | +0.082 | [0.005, 0.157] | 0 |
| scripted, 10% ngau nhien | -0.472 | [-0.547, -0.397] | 0 |
| scripted, 30% ngau nhien | -0.167 | [-0.247, -0.088] | 0 |

Doc ket qua:
- Voi 2000 lobby, CI hep (~0.15). Ket luan 200 lobby truoc ("universal bang scripted") la sai: universal **kem hon scripted mot chut** (+0.08, CI khong chua 0).
- Ngau nhien 10% va 30% deu **tot hon** scripted co y nghia thong ke. Teacher scripted yeu; placement khong phai do tot cua viec bat chuoc teacher.
- **Kiem tra null** (scripted vs scripted, cung 2000 seed, `scripts/null_check.py`): diff **+0.034 [-0.040, 0.110]**. Harness lech nhe ve phia du (~+0.03) va CI rong ~0.15. Hieu clone +0.082 [0.005, 0.157] chi cao hon null ~0.05, KHONG tach ro. **Ket luan "clone kem hon scripted" CHUA duoc chung minh.** Chi noi duoc: clone khong tot hon scripted o muc nhieu do duoc.
- Vi vay, chi tieu "placement" khong the xep hang clone voi teacher o muc nho. Metric chinh van la dong y theo hanh dong.

Closed loop universal 40 epoch, 200 lobby (seed 10000-10199): 0 illegal tren A va B; dong y tren trang thai clone: PASS 99%, BUY_SHOP 98%, BUY_XP 99.8%, REROLL 97%, PICK_AUGMENT 61%, REROLL_AUGMENT 0% (n=48).

## Tier augment (buoc 3)

Them tier 3 augment dang duoc chao (truong `tiers`, ngoai `aux`, 20 cot giu nguyen). Du lieu thu lai bang `scripts/collect_tiers.py`, so dong khop lan truoc.

| Chi so (A) | Truoc | Sau |
|---|---|---|
| PICK_AUGMENT dong y (val, >=2 hop le) | 61% | 99,9% |
| REROLL_AUGMENT dong y (val, n=23) | 0% | 96% (rat it mau) |
| Closed loop 2000 lobby, diff vs scripted | +0,082 [0,005; 0,157] | +0,085 [0,011; 0,160] |
| Closed loop, dong y PICK_AUGMENT / REROLL_AUGMENT tren trang thai clone | 61% / 0% | 99,99% / 97% (n=524) |

**Ket luan:** tier augment sua duoc hanh vi augment, nhung KHONG thay doi chenh lech so voi scripted. Chenh lech nay khong do thieu augment. Null (scripted vs scripted) la +0,034, nen phan con lai khong ro nguyen nhan.

## Choi tren noi dung that: CDragon 18.7, Set 17 block (2000 lobby, seed 20000-21999)

Nhan: "CDragon latest (18.7), Set 17 block". Doi thu la **bot scripted**, khong phai nguoi choi TFT that, nen day khong phai bang chung ve TFT that. Script: `scripts/play_real.py`; ket qua: `results/fixed/real/play_*.json` (hieu hang tung lobby A-B; placement thap hon la tot hon).

| Thi nghiem | Hieu A-B | CI95 | Ghi chu |
|---|---|---|---|
| Null: scripted vs scripted | +0.013 | [-0.062, +0.084] | Chua 0: cong cu do hop le |
| Random vs scripted | +3.58 | [3.55, 3.60] | Replay 100 seed dau khop hoan toan |
| Universal clone (huan luyen tren Set 17) vs scripted | -0.0003 | [-0.075, +0.073] | Ngang bang teacher, chua vuot |
| Scripted voi eps=0.1 vs scripted | -0.263 | [-0.337, -0.192] | Tot hon scripted, CI khong chua 0 |

Doc ket qua:
- Clone khong vuot duoc teacher. Tran hien tai cua BC la teacher, khong phai dac trung. Khong them bien the BC nua.
- Teacher co 10% hanh dong ngau nhien lai tot hon teacher thuan. Chua biet do kham pha hay do mot loai hanh dong cu the; buoc tiep theo la tach theo loai.

## Loi teacher scripted tren noi dung that (phat hien buoc 2 cua advisor)

Teacher scripted co loi: **khong bao gio ban** unit. Tren CDragon 18.7 Set 17, teacher giu banc day
86% buoc (vang trung binh ~45); khi banc day va vang >= 2 no chon PASS/BUY_XP/REROLL va khong bao gio mua
(BUY_SHOP bi chan boi banc day). Hieu qua: chi ~22 lan mua moi game, ~342 lan PASS.
Ban ngau nhien (eps ban 0.1) tot hon teacher thuan (-0.36 khi chi cho SELL_BENCH) vi no giai phong banc.
Day la loi cua teacher, cung loai voi loi EQUIP truoc day, khong phai khai pha chien thuat.

Luu y: nhan xet "phan lon loi the den tu chu trinh mua-ban" trong commit truoc la **sai**; hoan gia ban
la luat TFT (`economy.py`). Khi hoan gia = 0, quy tac ban van cai thien ~0,59 tren 200 lobby (tuning). Con
phan con lai duoc quy cho loi banc day.

Ket qua quet quy tac (2000 lobby, seed tinh chinh 20000-21999, A-B; so am = quy tac tot hon):

| Bien the | Hieu A-B | CI95 |
|---|---|---|
| Ban unit re nhat khi banc day | -2,42 | [-2,47, -2,36] |
| Ha nguong vang 50 / 40 / 30 / 20 (khong ban) | +0,13 / +0,10 / +0,07 / +0,05 | chua 0 hoac gan 0 |

Ha nguong vang lam **te hon** (khong tot hon). Dong cac bien the nguong.

Chan doan tran (200 lobby tinh chinh, quy tac "cheapest"): 1,7% unit bi ban la 2 sao+; 21% co ban sao khac cua
cung tuong; 65% chung trait voi board. Tuc quy tac "cheapest" thuong ban unit con dung.

Ba bien the (2000 lobby, seed tinh chinh 20000-21999, A-B; so am = tot hon):

| Bien the | Hieu A-B | CI95 |
|---|---|---|
| cheapest: ban unit re nhat khi banc day | -2,42 | [-2,47, -2,36] |
| useless: chi ban unit mot ban, khong chung trait voi board (khong co thi khong ban) | -0,66 | [-0,73, -0,59] |
| hybrid: useless truoc, khong co thi cheapest | -2,58 | [-2,63, -2,52] |

Quy tac **hybrid** duoc chon (tot nhat tren seed tinh chinh) va dong bang truoc khi kiem dinh tren seed moi.

**Kiem dinh giu-lai (seed 30000-31999, chua dung de chon):**

| Noi dung | Quy tac hybrid vs scripted | Null (scripted vs scripted) |
|---|---|---|
| CDragon 18.7, Set 17 block | -2,62 [-2,67, -2,56] | +0,047 [-0,03, +0,12] |
| Set 18 roster (DA-only) | -3,02 [-3,07, -2,97] | chua chay |

Chua giai thich duoc muc -2,6 den -3,0: so unit tren board gan bang nhau giua hai ben (6,8 so voi 6,6), nen
co che can do them. Doi thu la bot scripted trong mo phong, khong phai TFT that.

## Vong sua teacher lan 2 (teacher hybrid) va so seed

**So seed (de khong dung lai):**
- 20000-21999: tinh chinh quy tac (cheapest, useless, hybrid).
- 30000-31999: kiem dinh giu-lai quy tac hybrid (Set 17 va Set 18, null Set 17).
- 40000-41999: chon loai nhieu (dung seed thu BC tren 40000-40499 va 41000-41199, nen khong phai "chua dung" tuyet doi).
- 50000-51999: lap lai BENCH_BOARD va null.
- 60000-61999: giu-lai cho quy tac cuoi (chua dung).

**Nhieu eps=0,1 tren teacher hybrid (seed 40000-41999):** -0,093 [-0,175, -0,013]. Sat do phan giai; teacher con sai o mot loai.

**Tach nhieu theo 11 loai tren hybrid (seed 40000-41999, A-B; am = nhieu lam teacher tot hon):**

| Loai | Hieu | CI 95% |
|---|---|---|
| BENCH_BOARD (board -> banc) | -0,36 | [-0,43, -0,28] |
| BUY_SHOP | +0,04 | [-0,03, +0,12] |
| FIELD, EQUIP, PICK_AUGMENT, PICK_GOD, REROLL_AUGMENT | -0,03 den +0,06 | chua 0 |
| SELL_BENCH | +0,31 | [+0,24, +0,39] |
| BUY_XP | +0,41 | [+0,33, +0,48] |
| REROLL | +0,93 | [+0,86, +1,00] |
| PASS | +0,93 | [+0,86, +1,00] |

**Lap lai BENCH_BOARD tren seed moi 50000-51999:** nhieu BENCH_BOARD -0,35 [-0,43, -0,27]; null hybrid vs hybrid +0,03 [-0,05, +0,11]. Hieu ung lap lai, null khong vuot 0.

Chua viet quy tac cho BENCH_BOARD: can chan doan co che truoc (`scripts/diag_bb.py`).

## Teacher v3 (hybrid + doi unit) va kiem dinh giu-lai tren seed 60000-61999 (HeuristicResolver)

Quy tac: hybrid + doi unit (FIELD unit banc manh nhat; khi board day, doi unit board yeu nhat lay unit banc manh hon).
Khoa so sanh chon tren seed tinh chinh 20000-21999 (dev): value -3,48; star_cost -3,40; cost -3,13; hybrid -2,58. Dong bang "value".

| Noi dung | Doi unit (value) vs | Hieu A-B | CI 95% |
|---|---|---|---|
| Set 17 | scripted goc | -3,50 | [-3,53, -3,46] |
| Set 17 | hybrid | -1,88 | [-1,95, -1,82] |
| Set 17 | null: scripted vs scripted | +0,013 | [-0,07, +0,09] |
| Set 18 DA-only | scripted goc | -3,80 | [-3,82, -3,78] |
| Set 18 DA-only | null: scripted vs scripted | -0,05 | [-0,13, +0,02] |

Doc ket qua: doi unit lam teacher tot hon ro rang tren seed giu-lai, va null khong vuot 0. Day van la doi thu scripted trong mo phong, khong phai TFT that. Muc chenh voi scripted goc (~-3,5) gan toi da co the cua thang do.

## Dong giai doan 1 va so seed (cap nhat)

**Giai doan 1 dong:** nhieu eps=0,1 tren teacher v3 (doi unit, value), seed 70000-71999: +0,197 [+0,118, +0,273]. Nhieu gio lam hai teacher, nen teacher v3 duoc chap nhan la teacher cho giai doan 2.

**So seed (cap nhat, da dung):**
- 20000-21999: tinh chinh (cheapest, useless, hybrid, value).
- 30000-31999: giu-lai hybrid.
- 40000-41999: chon loai nhieu (trung seed thu BC 40000-40499 va 41000-41199).
- 50000-51999: lap lai BENCH_BOARD va null.
- 60000-61999: giu-lai teacher v3 (dong).
- 70000-71999: dong giai doan 1 (eps tren v3).

**Gioi han da sua:** board co the den 10 unit (cap = cap do, toi da 10). BENCH_BOARD chi co 9 hanh dong, nen quy tac doi unit chi xet 9 slot board dau. Truoc khi sua, o cap 10 quy tac co the tra ve EQUIP (35) do lech chi so; da sua va kiem tra 50 lobby cho 0 hanh dong bat hop le.

**Giai doan 2 (dang chay):** uni2 = uni (85) + bench/board (94) = 179 chieu. Seed: train 80000-80399, val 80400-80499, test 81000-81199 (du lieu voi teacher v3 tren ca 8 ghe). Choi: 90000-91999 (chua dung).

## Giai doan 2: clone v2 (uni2) ngang teacher v3

**Du lieu:** teacher v3 tren ca 8 ghe. Train 80000-80399 (1,50 trieu dong), val 80400-80499 (375 nghin), test 81000-81199 (748 nghin). Dac trung uni2 = uni (85) + bench/board (94) = 179 chieu.

**Do khop (test, 3 seed):** 99,6-99,7% tong; theo loai thap nhat la REROLL (94-97%) va BENCH_BOARD (96-97%). Do khop da bao hoa; quyet dinh bang choi.

**Choi (seed 90000-91999, chua dung):**

| Phep | Hieu A-B | CI 95% |
|---|---|---|
| null: v3 vs v3 | +0,013 | [-0,06, +0,09] |
| clone vs v3 (Set 17) | +0,002 | [-0,07, +0,08] |
| clone vs scripted goc (Set 17) | -3,46 | [-3,50, -3,43] |
| clone (huan luyen Set 17) vs v3, Set 18 DA-only | -0,08 | [-0,16, +0,002] |

**Ket luan:** clone ngang teacher v3 tren Set 17 (CI chua 0) va gan ngang tren Set 18 DA-only. Tran cua clone la teacher v3; de vuot can giai doan 3 (tim kiem hoac RL).

## Giai doan 3: tim kiem tham so tren v3 (dong, HeuristicResolver)

**Ket qua:** CEM 4 the he, 12 ung vien moi the he, 400 lobby moi ung vien (seed dev 100000-100399). Trung binh quan the ~ +0,10 (da so kem v3); ung vien tot nhat trong +-0,03. **Chua tim thay cau hinh nao tot hon v3 o do phan giai +-0,17.** Khong chay giu-lai (seed 110000 chua dung).

**Kiem tra nut:** nut xp_floor va reroll_floor co tac dung (dem BUY_XP 11.744 so voi 19.337 o theta mac dinh; vang cuoi 4 so voi 51). Nghia la cac nut song, nhung khong cai nao cai thien placement o do phan giai nay.

**Bien du bao placement (Spearman, 1.600 seat-game, v3 vs v3):** cap (level) 0,86; suc manh ban (board_strength) 0,77; vang 0,61; so unit 2 sao 0,40; HP ~0 (HP la ket qua, khong phai nguyen nhan).

**Ket luan:** do phan giai cua tham so hoa la +-0,17 tren 400 lobby. Cap va suc manh ban du bao placement manh, nhung v3 da toi uu chung qua quy tac swap va nut kinh te. **Ket luan giai doan 3 tren HeuristicResolver (da cu, xem muc Engine ben duoi):** khong cau hinh tham so nao vuot v3 trong do phan giai +-0,17. Dieu nay chi dung voi tham so hoa do thi; no KHONG chung minh rang khong con cai thien nao o cap quy tac. Muc "sat tran" cua README cu la sai va da bo.

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
- Nghien cuu theo patch: xem `docs/knowledge/`. Thiet ke: `docs/PATCH_MODEL.md`. Transfer A -> B (BUY_SHOP, noi dung tong hop) da chay; tieu chi vs scripted cua PATCH_MODEL §5 chua chay.

## Ket qua cloud agent (giam sat tu dong, 2026-11-24)

Quet `origin` sau commit `0ba34f3`. Hai nhanh co commit moi; hai nhanh chua co gi moi hoac chua ton tai. Moi so duoi day lay tu file trong nhanh, kem seed.

**DT — `codex/sim-dt` @ `01d2339` (che do giam: `reduced_low_memory`).** Khong phai ke hoach 2.000 van: chi thu thap `s1` (seed 300000–300499, 500 van) va `s4` (seed 301500–301999, val + test). `s2`, `s3` khong thu. Nguon: `results/fixed/real/shard_summary.json`.
- Tach: train 1.479.411 dong (300000–300499); val 295.884 (301500–301599); test 1.183.655 (301600–301999).
- Thoi gian 1.248 s; RAM dinh lay mau 6.350 MB (huan luyen 5.143 MB). Kiem tra lai 3 seed dau (300000–300002): dong va action giong het.
- Clone v5, 3 seed × 40 epoch (`results/fixed/real/bc_v5.json`), do **do khop hanh dong voi teacher** tren test, khong phai placement:
  - tong: seed0 0,9889; seed1 0,9978; seed2 0,9971.
  - thap nhat theo loai: REROLL seed0 0,6544 (seed1 0,9327; seed2 0,9939); BENCH_BOARD 0,9628–0,9736; BUY_XP seed0 0,9131.
- Checkpoint `results/checkpoints/clone_v5_seed0.pt` (188.905 byte) da commit.
- **Chua co so placement cho v5.** Chua co CI95; vong E chua chay.

**R — `cursor/sim-r` @ `bcf9ebe`.** `docs/handoff/set18-sources.md` cap nhat: cap 7 = 19/30/40/10/1 (Riot 17.1, da kiem nguon cong khai); XP 2→7 = 2/6/10/20/36 (Riot 14.15, khop 13.23). Da doi chieu (2026-11-25): doc R dan `content-metadata.json` ghi version 16.23; snapshot co `DA_18_Kennen` = Inferno + Executioner, `DA_18_Ivern` = Greenfather, `DA_Krug18` = Riftbeast + Brawler, la trang thai truoc 18.7. Nhan "18.7" cho snapshot la sai. Anh huong: du lieu Set 18 (DA) trong mo phong khong khop 18.7. Set 17 (dung cho E) khong duoc kiem tra rieng, nen nhan "18.7" tren snapshot can sua khi co file dung.
- Commit `bcf9ebe` noi snapshot CDragon trong repo co version string **16.23**, khong phai 18.7. Toi kiem tra snapshot `tft-sim/data/cdragon/cdragon_18.7_2026-11-23.json.gz`: sha256 khop README, nhung khong tim thay chuoi version nao trong noi dung. **Chua giai quyet duoc; can kiem tra truoc khi tin nhan 18.7 cho Set 18.**
- File ghi "Cap nhat: 2026-11-25 (gio Bangkok)". Day la dung: 21:00 UTC ngay 24 la 04:00 ngay 25 o Bangkok, khong phai loi.

**C — `codex/sim-c`:** chua co commit moi (van `0ba34f3`).

**E — `codex/sim-e`:** chua ton tai. DT da commit checkpoint nen E co the bat dau khi nguoi dieu phoi tao nhanh tu `codex/sim-dt`. Chua chay gi.

Commit ket qua nay chi them muc moi; so cu khong sua.


## Ket qua CEM trang bi (vai C, codex/sim-c @ 65f6c1c, 2026-11-24)

Nguon: `results/fixed/real/cem_item_v2.json` va `item_valuemax_vs_default_240000.json` tren `codex/sim-c`. CEM 6 the he, 12 ung vien, dev 220000–220199 (200 van moi ung vien). Kiem dinh cuoi tren seed giu-lai 240000–240999 (1.000 van, chua dung truoc do).

- **Tuyen tinh CEM (vs mac dinh):** A−B = **−1,095**, CI95 [−1,198; −0,987], n = 1.000. Am = CEM tot hon mac dinh. Trong so: [0,084; −0,175; 0,063; 0,555; 1,010].
- **Valuemax vs mac dinh (240000–240999):** A−B = **−1,006**, CI95 [−1,105; −0,899] (bootstrap 2.000 lan, tu `per_lobby_diff`, n = 1.000). Khop voi uoc luong truoc do (~1,1 vi tri), nhung giu-lai hep hon.
- **So sanh truc tiep CEM vs valuemax chua lam.** Chenh lech giua hai ket qua (−1,095 so voi −1,006) nho hon do rong CI, nen chua the noi CEM tot hon valuemax.
- Dev best_fit o the he 5 khoang −1,19 (dev 200 van, nhieu mau); khong dung so dev lam ket luan.

Trang thai: vai C xong ve trang bi. Chua co placement cho clone v5 (vai E chua chay).


## Ket qua kiem dinh clone v5 (vai E, codex/sim-e @ 48a228f, 2026-11-25)

Nguon: `results/fixed/real/play_v5_v4null.json` tren `codex/sim-e`. Nhan: v5 rut gon (500 van train), seed0. Seed 241000–241999 (1.000 van, chua dung truoc do). Engine (Set 17).

- **v4null (kiem tra am, v4 vs v4):** A−B = **−0,058**, CI95 [−0,164; +0,048] (bootstrap 2.000 lan, tu `per_lobby_diff`, n = 1.000). CI chua 0, dung nhu ky vong. Khong co luot di khong hop le.
- **Chua co:** clone_v4, clone_v3, clone_scr. E van dang chay; se ghi khi co file.


## Ket qua kiem dinh clone v5 — day du 4 phep (vai E, codex/sim-e @ ff95d66, 2026-11-25)

Nguon: `results/fixed/real/play_v5_<mode>.json` tren `codex/sim-e`. Nhan: v5 rut gon (500 van train), seed0. Seed 241000–241999 (1.000 van moi phep, chua dung truoc do). Engine (Set 17). A−B am = A tot hon. CI95 tinh lai bang bootstrap 2.000 lan tu `per_lobby_diff`; khop voi CI trong file (lech toi da 0,011).

| Phep | A−B | CI95 | n | Luot khong hop le | Ky vong | Dat? |
|---|---|---|---|---|---|---|
| v4null (v4 vs v4) | −0,058 | [−0,164; +0,048] | 1.000 | 0 | CI chua 0 | Dat |
| clone_v4 (clone vs teacher v4) | −0,050 | [−0,162; +0,061] | 1.000 | 0 | CI chua 0 | Dat |
| clone_v3 (clone vs teacher v3) | −0,797 | [−0,901; −0,699] | 1.000 | 0 | hieu am | Dat |
| clone_scr (clone vs scripted) | −2,396 | [−2,483; −2,308] | 1.000 | 0 | hieu am | Dat |

**Ket luan:** clone v5 (ban rut gon, seed0) bat chuoc duoc teacher v4 (CI chua 0 o phep clone_v4, hieu gan 0). Clone tot hon teacher v3 va scripted goc, CI khong chua 0.

**Han che:** day la 1 checkpoint (seed0) tren 1.000 lobby moi phep, chi do tren Set 17 engine. Chua co Set 18. Clone_v4 chua chung minh bang nhau voi v4, chi chua co bang chung chenh lech (CI rong ±0,11).


## Kiem dinh valuemax vs mac dinh tren seed moi (2026-11-25, chay cuc bo)

Nguon: `results/fixed/real/item_valuemax_vs_default_250000.json` (gop 4 shard 250000–250999, moi shard 250 van). Luat: teacher v4 (`make_aug_rule`), chi thay luat chon muc tieu trang bi: `valuemax` (unit gia tri cao nhat, gia tri = cost × 3^(sao−1)) so voi `default` (unit cost cao nhat, muc mac dinh cua engine). Seed 250000–250999 (1.000 van, chua dung truoc do; ngoai dai P 242000–249999 da dat truoc). Engine (Set 17).

- **A−B = −1,016**, CI95 [−1,113; −0,913] (bootstrap 2.000 lan, n = 1.000). Am = valuemax tot hon.
- Lan dau tren seed 240000–240999: −1,006, CI [−1,105; −0,899]. Hai khoi seed doc lap cho ket qua gan nhau.

**Ket luan:** valuemax tot hon mac dinh khoang 1 vi tri tren teacher v4. Day la lan lap lai thu ba tren khoi seed moi (190000, 240000, 250000), khong phai phat hien moi. Chua co noi dung nao trong engine (`decide.js`) su dung luat chon muc tieu trang bi, nen chua co noi nhan ket qua nay.

**Cach doc:** ket qua nay do teacher, khong phai engine. Chua dua vao `decide.js` hay `src/`; viec do thuoc workstream `engine` va can kiem chung tren du lieu that (Phase 4 trong roadmap). Ket qua chon valuemax duoc mo ta trong sim, khong phai hoc trong so: CEM (−1,095) chua duoc so truc tiep voi valuemax va khong du bang chung de chon.

**Han che:** tat ca do tren engine voi bot, khong phai nguoi choi that. Khong co kiem dinh tren Set 18.

## Ket thuc vong cloud

- Sau vong nay, khong con phep cloud nao dang chay. Clone khop teacher v4 (kiem dinh E). Clone khong the vuot teacher, nen khong thu them du lieu DT.
- Ket qua clone_v3 (−0,797) va clone_scr (−2,396) phan anh loi the cua v4, truyen qua clone; khong phai loi the moi cua clone.
- Vai P (dinh vi) va Set 18 de tam dung.

## Thí nghiệm mask nhóm HUD (2026-11-25, bằng chứng bot)

Đăng ký trước: `docs/model-plan.md` 10.6. Teacher v4 (`make_aug_rule`), EngineResolver, TFTSet17. Huấn luyện: seed 150000–150399 (train, 1,18 triệu dòng), 151000–151199 (test). Chơi: seed 260000–260999, 1000 lobby, A = clone, B = teacher v4. CI95 bootstrap theo lobby.

| Điều kiện | Số chiều | Khớp test | A−B (CI95) |
|---|---|---|---|
| full | 185 | 0,9966 | A−B = −0,051 [−0,157; +0,057] (kiểm soát hậu kỳ, xem mục dưới) |
| a: HUD | 14 | 0,6355 | +2,181 [2,090; 2,271] |
| b: a + HP, round | 16 | 0,6357 | +2,306 [2,225; 2,390] |
| c: b + bàn, bàn chờ | 120 | 0,9927 | +0,498 [0,397; 0,591] |
| null: v4 vs v4 | — | — | −0,023 [−0,128; 0,086] |

So sánh theo cặp (per-lobby): b−a = +0,126 [0,004; 0,244]; c−b = −1,809 [−1,940; −1,683]; c−a = −1,684 [−1,820; −1,538].

Đọc kết quả:
- Bàn và bàn chờ là nhóm có tác động lớn nhất. Khi thêm nhóm này, clone gần teacher hơn 1,8 điểm.
- HP và round không giúp: b−a nhỏ hơn ngưỡng 0,2 đã đăng ký. Điều này khớp kiểm tra: teacher v4 không đổi hành động khi đổi HP (20/20).
- Clone c vẫn kém teacher khoảng 0,5 điểm, CI không chứa 0. Clone chưa bằng teacher.
- Null gần 0, nên harness không lệch.
- Nội dung là `TFTSet17` (real_content, dữ liệu CDragon), không phải 8 tướng synthetic. Vẫn là mô phỏng: không có bằng chứng so với trận thật.
- Điều kiện c vẫn còn ẩn augment (khớp PICK_AUGMENT 0,44 so với 0,999 ở full), và full chưa được chơi. Vì vậy khoảng +0,50 của c **bị lẫn** với việc thiếu augment. Không được kết luận "clone kém teacher" từ c. Cần chơi full để có mốc.
- Chênh full − c (ghép cặp theo lobby, cùng seed, cùng teacher, seed 260000–260999): **−0,548 [−0,686; −0,411]**. Khoảng này là tác động của nhóm ẩn (augment, gods, opponents) gộp lại; không tách được từng nhóm, vì chưa có điều kiện riêng.

## Kiểm soát hậu kỳ: full (2026-11-25, bằng chứng bot)

**Full (hậu kỳ, không có trong đăng ký 10.6):** clone `mask_full` (185 chiều) vs teacher v4, seed 260000–260999, EngineResolver. A−B = −0,051 [−0,157; +0,057]. Full không khác teacher. Vậy khoảng +0,50 của điều kiện c so với teacher là do các chiều bị ẩn (augment, gods, opponents), không do bàn hay bàn chờ.

**Giải đấu hỗn hợp v1 (đăng ký 10.8, bị thay thế bởi v2):** lỗi thiết kế: policy có thể trùng ghế, hoán vị ghế không độc lập với luồng env, CI không khớp với trung bình theo lobby. Các số dưới đây giữ để đối chiếu, không dùng để kết luận. Xem "Giải đấu v2".

**Giải đấu hỗn hợp v1 - số liệu:** seed 270000–270999, 1000 lobby, 8 ghế, mỗi ghế chọn policy từ pool bằng `default_rng(seed)`, có thể trùng. Trung bình placement (CI95 bootstrap theo lobby, số ghế):

| Policy | Placement TB | CI95 | Ghế |
|---|---|---|---|
| v4 | 3,944 | [3,774; 4,024] | 1365 |
| mask_full | 4,018 | [3,801; 4,045] | 1377 |
| v4_null | 4,104 | [3,956; 4,212] | 1276 |
| mask_c | 4,306 | [4,201; 4,448] | 1316 |
| v3 | 4,583 | [4,466; 4,717] | 1392 |
| scripted | 6,122 | [6,112; 6,353] | 1274 |

Đọc kết quả:
- v4 và v4_null là cùng một policy nhưng cách nhau 0,16 điểm. Đây là nhiễu của giải đấu không cân bằng. Chênh này dưới ngưỡng 0,2 đã đăng ký nhưng không bằng 0, nên giải đấu chưa đủ để xếp hạng. Cần thêm lobby và cân bằng ghế trước khi dùng bảng này.
- Bảng này là placement trung bình trong lobby hỗn hợp, không phải đấu trực tiếp. Phụ thuộc vào 7 đối thủ còn lại.
- Thứ tự chung: teacher ≈ full < c < v3 < scripted. Phù hợp với các kết quả trước.
- valuemax và CEM chưa đưa vào pool (monkeypatch toàn cục).



## Giải đấu v2 (2026-11-25, bằng chứng bot)

Đăng ký: `docs/model-plan.md` 10.9. 4000 lobby, seed 280000–283999, EngineResolver, TFTSet17. 8 policy cố định mỗi lobby, hoán vị ghế độc lập. Completed 32000/32000 ghế, illegal 0. Kiểm `league2.py selftest`: PASS trên 5 seed.

| Policy | Placement TB | CI95 | Chênh so với v4 (CI95) |
|---|---|---|---|
| v4_valuemax | 2,897 | [2,832; 2,962] | −1,049 [−1,144; −0,950] |
| v4 | 3,946 | [3,886; 4,005] | — |
| v4_null | 3,961 | [3,900; 4,026] | +0,015 [−0,080; +0,110] |
| mask_full | 3,991 | [3,929; 4,051] | +0,045 [−0,045; +0,136] |
| mask_c | 4,396 | [4,335; 4,457] | +0,450 [0,355; 0,545] |
| v3 | 4,595 | [4,535; 4,653] | +0,648 [0,558; 0,738] |
| mask_a | 6,013 | [5,948; 6,079] | +2,067 [1,970; 2,161] |
| scripted | 6,201 | [6,135; 6,263] | +2,255 [2,161; 2,351] |

Đọc kết quả:
- **Tiêu chí đạt:** v4 − v4_null có CI [−0,080; +0,110], chứa 0. Nửa độ rộng khoảng 0,095, gần mục tiêu 0,1.
- valuemax (luật trang bị theo giá trị, chỉ trên ghế đó) tốt hơn v4 khoảng 1,05 điểm, trong cùng giải đấu.
- mask_full không khác v4. mask_c kém hơn 0,45; điều này khớp với nhóm augment bị ẩn (xem mục trên).
- Thứ tự: v4_valuemax < v4 ≈ v4_null ≈ mask_full < mask_c < v3 < mask_a < scripted.

Thông lượng: 4000 lobby trong 738 giây trên 4 tiến trình, khoảng 19.500 lobby mỗi giờ (chỉ chơi). Thu dữ liệu có đặc trưng: khoảng 0,9 giây mỗi lobby trên một tiến trình, gồm cả thời gian khởi động.

## Giải đấu drop: mô hình group-dropout (2026-11-25, bằng chứng bot)

Đăng ký: `docs/model-plan.md` 10.10. Seed 284000–287999, 4000 lobby, pool drop, EngineResolver, TFTSet17. Hoàn tất 32000/32000 ghế, illegal 0. Phân tích: `scripts/dropout_analyze.py`, kết quả `results/fixed/real/dropout_league.json`.

| Cặp (chênh theo lobby) | Trung bình | CI95 | Tiêu chí |
|---|---|---|---|
| v4 − v4_null | +0,034 | [−0,065; +0,127] | CI chứa 0: đạt |
| drop@full − mask_full | +0,030 | [−0,074; +0,125] | trong ±0,2: đạt |
| drop@c − mask_c | +0,002 | [−0,101; +0,097] | trong ±0,2: đạt |
| drop@a − mask_a | −0,048 | [−0,152; +0,054] | trong ±0,2: đạt |

Đọc kết quả: một mô hình dropout cho ba điều kiện không kém các mô hình mask riêng. Kiểm tra trước khi chơi cũng đạt (khớp test lệch ≤ 0,005, leak test 0). Chỉ nói về Set 17 với bot teacher v4, không nói về HUD thật hay Set 18.

## Nghiên cứu combat (2026-11-25, mô phỏng Set 17, bot v4)

Chi tiết: `docs/research/combat-public-data.md`. Công cụ: `scripts/combat/` (schema `fight-v1`, wrapper, CLI `fight_cli.py`, selftest).

Số liệu cùng vòng (256 cặp quyết định, bootstrap theo lobby):
- Sức mạnh đơn giản (tổng cost·sao, trang bị, cấp, trait): 66% [59; 73], baseline 51%. Huấn luyện chỉ trên cặp cùng vòng.
- Bỏ ability: đồng thuận với engine đầy đủ 86%; bỏ trang bị: 83%. Khác biệt giữa hai cấu hình không tách được (CI chứa 0).
- Nuke mặc định đổi kết quả 14% cặp riêng lẻ, nhưng không thiên về một bên.

Lưu ý: con số 80% ở bản trước bị thổi phồng bởi cặp xuyên vòng (92%). Không dùng.

Chặn cần biết: augment Set 18 không có hook; 81/91 tướng Set 18 thiếu biến ability; 11/91 có vai trò. Set 18 chưa thể dự đoán chính xác bằng wrapper này.
