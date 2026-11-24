# Runbook thu thập HUD (chạy trên máy cloud)

Cập nhật: 2026-11-24.

## Chạy
```bash
export TFT_CAMPAIGN_DIR=/home/user/campaign/campaign
cd /home/user/TFT && nohup python3 scripts/hud-campaign/run.py > /home/user/campaign/run.out 2> /home/user/campaign/run.err &
```

## Theo dõi
- Trạng thái: `$TFT_CAMPAIGN_DIR/status.json` (heartbeatUtc, counts, diskFreeBytes).
- Log: `/home/user/campaign/run.out`, `run.err`.
- Kết quả theo mẫu: `$TFT_CAMPAIGN_DIR/results/*.jsonl.gz`.

## Dừng
```bash
pkill -f "hud-campaign/run.py"
```

## Điều kiện dừng thủ công
- Đĩa trống dưới 4 GiB (`RESERVE_BYTES` trong `run.py` tự tạm dừng tải).
- `run.err` có lỗi lặp lại.

## Ghi chú
- Không có `verified-matches.json`, nên MP4 không tự bị xóa. Khi đĩa đầy, hàng đợi tự tạm dừng. Cần thêm danh sách đã kiểm tra để dọn MP4.
- Không có crop HUD được lưu. Đọc dự phòng bằng model cần thêm bước xuất crop (việc của `hud`).
- Khóa API không được ghi vào file. Proxy gắn khóa cho host `agy.4u.io.vn`.
- Bản vá `run.py` (2026-11-24): các file cgroup là tùy chọn, có dự phòng qua `/proc`.
