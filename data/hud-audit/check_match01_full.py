import json, sys
d = json.load(open('data/hud-audit/match01_full.json'))
rounds = d['rounds']
FIELDS = ['hp','hp_changed_in_round','panels','roster_candidates','augment','board_units','bench_units','stars','items','shop_purchases','round_type','opponent']
unresolved = {}
complete = 0
for r in rounds:
    missing = []
    for f in FIELDS:
        v = r.get(f)
        if v is None:
            missing.append(f); continue
        tag = v.get('tag') if isinstance(v, dict) else None
        if tag == 'unresolved' or (isinstance(v, dict) and v.get('value') is None and tag != 'read'):
            missing.append(f)
    if not missing: complete += 1
    if missing: unresolved[r['round']] = missing
print(f"rounds total: {len(rounds)}; rounds with every field resolved: {complete}")
print("unresolved per round:")
for k, v in unresolved.items(): print(f"  {k}: {', '.join(v)}")
