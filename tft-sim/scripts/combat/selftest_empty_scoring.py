"""Ca scoring.jsonl rong: validate_vod.py va fidelity.py phai thoat 0, fidelity bao inconclusive. Khong dung du lieu VOD."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ok = True
with tempfile.TemporaryDirectory() as d:
    empty = Path(d) / "scoring.jsonl"
    empty.write_text("", encoding="utf-8")
    v = subprocess.run([sys.executable, str(HERE / "validate_vod.py"), str(empty)], capture_output=True, text=True)
    c1 = v.returncode == 0
    f = subprocess.run([sys.executable, str(HERE / "fidelity.py"), str(empty)], capture_output=True, text=True)
    c2 = f.returncode == 0 and json.loads(f.stdout).get("inconclusive") is True
    print(f"{'PASS' if c1 else 'FAIL'} validate rong thoat={v.returncode}")
    print(f"{'PASS' if c2 else 'FAIL'} fidelity rong thoat={f.returncode} inconclusive")
    ok = c1 and c2
print("SELFTEST EMPTY SCORING", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
