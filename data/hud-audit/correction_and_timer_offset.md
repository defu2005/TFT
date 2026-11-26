# Correction and timer offset check

## Correction
Commit f54939a said a stage read "agreed twice on a wrong value". That is not supported
by the mismatch list: each listed mismatch settled 9 to 57 s before the labelled frame,
so it is stale state, not a misread. Treat the earlier mismatch explanation as unverified.

## Timer label minus collector value (v2, file 02, within 5 s)
Counts: {-18:1, -5:3, -4:2, -3:5, -2:4, -1:32, +1:7, +11:1, +12:1, +26:1}.
Most cells are -1, consistent with alignment, but about 15 cells are off by 3 or more
and some by 11 to 26 seconds. Alignment alone does not explain the whole error.
Timer is not accepted at collector level; report it at reader level only.
