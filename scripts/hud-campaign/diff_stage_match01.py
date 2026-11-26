"""Diff collector stage records against the 38 rounds in match01_full.json.

Stage is the only field in match01_full that maps one-to-one to a collector
field. For each round, check whether the collector settled that stage, and
whether it settled any stage that is not a round of this match. Reports coverage
and wrong stage emissions. HP, gold, level, XP and streak are not compared here.
"""
import json, sys

COLLECT = sys.argv[1] if len(sys.argv) > 1 else 'data/hud-audit/collect/file01_collect_v1.jsonl'
MATCH = 'data/hud-audit/match01_full.json'

match = json.load(open(MATCH))
rounds = [r['round'] for r in match['rounds']]
round_t = {r['round']: r['t_planning_s'] for r in match['rounds']}
recs = [json.loads(l) for l in open(COLLECT) if l.strip()]
stage_recs = [r for r in recs if r['field'] == 'stage']

seen = {}
for r in stage_recs:
    seen.setdefault(r['value'], r['t_file_s'] + 210)  # VOD time = file time + 210
missing = [s for s in rounds if s not in seen]
extra = [s for s in seen if s not in rounds]
out = {
    'rounds_in_match': len(rounds),
    'rounds_settled_by_collector': len(rounds) - len(missing),
    'stages_settled_not_in_match': extra,
    'rounds_missing': missing,
    'stage_records': len(stage_recs),
    'note': 'stage only; file time + 210 s gives VOD time for comparison',
}
print(json.dumps(out, ensure_ascii=False, indent=1))
