"""Per-round aggregation of collector output (schema 5), no carry-forward.

A round = maximal run of consecutive rows with the same accepted stage value
(stage is the round key). For each field, the record is the last accepted
non-null value inside that run; a field with no accepted value in the run is null.
Usage: python3 round_aggregate.py <collect.jsonl>
"""
import json, sys

FIELDS = ["gold", "level", "xp", "streak", "timer"]

def rounds(rows):
    out = []
    cur = None
    for r in rows:
        if r.get("hud_visible") is False:
            continue
        acc = r["accepted"]
        st = acc.get("stage")
        if st is None:
            continue
        if cur is None or cur["stage"] != st:
            cur = {"stage": st, "t_start": r["t_file_s"], "t_end": r["t_file_s"],
                   "fields": {f: None for f in FIELDS}, "fields_t": {f: None for f in FIELDS}}
            out.append(cur)
        cur["t_end"] = r["t_file_s"]
        for f in FIELDS:
            if acc.get(f) is not None:
                cur["fields"][f] = acc[f]
                cur["fields_t"][f] = r["t_file_s"]
    return out

if __name__ == "__main__":
    rows = [json.loads(l) for l in open(sys.argv[1])]
    rs = rounds(rows)
    print(f"rounds(by stage run): {len(rs)}")
    for x in rs:
        vals = " ".join(f"{f}={x['fields'][f]}" for f in FIELDS)
        print(f"stage={x['stage']:>3} t={x['t_start']:.0f}-{x['t_end']:.0f} {vals}")
