"""Thu thap du lieu BC tu lobby toan scripted. Dai seed (README): train 200-499, val 800-849, test 1000-1199."""
import sys, time
import numpy as np
from tft_goat.data.sample import build_sample_content
from tft_sim.tftgoat import make_env, play, scripted_policy

split, start, stop, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
env = make_env(build_sample_content())
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
print(split, "rows", len(acts), "lobbies", stop - start, "elapsed_s", round(time.time() - t0, 1))
