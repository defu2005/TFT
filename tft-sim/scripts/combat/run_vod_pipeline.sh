#!/usr/bin/env bash
# Chạy một lệnh: gộp -> khử trùng -> kiểm tra từng fight. Dừng ngay nếu cổng gộp đỏ.
# Dùng:  bash scripts/combat/run_vod_pipeline.sh <manifest> <out_root> <dest_dir>
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
MAN="$1"; OUT="$2"; DEST="$3"
echo "1/3 gộp: merge_check_vod.py"
python3 "$HERE/merge_check_vod.py" "$MAN" "$OUT" --report "$DEST.merge.json" || { echo "DỪNG: cổng gộp đỏ (xem $DEST.merge.json)"; exit 1; }
echo "2/3 khử trùng: ingest_vod.py"
python3 "$HERE/ingest_vod.py" "$MAN" "$OUT" "$DEST"
echo "3/3 kiểm tra từng fight: validate_vod.py"
python3 "$HERE/validate_vod.py" "$DEST/fights.jsonl" --out "$DEST/validate.json" || echo "CÓ FIGHT BỊ BỎ (xem $DEST/validate.json; winner_null là bình thường)"
echo "xong: $DEST"
