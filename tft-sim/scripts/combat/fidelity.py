"""Doi chieu do trung thuc: xac suat engine du doan vs ket qua that. Args: records.jsonl [mode] [n].
Chi dung cac ban ghi co result.winner khac null. Ban ghi label 'sim' hoac 'fixture' se bi tu choi:
dung 'real' khi co bang chung tran that. Tra ve n = 0 neu chua co ban ghi nao (trang thai hien tai)."""
import json, sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import fight as F  # noqa: E402
from fight import load_jsonl, predict_win  # noqa: E402


def main(path, mode="public", n=40):
    recs = [r for r in load_jsonl(path) if r.get("result", {}).get("winner") is not None]
    if any(r["label"] != "real" for r in recs):
        raise SystemExit("tu choi: co ban ghi khong phai real")
    if not recs:
        print(json.dumps({"n": 0, "note": "chua co ban ghi real co ket qua"}, ensure_ascii=False))
        return
    p = np.array([predict_win(r, n, mode)["p_a"] for r in recs])
    y = np.array([1.0 if r["result"]["winner"] == 0 else 0.0 for r in recs])
    brier = float(np.mean((p - y) ** 2))
    acc = float(np.mean((p > 0.5) == (y > 0.5)))
    print(json.dumps({"n": len(recs), "mode": mode, "accuracy": round(acc, 4), "brier": round(brier, 4)}, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "public", int(sys.argv[3]) if len(sys.argv) > 3 else 40)
