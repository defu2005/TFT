import json, sys
d = json.load(open('data/hud-audit/match01_full.json'))
REQUIRED = ['planning', 'combat', 'result', 'round_type', 'augment', 'actions']
FULL = ['board_units', 'hexes', 'bench_units', 'stars', 'items', 'opponent', 'opponent_board']
ok = {'read', 'derived', 'assigned', 'n/a'}
def resolved(v):
    return isinstance(v, dict) and v.get('tag') in ok and v.get('value') is not None
complete, report = 0, {}
full_counts = {f: 0 for f in FULL}
for r in d['rounds']:
    miss = [f for f in REQUIRED if not resolved(r.get(f))]
    if not miss: complete += 1
    else: report[r['round']] = miss
    for f in FULL:
        if resolved(r.get(f)): full_counts[f] += 1
n = len(d['rounds'])
print(f"REQUIRED rounds complete: {complete} of {n}")
for k, v in report.items(): print(f"  {k}: {', '.join(v)}")
print("FULL fields resolved per round (of %d):" % n)
for f in FULL: print(f"  {f}: {full_counts[f]}")
pl = d.get('placements')
print("placements:", 'missing' if not pl else pl)
print("final_comps:", 'missing' if not d.get('final_comps') else 'present')
br = d.get('blind_reread')
print("blind_reread:", 'missing' if not br else br.get('summary', 'present'))

# closed = resolved, or unresolved with attempt and reason recorded
BAD = ['not yet run', 'not read', 'not performed', 'no solver run', 'not done', 'not run', 'not attempted', 'not rerun', 'not calibrated']
def closed(v):
    if not isinstance(v, dict): return False
    if resolved(v): return True
    a = ' '.join(str(v.get(x) or '') for x in ('attempt','reason','note')).lower()
    if any(b in a for b in BAD): return False
    return v.get('tag') == 'unresolved' and bool(a) and bool(v.get('reason') or v.get('note'))
open_counts = {f: 0 for f in FULL + REQUIRED}
for r in d['rounds']:
    for f in FULL + REQUIRED:
        if not closed(r.get(f)): open_counts[f] += 1
print("OPEN per field (not closed):")
for f, c in open_counts.items(): print(f"  {f}: {c}")
print("OPEN PAIRS:")
for r in d['rounds']:
    for f in FULL + REQUIRED:
        if not closed(r.get(f)): print(f"  {r['round']} {f}")
bench_rounds=[r for r in d['rounds'] if isinstance(r.get('opponent_board'),dict) and r['opponent_board'].get('tag')!='n/a']
bench_open=[r['round'] for r in bench_rounds if not closed(r['opponent_board'].get('bench'))]
open_counts['opponent_bench']=len(bench_open)
print(f"opponent_bench: {len(bench_rounds)-len(bench_open)} closed of {len(bench_rounds)} non-n/a rounds; open {len(bench_open)}")
total_open = sum(open_counts.values())
print("TOTAL OPEN:", total_open)

import os
if os.path.exists('data/hud-audit/blind_reread_rates.json'):
    b=json.load(open('data/hud-audit/blind_reread_rates.json'))
    print("BLIND RE-READ (script OCR, 10 rounds):")
    print("  protocol:", b['protocol'])
    for f,v in b['rates'].items(): print(f"  {f}: {v['matched']}/{v['of']} = {v['rate']}")

print("RESOLVED (tag read/derived/assigned/n-a with value), of 38 rounds:")
for f in FULL + REQUIRED:
    c = sum(1 for r in d['rounds'] if resolved(r.get(f)))
    print(f"  {f}: {c}")
