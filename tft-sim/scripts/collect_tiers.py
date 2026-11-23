"""Thu thap lai (co tier augment): collect_tiers.py <A|B> <start> <stop> <out.npz>.
Giu nguyen flat (126), aux (20); them truong tiers (3) = tier 3 augment dang duoc chao."""
import sys, time
import numpy as np
from tft_sim.tftgoat import default_content, make_env, play, scripted_policy
from tft_sim.content_b import build_shuffled_content

which, start, stop, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
content = default_content() if which == "A" else build_shuffled_content()
env = make_env(content)
t0 = time.time()
flats, auxs, masks, acts, seeds, seats, steps, tiers = [], [], [], [], [], [], [], []
for s in range(start, stop):
    lob = play(env, s, scripted_policy, scripted_policy, collect=True)
    assert len(lob.tiers) == len(lob.rows)
    for (flat, aux, mask, a, sd, seat, st), tr in zip(lob.rows, lob.tiers):
        flats.append(flat); auxs.append(aux); masks.append(mask); acts.append(a)
        seeds.append(sd); seats.append(seat); steps.append(st); tiers.append(tr)
np.savez_compressed(out,
    flat=np.stack(flats).astype(np.float32), aux=np.stack(auxs).astype(np.float32),
    mask=np.stack(masks), action=np.asarray(acts, dtype=np.int64),
    seed=np.asarray(seeds, dtype=np.int64), seat=np.asarray(seats, dtype=np.int64),
    step=np.asarray(steps, dtype=np.int64), tiers=np.stack(tiers).astype(np.float32))
print(which, start, stop, "rows", len(acts), "elapsed_s", round(time.time() - t0, 1), flush=True)
