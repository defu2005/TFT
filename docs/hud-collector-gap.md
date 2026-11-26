# Khoảng trống bộ thu thập HUD so với file sim

Mục tiêu "100%" được định nghĩa để kiểm tra được: trên một trận có nhãn giữ riêng, số giá trị sai bằng 0 trong các giá trị bộ thu thập phát ra. Giá trị không xác nhận được thì ghi là chưa giải và đưa vào hàng chờ cho agent. Độ phủ báo riêng. Không có số liệu nào được gọi là độ chính xác nếu chưa có nhãn.

Nguồn: `docs/hud-reader.md` (trường bộ đọc phát ra), `data/hud-audit/match01_full.json` (cách đã chứng minh bằng tay trên trận 01), `data/hud-audit/blind_oos28_rates.json` và các số đo đọc lại mù trong `docs/sim/match01-rounds.md`.

| Trường trong file sim | Bộ đọc trong repo phát ra (khóa thật trong `results/*.jsonl.gz`) | Bộ đọc ngoài repo `ocrtest/extract/fields4.py` | Phương pháp đã chứng minh trên trận 01 (tay, không phải bộ đọc) | Độ đúng đo được (bộ đọc nào) | Việc cần làm |
|---|---|---|---|---|---|
| HP 8 người theo thời gian | Không có khóa HP | Không có | HP từ rail, 38/38 vòng | Chưa đo | Thêm bộ đọc HP có nhãn |
| Stage/round | Không có khóa stage | Có stage | Bảng stage đơn điệu | Chưa đo trên bộ đọc | Đo trên nhãn mù |
| Timer | Không có | Có timer | Hộp timer, 28/38 vòng | Chưa đo trên bộ đọc | Đo trên nhãn mù |
| Vàng | `gold` | Có gold | Đọc lại mù, planning | Trên `blind_ocr_planning.py`: trong mẫu 10/10; ngoài mẫu 13/16 (3 khung không có ô vàng). Chưa đo trên `hud_ocr.py` | Đo trên bộ đọc trong repo |
| Cấp | `level` (kèm `levelRetry`) | Có level | Đọc lại mù, planning | Trên `blind_ocr_planning.py`: trong mẫu 10/10; ngoài mẫu 11/15 (lỗi 13 thay cho 5 ở 2-6). Chưa đo trên `hud_ocr.py` | Đo trên bộ đọc trong repo |
| XP | Không có khóa XP | Có XP | Đọc lại mù, planning | Trên `blind_ocr_planning.py`: trong mẫu 10/10; ngoài mẫu 13/14. Không áp dụng cho bộ đọc trong repo | Thêm vào bộ đọc trong repo |
| Streak | Không có | Có streak | Badge, 24/38 vòng | Ngoài mẫu (`blind_ocr_planning.py`) 4/14; chưa đo trên bộ đọc khác | Cần bộ đọc riêng và đo lại |
| Bàn (tướng và số) | Không có khóa bàn (`board` chỉ là từ trong `hud-reader.py`) | Không có | Panel và phép giải, 33 vòng suy ra | Chưa đo | Cần bộ đọc và nhãn |
| Bàn chờ | Không có | Không có | Đếm sprite bằng mắt, 25 vòng | Chưa đo | Cần bộ đọc và nhãn |
| Sao của tướng | Không có | Không có | Không đọc được ở 720p, 2/38 vòng | Không có | Thử đọc ở 1080p sau khi kiểm tra vị trí badge |
| Trang bị | Không có khóa trang bị (`item` chỉ là từ trong `hud_ocr.py`) | Không có | Không đọc được ở 720p, 2/38 vòng | Không có | Cần bộ đọc và nhãn |
| Augment kèm tier | Không có | Không có | Chỉ ở vòng có màn chọn, 3/38 vòng | Không có | Cần bộ đọc và nhãn |
| Kết quả combat từng round | Không có | Không có | Suy ra từ màu biểu tượng, 33/38 vòng | Chưa đo | Đo trên nhãn mù |
| Thứ hạng cuối trận | Không có | Không có | Suy ra từ thứ tự rail | Chưa đo | Đo trên nhiều trận |
| HP đối thủ | Không có | Không có | Cùng trường HP 8 người | Chưa đo | Như dòng HP |
| Đối thủ (mã P) | Không có | Không có | Tên qua tooltip và nameplate, đối chiếu bảng alias riêng | Không đo | Cần bộ đọc và nhãn |
| Cửa hàng (không có trong file sim, nhưng bộ đọc phát ra) | `shop`, `shopSlots` | Không có | Không áp dụng | Chưa đo | Đo nếu cần |
| Log set thứ hai | Không có | Không có | Không có | Không có | Ngoài phạm vi trận này |

**Lưu ý nguồn:** `scripts/hud-campaign/` và `docs/agents/sources/collector-claude-seed.md` ghi rằng bộ 45 nguồn seed, gồm VOD `2924500482-210000` của trận 01, thuộc một collector khác (`claude/hud-data-set18`, trạng thái `đang tải`). Trận 01 trên nhánh này dùng file đã có sẵn trên đĩa, không claim, nên cần người điều phối xác nhận quyền trước khi thu thêm từ VOD này.

hiệm đọc |
| Augment kèm tier | Không thấy | Chỉ có ở vòng có màn chọn; 3/38 vòng | Không có | Cần bộ đọc và nhãn |
| Kết quả combat từng round | Không thấy | Suy ra từ màu biểu tượng, 33/38 vòng | Chưa đo | Đo trên nhãn mù |
| Thứ hạng cuối trận | Không thấy | Suy ra từ thứ tự rail, 8 vị trí | Chưa đo | Đo trên nhiều trận |
| HP của đối thủ | Không thấy | Cùng trường HP 8 người | Chưa đo | Như dòng HP |
| Đối thủ (mã P) | Không thấy | Đọc tên qua tooltip và nameplate, so với bảng alias riêng | Không đo | Cần bộ đọc và nhãn |
| Log set thứ hai | Không có | Không có | Không có | Ngoài phạm vi trận này |

## Kết luận

- Bộ đọc trong repo phát ra vàng, cấp, cửa hàng và `hudDetected`. Không có HP, timer, streak, XP, bàn, sao, trang bị, combat hay thứ hạng.
- Tỉ lệ đo được là của `blind_ocr_planning.py` (ngoài repo bộ đọc), không phải của `hud_ocr.py`.
- Các trường lớn nhất còn thiếu: HP, streak, timer, bàn chờ, sao, trang bị, augment, kết quả combat, đối thủ.
- Đường đi để có 100% độ đúng là đo trên nhãn mù từng trường, không phải tuyên bố.
