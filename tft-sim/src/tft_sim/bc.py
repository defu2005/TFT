"""Behavior cloning MLP nho voi loss cross-entropy co mask hop le. Can torch (extra 'bc')."""

from __future__ import annotations

import torch
from torch import nn

from .env import N_SEATS  # noqa: F401  (giu import de bao dam goi duoc tai)


def featurize(obs: dict) -> list[float]:
    return [float(obs["gold"]) / 50.0, float(obs["strength"]) / 20.0, float(obs["round"]) / 10.0]


class MaskedMLP(nn.Module):
    def __init__(self, in_dim: int, n_actions: int, hidden: int = 32):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(in_dim, hidden), nn.ReLU(), nn.Linear(hidden, n_actions))

    def forward(self, x: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        logits = self.net(x)
        return logits.masked_fill(~mask, float("-inf"))


def train_bc(rows: list[dict], n_actions: int = 2, epochs: int = 200, lr: float = 1e-2, seed: int = 0) -> MaskedMLP:
    torch.manual_seed(seed)
    x = torch.tensor([featurize(r["obs"]) for r in rows], dtype=torch.float32)
    mask = torch.zeros(len(rows), n_actions, dtype=torch.bool)
    for k, r in enumerate(rows):
        for a in r["obs"]["legal"]:
            mask[k, a] = True
    y = torch.tensor([r["action"] for r in rows], dtype=torch.long)
    model = MaskedMLP(x.shape[1], n_actions)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    for _ in range(epochs):
        opt.zero_grad()
        loss = nn.functional.cross_entropy(model(x, mask), y)
        loss.backward()
        opt.step()
    return model


def make_policy(model: MaskedMLP) -> "callable":
    def policy(obs: dict, rng) -> int:
        n = 2
        mask = torch.zeros(1, n, dtype=torch.bool)
        for a in obs["legal"]:
            mask[0, a] = True
        x = torch.tensor([featurize(obs)], dtype=torch.float32)
        with torch.no_grad():
            logits = model(x, mask)
        return int(torch.argmax(logits, dim=1).item())

    return policy
