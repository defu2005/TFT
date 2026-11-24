# Hợp đồng dữ liệu giữa các workstream

Tài liệu này cho biết dữ liệu nào một workstream cần từ workstream khác, ai sinh ra nó, và các agent trao đổi yêu cầu thế nào. Tình trạng được ghi theo ngày quan sát: **2026-11-24**, từ các nguồn nêu bên dưới.

## 1. ID workstream

Dùng ID này để gọi nhau. Tên nhánh do phiên cấp và có thể đổi, nên không dùng tên nhánh để địa chỉ hóa.

| ID | Việc | Nhánh hiện tại |
|---|---|---|
| `engine` | Engine, coach, MCP, ingest trạng thái | `claude/dazzling-feynman-g7a0b9` (chưa merge) |
| `hud` | OCR HUD Set 18, chiến dịch VOD | `codex/hud-realtime-handoff` (chưa merge) |
| `sim` | Mô phỏng và học chính sách `tft-sim/` | `claude/claude-fable-5-2-awwmf5` (chưa merge) |
| `user` | Người điều phối và máy ingest của người dùng | `master`, và máy người dùng |

## 2. Cách trao đổi

Mỗi agent chỉ **ghi lên nhánh của chính mình**. Đọc nhánh của người khác bằng `git show`. Không ai sửa file của workstream khác, nên không có xung đột.

### Yêu cầu (request)

- Đường dẫn: `docs/agents/requests/<YYYYMMDD>-<from>-to-<to>-<slug>.md`, nằm trên **nhánh của bên yêu cầu**.
- Nội dung bắt buộc:
  - `dataset`: tên dữ liệu.
  - `fields`: các trường cần, kèm kiểu và đơn vị.
  - `schema`: phiên bản schema mong muốn.
  - `why`: vì sao cần.
  - `unblocks`: việc nào bị chặn nếu thiếu.
  - `deadline`: nếu có.
  - `status`: `mở` khi tạo. Bên yêu cầu đổi sang `đóng` khi đã kiểm chứng.

### Trả lời (response)

- Đường dẫn: `docs/agents/responses/<cùng-id>.md`, nằm trên **nhánh của bên sinh dữ liệu**.
- Trạng thái:
  - `nhận`: đã nhận, đang làm.
  - `từ chối`: kèm lý do.
  - `đã giao`: kèm commit hash, đường dẫn file, phiên bản schema.

### Đóng yêu cầu

- Bên yêu cầu kiểm chứng dữ liệu theo đúng commit đã giao (bằng test hoặc đọc thử).
- Sau đó đổi `status` thành `đóng` trong file yêu cầu của mình.

### Ghim commit

- Luôn dùng **commit hash** khi tham chiếu dữ liệu, không dùng tên nhánh. Nhánh có thể bị rebase trước khi merge.

### Quét đầu phiên

Mỗi agent chạy khi bắt đầu phiên, và trước khi sửa vùng dùng dữ liệu của người khác:

```bash
git fetch origin --prune
# Yêu cầu gửi cho tôi (thay <me> bằng ID của mình, ví dụ engine)
for b in $(git branch -r | grep -v HEAD); do
  git ls-tree --name-only "$b" docs/agents/requests/ 2>/dev/null | grep -- "-to-<me>-" | sed "s|^|$b: |"
done
# Trả lời cho yêu cầu tôi đã gửi
git ls-tree --name-only origin/<nhánh-của-tôi> docs/agents/responses/ 2>/dev/null
```

Lưu ý: quét chỉ thấy các nhánh **đã push**. Nhánh chỉ có trên máy cá nhân thì không ai thấy.

## 3. Nguyên tắc dữ liệu

- **Một bên sinh cho mỗi tập dữ liệu.** Nếu hai bên cùng sinh, phải chọn một và ghi quyết định.
- **Thay đổi schema phải tăng phiên bản.** Theo mẫu `hudSchema === 2` mà `standaloneSource.js` đã dùng. Bên đọc kiểm tra phiên bản và báo khi lệch.
- **Dữ liệu lớn hoặc nhạy cảm không đi qua git:** capture, khung VOD, Riot ID. Hợp đồng chỉ ghi vị trí, checksum, và cách lấy lại (xem `hygiene.md`).
- Dữ liệu nhỏ, dùng làm fixture hoặc cấu hình, được commit, nhưng phải ghi nguồn và ngày lấy.

