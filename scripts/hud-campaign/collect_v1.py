"""Collect HUD fields from a VOD segment with reader v1.

Samples frames with ffmpeg at --fps, runs hud_reader_v1.read on each, and emits a
field only after K consecutive equal valid reads (data-rules section 3). Values
that never settle stay null. Records carry src, raw read, schemaVersion and the
commit that produced them (data-rules section 2).
"""
import argparse, io, json, os, subprocess, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hud_reader_v1 as reader

SCHEMA_VERSION = 1
FIELDS = ['stage', 'timer', 'gold', 'level', 'xp', 'streak']


def git_commit():
    try:
        return subprocess.run(['git', '-C', HERE, 'rev-parse', '--short', 'HEAD'],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return 'unknown'


def frames(video, start, duration, fps):
    """Stream PNG frames from ffmpeg one at a time (no whole-segment buffering)."""
    cmd = ['ffmpeg', '-v', 'error', '-ss', str(start), '-t', str(duration), '-i', video,
           '-vf', f'fps={fps},scale=1280:720', '-f', 'image2pipe', '-vcodec', 'png', '-']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    try:
        stream = proc.stdout
        while True:
            sig = stream.read(8)
            if len(sig) < 8:
                break
            chunks = [sig]
            while True:
                ln = stream.read(4)
                if len(ln) < 4:
                    return
                typ = stream.read(4)
                body = stream.read(int.from_bytes(ln, 'big') + 4)
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
    history = {f: [] for f in FIELDS}
    settled = {f: None for f in FIELDS}
    n = 0
    skipped_layout = 0
    with open(a.out, 'w') as out:
        for k_idx, im in enumerate(frames(a.video, a.start, a.duration, a.fps)):
            t = a.start + k_idx / a.fps
            n += 1
            if im.size != (1280, 720):      # layout gate: only the 1280x720 HUD layout
                skipped_layout += 1
                continue
            res = reader.read(im)
            for f in FIELDS:
                v = res[f]
                history[f].append(v)
                h = history[f][-a.k:]
                if len(h) == a.k and h[0] is not None and all(x == h[0] for x in h):
                    if settled[f] != h[0]:
                        settled[f] = h[0]
                        out.write(json.dumps({
                            'schemaVersion': SCHEMA_VERSION, 't_file_s': round(t, 1),
                            'field': f, 'value': h[0], 'src': 'ocr',
                            'k': a.k, 'reader_commit': commit,
                            'source': os.path.basename(a.video)}, ensure_ascii=False) + '\n')
    print(json.dumps({'frames': n, 'skipped_layout': skipped_layout, 'out': a.out}))


if __name__ == '__main__':
    main()
