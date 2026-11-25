import json, sys
d = json.load(open('data/hud-audit/match01_full.json'))
REQUIRED = ['planning', 'combat', 'result', 'round_type', 'augment', 'actions']
ok = {'read', 'derived', 'assigned', 'n/a'}
def resolved(v):
    return isinstance(v, dict) and v.get('tag') in ok and v.get('value') is not None
complete, report = 0, {}
for r in d['rounds']:
    miss = [f for f in REQUIRED if not resolved(r.get(f))]
    if not miss: complete += 1
    else: report[r['round']] = miss
print(f"rounds total {len(d['rounds'])}; complete {complete}")
for k, v in report.items(): print(f"  {k}: {', '.join(v)}")
