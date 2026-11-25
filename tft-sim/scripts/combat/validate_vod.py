"""Kiem tra file ban ghi tran VOD (fight-v1, nhan real) truoc khi gui di.

Dung:  python3 scripts/combat/validate_vod.py <file.jsonl> [--out ket_qua.json]

Quy tac giong bo cham diem (fidelity.read_real):
  - moi dong la JSON object; label phai la "real" (file do luong khong nhan nhan khac)
  - moi ly do bo qua duoc dem rieng va in ra kem so dong
Chi kiem tra TRAN (fight-v1). Ban ghi game, snapshot, su kien va chup hieu chuan
nam trong file rieng va khong chay qua script nay.
Thoat voi ma 0 khi khong co dong nao bi bo, 1 neu co dong bi bo.
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "src"))

import fidelity as Fd  # noqa: E402
import fight as F  # noqa: E402
from tft_sim.real_content import build_real  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--out", default=None, help="ghi tom tat JSON")
    args = ap.parse_args()
    F.set_content(18, build_real("TFTSet18"))

    path = Path(args.path)
    text = path.read_text(encoding="utf-8")
    ok, skipped, rows = 0, Counter(), []
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            skipped["json_hong"] += 1
            rows.append({"line": n, "reason": "json_hong"})
            continue
        if not isinstance(r, dict):
            skipped["khong_phai_object"] += 1
            rows.append({"line": n, "reason": "khong_phai_object"})
            continue
        if r.get("label") != "real":
            reason = f"label_khong_phai_real:{r.get('label')}"
        else:
            try:
                reason = Fd._validate(r, allow_dryrun=False)
            except Exception as e:  # noqa: BLE001 - bao cao, khong dung
                reason = f"exception:{type(e).__name__}"
        if reason:
            skipped[reason] += 1
            rows.append({"line": n, "source": r.get("source"), "reason": reason})
        else:
            ok += 1

    print(f"file: {path}")
    print(f"ban ghi hop le: {ok}")
    print(f"ban ghi bi bo: {sum(skipped.values())}")
    for reason, c in skipped.most_common():
        print(f"  {c:4d}  {reason}")
    for row in rows[:50]:
        print(f"  dong {row['line']}: {row.get('source')} -> {row['reason']}")
    if args.out:
        Path(args.out).write_text(json.dumps({"ok": ok, "skipped": dict(skipped), "rows": rows},
                                             ensure_ascii=False, indent=1), encoding="utf-8")
    return 0 if not skipped else 1


if __name__ == "__main__":
    raise SystemExit(main())
