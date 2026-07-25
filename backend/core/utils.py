"""Utility helpers."""
import re
import unicodedata


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-zA-Z0-9\s-]", "", value).strip().lower()
    value = re.sub(r"[\s_-]+", "-", value)
    return value.strip("-") or "producto"


def calc_shipping(subtotal: float, customer_type: str) -> dict:
    """Simple shipping calculator. Free over threshold."""
    from core.config import (
        FREE_SHIPPING_THRESHOLD,
        SHIPPING_BASE,
        SHIPPING_PROFESSIONAL,
    )

    base = SHIPPING_PROFESSIONAL if customer_type == "professional" else SHIPPING_BASE
    if subtotal >= FREE_SHIPPING_THRESHOLD:
        shipping_cost = 0.0
        remaining = 0.0
        free = True
    else:
        shipping_cost = base
        remaining = round(FREE_SHIPPING_THRESHOLD - subtotal, 2)
        free = False
    total = round(subtotal + shipping_cost, 2)
    return {
        "subtotal": round(subtotal, 2),
        "shipping_cost": shipping_cost,
        "total": total,
        "free_shipping_threshold": FREE_SHIPPING_THRESHOLD,
        "remaining_for_free_shipping": remaining,
        "free_shipping": free,
    }
