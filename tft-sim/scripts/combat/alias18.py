"""Do anh huong cua alias item Set 18 tren cap sim cung vong (sim, khong phai tran that).
  collect LO HI OUT.jsonl     : choi lobby Set 18 (noi dung clean, bo TFT_Item), ghi cap cung vong (label sim).
  score IN.jsonl OUT.json off|on : p_a voi ability generic, 20 seed; 'on' dang ky alias truoc khi do.
Ledger: dung seed rieng, xem docs/handoff/cloud-agents.md.
"""
import json, random, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import fight as F  # noqa: E402
from tft_goat.engine.resolver import EngineResolver  # noqa: E402
from tft_goat.env.tft_env import TftEnv  # noqa: E402
from tft_sim.params import make_aug_rule  # noqa: E402
from tft_sim.real_content import build_real_set18_clean  # noqa: E402

CONTENT = build_real_set18_clean()


def _units(board):
    out = []
    for u in board:
        apis = list(getattr(u, "item_apis", ()) or ())
        out.append({"api": u.champion_api, "star": int(u.star), "items": apis, "pos": None})
    return out


def _side(p):
    return {"level": int(p.level), "augments": list(p.chosen_augments), "units": _units(p.board)}


def collect(lo, hi, out):
    env = TftEnv(set_content=CONTENT, resolver=EngineResolver())
    v4 = make_aug_rule()
    n = 0; da_units = 0
    with open(out, "w", encoding="utf-8") as f:
        for seed in range(lo, hi):
            obs, infos = env.reset(seed=seed)
            rngs = {a: random.Random(seed * 100 + i) for i, a in enumerate(sorted(env.agents))}
            snaps = {}; last = None; step = 0
            while env.agents and step < 20000:
                st = env._state; r = st.round_index
                if r != last and r >= 2:
                    last = r
                    snaps[r] = {a: _side(st.players[a]) for a in env.agents if st.players[a].board}
                actions = {a: v4(env, a, obs[a], infos[a]["action_mask"], rngs[a]) for a in list(env.agents)}
                obs, _, _, _, infos = env.step(actions); step += 1
            for rr, sides in snaps.items():
                keys = sorted(sides)
                for i in range(len(keys)):
                    for j in range(i + 1, len(keys)):
                        a, b = sides[keys[i]], sides[keys[j]]
                        for side in (a, b):
                            da_units += sum(1 for u in side["units"] if any(x.startswith("DA_") for x in u["items"]))
                        rec = {"schema": "fight-v1", "set": 18, "label": "sim", "source": f"same {seed} {rr}",
                               "a": a, "b": b, "result": {"winner": None}}
                        f.write(json.dumps(rec, ensure_ascii=False) + "\n"); n += 1
    print("collected", n, "units_with_DA_items", da_units, flush=True)


def score(inp, out, mode):
    if mode == "on":
        import tft_sim.item_alias as A
        content, amap = A.build_set18_aliased()
        print("aliases registered", len(amap), flush=True)
    else:
        content = CONTENT
    F.set_content(18, content)
    res = []
    for r in F.load_jsonl(inp):
        res.append({"source": r["source"], "p": F.predict_win(r, 20, "generic", True, 0)["p_a"]})
    Path(out).write_text(json.dumps(res), encoding="utf-8")
    print("scored", len(res), flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "collect":
        collect(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    else:
        score(sys.argv[2], sys.argv[3], sys.argv[4])
