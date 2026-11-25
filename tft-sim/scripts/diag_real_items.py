from tft_sim.real_content import load_raw_snapshot
"""Chan doan EQUIP tren noi dung that (CDragon latest, nhan 'CDragon latest (18.7), Set 17 block').
Dem: item co composition rong (thanh phan co so), bao nhieu xuat hien trong mot cong thuc nao, va
bao nhieu EQUIP khong tieu thu. In so chieu block quan sat de kiem tra cot universal."""
import json, collections, sys
from pathlib import Path
from tft_goat.data.content import build_set_content
from tft_goat.env.tft_env import TftEnv
from tft_goat.agent.scripted import scripted_action
from tft_goat.env.actions import EQUIP
from tft_sim.tftgoat import make_env

raw = load_raw_snapshot()
content = build_set_content(raw, "latest-2026-11-23-set17block")
items = content.items
base = [k for k, v in items.items() if not tuple(v.composition)]
recipes = [k for k, v in items.items() if tuple(v.composition)]
in_recipe = set()
for k in recipes:
    for c in items[k].composition: in_recipe.add(c)
print("items", len(items), "base (empty composition)", len(base), "craftable", len(recipes))
print("base in any recipe", len([b for b in base if b in in_recipe]), "base in no recipe", len([b for b in base if b not in in_recipe]))
print("champions", len(content.champions), "traits", len(content.traits))
env = make_env(content)
obs, infos = env.reset(seed=1)
a = env.agents[0]
print("obs block sizes", {k: len(v) if hasattr(v, '__len__') else v for k, v in obs[a].items()})
