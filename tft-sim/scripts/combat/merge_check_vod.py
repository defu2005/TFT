"""Kiem tra gop cac dau ra VOD cua nhieu agent truoc khi ghep va cham diem.

Dung:  python3 scripts/combat/merge_check_vod.py <manifest.json> <out_root> [--report bao_cao.json]

Layout dau ra (moi agent ghi, chi trong thu muc cua slot minh):
    <out_root>/<slot>/<vod_id>/handoff.json    (vod-handoff-v1, xem docs/handoff/vod-collection.md)
    <out_root>/<slot>/<vod_id>/games.jsonl     (game)
    <out_root>/<slot>/<vod_id>/fights.jsonl    (fight, fight-v1)
    <out_root>/<slot>/<vod_id>/others.jsonl    (cac loai khac)

Ma loi (ERR chan ghep; WARN chi bao):
  bad_id                      vod_id sai dang, hoac co ':'
  bad_slot                    slot trong manifest khong co trong danh sach slots
  vod_primary_duplicate       mot vod_id co hai dong role=primary
  streamer_multi_slot         mot streamer co dong primary o hai slot (phan vung bi vo)
  hud_processed_output        co dau ra cho vod thuoc slot "none"
  stray_output                thu muc khong khop dong manifest (WARN)
  handoff_mismatch            handoff.json co vod_id/slot khac duong dan thu muc
  bad_range                   covered_ranges_s khong phai [a, b] voi a < b
  overlap_within_slot         cac khoang covered trong mot handoff chong nhau
  covered_remaining_overlap   covered va remaining cung handoff chong nhau
  overlap_across_slots        khoang cua hai thu muc cung vod_id chong nhau (thu muc cu chua duoc go)
  bad_game_id                 game_id hoac phan game cua source khong dung dang <vod_id>-g<so>
  bad_lobby                   lobby_names khong co 8 ten duy nhat sau chuan hoa
  bad_source_url               vod_url khong phai Twitch hoac YouTube (xem SRC_RE)
  duplicate_source            hai dong fight cung 'source' (cung vod: ERR; khac vod: ERR)
  missing_handoff             co du lieu nhung thieu handoff.json
  missing_game                fight tham chieu game_id khong co trong games.jsonl cung thu muc
  shared_lobby_needs_ingest   (WARN) cung lobby (sau chuan hoa) o hai vod: ingest phai khu trung
  duplicate_fight_key_needs_ingest (WARN) cung (lobby, stage, cap nguoi choi) o hai vod
  lobby_partial_overlap       (WARN) hai lobby khac nhau nhung chung 4-7 ten: kiem tra tay

Chuan hoa ten lobby: NFC, casefold, bo khoang trang dau cuoi. Ten khac nhau o hoa/thuong
hay khoang trang van duoc coi la cung nguoi.

Ghi chu: game_id = <vod_id>-g<so>, nen hai streamer cung lobby co game_id khac nhau. Viec
khu trung va viet lai source thanh <lobby_id>:<stage> la buoc ingest (scripts/combat/ingest_vod.py).
"""
import argparse
import hashlib
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

VOD_RE = re.compile(r"^(twitch-\d+|youtube-[A-Za-z0-9_-]+)$")
SRC_RE = re.compile(r"^https://(www\.twitch\.tv/videos/\d+|www\.youtube\.com/watch\?v=[A-Za-z0-9_-]+|youtu\.be/[A-Za-z0-9_-]+)$")


def _norm(name) -> str:
    return unicodedata.normalize("NFC", str(name)).casefold().strip()


