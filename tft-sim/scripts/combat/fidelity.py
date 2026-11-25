"""Doi chieu do trung thuc: xac suat engine du doan vs ket qua that.
Args: records.jsonl [ability=hand|generic|none] [items=1|0] [n=40]
Chi dung ban ghi co result.winner khac null. Tu choi moi ban ghi khong phai label 'real'.
Tra ve n = 0 neu chua co ban ghi real co ket qua (trang thai hien tai)."""
import json, sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from fight import load_jsonl, predict_win  # noqa: E402


def score(path, ability=None, items=True, n=40):
    recs = load_jsonl(path)
    done = [r for r in recs if r.get("result", {}).get("winner") is not None]
    if any(r["label"] != "real" for r in done):
        raise SystemExit("tu choi: co ban ghi khong phai real")
    if not done:
        return {"n": 0, "note": "chua co ban ghi real co ket qua"}
    def mode(r):
        return ability or ("hand" if r["set"] == 17 else "generic")
    p = np.array([predict_win(r, n, mode(r), items)["p_a"] for r in done])
    y = np.array([1.0 if r["result"]["winner"] == 0 else 0.0 for r in done])
    return {"n": len(done), "ability": ability or "auto(hand Set17, generic Set18)", "items": items,
            "accuracy": round(float(np.mean((p > 0.5) == (y > 0.5))), 4),
            "brier": round(float(np.mean((p - y) ** 2)), 4)}


if __name__ == "__main__":
    ab = sys.argv[2] if len(sys.argv) > 2 else None
    it = (sys.argv[3] if len(sys.argv) > 3 else "1") == "1"
    print(json.dumps(score(sys.argv[1], ab, it, int(sys.argv[4]) if len(sys.argv) > 4 else 40), ensure_ascii=False))
