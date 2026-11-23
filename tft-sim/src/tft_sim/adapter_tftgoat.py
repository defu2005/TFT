"""Adapter tu TFT_GOAT. CHUA KIEM THU: viet tu doc code, chua chay.

Chi import khi goi ham. Khong download du lieu. Can goi tft_goat tu venv rieng.
"""

from __future__ import annotations


def scripted_teacher():
    """Tra ve policy goi tft_goat.agent.scripted.scripted_action. Can state day du (privileged)."""
    from tft_goat.agent.scripted import scripted_action  # noqa: WPS433

    def policy(state_and_player, rng):  # chu ky khac voi toy env: adapter chua hoan thien
        state, player = state_and_player
        return int(scripted_action(state, player))

    return policy
