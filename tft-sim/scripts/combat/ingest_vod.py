"""Khu trung va viet lai source truoc khi cham diem (spec 10.2; docs/handoff/vod-collection.md muc 8).

Dung:  python3 scripts/combat/ingest_vod.py <manifest.json> <out_root> <dest_dir>

Dieu kien: merge_check_vod.py phai thoat 0 (khong co ERR). Chi doc dong role=primary.
  lobby_id     = sha1 cua 8 ten lobby da chuan hoa (NFC, casefold, bo khoang trang, sap xep), 12 ky tu dau.
  khoa khu trung = (lobby_id, stage_round, cap ten nguoi choi da chuan hoa).
  Giu mot ban ghi cho moi khoa (VOD co vod_id nho nhat; ten hop le ve thu tu, khong dua tren khung hinh
  vi chua co so do chat luong khung). Cac nguon con lai ghi vao fight_extra.
  source duoc viet lai thanh <lobby_id>:<stage_round>; fight_key thanh <lobby_id>|<stage>|<a>|<b>.

Ghi ra:
  <dest>/fights.jsonl       fight-v1, nhan real, da khu trung (dau vao cho validate_vod.py va fidelity.read_real)
  <dest>/fight_extra.jsonl  mot dong cho moi khoa co nhieu nguon: {"type": "fight_extra", "fight_key", "sources"}
  <dest>/ingest_report.json so lieu va danh sach lobby
"""
import hashlib
import json
import subprocess
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _norm(name) -> str:
    return unicodedata.normalize("NFC", str(name)).casefold().strip()


def _jsonl(p: Path) -> list[dict]:
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def ingest(manifest: Path, out_root: Path, dest: Path) -> dict:
    chk = subprocess.run([sys.executable, str(HERE / "merge_check_vod.py"), str(manifest), str(out_root)],
                         capture_output=True, text=True)
    if chk.returncode != 0:
        raise SystemExit("tu choi: merge_check_vod.py con loi:\n" + chk.stdout)

    man = json.loads(manifest.read_text(encoding="utf-8"))
    prim = [(r["slot"], r["vod_id"]) for r in man["vods"] if r["role"] == "primary"]

    lobby_of = {}                 # (vod, game_id) -> lobby_id
    lobby_vods = defaultdict(set)
    groups = defaultdict(list)    # (lobby, stage, pair) -> [(vod, game_id, record)]
    for slot, vid in sorted(prim, key=lambda x: x[1]):
        vdir = out_root / slot / vid
        for g in _jsonl(vdir / "games.jsonl"):
            names = sorted(_norm(n) for n in g["lobby_names"])
            lid = hashlib.sha1("|".join(names).encode("utf-8")).hexdigest()[:12]
            lobby_of[(vid, g["game_id"])] = lid
            lobby_vods[lid].add(vid)
        for f in _jsonl(vdir / "fights.jsonl"):
            gid, stage = str(f["source"]).split(":")
            lid = lobby_of.get((vid, gid))
            if lid is None:
                raise SystemExit(f"thieu game {gid} trong {vid}")
            pair = tuple(sorted(_norm(p) for p in str(f["fight_key"]).split("|")[-2:]))
            groups[(lid, stage, pair)].append((vid, gid, f))

    out, extra = [], []
    for (lid, stage, pair), lst in sorted(groups.items()):
        lst.sort(key=lambda x: x[0])
        vod, gid, keep = lst[0]
        keep = dict(keep)
        keep["source"] = f"{lid}:{stage}"
        keep["fight_key"] = f"{lid}|{stage}|{pair[0]}|{pair[1]}"
        out.append(keep)
        if len(lst) > 1:
            extra.append({"type": "fight_extra", "fight_key": keep["fight_key"],
                          "sources": [{"vod": v, "game_id": g, "source_raw": x["source"]} for v, g, x in lst]})

    dest.mkdir(parents=True, exist_ok=True)
    (dest / "fights.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in out) + "\n",
                                       encoding="utf-8")
    (dest / "fight_extra.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in extra)
                                            + ("\n" if extra else ""), encoding="utf-8")
    report = {"fights_in": sum(len(v) for v in groups.values()), "fights_out": len(out),
              "fight_extra": len(extra), "lobbies": len({k[0] for k in groups}),
              "games_clusters_out": len({r["source"].split(":")[0] for r in out}),
              "lobby_vods": {k: sorted(v) for k, v in lobby_vods.items()}}
    (dest / "ingest_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return report


def main() -> int:
    if len(sys.argv) != 4:
        print(__doc__)
        return 2
    r = ingest(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
    print(json.dumps(r, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
