# Phân tích và Thực thi Bắt dữ liệu Tầng Network & RAM (TFT Coach)

Ghi nhận ngày: 2026-11-22

## 1. Khảo sát & Phân tích Thực nghiệm

Bản cài đặt TFT hiện tại là bản **TFT Standalone** trên nền tảng **Unreal Engine** (`TFTClient-Win64-Shipping.exe`, dung lượng ~218 MB), tách biệt khỏi client League of Legends truyền thống.

### A. Tầng Mạng (Network Layer)

Qua phân tích log khởi động (`captures/tft-client-full.log`) và quét kết nối mạng (`scripts/probe-network.py`):
1. **Giao thức Game Server**:
   - Sử dụng **Unreal Engine Iris Replication model** qua socket UDP (`RGINetDriver` / `GameNetDriver`).
   - Khi vào trận đấu, client kết nối tới server game qua UDP (ví dụ IP máy chủ: `151.106.248.19:7415`).
   - Phiên kết nối được bảo vệ bằng handshake token (`PlayerKey="..."`). Dữ liệu payload là bit-packed stream theo channel của Iris Replication.
2. **Lưu lượng REST / Dịch vụ**:
   - Giao tiếp web và backend Riot đi qua HTTPS (port 443, Cloudflare/AWS) được mã hóa TLS.
   - Riot Chat chạy qua TLS port 5223 (`sa3.chat.si.riotgames.com:5223`).
3. **Riot Client Local API**:
   - Cổng cục bộ của `RiotClientServices.exe` (đọc qua lockfile tại `%LOCALAPPDATA%\Riot Games\Riot Client\Config\lockfile`).
   - API này quản lý session, authentication và chat, nhưng **không** mở cổng Live Client Data `127.0.0.1:2999` cho trận đấu như client LMHT cũ.
4. **Đánh giá tầng Network**:
   - Việc bắt gói tin mạng thụ động (packet sniffing UDP/TCP) gặp rào cản lớn do dữ liệu replication được nén bit và mã hóa phiên. Tốn nhiều chi phí giải mã và rất dễ gãy khi game cập nhật version (NetCL/Iris checksum).

---

### B. Tầng Bộ nhớ (RAM Layer)

Khảo sát quyền truy cập bộ nhớ của tiến trình `TFTClient-Win64-Shipping.exe`:
1. **Khả năng đọc bộ nhớ**:
   - Đã kiểm tra mở tiến trình bằng Windows API `OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ)`.
   - Kết quả: **Thành công (LastError = 0)**. Tiến trình user-mode cho phép đọc bộ nhớ qua `ReadProcessMemory` mà không bị driver kernel chặn.
2. **Cấu trúc đối tượng game trong RAM (Unreal Engine Subsystems)**:
   - Các subsystem chính điều khiển trạng thái trận đấu:
     - `UTFTShopPlayerSubsystem`: Quản lý 5 slot tướng trong shop, lượt roll, khoá shop.
     - `UTFTRoundSubsystem`: Quản lý round, stage và phase hiện tại.
     - `ATFTMatchPlayerController` & PlayerState: Lưu trữ chỉ số vàng (`gold`), máu (`hp`), kinh nghiệm (`xp`), level.
3. **Chiến lược đọc RAM**:
   - Dùng phương pháp **Differential Memory Scanning** (quét tìm theo giá trị thay đổi):
     - Lần 1: Quét toàn bộ bộ nhớ Committed Read/Write để tìm các địa chỉ mang giá trị hiển thị (ví dụ số vàng hiện tại).
     - Lần 2: Người chơi mua đồ/thay đổi vàng, quét lọc lại trên tập địa chỉ tìm thấy ở lần 1.
     - Sau 2-3 lần lọc, xác định được địa chỉ/offset tĩnh của biến `gold`, `hp`, `level`.
   - Khi đã có cấu hình địa chỉ, module `probe-ram.py --live` đọc định kỳ 250ms và xuất trạng thái thời gian thực ra `captures/ram-state.json`.

---

## 2. Các công cụ đã xây dựng

| Script / Module | Chức năng |
| --- | --- |
| `scripts/probe-network.py` | Quét và phân loại toàn bộ kết nối TCP/UDP, xác định port của GameNetDriver và Riot Client API |
| `scripts/probe-ram.py` | Công cụ tương tác quét RAM tìm offset (`--interactive`), kiểm tra quyền (`--check`), và chạy daemon thời gian thực (`--live`) |
| `src/ingest/ramSource.js` | Adapter nạp dữ liệu từ RAM vào core engine của TFT Coach |
| `src/app.js` | Hỗ trợ cấu hình `TFT_SOURCE=ram` |

---

## 3. Quy trình vận hành

1. **Kiểm tra kết nối mạng**:
   ```bash
   python scripts/probe-network.py
   ```
2. **Xác định Offset trong RAM (khi đang trong trận)**:
   ```bash
   python scripts/probe-ram.py --interactive
   ```
   - Nhập số vàng hiện tại trên màn hình -> script quét lần 1.
   - Thay đổi số vàng trong game -> nhập giá trị mới -> script lọc ra địa chỉ chính xác.
   - Lưu địa chỉ vào `captures/ram-offsets.json`.
3. **Khởi động nguồn dữ liệu RAM**:
   - Terminal 1 (RAM Reader daemon):
     ```bash
     python scripts/probe-ram.py --live
     ```
   - Terminal 2 (TFT Coach):
     ```bash
     TFT_SOURCE=ram npm start
     ```
