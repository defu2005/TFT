# Freeze before the single file 03 run

- Pipeline: scripts/hud-campaign/collect_v4.py (schema 5, XP gate fixed) + hud_reader_v1.py + score_v3.py.
- k = 3 (frozen). k=2 is not used for the final run.
- Labels: data/hud-audit/test3_labels_file03.jsonl (60 frames, seed 20261129), labelled before any file 03 run.
- Dev sets used for design: file 01 labels and file 02 held-out 1, held-out 2, validation 3.
- Criterion: zero wrong accepted cells, per stage (round) and overall, plus coverage and 95% upper bounds (about 3/n).
- Timer is not accepted at collector level; reported as raw only.
- Not run yet: the file 03 run follows this commit.
