"""Mot mo hinh group-dropout (model-plan muc 10.10). Moi dong huan luyen duoc gan MOT dieu kien trong {a, c, full}
bang RNG co dinh; dau vao = 185 dim da mask theo dieu kien (mask_exp.fmask_for) + 4 bit hien dien
(HUD, HP, BB, OTHER) de so 0 that khong bi nham voi cot bi an.
Nguon duy nhat cho dau vao: dropout_input(). Dung chung khi huan luyen, kiem tra va khi choi."""
import sys
from pathlib import Path
import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).parent))
from mask_exp import fmask_for  # noqa: E402

CONDS = ["a", "c", "full"]
N_IN = 189
PRESENCE = {"a": [1, 0, 0, 0], "c": [1, 1, 1, 0], "full": [1, 1, 1, 1]}  # HUD, HP, BB, OTHER
_FM = {c: fmask_for(c) for c in CONDS}


def row_conditions(n: int, seed: int = 0) -> np.ndarray:
    """Gan dieu kien cho tung dong, RNG co dinh: default_rng([seed, 7])."""
    return np.random.default_rng([seed, 7]).choice(np.array(CONDS), size=n)


def dropout_input(X185, conds) -> np.ndarray:
    """X185: (n,185). conds: chuoi dieu kien cho ca batch, hoac mang (n,) moi dong mot dieu kien."""
    X = np.asarray(X185, np.float32)
    n = len(X)
    cs = np.full(n, conds) if isinstance(conds, str) else np.asarray(conds)
    out = np.zeros((n, N_IN), np.float32)
    for c in CONDS:
        idx = cs == c
        if idx.any():
            out[idx, :185] = X[idx] * _FM[c]
            out[idx, 185:] = PRESENCE[c]
    return out


def drop_policy(ckpt: str, cond: str):
    """Chu ky policy cho league: dieu kien CO DINH cond (drop@cond). Cung ham dau vao dropout_input."""
    from tft_sim.bc_train import MaskedMLP
    from tft_sim.features_v4 import universal_features_v4
    ck = torch.load(ckpt, weights_only=False)
    model = MaskedMLP(ck["in_dim"]); model.load_state_dict(ck["state"]); model.eval()
    mu, sd = ck["mu"], ck["sd"]

    @torch.no_grad()
    def pol(env_, agent, obs, mask, rng):
        x = dropout_input(universal_features_v4(obs, env_, agent)[None], cond)
        xt = torch.from_numpy(((x - mu) / sd).astype(np.float32))
        return int(torch.argmax(model(xt, torch.from_numpy(np.asarray(mask, dtype=bool))[None]), dim=1).item())
    return pol


if __name__ == "__main__":
    rc = row_conditions(10)
    print(rc, dropout_input(np.ones((10, 185), np.float32), rc).shape)
