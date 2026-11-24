"""BC: MLP nho, cross-entropy co mask hop le, nhan = hanh dong cua teacher scripted."""
from __future__ import annotations
import numpy as np
import torch
from torch import nn

N_ACTIONS = 43


class MaskedMLP(nn.Module):
    def __init__(self, in_dim: int, hidden: int = 128):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(in_dim, hidden), nn.ReLU(), nn.Linear(hidden, hidden), nn.ReLU(),
                                 nn.Linear(hidden, N_ACTIONS))

    def forward(self, x, mask):
        return self.net(x).masked_fill(~mask, float("-inf"))


def features(npz, variant: str) -> np.ndarray:
    if variant == "flat":
        return npz["flat"]
    if variant == "flat+slot":
        return np.concatenate([npz["flat"], npz["aux"]], axis=1)
    raise ValueError(variant)


def train(X: np.ndarray, M: np.ndarray, y: np.ndarray, epochs: int = 3, batch: int = 4096, lr: float = 1e-3,
          seed: int = 0) -> MaskedMLP:
    torch.manual_seed(seed)
    mu, sd = X.mean(0), X.std(0)
    sd = np.where(sd < 1e-6, 1.0, sd)  # cot hang so: khong chia cho ~0 (xem README, muc noi dung that)
    Xt = torch.from_numpy(((X - mu) / sd).astype(np.float32))
    Mt = torch.from_numpy(np.asarray(M).astype(bool))
    yt = torch.from_numpy(y)
    model = MaskedMLP(X.shape[1])
    model.norm = (mu, sd)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    n = len(yt)
    g = torch.Generator().manual_seed(seed)
    for ep in range(epochs):
        perm = torch.randperm(n, generator=g)
        tot = 0.0
        for i in range(0, n, batch):
            idx = perm[i:i + batch]
            opt.zero_grad()
            loss = nn.functional.cross_entropy(model(Xt[idx], Mt[idx]), yt[idx])
            loss.backward()
            opt.step()
            tot += float(loss) * len(idx)
        print(f"epoch {ep} loss {tot / n:.4f}", flush=True)
    return model


@torch.no_grad()
def val_agreement(model, X, M, y) -> float:
    mu, sd = model.norm
    Xt = torch.from_numpy(((X - mu) / sd).astype(np.float32))
    pred = torch.argmax(model(Xt, torch.from_numpy(np.asarray(M).astype(bool))), dim=1).numpy()
    return float((pred == y).mean())


def policy_from(model, variant: str, env_slot_fn=None):
    """Chu ky policy (env, agent, obs, mask, rng). Flat tu obs, slot tu env neu variant co slot."""
    from tft_sim.tftgoat import flat_obs, slot_features
    mu, sd = model.norm

    @torch.no_grad()
    def pol(env, agent, obs, mask, rng):
        x = flat_obs(obs)
        if variant == "flat+slot":
            x = np.concatenate([x, slot_features(env, agent)])
        xt = torch.from_numpy(((x - mu) / sd).astype(np.float32))[None]
        m = torch.from_numpy(np.asarray(mask, dtype=bool))[None]
        return int(torch.argmax(model(xt, m), dim=1).item())

    return pol
