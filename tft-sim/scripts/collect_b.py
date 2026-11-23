"""Thu thap trang thai teacher (scripted) tren noi dung B. Dung: collect_b.py <start> <stop> <out.npz>."""
import sys, time
import numpy as np
from tft_sim.content_b import build_shuffled_content
from tft_sim.tftgoat import make_env, play, scripted_policy

start, stop, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
env = make_env(build_shuffled_content())
t0 = time.time()
flats, auxs, masks, acts, seeds, seats, steps = [], [], [], [], [], [], []
for s in range(start, stop):
    lob = play(env, s, scripted_policy, scripted_policy, collect=True)
    for flat, aux, mask, a, sd, seat, st in lob.rows:
        flats.append(flat); auxs.append(aux); masks.append(mask); acts.append(a)
        seeds.append(sd); seats.append(seat); steps.append(st)
np.savez_compressed(out,
    flat=np.stack(flats).astype(np.float32), aux=np.stack(auxs).astype(np.float32),
    mask=np.stack(masks), action=np.asarray(acts, dtype=np.int64),
    seed=np.asarray(seeds, dtype=np.int64), seat=np.asarray(seats, dtype=np.int64),
    step=np.asarray(steps, dtype=np.int64))
print("B", start, stop, "rows", len(acts), "elapsed_s", round(time.time() - t0, 1), flush=True)
