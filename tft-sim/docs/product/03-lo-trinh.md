# 3. Lộ trình

Nguồn: `docs/roadmap.md` trên `origin/claude/nifty-lovelace-252i30`, cập nhật 2026-11-23, ghi chú 2026-11-24. Bản sao đầy đủ nằm trên nhánh đó; bộ tài liệu này tóm tắt.

## Đường găng

**Không phase nào đo được trên dữ liệu thật cho đến khi có một nguồn live tạo đủ trạng thái engine cần: vàng, cấp, HP, giai đoạn, shop.** Ưu tiên cao nhất là chốt nguồn đó.

Ba hướng live đã xét, chưa hướng nào được xác nhận đủ:
1. Live Client `127.0.0.1:2999`: `ECONNREFUSED` với client TFT Standalone. Không dùng được với bản hiện tại.
2. Snapshot và log client: có HP, bàn cờ, trang bị. Không có shop, vàng; chưa kiểm chứng đủ.
3. HUD OCR (nhánh `hud`): đọc vàng, cấp, tên, giá shop. Là hướng duy nhất có kết quả đo, nhưng độ chính xác chưa đạt mục tiêu.

## Các phase

Mỗi phase kết thúc bằng một cổng đo được. Không chuyển phase khi cổng chưa đạt.

| Phase | Mục tiêu | Trạng thái (theo roadmap 2026-11-24; chưa kiểm lại nhánh hud) |
|---|---|---|
| 1. Củng cố | Nền chung; xác định set; chọn đường live và chính sách | **Một phần.** Quy tắc agent đã lên master (PR #1, 2026-11-24). Set 18 xác định theo CDragon 18.7 và Blitz (chưa kiểm chứng nguồn chính thức). Trạng thái đường RAM chưa rõ (xem dưới). Chưa chọn đường live chính. |
| 2. Tích hợp nhánh | Master có đủ nội dung, test xanh | **Xong** (2026-11-24): PR #1–#4 merge; 182 test Node, 8 pytest. |
| 3. Đường live | Đọc đúng trạng thái trận trên dữ liệu thật | **Chưa xong, bị chặn.** Việc còn: ghi tay 5 ô từ 16 ảnh HUD, đo độ chính xác trên trận giữ lại, kiểm Windows. Mục tiêu "100% trong 250 ms" cần người dùng xác nhận vì 100% rất chặt. |
| 4. Engine đúng trên dữ liệu thật | Engine ra quyết định hợp lý trên trạng thái thật | **Chưa bắt đầu.** Cần Phase 3. Có việc xác minh bảng odds, pool, XP (`needs.md` U1, U2). |
| 5. Nghiên cứu chính sách (`tft-sim`) | Tìm quy tắc tốt hơn; không đưa vào engine khi chưa kiểm chứng | **Đang làm ở mức mô phỏng.** Đây là phạm vi của nhánh sim. |
| 6. Sản phẩm | Đóng gói Windows, đo độ trễ, trải nghiệm MCP | Chưa bắt đầu. Do người dùng quyết khi đến lúc. |

**Cổng Phase 5 → engine:** quy tắc chỉ vào engine sau khi thắng trên harness Phase 4 (dữ liệu thật). Mô phỏng với bot scripted không đủ.

## Quyết định ngày 2026-11-24 (bảng cập nhật 2026-11-26 theo ủy quyền của người dùng; xem progress/sessions/2026-11-26-truy-vet-quyet-dinh-roadmap.md)

| # | Quyết định |
|---|---|
| 1, 2, 2b | Đã bỏ khỏi bảng: 1 (đề xuất đóng đường RAM; đường RAM không đóng, xem dưới), 2 sản phẩm sau trận là mặc định, 2b công cụ mô tả trong trận. |
| 3 | Chủ roster Set 18: `engine`. |
| 4 | Thứ tự tích hợp: PR #1, rồi `dazzling`, rồi `codex/hud-realtime-progress`, rồi `fable`. |
| 5 | **Dừng mở rộng chiến dịch VOD.** `hud` làm tiếp: 16 khung nhãn mù, tỷ lệ phủ và tỷ lệ sai tự tin cho từng trường, một phiên Windows. |
| 6 | Ảnh chụp EoG giữa trận do người dùng gửi (3–5 file, đã ẩn tên và PUUID). Chờ người dùng gửi. |

Bổ sung cùng ngày (người dùng đã cho phép dùng dữ liệu cho huấn luyện): dùng VOD streamer cho huấn luyện, rủi ro pháp lý chưa kiểm và người dùng đã nhận thức; giai đoạn hiện tại là thu thập và làm sạch dữ liệu; quyết định mô hình học gì trước do một phiên chuyên trách.

Lô VOD `2026-11-25-set18-vod` (`vod-collection.md`) là thu `fight-v1` do người dùng yêu cầu trong phiên, không phải chiến dịch OCR của quyết định 5.

## Đường RAM: không đóng, người dùng sẽ phát triển sau

- **Quyết định:** đường RAM (đọc bộ nhớ của tiến trình game) **không bị đóng**. Người dùng sẽ tự phát triển đường này sau. Đây là quyết định của người dùng (2026-11-26), thay cho cách hiểu trước đó trong phiên.
- **Rủi ro cần tính khi phát triển:** trang hỗ trợ Riot "game memory access removed for third party apps" ghi chính sách chặn đọc bộ nhớ của app bên thứ ba chưa được phê duyệt từ 6/10/2026, gồm TFT. Không có thông báo riêng cho TFT. Chính sách này chưa được đối chiếu với kế hoạch của người dùng.
- **Mâu thuẫn kỹ thuật chưa giải:** `data-sources.md` ghi Vanguard chặn `PROCESS_VM_READ`; `network-and-ram-layer.md` ghi `OpenProcess` thành công ngày 2026-11-22. Kết quả 22/11 không chứng minh trạng thái hiện tại.
- **Trạng thái trên nhánh roadmap:** dòng Lịch sử 2026-11-24 ghi "đóng nhánh RAM", và quyết định 1 ghi "đã bỏ". Hai chỗ này cần người dùng đối chiếu lại với ý định trên.

## Kế hoạch Set 18 (model-plan mục 11, 2026-11-25)

Lý do có hạn: Set 19 đang PBE. Khi Set 19 lên sóng, trận Set 18 mới sẽ dừng, nên bản ghi thật phải thu sớm.

- **Phase 0 (chặn):** sửa đường ghi bản ghi thật dùng nội dung đã alias. **Đã làm:** selftest item `TFT_Item_*` không phải twin cho `items_unknown == 0`.
- **Phase 1 (rẻ):** xếp hạng đòn bẩy trên Set 17 (sim) theo tỷ lệ đảo so với `hand`. Chỉ là sim.
- **Phase 2 (cổng):** bản ghi trận Set 18 thật. Cần khóa API Riot, **do người dùng cấp**; chưa có yêu cầu nào được gửi.
- **Phase 3 (phủ):** wrapper theo set, không sửa `tft_goat`. Đã sửa 2 khóa trait sai (Vanguard `MaxHealthShield`, Spellweaver `APPerCast`). Còn: ánh xạ 25 trait, ability (số Blitz, 58/74 căn chỉnh được), augment khi có tần suất.
- **Phase 4 (đánh giá):** mỗi thay đổi đo bằng chênh lệch cặp trên bộ Set 18 thật. Nếu Set 19 lên mà chưa có bản ghi thật: ghi nhãn "chưa kiểm chứng" và dừng.

Nếu người dùng từ chối khóa Riot, Phase 0, 1 và 3 vẫn chạy.
