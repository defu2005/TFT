# Dữ liệu trận 01 (Set 18) theo vòng

Nguồn: `data/hud-audit/match01_full.json`, xuất bằng `data/hud-audit/export_sim_md.py`. Một trận, 38 vòng. Mục tiêu theo `workstream_sim`: HP, stage/round, timer, streak, bàn và bàn chờ, sao, trang bị, augment, kết quả combat, thứ hạng, HP đối thủ.

Chú thích: không đánh dấu = đọc trực tiếp (`read`); `[d]` = suy ra (`derived`); `[u]` = chưa giải (`unresolved`); `[n]` = không áp dụng (`n/a`). Đối thủ dùng mã P, không dùng tên người chơi.

## 1. Bảng theo vòng

| Vòng | t kế hoạch (s) | Timer | Cấp | XP | Vàng | Streak | HP P1..P8 | Kết quả | Loại | Đối thủ | Bàn (số, tướng) | Bàn chờ | Sao | Trang bị | Augment |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1-1 | 313.8 | —[u] | —[u] | —[u] | —[u] | —[u] | 100/100/100/100/100/100/100/100 | —[n/a] | shared arena (PvE-style or shared board), same pattern as 3-4 [d] | —[n] | —[u] | —[u] | —[u] | —[u] | —[n/a] |
| 1-2 | 328.5 | 30 | —[u] | —[u] | —[u] | —[u] | 100/100/100/100/100/100/100/100 | no damage taken (win or no-damage round, not confirmed) [d] | PvE [d] | —[n] | 1: Veigar [d] | 0 | —[u] | —[u] | —[n/a] |
| 1-3 | 364.1 | —[u] | —[derived] | —[u] | 2 [d] | —[u] | 100/100/100/100/100/100/100/100 | no damage taken (win or no-damage round, not confirmed) [d] | PvE [d] | —[n] | 1: Veigar [d] | 3 | —[u] | —[u] | —[n/a] |
| 1-4 | 399.9 | —[u] | —[derived] | —[u] | 2 [d] | —[u] | 100/100/100/100/100/100/100/100 | no damage taken (win or no-damage round, not confirmed) [d] | PvE [d] | —[n] | 2: Veigar, Veigar [d] | 5 | —[u] | —[u] | —[n/a] |
| 2-1 | 438.8 | 47 | —[u] | —[u] | —[u] | —[u] | 100/100/100/100/100/100/100/100 | loss [d] | PvP [d] | P4 [d] | 2: Alistar, Caitlyn [d] | —[u] | —[u] | —[u] | {'choice_442_458': ['U.R.F', 'Replication', 'Capital Gains II'], 'choice_459': ['U.R.F', 'Replication', 'Warpath'], 'pick': 'Warpath'} [d] |
| 2-2 | 526.1 | 22 | 4 | 2/10 | 0 | —[u] | 97/95/100/100/96/100/95/100 | win [d] | PvP [d] | P7 | 4: Alistar, Caitlyn, Rakan, Sejuani [d] | 1 | —[u] | —[u] | —[n/a] |
| 2-3 | 597.9 | 22 | 4 | 4/10 | 5 | 1 | 97/95/100/96/87/97/90/93 | win [d] | PvP [d] | P5 | 4: Alistar, Caitlyn, Rakan, Sejuani [d] | 5 | —[u] | —[u] | —[n/a] |
| 2-4 | 664.0 | —[u] | —[u] | —[u] | 5 | —[u] | 97/90/95/96/81/91/90/93 | no PvP [d] | PvE [d] | —[n] | 4: Alistar, Caitlyn, Rakan, Sejuani [d] | —[u] | —[u] | —[u] | —[n/a] |
| 2-5 | 700.7 | 17 | 5 | 0/20 | 6 | 2 | 97/90/95/96/81/91/90/93 | win [d] | PvP [d] | P2 | 5: Alistar, Kobuko, LeBlanc, Mama Beak, Xayah [d] | —[u] | —[u] | —[u] | —[n/a] |
| 2-6 | 759.3 | 21 | 5 | 2/20 | 15 | 3 | 97/84/90/96/74/91/83/93 | win [d] | PvP [d] | P6 [d] | —[u] | 7 | —[u] | —[u] | —[n/a] |
| 2-7 | 835.1 | 4 | 5 | 4/20 | 29 | 4 | 97/84/86/96/67/85/83/88 | no change in streak [d] | PvE [d] | —[n] | 5: Alistar, Kobuko, LeBlanc, Mama Beak, Xayah [d] | 6 | —[u] | —[u] | —[n/a] |
| 3-1 | 881.1 | —[u] | —[derived] | —[u] | 39 [d] | —[u] | 97/84/86/96/67/85/83/88 | win [d] | PvP [d] | P3 | 5: Alistar, Kobuko, LeBlanc, Mama Beak, Xayah [d] | 3 | —[u] | —[u] | —[n/a] |
| 3-2 | 956.3 | —[u] | —[derived] | —[u] | 40 [d] | —[u] | 97/74/76/96/67/76/81/88 | win [d] | PvP [d] | P8 | 5: Xayah, Ezreal, Kobuko, Alistar, Mama Beak [d] | —[u] | —[u] | —[u] | Heroic Grab Bag+ [d] |
| 3-3 | 1048.2 | —[u] | —[derived] | —[u] | 55 [d] | —[u] | 97/64/65/96/67/76/70/79 | win [d] | PvP | P7 | 6: Xayah, Ezreal, Kobuko, Kobuko, Alistar, Mama Beak [d] | —[u] | —[u] | —[u] | —[n/a] |
| 3-4 | 1128.5 | 2 | —[u] | —[u] | —[u] | —[u] | 97/53/65/96/60/76/62/66 | no damage taken (win or no-damage round, not confirmed) [d] | PvE [d] | —[n] | —[u] | —[u] | —[u] | —[u] | —[n/a] |
| 3-5 | 1165.4 | 7 | 7 | 2/56 | 25 | 7 | 97/53/65/96/60/76/62/66 | win [d] | PvP [d] | P5 | 7: Alistar, Ezreal, Kobuko, Malphite, Mama Beak, Rek'Sai, Xayah [d] | 9 | —[u] | —[u] | —[n/a] |
| 3-6 | 1236.1 | 14 | 7 | 4/56 | 33 | 8 | 97/41/65/96/52/76/51/56 | win [d] | PvP [d] | P2 | 7: Alistar, Ezreal, Hecarim, Krug, LeBlanc, Mama Beak, Xayah [d] | 7 | —[u] | —[u] | —[n/a] |
| 3-7 | 1317.1 | 14 | 7 | —[u] | 63 | 9 | 97/30/56/96/52/66/51/43 | no PvP (streak unchanged) [d] | PvE [d] | —[n] | 7: Alistar, Ezreal, Hecarim, Krug, LeBlanc, Mama Beak, Xayah [d] | —[u] | —[u] | —[u] | —[n/a] |
| 4-1 | 1355.3 | 18 | 8 | 0/68 | 1 | 9 | 97/30/56/96/52/66/51/43 | win [d] | PvP [d] | P3 | —[u] | 9 | —[u] | —[u] | —[n/a] |
| 4-2 | 1433.8 | 13 | 8 | 2/68 | 22 | 10 | 97/30/43/96/44/53/51/31 | loss [d] | PvP [d] | P4 [d] | 8: Alistar, Draven, Ezreal, Gnar, Hecarim, Krug, Maokai, Sett [d] | 7 | —[u] | —[u] | Cybernetic Implants [d] |
| 4-3 | 1529.7 | 17 | 8 | 4/68 | 40 | 1 | 88/30/35/96/44/53/39/22 | win [d] | PvP [d] | P6 | 8: Alistar, Draven, Ezreal, Gnar, Hecarim, Krug, Maokai, Sett [d] | 2 | —[u] | —[u] | —[n/a] |
| 4-4 | 1604.0 | —[u] | —[u] | —[u] | —[u] | —[u] | 88/30/25/96/33/41/39/7 | —[n/a] | shared arena (PvE-style or shared board), same pattern as 3-4 [d] | —[n] | 8: Alistar, Draven, Ezreal, Gnar, Hecarim, Krug, Maokai, Sett [d] | —[u] | —[u] | —[u] | —[n/a] |
| 4-5 | 1640.8 | 16 | 8 | 6/68 | 62 | 1 | 88/30/25/96/33/41/39/7 | win [d] | PvP [d] | P5 [d] | 8: Alistar, Draven, Ezreal, Gnar, Hecarim, Krug, Maokai, Sett [d] | 4 | —[u] | —[u] | —[n/a] |
| 4-6 | 1716.5 | 21 | 8 | 8/68 | 71 | 2 | 88/30/13/84/21/29/39/7 | win [d] | PvP [d] | P8 | 8: Alistar, Draven, Ezreal, Gnar, Hecarim, Krug, Maokai, Sett [d] | 4 | —[u] | —[u] | —[n/a] |
| 4-7 | 1792.5 | 22 | 8 | 10/68 | 91 | 3 | 88/30/13/72/12/17/39/0 | no PvP (streak unchanged) [d] | PvE [d] | —[n] | 8: Alistar, Draven, Ezreal, Gnar, Hecarim, Krug, Maokai, Sett [d] | 4 | —[u] | —[u] | —[n/a] |
| 5-1 | 1829.7 | 20 | 9 | 0/68 | 57 | 3 | 88/30/13/72/12/17/39/0 | loss [d] | PvP [d] | P2 | 8: Alistar, Draven, Ezreal, Gnar, Hecarim, Krug, Maokai, Sett [d] | 2 | {'Sett': 2} | {'Sett': 3} | —[n/a] |
| 5-2 | 1907.9 | 21 | 9 | 2/68 | 11 | 1 | 74/30/13/72/0/4/39/0 | win [d] | PvP [d] | P3 | 8: Alistar, Draven, Ezreal, Gnar, Ivern, Kennen, Krug, Maokai [d] | 6 | —[u] | —[u] | —[n/a] |
| 5-3 | 1993.3 | 20 | 9 | 4/68 | 5 | 1 | 74/30/0/72/0/0/28/0 | win [d] | PvP [d] | P7 | 9: Alistar, Amumu, Draven, Ezreal, Gnar, Ivern, Kennen, Maokai, Taric [d] | 4 | —[u] | —[u] | —[n/a] |
| 5-4 | 2062.8 | —[u] | —[u] | —[u] | —[u] | —[u] | 74/30/0/57/0/0/14/0 | —[n/a] | shared arena (PvE-style or shared board), same pattern as 3-4 [d] | —[n] | 9: Alistar, Amumu, Draven, Ezreal, Gnar, Ivern, Kennen, Maokai, Taric [d] | —[u] | —[u] | —[u] | —[n/a] |
| 5-5 | 2087.5 | 21 | 9 | 6/68 | 7 | 2 | 74/30/0/57/0/0/14/0 | win [d] | PvP [d] | P4 [d] | 9: Alistar, Amumu, Draven, Ezreal, Gnar, Ivern, Kennen, Maokai, Taric [d] | —[u] | —[u] | —[u] | —[n/a] |
| 5-6 | 2165.3 | 20 | 9 | 8/68 | 6 | 3 | 74/30/0/40/0/0/0/0 | loss [d] | PvP [d] | —[u] | 9: Alistar, Amumu, Draven, Ezreal, Gnar, Ivern, Kennen, Maokai, Taric [d] | 5 | —[u] | {'Kennen': 3} | —[n/a] |
| 5-7 | 2230.8 | 7 | 9 | 10/68 | 6 | 1 | 59/30/0/23/0/0/0/0 | no PvP (streak unchanged) [d] | PvE [d] | —[n] | 9: Alistar, Amumu, Draven, Ezreal, Gnar, Ivern, Kennen, Maokai, Taric [d] | 3 | {'Kennen': 2} | —[u] | —[n/a] |
| 6-1 | 2269.1 | 5 | 9 | 12/68 | 16 | 1 | 59/30/0/23/0/0/0/0 | win [d] | PvP [d] | P4 | —[u] | —[u] | —[u] | —[u] | —[n/a] |
| 6-2 | 2335.2 | 20 | 9 | 14/68 | 8 | 1 | 59/16/0/10/0/0/0/0 | loss [d] | PvP [d] | —[u] | 9: Alistar, Amumu, Draven, Ezreal, Gnar, Ivern, Kennen, Maokai, Taric [d] | 2 | —[u] | —[u] | —[n/a] |
| 6-3 | 2398.9 | 22 | 9 | 16/68 | 3 | 1 | 43/16/0/0/0/0/0/0 | loss [d] | PvP [d] | P2 [d] | 9: Alistar, Amumu, Draven, Ezreal, Gnar, Ivern, Kennen, Maokai, Taric [d] | 3 | —[u] | —[u] | —[n/a] |
| 6-4 | 2463.3 | —[u] | —[u] | —[u] | —[u] | —[u] | 27/16/0/0/0/0/0/0 | —[n/a] | shared arena, same pattern as 3-4 [d] | —[n] | 9: Alistar, Amumu, Draven, Ezreal, Gnar, Ivern, Kennen, Maokai, Taric [d] | —[u] | —[u] | —[u] | —[n/a] |
| 6-5 | 2481.8 | 21 | 9 | 18/68 | 6 | 2 | 27/16/0/0/0/0/0/0 | loss [d] | PvP [d] | P2 [d] | 9: Alistar, Amumu, Draven, Ezreal, Gnar, Ivern, Kennen, Maokai, Taric [d] | 3 | —[u] | —[u] | —[n/a] |
| 6-6 | 2547.4 | 21 | 9 | 20/68 | 7 | 3 | 9/16/0/0/0/0/0/0 | loss | no_damage_pattern [d] | P2 | 9: Alistar, Amumu, Draven, Ezreal, Gnar, Ivern, Kennen, Maokai, Taric [d] | 1 | —[u] | —[u] | —[n/a] |

