"""Kiem tra nguon goc du lieu VOD theo slot (chi doc; khong sua gi).

Dung:  python3 scripts/combat/audit_vod_provenance.py [out_root] [--out bao_cao.json]

Moi slot duoc tinh rieng cac dau hieu:
  start_round_share     ty le game_id co giay bat dau chia het cho 60 (moc tron, nghi ngo)
  start_repeat_cross    so giay bat dau (trong cung slot) xuat hien o >= 2 VOD khac nhau
  games / stub_games    game khong co fight nao, hoac capture_notes chua stub/densify
  frame_refs / frame_missing   tham chieu khung hinh va so file khong ton tai trong thu muc VOD
  placeholder_games     game co ten lobby dang unknown_* / unk_* ; fight co unk_ trong fight_key
  board_repeat_games    so ván co bang (a, b) trung voi bang cua ván o VOD khac
  winner_known / winner_0 / winner_1   so luong ket qua biet duoc
  streamer_won_share    trong ket qua biet duoc, ty le ben streamer thang (side_of_streamer)
Ket qua: in bang va ghi JSON. Thoat 0 luon (day la bao cao, khong phai cong).
"""
import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PH_NAME = re.compile(r"^(unknown|unk)_", re.I)
PH_KEY = re.compile(r"unk_|unknown_", re.I)


def _jsonl(p: Path):
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                out.append({"_bad": True})
    return out


def _sig(side: dict) -> tuple:
    return tuple(sorted((u.get("api") or u.get("api_display") or "?", u.get("star")) for u in side.get("units", [])))


def audit(out_root: Path) -> dict:
    slots = defaultdict(lambda: Counter())
    starts = defaultdict(lambda: defaultdict(set))  # slot -> start_s -> {vod}
    boards = defaultdict(list)         # (slot, sig) -> [(vod, game)]
    for sdir in sorted(p for p in out_root.iterdir() if p.is_dir()):
        slot = sdir.name
        if slot == "none":
            continue
        C = slots[slot]
        for vdir in sorted(p for p in sdir.iterdir() if p.is_dir()):
            vod = vdir.name
            games = _jsonl(vdir / "games.jsonl")
            fights = _jsonl(vdir / "fights.jsonl")
            fights_by_game = defaultdict(int)
            for f in fights:
                if f.get("_bad"):
                    C["bad_lines"] += 1
                    continue
                gid = str(f.get("source", "")).split(":")[0]
                fights_by_game[gid] += 1
                if PH_KEY.search(str(f.get("fight_key", ""))):
                    C["fight_placeholder_key"] += 1
                C["fights"] += 1
                for side in ("a", "b"):
                    for u in (f.get(side) or {}).get("units", []):
                        for fr in u.get("frames", []) or []:
                            C["frame_refs"] += 1
                            if not (vdir / fr).exists():
                                C["frame_missing"] += 1
                w = (f.get("result") or {}).get("winner")
                if w is not None:
                    C["winner_known"] += 1
                    C[f"winner_{w}"] += 1
                    sos = f.get("side_of_streamer")
                    if sos in ("a", "b") and w in (0, 1):
                        C["streamer_won" if (w == 0) == (sos == "a") else "streamer_lost"] += 1
                if f.get("a") and f.get("b"):
                    boards[(slot, _sig(f["a"]), _sig(f["b"]))].append((vod, f.get("source")))
            for g in games:
                if g.get("_bad"):
                    C["bad_lines"] += 1
                    continue
                gid = str(g.get("game_id", ""))
                C["games"] += 1
                m = re.search(r"-g(\d+)$", gid)
                if m:
                    sec = int(m.group(1))
                    starts[slot][sec].add(vod)
                    if sec % 60 == 0:
                        C["start_round_minute"] += 1
                if fights_by_game.get(gid, 0) == 0:
                    C["stub_games"] += 1
                notes = str(g.get("capture_notes", "")).lower()
                if "stub" in notes or "densify" in notes:
                    C["stub_notes"] += 1
                if any(PH_NAME.match(str(n)) for n in g.get("lobby_names") or []):
                    C["placeholder_games"] += 1
                if len(g.get("lobby_names") or []) < 8:
                    C["short_lobby_games"] += 1
    report = {}
    for slot, C in sorted(slots.items()):
        g = C["games"] or 1
        report[slot] = dict(C)
        report[slot]["start_round_share"] = round(C["start_round_minute"] / g, 3)
        report[slot]["start_repeat_cross"] = sum(1 for vs in starts[slot].values() if len(vs) >= 2)
    # boards: cung bang (a,b) o VOD khac nhau cua cung slot
    per_slot_repeat = Counter()
    for (slot, sa, sb), refs in boards.items():
        vods = {v for v, _ in refs}
        if len(vods) >= 2 and sa and sb:
            per_slot_repeat[slot] += 1
    for slot in report:
        report[slot]["board_repeat_games"] = per_slot_repeat.get(slot, 0)
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("out_root", nargs="?", default=str(ROOT / "data/vod_out/20261125"))
    ap.add_argument("--out", default=str(ROOT / "results/fixed/combat/vod_provenance_audit.json"))
    args = ap.parse_args()
    rep = audit(Path(args.out_root))
    keys = ["games", "fights", "stub_games", "stub_notes", "placeholder_games", "short_lobby_games",
            "fight_placeholder_key", "frame_refs", "frame_missing", "start_round_share",
            "start_repeat_cross", "board_repeat_games", "winner_known", "winner_0", "winner_1", "streamer_won", "streamer_lost", "bad_lines"]
    print("slot  " + " ".join(f"{k[:12]:>12}" for k in keys))
    for slot, C in rep.items():
        print(f"{slot:<5} " + " ".join(f"{str(C.get(k, 0))[:12]:>12}" for k in keys))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"ghi {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
