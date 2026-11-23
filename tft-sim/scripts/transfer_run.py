"""Transfer A -> B theo tieu chi trong README (viet truoc khi chay).
Bien the: flat (L/no-transfer), flat+slot, universal (scalars+opp+gods+aux, khong shop/bench/board/traits).
Epoch 10 (chon tu transfer_prep_check.json: val on dinh). Seed torch co dinh.
Metric: dong y chinh xac (exact action) tren hang >=2 hop le. Chinh: BUY_SHOP.
A->A: train A, test val A (dieu khien). A->B: train A, test B test. B->B: train B, test B test (U).
Pass: T(universal A->B) >= L(flat A->B) + 0.8 * (U - L), U = max B->B variant. Void neu U - L < 0.05.
Bootstrap theo lobby (seed) de lay CI cho T-L va U-L."""
import json, sys
from pathlib import Path
import numpy as np
import torch
from tft_sim.bc_train import train
from tft_sim.tftgoat import action_type

SA = Path(sys.argv[1]); SB = Path(sys.argv[2]); R = Path(sys.argv[3]); R.mkdir(parents=True, exist_ok=True)
EP = 10
torch.manual_seed(0); np.random.seed(0)
SCAL = slice(0, 10); OPP = slice(74, 95); GODS = slice(95, 126)

def feats(npz, variant):
    f = npz["flat"]
    if variant == "flat": return f
    if variant == "flat+slot": return np.concatenate([f, npz["aux"]], 1)
    if variant == "universal": return np.concatenate([f[:, SCAL], f[:, OPP], f[:, GODS], npz["aux"]], 1)

def load(p):
    return np.load(p)

trA, vaA = load(SA / "train.npz"), load(SA / "val.npz")
trB = load(SB / "B_train.npz"); teB = load(SB / "B_test.npz")

def evaluate(model, npz, variant):
    X = feats(npz, variant); mu, sd = model.norm
    M = np.asarray(npz["mask"]).astype(bool); y = npz["action"]
    with torch.no_grad():
        pred = torch.argmax(model(torch.from_numpy(((X - mu) / sd).astype(np.float32)),
                                  torch.from_numpy(M)), 1).numpy()
    ge2 = M.sum(1) >= 2
    names = np.array([action_type(int(a)) for a in y])
    corr = (pred == y)
    return {"ge2_mask": ge2, "names": names, "correct": corr, "seed": npz["seed"]}

def summarize_eval(ev):
    ge2 = ev["ge2_mask"]; names = ev["names"]; corr = ev["correct"]
    out = {"overall_ge2": round(float(corr[ge2].mean()), 4)}
    per = {}
    for t in np.unique(names[ge2]):
        sel = ge2 & (names == t)
        per[t] = {"n": int(sel.sum()), "agree": round(float(corr[sel].mean()), 4)}
    out["per_type_ge2"] = per
    return out

def boot_gap(ev_x, ev_y, typ, n=2000, seed=0):
    """Chenh lech agreement (x - y) tren BUY_SHOP ge2, bootstrap theo lobby."""
    rng = np.random.default_rng(seed)
    sel_x = ev_x["ge2_mask"] & (ev_x["names"] == typ); sel_y = ev_y["ge2_mask"] & (ev_y["names"] == typ)
    lob_x = ev_x["seed"][sel_x]; c_x = ev_x["correct"][sel_x]
    lob_y = ev_y["seed"][sel_y]; c_y = ev_y["correct"][sel_y]
    ux = np.unique(lob_x); uy = np.unique(lob_y); common = np.intersect1d(ux, uy)
    gx = {u: c_x[lob_x == u] for u in common}; gy = {u: c_y[lob_y == u] for u in common}
    diffs = []
    for _ in range(n):
        pick = rng.choice(common, size=len(common), replace=True)
        a = np.concatenate([gx[u] for u in pick]); b = np.concatenate([gy[u] for u in pick])
        diffs.append(a.mean() - b.mean())
    return [round(float(np.percentile(diffs, 2.5)), 4), round(float(np.percentile(diffs, 97.5)), 4)]

out = {"epochs": EP, "variants": {}, "controls_A_to_A_vs_A_to_B": {}, "bootstrap_on_test_lobbies": {}}
models = {}
for v in ["flat", "flat+slot", "universal"]:
    models[("A", v)] = train(feats(trA, v), trA["mask"], trA["action"], epochs=EP)
    models[("B", v)] = train(feats(trB, v), trB["mask"], trB["action"], epochs=EP)
    print("trained", v, flush=True)

res = {}
for v in ["flat", "flat+slot", "universal"]:
    aa = summarize_eval(evaluate(models[("A", v)], vaA, v))
    ab = summarize_eval(evaluate(models[("A", v)], teB, v))
    bb = summarize_eval(evaluate(models[("B", v)], teB, v))
    res[v] = {"A_to_A_val": aa, "A_to_B_test": ab, "B_to_B_test": bb}
    print(v, "BUY_SHOP A->A", aa["per_type_ge2"].get("BUY_SHOP"), "A->B", ab["per_type_ge2"].get("BUY_SHOP"),
          "B->B", bb["per_type_ge2"].get("BUY_SHOP"), flush=True)
out["variants"] = res

# BUY_SHOP main numbers
def bs(v, key):
    return res[v][key]["per_type_ge2"]["BUY_SHOP"]["agree"]
L = bs("flat", "A_to_B_test")
U_var = max(["flat", "flat+slot", "universal"], key=lambda v: bs(v, "B_to_B_test"))
U = bs(U_var, "B_to_B_test")
T = bs("universal", "A_to_B_test")
gap = U - L
passed = T >= L + 0.8 * gap
void = gap < 0.05
out["main"] = {"L_flat_A_to_B": L, "U_best_B_to_B": U, "U_variant": U_var, "T_universal_A_to_B": T,
               "gap_U_minus_L": round(gap, 4), "threshold_T": round(L + 0.8 * gap, 4),
               "void": bool(void), "pass": bool(passed) and not void}

# bootstrap CIs over test lobbies (BUY_SHOP ge2)
ev_L = evaluate(models[("A", "flat")], teB, "flat")
ev_U = evaluate(models[("B", U_var)], teB, U_var)
ev_T = evaluate(models[("A", "universal")], teB, "universal")
out["bootstrap_on_test_lobbies"] = {"T_minus_L": boot_gap(ev_T, ev_L, "BUY_SHOP"),
                                    "U_minus_L": boot_gap(ev_U, ev_L, "BUY_SHOP")}

# controls: other types A->A (val) vs A->B (test) for the flat model
for t in res["flat"]["A_to_A_val"]["per_type_ge2"]:
    a = res["flat"]["A_to_A_val"]["per_type_ge2"].get(t); b = res["flat"]["A_to_B_test"]["per_type_ge2"].get(t)
    if a and b:
        out["controls_A_to_A_vs_A_to_B"][t] = {"A_to_A": a["agree"], "A_to_B": b["agree"],
                                               "shift_pts": round((b["agree"] - a["agree"]) * 100, 1)}
(R / "transfer_results.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(out["main"], ensure_ascii=False), flush=True)
print("done", flush=True)
