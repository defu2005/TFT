# Hợp đồng dữ liệu giữa các workstream

Tài liệu này cho biết dữ liệu nào một workstream cần từ workstream khác, ai sinh ra nó, và các agent trao đổi yêu cầu thế nào. Tình trạng được ghi theo ngày quan sát: **2026-11-24**, từ các nguồn nêu bên dưới.

## 1. ID workstream

Dùng ID này để gọi nhau. Tên nhánh do phiên cấp và có thể đổi, nên không dùng tên nhánh để địa chỉ hóa.

| ID | Việc | Nhánh hiện tại |
|---|---|---|
| `engine` | Engine, coach, MCP, ingest trạng thái | `claude/dazzling-feynman-g7a0b9` (chưa merge) |
| `hud` | OCR HUD Set 18, chiến dịch VOD | `codex/hud-realtime-handoff` (chưa merge) |
| `sim` | Mô phỏng và học chính sách `tft-sim/` | `claude/claude-fable-5-2-awwmf5` (chưa merge) |
| `user` | Người điều phối và máy ingest của người dùng | `master`, và máy người dùng (không có nhánh riêng) |

## 2. Cách trao đổi

Mỗi agent chỉ **ghi lên nhánh của chính mình**. Đọc nhánh của người khác bằng `git show` hoặc `git ls-tree`. Không ai sửa file của workstream khác, nên không có xung đột.

### Yêu cầu (request)

- Đường dẫn: `docs/agents/requests/<YYYYMMDD>-<from>-to-<to>-<slug>.md`, nằm trên **nhánh của bên yêu cầu**.
- Mẫu, đúng thứ tự, và dòng `status:` phải nằm ở đầu một dòng để máy đọc được:

```markdown
# Yêu cầu: <tiêu đề ngắn>

dataset: <tên dữ liệu>
fields: <trường, kiểu, đơn vị>
schema: <phiên bản mong muốn>
why: <vì sao cần>
unblocks: <việc nào bị chặn>
deadline: <nếu có, nếu không để trống>
status: mở
```

- Bên yêu cầu đổi `status: mở` thành `status: đóng` khi đã kiểm chứng. Đổi trên **nhánh của mình**.

### Trả lời (response)

- Đường dẫn: `docs/agents/responses/<cùng-id>.md`, nằm trên **nhánh của bên sinh dữ liệu**.
- Dòng `status:` phải là một trong ba giá trị:
  - `status: nhận`: đã nhận, đang làm.
  - `status: từ chối`: kèm lý do ở dòng sau.
  - `status: đã giao`: kèm `commit:`, `path:`, `schema:`.

### Người dùng là bên sinh dữ liệu

`user` không có nhánh và không chạy quét git. Vì vậy:

- Yêu cầu gửi cho `user` **phải được nêu trong tin nhắn cuối cùng** của agent trong chat, và **ghi trong handoff** của nhánh (mục "Yêu cầu dữ liệu").
- Người dùng trả lời bằng một trong hai cách: trả lời trong chat, hoặc commit `docs/agents/responses/<id>.md` lên `master`.
- Agent khi quét thấy câu trả lời trên `master` thì ghi lại trong file yêu cầu của mình: đường dẫn, commit, và đổi `status` theo đó.

### Đóng yêu cầu

- Bên yêu cầu kiểm chứng dữ liệu theo đúng commit đã giao (bằng test hoặc đọc thử).
- Sau đó đổi `status: đóng` trong file yêu cầu của mình.

### Ghim commit

- Luôn dùng **commit hash** khi tham chiếu dữ liệu, không dùng tên nhánh. Nhánh có thể bị rebase trước khi merge.

### Quét đầu phiên

Mỗi agent chạy khi bắt đầu phiên, và trước khi sửa vùng dùng dữ liệu của người khác. Đặt `ME` là ID của mình:

```bash
git fetch origin --prune
ME=engine   # ID của mình: engine, hud, hoặc sim
for b in $(git branch -r | grep -v HEAD); do
  # Yêu cầu gửi cho tôi
  git ls-tree --name-only "$b" docs/agents/requests/ 2>/dev/null | grep -- "-to-$ME-" | sed "s|^|$b: |"
  # Trả lời cho yêu cầu tôi đã gửi (quét mọi nhánh, vì bên sinh dữ liệu ở nhánh khác)
  git ls-tree --name-only "$b" docs/agents/responses/ 2>/dev/null | grep -- "-$ME-to-" | sed "s|^|$b: |"
done
```

Lưu ý:

- Dấu `/` cuối tên thư mục là bắt buộc. Không có nó, `git ls-tree` chỉ in tên thư mục.
- Nếu thư mục không tồn tại trên nhánh đó, lệnh in rỗng và không báo lỗi.
- Quét chỉ thấy các nhánh **đã push**. Nhánh chỉ có trên máy cá nhân thì không ai thấy.
- Yêu cầu gửi cho `user` không nằm trong vòng quét này. Xem mục trên.

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
| `set` và `patch` từ nguồn | `hud` (fallback `user` nếu cần máy live để xác nhận) | `engine` | **Mở**. Chưa rõ số patch nào dùng | `engine`: `needs.md` I8 |
| Offer Wisp (loại, tướng ẩn, giá, shop nào có) | `hud` (fallback `user`: cần capture) | `engine` | **Mở**. Phụ thuộc capture | `engine`: `needs.md` I9 |
| Id Lux nhiều mục (`DA_Lux18_*`, `DA_18_Lux_*`) | `hud` (fallback `user`: cần xác nhận trên client) | `engine` | **Mở**. Ảnh hưởng cách đếm bản | `engine`: `needs.md` I6 |
| Bản chụp shop thật (`captures/`) | `user` (máy ingest) | `engine`, `hud` | **Chưa có trong repo**. Script `watch-and-capture.py` ghi đường dẫn Windows | `engine`: `needs.md` mục 2, U10 |
| Bảng XP theo cấp | `user` hoặc nguồn ngoài | `engine` | **Mở**. Đề xuất từ wiki, chưa xác minh | `engine`: `needs.md` U1 |
| Bảng odds theo cấp | `user` hoặc nguồn ngoài | `engine`, `sim` | **Mở**. Lệch Set 17 ở cấp 8, 9 | `engine`: `needs.md` U2 |
| Roster và trait Set 18 | **Ba bên sinh, chưa chọn** | `engine`, `sim` | **Cần quyết định của người dùng** (xem mục 5) | xem mục 5 |
| Snapshot CDragon đúng patch cho mô phỏng | `sim` | `sim` | **Chặn Gate 0** trên nội dung thật | `sim`: `tft-sim/README.md` |

Dòng I6 và I8 được gán cho `hud` theo mục "Từ phiên ingest" của `needs.md`, trong đó nhánh `codex/hud-realtime-handoff` được nêu là nhánh ingest. `user` chỉ là bên dự phòng khi cần máy người dùng.

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
