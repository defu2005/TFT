"""Thi nghiem mask nhom HUD (docs/model-plan.md muc 10.6). Nguon duy nhat cho mask:
fmask_for(cond) tao vector 0/1 dai 185 theo ten cot; apply_fmask() dung ca khi huan luyen va khi choi.

Bo cot (universal_features_v4, 185 chieu; da do bang probe ngay 2026-11-25):
  scalars 0..9: 0 gold, 1 level, 2 xp, 3 hp, 4 streak, 5 round (stage), 6 maxlvl, 7 components,
                8 augment_power, 9 augment_available
  opponents 10..30 (7 x 3), gods 31..61 (31), slot 62..81 (5 x [filled, owned/3, cost/5, traits/3]),
  augment tiers 82..84, bench/board 85..178 (94), augment flags 179..184.

Dieu kien (nhom HUD = thong tin quan sat duoc tren man hinh, theo fields4):
  a    = gold, level, xp, streak + slot filled, cost/5
  b    = a + hp, round
  c    = b + bench/board (94) + slot owned/traits (vi lay tu bench/board)
  full = tat ca 185 (kiem tra: mask toan 1 phai khop mo hinh cu)
Luon an: opponents, gods, augment (tier, flags), scalars 6..9.
"""
import numpy as np

HUD_SCALARS = [0, 1, 2, 4]
HP_SCALARS = [3, 5]
SLOT_BASE, BB_BASE, BB_DIM = 62, 85, 94


def slot_idx(i: int, j: int) -> int:
    return SLOT_BASE + 4 * i + j


GROUP_HUD = HUD_SCALARS + [slot_idx(i, 0) for i in range(5)] + [slot_idx(i, 2) for i in range(5)]
GROUP_HP = HP_SCALARS
GROUP_BB = list(range(BB_BASE, BB_BASE + BB_DIM)) + [slot_idx(i, 1) for i in range(5)] + [slot_idx(i, 3) for i in range(5)]
CONDITIONS = {
    "a": GROUP_HUD,
    "b": GROUP_HUD + GROUP_HP,
    "c": GROUP_HUD + GROUP_HP + GROUP_BB,
    "full": list(range(185)),
}


def fmask_for(cond: str) -> np.ndarray:
    v = np.zeros(185, np.float32)
    v[sorted(set(CONDITIONS[cond]))] = 1.0
    return v


def apply_fmask(X: np.ndarray, fmask: np.ndarray) -> np.ndarray:
    return (np.asarray(X, np.float32) * fmask).astype(np.float32)


if __name__ == "__main__":
    for c in CONDITIONS:
        print(c, int(fmask_for(c).sum()), "dims")
