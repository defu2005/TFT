import json
d = json.load(open('data/hud-audit/match01_full.json'))
FIELDS = ['hp','hp_changed_in_round','panels','roster_candidates','augment','board_units','bench_units','stars','items','shop_purchases','round_type','opponent']
ok_tags = {'read','derived','assigned'}
complete = 0; missing_all = {}
for r in d['rounds']:
    miss = []
    for f in FIELDS:
        v = r.get(f)
        if not isinstance(v, dict): miss.append(f); continue
        if v.get('tag') not in ok_tags or v.get('value') is None: miss.append(f)
    if miss: missing_all[r['round']] = miss
    else: complete += 1
print(f"rounds total: {len(d['rounds'])}; fully resolved: {complete}")
for k, v in missing_all.items(): print(f"  {k}: {', '.join(v)}")
