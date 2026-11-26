# 8. Vận hành

Bộ tài liệu này không liệt kê lệnh chính xác từng bước, vì các script thay đổi. Mỗi script có `--help` hoặc đầu file mô tả đối số. Khi chạy lại, luôn kiểm tra đầu file trước.

## Môi trường

- Repo engine `tft_goat` ở `/root/work/tft_goat`, commit `d5358e9`. Phải cài đúng commit này.
- Repo TFT, nhánh làm việc `claude/claude-fable-5-2-awwmf5`.
- Chạy trên một luồng. Không song song hóa nếu chưa đo.

## Các việc hay làm

| Việc | Script | Ghi chú |
|---|---|---|
| Chấm điểm | `scripts/combat/fidelity.py` | `python ... <path> [n]`, n mặc định 800. |
| Kiểm tự động | `scripts/combat/selftest_*.py` | Phải PASS trước khi báo cáo. |
| Kiểm n thích ứng | `check_adaptive_n_items.py` | `--workers`, `--n-full` (mặc định 400), `--out`. Với n=800, phải có 398 mẫu. |
| Phân loại item | `check_item_effects.py` | Ghi `results/fixed/combat/item_effect_classes.json`. |
| Quét augment | `check_augment_sweep.py` | Ghi `augment_sweep.json`. |
| Đối xứng và seed | `check_symmetry_seed.py` | Seed 0 và 1000. |

## Pipeline VOD (4 bước)

Chạy theo `run_vod_pipeline.sh`:
1. Ingest (`ingest_vod.py`).
2. Validate (`validate_vod.py`).
3. Cổng gộp (`merge_check_vod.py`).
4. Ghi `scoring.jsonl` nếu đạt.

Kiểm thư mục bằng `check_vod_dir.py`. **Cổng hiện đỏ**, nên bước 4 không sinh bản ghi dùng được.

## Kiểm tra trước khi báo cáo

1. Selftest PASS.
2. Chạy lại số liệu nếu đổi mã.
3. Ghi rõ cấu hình (PRIMARY/SECONDARY), n, seed.
4. Ghi rõ mẫu số.

## Khi có lỗi

Đừng đổi ngưỡng để qua. Ghi lỗi, ghi nguyên nhân đã loại trừ, và ghi điều gì sẽ xác định nguyên nhân. Xem nhật ký trong [10](10-nhat-ky-quyet-dinh.md).
