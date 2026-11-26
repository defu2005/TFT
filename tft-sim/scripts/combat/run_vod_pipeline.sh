#!/usr/bin/env bash
# Chạy một lệnh: gộp -> khử trùng -> kiểm tra fight -> kiểm tra file chấm điểm. Dừng ngay nếu cổng gộp đỏ
# hoặc file chấm điểm có bản ghi không qua fidelity._validate.
# Dùng:  bash scripts/combat/run_vod_pipeline.sh <manifest> <out_root> <dest_dir>
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
MAN="$1"; OUT="$2"; DEST="$3"
echo "1/4 gộp: merge_check_vod.py"
python3 "$HERE/merge_check_vod.py" "$MAN" "$OUT" --report "$DEST.merge.json" || { echo "DỪNG: cổng gộp đỏ (xem $DEST.merge.json)"; exit 1; }
echo "2/4 khử trùng và file chấm điểm: ingest_vod.py (scoring.jsonl qua usable.py)"
python3 "$HERE/ingest_vod.py" "$MAN" "$OUT" "$DEST"
echo "3/4 kiểm tra fight đã khử trùng: validate_vod.py (thông tin)"
python3 "$HERE/validate_vod.py" "$DEST/fights.jsonl" --out "$DEST/validate.json" || echo "CÓ FIGHT BỊ BỎ trong fights.jsonl (xem $DEST/validate.json; winner_null là bình thường)"
echo "4/4 kiểm tra file chấm điểm: validate_vod.py (dừng nếu có bản ghi bị bỏ)"
python3 "$HERE/validate_vod.py" "$DEST/scoring.jsonl" --out "$DEST/validate_scoring.json" || { echo "DỪNG: scoring.jsonl có bản ghi không qua scorer (xem $DEST/validate_scoring.json)"; exit 1; }
echo "bộ lọc dùng được: $(python3 -c "import json,sys;r=json.load(open(sys.argv[1]));print(f\"fight={r['scoring_fights']} ván={r['scoring_games']}\")" "$DEST/ingest_report.json")"
echo "xong: $DEST (chấm điểm chỉ đọc $DEST/scoring.jsonl)"