def _jsonl(p: Path) -> list[dict]:
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def _overlap(a, b) -> bool:
    return a[0] < b[1] and b[0] < a[1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("out_root")
    ap.add_argument("--report", default=None)
    args = ap.parse_args()

    man = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    out = Path(args.out_root)
    errs, warns = [], []

    def err(code, **kw):
        errs.append({"code": code, **kw})

    def warn(code, **kw):
        warns.append({"code": code, **kw})

    rows = man["vods"]
    slots = set(man["slots"])
    primary_by_vod = defaultdict(list)
    primary_by_streamer = defaultdict(set)
    expected = {}  # (slot, vod_id) -> role
    for r in rows:
        vid, slot, role = r["vod_id"], r["slot"], r["role"]
        if not VOD_RE.match(vid) or ":" in vid:
            err("bad_id", where="manifest", vod_id=vid)
        if slot not in slots:
            err("bad_slot", where="manifest", vod_id=vid, slot=slot)
        if role == "primary":
            primary_by_vod[vid].append(slot)
            primary_by_streamer[r.get("streamer")].add(slot)
        if role in ("primary", "second_label") and slot in slots:
            expected[(slot, vid)] = role
        if role == "hud_processed" and slot != "none":
            err("hud_processed_output", where="manifest", vod_id=vid, slot=slot)
    for vid, slist in primary_by_vod.items():
        if len(slist) > 1:
            err("vod_primary_duplicate", vod_id=vid, slots=slist)
    for streamer, sl in primary_by_streamer.items():
        if len(sl) > 1:
            err("streamer_multi_slot", streamer=streamer, slots=sorted(sl))

    actual = []
    if out.exists():
        for sdir in sorted(p for p in out.iterdir() if p.is_dir()):
            for vdir in sorted(p for p in sdir.iterdir() if p.is_dir()):
                actual.append((sdir.name, vdir.name, vdir))

    overlap_pool = defaultdict(list)            # (vod, nhom) -> [(slot, khoang)]
    fight_sigs = defaultdict(list)              # (sig, stage, cap) -> [(vod, slot, source)]
    sources_seen = defaultdict(list)            # source -> [(vod, slot)]
    lobby_vods = defaultdict(set)               # sig -> {vod}
    lobby_names = {}                            # (vod, game_id) -> frozenset(ten chuan hoa)

    for slot, vid, vdir in actual:
        if slot == "none":
            err("hud_processed_output", where="out", vod_id=vid)
            continue
        if not VOD_RE.match(vid) or ":" in vid:
            err("bad_id", where="out", vod_id=vid, slot=slot)
            continue
        role = expected.get((slot, vid))
        has_data = any((vdir / f).exists() for f in ("games.jsonl", "fights.jsonl", "others.jsonl"))
        if role is None:
            warn("stray_output", slot=slot, vod_id=vid)
        hp = vdir / "handoff.json"
        if has_data and not hp.exists():
            err("missing_handoff", slot=slot, vod_id=vid)
        if hp.exists():
            h = json.loads(hp.read_text(encoding="utf-8"))
            if h.get("vod_id") != vid or h.get("slot") != slot:
                err("handoff_mismatch", slot=slot, vod_id=vid,
                    handoff_vod=h.get("vod_id"), handoff_slot=h.get("slot"))
            ranges = []
            for x in h.get("covered_ranges_s", []):
                if isinstance(x, list) and len(x) == 2 and x[0] < x[1]:
                    ranges.append(tuple(x))
                else:
                    err("bad_range", slot=slot, vod_id=vid, value=x)
            for i in range(len(ranges)):
                for j in range(i + 1, len(ranges)):
                    if _overlap(ranges[i], ranges[j]):
                        err("overlap_within_slot", slot=slot, vod_id=vid, a=ranges[i], b=ranges[j])
            rem = [tuple(x) for x in h.get("remaining_ranges_s", []) if isinstance(x, list) and len(x) == 2]
            for rg in rem:
                for cg in ranges:
                    if _overlap(rg, cg):
                        err("covered_remaining_overlap", slot=slot, vod_id=vid, covered=cg, remaining=rg)
            group = "second" if role == "second_label" else "primary"
            for rg in ranges:
                overlap_pool[(vid, group)].append((slot, rg))

        gid_re = re.compile(rf"^{re.escape(vid)}-g\d+$")
        games = {}
        for g in _jsonl(vdir / "games.jsonl"):
            gid = g.get("game_id")
            if not isinstance(gid, str) or not gid_re.match(gid):
                err("bad_game_id", where="games", vod_id=vid, slot=slot, game_id=gid)
                continue
            if g.get("vod_url") is not None and not SRC_RE.match(str(g["vod_url"])):
                err("bad_source_url", vod_id=vid, slot=slot, game_id=gid, url=g["vod_url"])
            games[gid] = g
            names = [_norm(n) for n in (g.get("lobby_names") or [])]
            if len(names) != 8 or len(set(names)) != 8:
                err("bad_lobby", vod_id=vid, slot=slot, game_id=gid, n=len(names))
                continue
            if role == "primary":
                sig = hashlib.sha1("|".join(sorted(names)).encode("utf-8")).hexdigest()[:12]
                lobby_vods[sig].add(vid)
                lobby_names[(vid, gid)] = frozenset(names)
        if role != "primary":
            continue  # second_label chi doi chieu, khong vao gop

        for f in _jsonl(vdir / "fights.jsonl"):
            src = str(f.get("source", ""))
            if src.count(":") != 1:
                err("bad_id", where="source", vod_id=vid, source=src)
                continue
            game_part, stage = src.split(":")
            if not gid_re.match(game_part):
                err("bad_game_id", where="source", vod_id=vid, slot=slot, source=src)
                continue
            sources_seen[src].append((vid, slot))
            g = games.get(game_part)
            if g is None:
                err("missing_game", vod_id=vid, slot=slot, source=src)
                continue
            names = sorted(_norm(n) for n in g.get("lobby_names") or [])
            sig = hashlib.sha1("|".join(names).encode("utf-8")).hexdigest()[:12]
            pair = str(f.get("fight_key", "")).split("|")[-2:]
            fight_sigs[(sig, stage, tuple(sorted(_norm(p) for p in pair)))].append((vid, slot, src))

    for (vid, group), lst in overlap_pool.items():
        for i in range(len(lst)):
            for j in range(i + 1, len(lst)):
                (sa, ra), (sb, rb) = lst[i], lst[j]
                if sa != sb and _overlap(ra, rb):
                    err("overlap_across_slots", vod_id=vid, slots=[sa, sb], a=ra, b=rb)

    for src, where in sources_seen.items():
        if len(where) > 1:
            err("duplicate_source", source=src, where=where)

    for key, where in fight_sigs.items():
        vods = {w[0] for w in where}
        if len(where) > 1 and len(vods) == 1:
            err("duplicate_source", note="cung vod, nhieu dong fight", where=where, key=str(key))
        elif len(vods) > 1:
            warn("duplicate_fight_key_needs_ingest", lobby_sig=key[0], stage=key[1],
                 pair=list(key[2]), where=where)

    for sig, vs in lobby_vods.items():
        if len(vs) > 1:
            warn("shared_lobby_needs_ingest", lobby_sig=sig, vods=sorted(vs))
    keys = list(lobby_names)
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            (va, ga), (vb, gb) = keys[i], keys[j]
            if va == vb:
                continue
            inter = len(lobby_names[keys[i]] & lobby_names[keys[j]])
            if 4 <= inter < 8:
                warn("lobby_partial_overlap", games=[f"{va}/{ga}", f"{vb}/{gb}"], shared_names=inter)

    report = {"manifest": args.manifest, "out_root": args.out_root,
              "errors": errs, "warnings": warns, "ok": not errs}
    print(f"loi: {len(errs)}, canh bao: {len(warns)}")
    for e in errs:
        print("  ERR", e)
    for w in warns:
        print("  WARN", w)
    if args.report:
        Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0 if not errs else 1


if __name__ == "__main__":
    raise SystemExit(main())
