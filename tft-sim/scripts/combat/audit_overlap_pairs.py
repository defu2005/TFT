"""Phan tich cac cap lobby lech (chung 4-7 ten) giua hai VOD (chi doc).

Dung:  python3 scripts/combat/audit_overlap_pairs.py [out_root] [manifest] [--out bao_cao.json]

Voi moi cap ván o hai VOD khac nhau co so ten chung 4..7:
  - cung streamer hay khac streamer (manifest)
  - voi cap chung >= 6 ten: co ván nao trung bang (a, b) o cung stage hay khong.
    Bang trung hoan toan o cung stage la dau hieu cung mot ván bi ghi hai lan.
"""
import argparse
import glob
import json
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _norm(n) -> str:
    return unicodedata.normalize("NFC", str(n)).casefold().strip()


def _sig(side: dict) -> tuple:
    return tuple(sorted((str(u.get("api")), str(u.get("star"))) for u in side.get("units", [])))


def analyse(out_root: Path, manifest: Path) -> dict:
    man = json.loads(manifest.read_text(encoding="utf-8"))
    streamer = {r["vod_id"]: r.get("streamer") for r in man["vods"]}
    games, fights = {}, defaultdict(list)
    for f in glob.glob(str(out_root / "*" / "*" / "games.jsonl")):
        vod = Path(f).parent.name
        for line in Path(f).read_text(encoding="utf-8").splitlines():
            if line.strip():
                g = json.loads(line)
                games[(vod, g["game_id"])] = [_norm(n) for n in g.get("lobby_names") or []]
    for f in glob.glob(str(out_root / "*" / "*" / "fights.jsonl")):
        vod = Path(f).parent.name
        for line in Path(f).read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                gid, stage = str(r["source"]).split(":")
                fights[(vod, gid)].append((stage, r))
    keys = [k for k, v in games.items() if len(v) >= 4]
    pairs = []
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = keys[i], keys[j]
            if a[0] == b[0]:
                continue
            sh = len(set(games[a]) & set(games[b]))
            if 4 <= sh < 8:
                pairs.append((sh, a, b))
    same = [p for p in pairs if streamer.get(p[1][0]) == streamer.get(p[2][0])]
    ge6 = [p for p in pairs if p[0] >= 6]
    identical = 0
    for _, a, b in ge6:
        fa = {s: (_sig(r["a"]), _sig(r["b"])) for s, r in fights.get(a, [])}
        fb = {s: (_sig(r["a"]), _sig(r["b"])) for s, r in fights.get(b, [])}
        if any(fa[s] == fb[s] for s in set(fa) & set(fb)):
            identical += 1
    return {
        "pairs_total": len(pairs),
        "shared_histogram": dict(sorted(Counter(p[0] for p in pairs).items())),
        "same_streamer": len(same),
        "cross_streamer": len(pairs) - len(same),
        "pairs_shared_ge6": len(ge6),
        "pairs_ge6_identical_board_same_stage": identical,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("out_root", nargs="?", default=str(ROOT / "data/vod_out/20261125"))
    ap.add_argument("manifest", nargs="?", default=str(ROOT / "data/vod_manifest_20261125.json"))
    ap.add_argument("--out", default=str(ROOT / "results/fixed/combat/overlap_pairs_audit.json"))
    a = ap.parse_args()
    rep = analyse(Path(a.out_root), Path(a.manifest))
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