## 2. Thứ hạng cuối trận

- 1: P2
- 2: P1 (streamer)
- 3: P4 (6-2)
- 4: P7 (5-5)
- 5: P3 (5-2, derived: 2410 s rail order of dead rows P4,P7,P3,P6,P5,P8 matches placements 3 to 8)
- 6: P6 (5-2, derived: same 2410 s rail order; P6 sits below P3)
- 7: P5 (5-1)
- 8: P8 (4-6)

## 3. Trạng thái theo trường (số vòng)

| Trường | Đọc | Suy ra | Chưa giải | n/a |
|---|---|---|---|---|
| HP 8 người | 38 | 0 | 0 | 0 |
| Stage/round | 38 | 0 | 0 | 0 |
| Timer | 28 | 0 | 10 | 0 |
| Streak | 24 | 0 | 14 | 0 |
| Bàn | 0 | 33 | 5 | 0 |
| Bàn chờ | 25 | 0 | 13 | 0 |
| Sao | 2 | 0 | 36 | 0 |
| Trang bị | 2 | 0 | 36 | 0 |
| Augment | 0 | 3 | 0 | 35 |
| Kết quả | 1 | 33 | 0 | 4 |
| Đối thủ | 16 | 7 | 2 | 13 |

## 4. Tỉ lệ đúng đã đo

- Đọc lại mù trong mẫu (10 vòng): vàng 10/10, chuỗi thắng 9/10, cấp 10/10, XP 10/10 (crop đã tinh chỉnh sau khi xem mẫu).
- Ngoài mẫu (19 vòng có khung kế hoạch, `data/hud-audit/blind_oos28_rates.json`): vàng 13/16, chuỗi thắng 4/14, cấp 11/15, XP 13/14.
- HP, bàn, bàn chờ, kết quả, thứ hạng, HP đối thủ: chưa đo tỉ lệ đúng.

## 5. Khoảng trống

- Sao và trang bị: phần lớn chưa giải; nguồn 720p không đủ để đọc. Có một đối chứng 1080p, chưa đọc thử.
- Augment: chỉ có trong vòng có màn chọn augment.
- Chỉ có một trận; workstream sim cần nhiều trận và log set thứ hai.
