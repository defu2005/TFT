# Phiên 2026-11-26 · agent Claude · bộ tài liệu product

- **Yêu cầu:** nạp context cho advisor để viết bộ tài liệu đầy đủ cho dự án như một product lớn.
- **Commit đầu / cuối:** `90192c21` → (xem `git log -1`, commit ghi ở cuối phiên)
- **Đã làm:**
  - Thêm `docs/product/` (12 mục + README). Đối chiếu với `docs/roadmap.md` (nhánh nifty), `model-plan.md` 10.6–10.10, `vod-collection.md`, `cloud-agents.md`, `combat-public-data.md` 10c, `usable.py`, `run_vod_pipeline.sh`, `item_alias.py`.
  - Sửa STATUS: bỏ hash tự ghi; làm rõ +0,015 là kiểm harness, không phải kết quả mô hình.
  - Sửa `progress/README.md`: thuật ngữ Mô hình, Dự đoán thắng/thua.
  - Thêm link tới `docs/product/` từ STATUS, progress/README, README.
- **Kết quả:** không có số liệu mới. Các số trong bộ tài liệu lấy từ file kết quả hoặc `model-plan.md`.
- **Đính chính:** "+0,015 là mô hình vượt teacher" (sai, là kiểm harness); "65/776 item" (sai phạm vi, đúng 617/731); hash tự ghi trong STATUS; mô tả alias là twin (đúng: DA_* craftable và DA_Component_*); mâu thuẫn "không lưu blitz" (không tìm thấy quy tắc đó; có ghi nhận người dùng cho phép).
- **Còn mở:** xem `docs/product/11-rui-ro-cau-hoi-mo.md`, mục "Câu hỏi cho người dùng". Trạng thái đường RAM chưa rõ trong roadmap (hai câu trái nhau).
- **Cập nhật `STATUS.md`:** có.
