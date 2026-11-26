"""Score collector v3 rows against label files by nearest-frame join.

For each labelled frame (file time t), take the collector row with the nearest t_file_s.
Per field with a label and a non-null accepted value: match -> covered-correct;
mismatch -> check the adjacent row (previous or next sample); if the adjacent
row matches the label, count a boundary cell; otherwise a wrong cell.
Timer is not accepted at collector level, so it is reported as raw only.
Usage: score_v3.py <collector.jsonl> <label.jsonl> [<label.jsonl> ...]
"""
import bisect, json, sys

coll_path = sys.argv[1]
rows = sorted((json.loads(l) for l in open(coll_path) if l.strip()), key=lambda r: r['t_file_s'])
times = [r['t_file_s'] for r in rows]
FIELDS = ['stage', 'gold', 'level', 'xp', 'streak']


def nearest(t):
    i = bisect.bisect_left(times, t)
    cands = [j for j in (i - 1, i) if 0 <= j < len(rows)]
    j = min(cands, key=lambda j: abs(times[j] - t))
    return j


def norm(x):
    return None if x is None else str(x)


out = {}
for lab in sys.argv[2:]:
    labels = [json.loads(l) for l in open(lab) if l.strip()]
    res = {f: dict(labelled=0, covered=0, correct=0, boundary=0, wrong=0) for f in FIELDS + ['timer_raw']}
    nohud = dict(frames=0, emissions=0)
    for lr in labels:
        t = lr['t_file_s']
        j = nearest(t)
        r = rows[j]
        if lr['hud_visible'] is False:
            nohud['frames'] += 1
            if any(v is not None for v in r['accepted'].values()):
                nohud['emissions'] += 1
            continue
        for f in FIELDS:
            want = lr.get(f)
            if want is None:
                continue
            res[f]['labelled'] += 1
            got = r['accepted'][f]
            if got is None:
                continue
            res[f]['covered'] += 1
            if norm(got) == norm(want):
                res[f]['correct'] += 1
                continue
            adj = [rows[k] for k in (j - 1, j + 1) if 0 <= k < len(rows)]
            if any(norm(a['accepted'][f]) == norm(want) for a in adj):
                res[f]['boundary'] += 1
            else:
                res[f]['wrong'] += 1
        if lr.get('timer') is not None and r['raw'].get('timer') is not None:
            res['timer_raw']['labelled'] += 1
            res['timer_raw']['covered'] += 1
            if abs(r['raw']['timer'] - lr['timer']) <= 1:
                res['timer_raw']['correct'] += 1
            else:
                res['timer_raw']['wrong'] += 1
    out[lab] = dict(fields=res, no_hud=nohud)
print(json.dumps(out, indent=1))
