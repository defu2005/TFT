"""CLI: mot ban ghi fight-v1 (JSON, mot dong) vao, xac suat ben A thang ra.
Usage: python fight_cli.py record.json [ability=hand|generic|none] [items=1|0] [n=40] [seed0=0]
Mac dinh: Set 17 -> hand, Set 18 -> generic (khong bao gio hand cho Set 18).
Ket qua la uoc tinh mo phong engine (label sim), khong phai du doan tran that."""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import fight as F  # noqa: E402
from tft_sim.real_content import build_real  # noqa: E402
from tft_sim.item_alias import build_set18_records  # noqa: E402

F.set_content(17, build_real("TFTSet17"))
F.set_content(18, build_set18_records()[0])  # CDragon nguyen goc; alias chi qua item_alias (muc 11.19)


def main(argv):
    rec = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    F.check_record(rec)
    ability = argv[2] if len(argv) > 2 else ("hand" if rec["set"] == 17 else "generic")
    items = (argv[3] if len(argv) > 3 else "1") == "1"
    n = int(argv[4]) if len(argv) > 4 else 40
    seed0 = int(argv[5]) if len(argv) > 5 else 0
    out = F.predict_win(rec, n, ability, items, seed0)
    out["label"] = rec["label"]
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv)
