"""Display-unit helpers (g / kg / lb).

Authoritative storage remains grams (*_g columns / JSONL).
Display conversion is operator UX only — not legal-for-trade.
"""
from __future__ import annotations

from typing import Literal

DisplayUnit = Literal["g", "kg", "lb"]
ALLOWED_DISPLAY_UNITS: frozenset[str] = frozenset({"g", "kg", "lb"})

# Exact SI / international avoirdupois constants used for display conversion only.
GRAMS_PER_KG = 1000.0
GRAMS_PER_LB = 453.59237


def normalize_display_unit(unit: str | None) -> DisplayUnit:
    value = (unit or "g").strip().lower()
    if value not in ALLOWED_DISPLAY_UNITS:
        raise ValueError(f"unsupported display unit {unit!r}; allowed: g, kg, lb")
    return value  # type: ignore[return-value]


def grams_to_display(grams: float, unit: str) -> float:
    display = normalize_display_unit(unit)
    if display == "g":
        return float(grams)
    if display == "kg":
        return float(grams) / GRAMS_PER_KG
    return float(grams) / GRAMS_PER_LB


def display_to_grams(value: float, unit: str) -> float:
    display = normalize_display_unit(unit)
    if display == "g":
        return float(value)
    if display == "kg":
        return float(value) * GRAMS_PER_KG
    return float(value) * GRAMS_PER_LB


def format_weight(grams: float, unit: str, *, decimals: int | None = None) -> str:
    display = normalize_display_unit(unit)
    if decimals is None:
        decimals = 3 if display == "g" else 4
    converted = grams_to_display(grams, display)
    return f"{converted:,.{decimals}f} {display}"


def unit_label(unit: str) -> str:
    return normalize_display_unit(unit)
