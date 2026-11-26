"""Collector v3: one row per sampled frame, with raw and accepted values per field.

Accepted value = the newest read when the last K reads are equal and non-null;
otherwise null. A change in the newest read drops the accepted value to null at
once. No timeout. Timer is never accepted at collector level (raw only).
"""
import argparse, io, json, os, subprocess, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hud_reader_v1 as reader
# Denominator gate is learned per match in this collector, so the reader accepts any two-digit denominator.
reader.XP_DENOMS = set(range(2, 100))
LEARN_N = 3   # reads of a (level, denominator) pair before it is locked for this match

SCHEMA_VERSION = 5
FIELDS = ['stage', 'timer', 'gold', 'level', 'xp', 'streak']
ACCEPT_FIELDS = [f for f in FIELDS if f != 'timer']


def git_commit():
    try:
        return subprocess.run(['git', '-C', HERE, 'rev-parse', '--short', 'HEAD'],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return 'unknown'


def frames(video, start, duration, fps):
    cmd = ['ffmpeg', '-v', 'error', '-ss', str(start), '-t', str(duration), '-i', video,
           '-vf', f'fps={fps},scale=1280:720', '-f', 'image2pipe', '-vcodec', 'png', '-']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    try:
        s = proc.stdout
        while True:
            sig = s.read(8)
            if len(sig) < 8:
                break
            chunks = [sig]
            while True:
                ln = s.read(4)
                if len(ln) < 4:
                    return
                typ = s.read(4)
                body = s.read(int.from_bytes(ln, 'big') + 4)
                chunks.append(ln + typ + body)
                if typ == b'IEND':
                    break
            yield Image.open(io.BytesIO(b''.join(chunks))).convert('RGB')
    finally:
        proc.stdout.close()
        proc.wait()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('video')
    ap.add_argument('--start', type=float, required=True)
    ap.add_argument('--duration', type=float, required=True)
    ap.add_argument('--fps', type=float, default=1.0)
    ap.add_argument('--k', type=int, default=3)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    commit = git_commit()
    hist = {f: [] for f in FIELDS}
    pair_count = {}      # (level, denominator) -> count of agreeing reads
    locked = {}          # level -> denominator, learned from this match only
    n = 0
    with open(a.out, 'w') as out:
        for i, im in enumerate(frames(a.video, a.start, a.duration, a.fps)):
            t = round(a.start + i / a.fps, 2)
            n += 1
            if im.size != (1280, 720):
                continue
            res = reader.read(im)
            row = {'schemaVersion': SCHEMA_VERSION, 't_file_s': t, 'reader_commit': commit,
                   'k': a.k, 'raw': {}, 'accepted': {}}
            for f in FIELDS:
                v = res[f]
                if isinstance(v, list):
                    v = f"{v[0]}/{v[1]}"
                hist[f].append(v)
                row['raw'][f] = v
                last = hist[f][-a.k:]
                ok = len(last) == a.k and last[0] is not None and all(x == last[0] for x in last)
                row['accepted'][f] = last[0] if (ok and f in ACCEPT_FIELDS) else None
            # XP: accept only when the denominator is the one learned for this level in this match
            x = row['accepted'].get('xp'); lv = row['accepted'].get('level')
            if x and lv is None:
                row['accepted']['xp'] = None   # no level, no denominator check: reject
            if x and lv is not None:
                y = int(x.split('/')[1])
                pair_count[(lv, y)] = pair_count.get((lv, y), 0) + 1
                if pair_count[(lv, y)] >= LEARN_N and lv not in locked:
                    locked[lv] = y
                if locked.get(lv) != y:
                    row['accepted']['xp'] = None
            out.write(json.dumps(row, ensure_ascii=False) + '\n')
    print(json.dumps({'frames': n, 'out': a.out}))


if __name__ == '__main__':
    main()
