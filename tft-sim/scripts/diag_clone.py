"""Chan doan clone BC va do do nhay cua metric (fresh seeds 2000-2199, khong dung 1000-1199).
(1) val per-type tren hang >=2 hop le, ma tran nham PASS.
(2) ma tran nham teacher x clone tren trang thai clone tham, do dai pha lap ke hoach.
(3) thang do: scripted voi eps ngau nhien (0.1/0.3/0.6) va ablation bo mua shop, so voi scripted goc."""
import json, sys, random
from collections import Counter
from pathlib import Path
import numpy as np
import torch
from tft_sim.tftgoat import (default_content, make_env, seat_groups, scripted_policy, teacher_action,
                             action_type, play, summarize, MAX_STEPS)
from tft_sim.bc_train import features, MaskedMLP, policy_from

S = Path(sys.argv[1]); R = Path(sys.argv[2]); R.mkdir(parents=True, exist_ok=True)
SEEDS = range(2000, 2200)
BUY = range(3, 8)  # BUY_SHOP_START..+4

def load(v):
    ck = torch.load(R.parent / "bc" / f"bc_{v}.pt", weights_only=False)
    m = MaskedMLP(ck["state"]["net.0.weight"].shape[1] if "net.0.weight" in ck["state"]
                  else next(iter(ck["state"].values())).shape[1])
    m.load_state_dict(ck["state"]); m.norm = ck["norm"]; m.eval()
    return m

out = {"seeds": "2000-2199", "val": {}, "clone": {}, "ladder": {}}

# (1) val per-type on rows >=2 legal
va = np.load(S / "val.npz")
M = np.asarray(va["mask"]).astype(bool); y = va["action"]; multi = M.sum(1) >= 2
names = np.array([action_type(int(a)) for a in y])
for v in ["flat", "flat+slot"]:
    m = load(v); X = features(va, v); mu, sd = m.norm
    with torch.no_grad():
        pred = torch.argmax(m(torch.from_numpy(((X - mu) / sd).astype(np.float32)),
                              torch.from_numpy(M)), 1).numpy()
    pt = {t: {"n": int((multi & (names == t)).sum()),
              "agree": round(float((pred[multi & (names == t)] == y[multi & (names == t)]).mean()), 4)}
          for t in np.unique(names[multi])}
    conf = Counter(action_type(int(p)) for p in pred[multi & (names == "PASS")])
    out["val"][v] = {"per_type_ge2": pt, "teacher_PASS_rows_predicted_as": dict(conf.most_common())}
    print("val", v, flush=True)

# (2) clone on fresh seeds: confusion teacher x clone, phase lengths, illegal
def diag_run(env, seed, pol):
    groups = seat_groups(seed)
    rngs = {a: random.Random(seed * 100 + i) for i, a in enumerate(groups)}
    obs, infos = env.reset(seed=seed)
    conf = Counter(); phases = Counter(); illegal = 0; step = 0
    while env.agents and step < MAX_STEPS:
        actions = {}
        for a in list(env.agents):
            g = groups[a]; mask = infos[a]["action_mask"]
            act = pol(env, a, obs[a], mask, rngs[a])
            if not mask[act]: illegal += 1
            if g == "A" and int(mask.sum()) >= 2:
                conf[(action_type(teacher_action(env, a)), action_type(act))] += 1
            actions[a] = act
        pre = env._phase_steps
        obs, rewards, terms, truncs, infos = env.step(actions)
        step += 1
        if env._phase_steps == 0 and pre > 0:
            phases[pre + 1] += 1
    return conf, phases, illegal, step

env = make_env(default_content())
clone_pol = policy_from(load("flat+slot"), "flat+slot")
conf_all = Counter(); phase_all = Counter(); steps_c = []; ill_c = 0
for s in SEEDS:
    c, p, il, st = diag_run(env, s, clone_pol)
    conf_all.update(c); phase_all.update(p); ill_c += il; steps_c.append(st)
per_t = {}
for (t, c_), n in conf_all.items():
    per_t.setdefault(t, Counter())[c_] += n
out["clone"] = {
    "illegal": ill_c,
    "steps_per_game_mean": round(float(np.mean(steps_c)), 1),
    "phase_len_hist_top": dict(sorted(phase_all.items())[-6:]),
    "phases_total": int(sum(phase_all.values())),
    "phases_len_50_cap_hits": int(phase_all.get(50, 0)),
    "confusion_teacher_to_clone": {t: dict(c.most_common()) for t, c in per_t.items()},
}
print("clone diag done", flush=True)

# (3) ladder and ablation, paired seeds, against scripted (group A = degraded)
def eps_policy(eps):
    def pol(env, agent, obs, mask, rng):
        if rng.random() < eps:
            return int(rng.choice(list(np.flatnonzero(mask))))
        return scripted_policy(env, agent, obs, mask, rng)
    return pol

def nobuy_policy(env, agent, obs, mask, rng):
    act = scripted_policy(env, agent, obs, mask, rng)
    return 0 if act in BUY else act  # 0 = PASS

conds = {"eps_0.1": eps_policy(0.1), "eps_0.3": eps_policy(0.3), "eps_0.6": eps_policy(0.6),
         "scripted_no_buy": nobuy_policy, "clone_flat+slot": clone_pol}
for name, pol in conds.items():
    ev = [play(env, s, pol, scripted_policy) for s in SEEDS]
    out["ladder"][name] = summarize(ev)
    print("ladder", name, out["ladder"][name]["diff_A_minus_B"], out["ladder"][name]["ci95_diff"], flush=True)

(R / "clone_diag.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("done", flush=True)
