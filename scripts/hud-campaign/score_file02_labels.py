"""Score collector output (file 02) against the held-out frame labels by timestamp.

For a labelled frame at file time t, the collector value is the last settled record
for the same field at or before t, if it is no older than WINDOW seconds. A label with a value and no fresh
record is 'not covered'. A fresh record that disagrees is 'wrong'. A label with
hud_visible false and any fresh record is a wrong emission. Two label sets are
scored separately: heldout1 (used once for reader v1 before the XP slash rule)
and heldout2 (fresh set). Counts only; no per-frame text written.
"""
import json, sys
COLLECT = 'data/hud-audit/collect/file02_collect_v1.jsonl'
WINDOW = 60.0  # state semantics: last settled value before t, stale after WINDOW s
FIELDS = ['stage', 'timer', 'gold', 'level', 'xp', 'streak']
recs = [json.loads(l) for l in open(COLLECT) if l.strip()]
by_field = {f: [] for f in FIELDS}
for r in recs:
    v = r['value']
    if isinstance(v, list):
        v = f"{v[0]}/{v[1]}"
    by_field[r['field']].append((r['t_file_s'], v))

def fresh(field, t):
    prior = [(tt, v) for (tt, v) in by_field[field] if tt <= t]
    if not prior:
        return []
    tt, v = max(prior, key=lambda x: x[0])
    return [v] if t - tt <= WINDOW else []

report = {}
for name, lab in [('heldout1', 'data/hud-audit/heldout_labels_file02.jsonl'),
                  ('heldout2', 'data/hud-audit/heldout2_labels_file02.jsonl')]:
    rows = [json.loads(l) for l in open(lab)]
    res = {f: dict(labelled=0, covered=0, wrong=0) for f in FIELDS}
    nohud = dict(frames=0, wrong_emissions=0)
    for row in rows:
        t = row['t_file_s']
        if row['hud_visible'] is False:
            nohud['frames'] += 1
            if any(fresh(f, t) for f in FIELDS):
                nohud['wrong_emissions'] += 1
            continue
        for f in FIELDS:
            lv = row.get(f)
            if lv is None:
                continue
            res[f]['labelled'] += 1
            got = fresh(f, t)
            if not got:
                continue
            res[f]['covered'] += 1
            if str(got[-1]) != str(lv):
                res[f]['wrong'] += 1
    report[name] = dict(fields=res, no_hud=nohud)
print(json.dumps(report, indent=1))
json.dump(report, open('data/hud-audit/score_file02_collect_v1.json', 'w'), indent=1)