## 4. Sổ đăng ký (quan sát ngày 2026-11-24)

Mỗi dòng là một điểm trao đổi đã xác định từ các tài liệu. Các yêu cầu cụ thể **chưa được tạo**. Bên tiêu thụ tự tạo file yêu cầu khi cần.

| Dữ liệu | Bên sinh | Bên dùng | Trạng thái | Nguồn |
|---|---|---|---|---|
| Trường HUD: `shop[].price`, `hudGoldUnknown`, `hudLevelUnknown`, `shopUnknownSlots` | `hud` | `engine` | Đã có hợp đồng và đã được engine xử lý (I10) | `hud`: `docs/hud-reader.md`. `engine`: `needs.md` I10 |
| Hàng odds (5 tỷ lệ theo cấp) và ngưỡng XP `x/y` từ HUD | `hud` | `engine` | **Mở**, chưa có ai nhận. Engine cần để so với hồ sơ odds | `engine`: `needs.md` I11 |
| `set` và `patch` từ nguồn | `user` (xác nhận client gửi chuỗi nào) | `engine` | **Mở**. Chưa rõ số patch nào dùng | `engine`: `needs.md` I8 |
| Offer Wisp (loại, tướng ẩn, giá, shop nào có) | `hud` (cần xác nhận có đọc được) | `engine` | **Mở**. Phụ thuộc capture | `engine`: `needs.md` I9 |
| Id Lux nhiều mục (`DA_Lux18_*`, `DA_18_Lux_*`) | `user` (cần xác nhận) | `engine` | **Mở**. Ảnh hưởng cách đếm bản | `engine`: `needs.md` I6 |
| Bản chụp shop thật (`captures/`) | `user` (máy ingest) | `engine`, `hud` | **Chưa có trong repo**. Script `watch-and-capture.py` ghi đường dẫn Windows | `engine`: `needs.md` mục 2, U10 |
| Bảng XP theo cấp | `user` hoặc nguồn ngoài | `engine` | **Mở**. Đề xuất từ wiki, chưa xác minh | `engine`: `needs.md` U1 |
| Bảng odds theo cấp | `user` hoặc nguồn ngoài | `engine`, `sim` | **Mở**. Lệch Set 17 ở cấp 8, 9 | `engine`: `needs.md` U2 |
| Roster và trait Set 18 | **Ba bên sinh, chưa chọn** | `engine`, `sim` | **Cần quyết định của người dùng** (xem mục 5) | xem mục 5 |
| Snapshot CDragon đúng patch cho mô phỏng | `sim` | `sim` | **Chặn Gate 0** trên nội dung thật | `sim`: `tft-sim/README.md` |

## 5. Quyết định người dùng cần đưa ra

**Ai là chủ của dữ liệu roster và trait Set 18?** Hiện có ba nguồn, và chúng không khớp nhau:

- `engine`: `src/data/set18.json`, xuất từ CDragon phiên bản 16.23.8406595. Có overlay trait cho 18.7 nhưng không bật mặc định.
- `sim`: lấy CDragon 18.7 khi chạy `tft-sim`.
- `hud`: `src/data/set18-hud.json`, dùng để nhận diện tên trên màn hình.

Trước khi người dùng chọn, các nhánh **không được** tự sửa file roster của nhau. Mỗi bên chỉ ghi chú sự khác biệt trong `responses/` của mình.

## 6. Mẫu hợp đồng

Khi một workstream chốt một bộ dữ liệu để người khác dùng, tạo `docs/agents/contracts/<tên-dữ-liệu>.md` trên nhánh của mình:

```markdown
# Hợp đồng: <tên dữ liệu>

- Bên sinh: <ID>
- Đường dẫn: <file trong repo, hoặc vị trí ngoài git>
- Schema: <phiên bản>, <định dạng>
- Trường: <danh sách, kiểu, đơn vị, null có nghĩa gì>
- Nguồn và ngày lấy:
- Checksum (nếu là file lớn):
- Commit đã giao:
- Đã kiểm chứng bằng: <test hoặc phép đọc>
```
