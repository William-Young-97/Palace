from __future__ import annotations

from .card_effects import TenEffect, SevenEffect, ThreeEffect, TwoEffect

# Top-level helper – no need for a class wrapper
def get_card_effect(rank: str):
    mapping = {
        "10": TenEffect,
        "7": SevenEffect,
        "3": ThreeEffect,
        "2": TwoEffect,
    }
    effect_class = mapping.get(rank)
    return effect_class() if effect_class is not None else None
