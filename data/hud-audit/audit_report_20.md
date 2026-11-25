# Blind audit, interim (20 of 100 frames labelled)

Labels: audit_labels.jsonl (eye reads, written before extractor rows were loaded).
Scorer: score.py (right / null / wrong reported separately).
Source: full match-01 video /home/user/campaign/01-boxbox-2924500482-00210.mp4.

| Field | Right | Right-null | Null (label present) | Wrong | Notes |
|---|---|---|---|---|---|
| stage | 19 | 0 | 1 | 0 | |
| timer | 10 | 0 | 5 | 3 | wrong: 375.7 (17 vs 1), 398.4 (19 vs 20), 434.6 (9 vs 0) |
| level | 7 | 7 | 4 | 0 | false positive 356.7 (level 7 on absent bar) |
| gold | 10 | 8 | 1 | 0 | |
| xp | 5 | 8 | 6 | 0 | 375.7 raw "02" dropped (split rule); 430.4/431.5 correct after normalisation |
| streak | 10 | 8 | 1 | 0 | |
| shop slot | 31 | 17 | 1 | 1 | wrong: m01 shows Rakan at 431.5 slot 3, eye shows empty (gold 0 to 2) |

Unresolved: 415.5 partial overlay (extractor returns level 3 / gold 0 / 0-6 / streak 0; label null because of overlay; not scored).
Unverified labels: 315.1 timer 12, 480.1 timer 7 (not zoomed).
Known issues confirmed: hudDetected gate and level null while bar visible (368.0, 375.7, 494.3); level junk 7 on absent bar; timer misread on 375.7/398.4/434.6; XP level-8 denominator still 80 (should be 68).
