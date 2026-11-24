# Kiểm thử và ghi kết quả

## Lệnh theo vùng

Chạy đúng lệnh của vùng mình sửa. Khi sửa nhiều vùng, chạy tất cả.

| Vùng | Lệnh | Ghi chú |
|---|---|---|
| Engine, MCP, ingest (Node) | `npm test` | Trên `master` hiện là 182 test |
| HUD OCR (Python) | `python3 scripts/test_hud_ocr.py -v` | **Có trên `master` (từ PR #3).** Cần `TFT_SET18_ART_ZIP` để chạy đủ bộ. Thiếu biến này một số test có thể bị bỏ qua. |
| Mô phỏng `tft-sim` | `cd tft-sim && PYTHONPATH=src python3 -m pytest -q` | **Có trên `master` (từ PR #4).** Thiếu `PYTHONPATH=src` sẽ lỗi thu thập (`No module named 'tft_sim'`). |
| Replay engine | `npm run bench` | Khi thay đổi logic quyết định |

Trước khi báo "xong", chạy đúng các lệnh trên trong worktree sạch của nhánh. Đừng dựa vào test đã chạy từ một nhánh khác.

## Sau khi merge

- Chạy `npm test` trên commit merge, không chỉ trên từng nhánh riêng.
- Nếu có nhiều nhánh cùng sửa `src/`, chạy lại test sau từng lần merge, không chỉ lần cuối.

## Ghi kết quả

Mỗi kết quả đo phải ghi đủ:

- Phiên bản mã (hash commit).
- Dữ liệu đầu vào: nguồn, khoảng thời gian, số mẫu, phiên bản tổng hợp hay thật.
- Lệnh đã chạy.
- Số mẫu, số mẫu bị bỏ, và các chỉ số chính.
- Đã đối chiếu với nhãn chưa, và nhãn lấy từ đâu.

Không dùng từ "độ chính xác" nếu chưa đối chiếu với nhãn tay. Báo riêng:

- ô bị che,
- ô không đọc được,
- mẫu bị bỏ,
- giá đọc sai.

## Kiểm định và giả thuyết

- Quy tắc chọn trên một tập seed, kiểm định trên tập khác. Không dùng tập kiểm định để chọn.
- Luôn chạy null check (so sánh với chính nó hoặc với ngẫu nhiên) khi báo cáo chênh lệch giữa hai chính sách.
- Ghi khoảng tin cậy cùng với số. Nếu khoảng chứa 0, không nói "tốt hơn".

## Thứ không được làm

- Không xóa, bỏ qua (`skip`), hoặc đánh dấu `todo` một test để có màu xanh, trừ khi có lý do ghi trong commit và người điều phối đồng ý.
- Không sửa test cho khớp với code sai. Nếu test đúng và code sai, sửa code. Nếu cả hai đều có thể đúng, hỏi.
- Không báo "đã kiểm thử" cho thứ chưa chạy.
