# Khai báo công việc (claim)

Claim cho biết ai đang làm trên vùng nào. Các agent không chia sẻ bộ nhớ và chạy trên nhánh hoặc cloud session riêng, nên bảng claim phải nằm ở một nơi mọi agent đọc được trước khi bắt đầu việc.

## Nơi đặt bảng

- Bảng sống trong `docs/agents/claims.md` trên **`master`**.
- **Chỉ người dùng (người điều phối) ghi bảng.** Người dùng thêm dòng khi giao workstream hoặc vùng nóng lúc khởi động phiên.
- Agent **không sửa bảng**, kể cả khi thấy dòng sai. Báo trong handoff và chờ người điều phối.

## Agent đọc bảng thế nào

Trước khi bắt đầu bất kỳ việc nào, và trước khi sửa vùng nóng:

```bash
git fetch origin master
git show origin/master:docs/agents/claims.md
```

## Khi cần vùng không được giao

- Nếu việc cần sửa một vùng nóng không nằm trong claim của nhánh mình, **dừng và hỏi** người điều phối.
- Không tự thêm claim, không sửa dòng của người khác.

## Khi xong việc

- Ghi "xong" trong handoff của nhánh (xem `handoff.md`).
- Người điều phối đóng dòng trong bảng bằng trạng thái `xong` kèm nhánh và commit.

## Quy tắc

- Claim vùng nóng là độc quyền: không ai khác sửa vùng đó cho đến khi có dòng `xong`.
- Claim vùng thường chỉ để thông báo, nhưng vẫn ghi để tránh trùng việc.
- Claim không có commit mới quá 7 ngày: người điều phối có thể đóng và ghi lý do.
- Claim không thay thế việc đọc code. Luôn `git fetch` và đọc commit mới trên `master` và nhánh liên quan trước khi sửa.
- Hai việc trùng vùng: claim ghi trước thắng. Việc còn lại dừng và hỏi.

## Bảng

| Ngày | Vùng / file | Nhánh | Agent | Trạng thái |
|---|---|---|---|---|
| 2026-11-23 | (ví dụ) `src/engine/decide.js` | `codex/hud-realtime-handoff` | codex | đang làm |

Dòng trên chỉ là ví dụ, không có hiệu lực. Người điều phối xóa khi có dòng thật.
