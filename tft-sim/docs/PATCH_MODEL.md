# Mo hinh theo patch va theo set (thiet ke)

Muc tieu: mo hinh khong gan cung vao mot patch, nhung van giu duoc dac trung cua tung set va patch.

## 1. Loi choi co ban (core)
- Khong chua so, khong chua ten tuong. Chi chua: vong lap, cac loai hanh dong chung, cach tinh lai suat theo cong thuc.
- Luat chung duoc nap tu goi `rules` theo patch.

## 2. Goi patch (patch pack)
- Moi patch: manifest (URL nguon, sha256, ngay), bang odds, bang XP, bang pool.
- Danh sach tuong tuong minh (roster), KHONG dung quy tac tien to ten (`TFT17_`) vi PvE va unit an co the cung tien to.
- Ban du lieu CDragon `latest` phai duoc gan dung nhan patch truoc khi dung.

## 3. Module co che cua set
- Moi set co mot khoi observation rieng va tap hanh dong rieng (vi du gods cua Set 17 trong TFT_GOAT; Wisps cua Set 18; nhac/unlocks cua Set 19).
- Module co che khong duoc phep thay doi core.

## 4. Dau vao mo hinh
- Khoi chung (universal): kinh te, per-slot {co tuong, so ban so huu, cost, so trait trung voi doi}, tien trinh trait.
- Khoi set: danh tinh tuong, trang thai co che (vi du wisp hoac unlock).
- Checkpoint luu: set, patch, phien ban feature, phien ban action.

## 5. Kiem tra chuyen giao (transfer test)

- Da chay phien ban BUY_SHOP tren noi dung tong hop (README, muc Transfer A -> B; 5 seed). Ket qua va caveat: `docs/model-plan.md` muc 10.2.
- Tieu chi goc ben duoi (vs scripted tren B): CHUA CHAY.
- Tao noi dung tong hop thu hai co cung kich thuoc nhung cost va trait bi xao tron.
- Train tren A, danh gia tren B khong train lai: flat, flat+slot, chi-universal.
- Tieu chi: chi-universal trong 0.5 cua scripted tren B. Ky vong flat giam; neu khong giam, phai tim vi sao.

## 6. Hai van de can cap nhat truoc khi tin ket qua BC
- EQUIP: 82% quyet dinh cua teacher la EQUIP, va phan lon la hanh dong khong co tac dung. Nguyen nhan da xac dinh: `_equip` khong tieu thu thanh phan khi cap khong co cong thuc, nhung mask van hop le. Do do ty le dong y 99.6% bi thoi phong. Can bao cao theo tung loai va loai tru EQUIP.
- Nguong 70% "da hoc" duoc dat sau khi da xem ket qua. Can ghi ro la nguong dieu chinh hau kiem.
