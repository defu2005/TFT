"""Tu kiem cho agent thu thap: liet ke ly do loai cua moi fight trong MOT thu muc VOD, truoc khi commit.

Dung:  python3 scripts/combat/check_vod_dir.py data/vod_out/20261125/<S>/<vod_id>
Doc fights.jsonl va kiem bang usable.reason (cung bo loc voi buoc cham diem). Chi doc, khong ghi.
Thoat 0 khi moi fight deu dung duoc hoac khong co fight; 1 neu co fight bi loai (chi de biet, khong phai loi).
"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "src"))

import fight as F  # noqa: E402
import usable as U  # noqa: E402
from tft_sim.real_content import build_real  # noqa: E402


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    vdir = Path(sys.argv[1])
    F.set_content(18, build_real("TFTSet18"))
    champs = F._CONTENT[18].champions
    fp = vdir / "fights.jsonl"
    rows = [json.loads(l) for l in fp.read_text(encoding="utf-8").splitlines() if l.strip()] if fp.exists() else []
    reasons, games_ok = Counter(), set()
    for f in rows:
        why = U.reason(f, champs, vdir)
        if why is None:
            games_ok.add(U.game_of(f))
        reasons[why or "dung_duoc"] += 1
    print(f"thu muc: {vdir}")
    print(f"fight: {len(rows)}; dung duoc: {reasons.get('dung_duoc', 0)}; van dung duoc: {len(games_ok)}")
    for k, v in reasons.most_common():
        print(f"  {k}: {v}")
    return 0 if all(k == "dung_duoc" for k in reasons) else 1


if __name__ == "__main__":
    raise SystemExit(main())
