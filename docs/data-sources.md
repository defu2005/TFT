# Nguồn dữ liệu và kiến trúc Ingestion (Cập nhật 2026-11-22)

## Kết quả kiểm tra & Triển khai thực nghiệm

| Nguồn | Kết quả & Đánh giá |
| --- | --- |
| Live Client `127.0.0.1:2999` | `ECONNREFUSED`. Client TFT Standalone Unreal Engine đã đóng hoàn toàn cổng HTTP này. |
| **Snapshot & Log Client** (`src/ingest/standaloneSource.js`) | **Chưa xác nhận đầy đủ**: đọc file `TFTEoGStats.json` và `TFT.log`. Thời điểm ghi `TFTEoGStats.json` (liên tục trong ván hay chỉ khi kết thúc ván) chưa xác định; nếu chỉ ghi khi kết thúc, hp, stage và board có thể là giá trị của ván trước. Cung cấp (khi file có dữ liệu): HP, boardPieces, cấp sao, trang bị của 8 người chơi, thời gian trận. |
| **High-Speed HUD Buffer** (`scripts/hud-reader.py`) | Chụp cửa sổ Windows bằng `PrintWindow`, chạy OCR theo vùng và ghi kết quả vào `captures/hud-live.json`. Chế độ ảnh và video chạy được trên Linux. Xem [kiểm thử và đo độ trễ](hud-reader.md). |
| **Tầng Network** (`scripts/probe-network.py`) | Socket UDP Unreal Engine Iris NetDriver (port `65501` -> Server port `7064`) được mã hóa theo session handshake key (AES). Payload bit-packed không khuyến khích giải mã do nguy cơ an ninh và độ giòn cao. |
| **Tầng RAM** (`src/ingest/ramSource.js`) | Vanguard kernel driver (`vgk.sys`) strip quyền `PROCESS_VM_READ` (lỗi error 5 `ACCESS_DENIED`). Do đó, giải pháp Snapshot + HUD reader là phương án tối ưu, bền vững và hợp lệ nhất. |

## Bảng ánh xạ trạng thái vào `decide()`

| Trường | Nguồn thu thập | Trạng thái tích hợp |
| :--- | :--- | :--- |
| **hp** | `TFTEoGStats.json` | chưa xác nhận real-time (phụ thuộc thời điểm ghi file) |
| **level** | `boardPieces.length` + HUD reader | OCR đo được trên video kiểm thử. Cần xác minh trên client Set 18 thật. |
| **gold** | HUD reader / Economy tracker | OCR đo được trên video kiểm thử. Cần xác minh trên client Set 18 thật. |
| **stage** | `gameLengthSeconds` + `TFTRoundSubsystem` | chưa xác nhận real-time (phụ thuộc thời điểm ghi file) |
| **shop** | HUD reader (`captures/hud-live.json`) | OCR đo được trên video kiểm thử. Cần xác minh trên client Set 18 thật. |
| **board & copiesOwned** | `TFTEoGStats.json` | chưa xác nhận real-time (phụ thuộc thời điểm ghi file) |

## Lệnh khởi chạy Live Coach

```bash
# Chạy bộ đọc HUD ngầm (nếu muốn đồng bộ Vàng và Shop trực tiếp từ màn hình):
npm run hud

# Chạy engine TFT Coach với nguồn Standalone Live:
npm run start:live
```
