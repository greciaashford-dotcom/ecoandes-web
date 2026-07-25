"""Shipping engine: zone detection + rule evaluation (user_type + zone + weight).

Business rules (confirmed by client):

PARTICULARES (retail / B2C):
  - ES + PT peninsular + Baleares: subtotal CON IVA >= 50€ -> gratis; si no -> 4,99€
  - Francia: subtotal CON IVA >= 70€ -> gratis; si no -> 10€
  - Ceuta / Melilla / Canarias: bloqueado
  - Resto de países: bloqueado (B2C)

PROFESIONALES (B2B):
  - ES + PT peninsular + Baleares:
      * gratis si base SIN IVA > 150€ Y todos los items <= 1 kg (retail)
      * si hay cualquier item > 1 kg -> siempre escala por peso
      * si base SIN IVA <= 150€ -> escala por peso
      * escala (peso total carrito): 0-2=4, 2-5=6, 5-10=10, 10-15=15, 15-20=20, 20-35=22, 35-100=25
      * > 100 kg -> presupuesto manual
  - Canarias y resto de Europa (incl. Francia para B2B): presupuesto manual

Zone detection: país + prefijo de código postal (07 Baleares incluido; 35/38 Canarias;
51 Ceuta; 52 Melilla).
"""
from typing import Optional

from core.config import db

CONFIG_ID = "shipping_config"

DEFAULT_SHIPPING_CONFIG = {
    "id": CONFIG_ID,
    "version": 1,
    "currency": "EUR",
    "weight_unit": "kg",
    "special_postal_prefixes": {
        "canarias": ["35", "38"],
        "ceuta": ["51"],
        "melilla": ["52"],
        "baleares": ["07"],
    },
    "rules": {
        "retail": {
            "ES_PT_BAL": {
                "method": "flat_with_free_threshold",
                "amount_basis": "total_with_vat",
                "free_threshold": 50.0,
                "free_operator": ">=",
                "flat_fee": 4.99,
            },
            "FR": {
                "method": "flat_with_free_threshold",
                "amount_basis": "total_with_vat",
                "free_threshold": 70.0,
                "free_operator": ">=",
                "flat_fee": 10.0,
            },
            "RESTRICTED": {
                "method": "blocked",
                "message": "Por el momento no realizamos envíos a Ceuta, Melilla y Canarias.",
            },
            "INTL": {
                "method": "blocked",
                "message": "Por el momento no realizamos envíos a tu país.",
            },
        },
        "professional": {
            "ES_PT_BAL": {
                "method": "weight_scale_conditional_free",
                "free_amount_basis": "base_without_vat",
                "free_min_amount": 150.0,
                "free_operator": ">",
                "retail_max_item_weight_kg": 1.0,
                "bulk_item_weight_threshold_kg": 1.0,
                "weight_scale": [
                    {"from_kg": 0, "to_kg": 2, "fee": 4.0},
                    {"from_kg": 2, "to_kg": 5, "fee": 6.0},
                    {"from_kg": 5, "to_kg": 10, "fee": 10.0},
                    {"from_kg": 10, "to_kg": 15, "fee": 15.0},
                    {"from_kg": 15, "to_kg": 20, "fee": 20.0},
                    {"from_kg": 20, "to_kg": 35, "fee": 22.0},
                    {"from_kg": 35, "to_kg": 100, "fee": 25.0},
                ],
                "over_max_weight_kg": 100.0,
            },
            "CANARIAS_EU": {
                "method": "manual_quote",
                "message": "El coste de transporte se calculará manualmente y se le comunicará tras revisar el pedido.",
            },
        },
    },
}


_COUNTRY_MAP = {
    "espana": "ES", "españa": "ES", "spain": "ES", "es": "ES",
    "portugal": "PT", "pt": "PT",
    "francia": "FR", "france": "FR", "fr": "FR",
}


def country_to_code(country: str) -> str:
    c = (country or "").strip().lower()
    return _COUNTRY_MAP.get(c, (c[:2].upper() if len(c) >= 2 else "XX"))


def detect_zone(country: str, postal_code: str, is_retail: bool, cfg: dict) -> str:
    cc = country_to_code(country)
    pp = (str(postal_code or "")).strip()[:2]
    prefixes = cfg.get("special_postal_prefixes", {})
    canarias = set(prefixes.get("canarias", []))
    ceuta = set(prefixes.get("ceuta", []))
    melilla = set(prefixes.get("melilla", []))
    special_es = canarias | ceuta | melilla

    if cc == "ES":
        if pp in special_es:
            return "RESTRICTED" if is_retail else "CANARIAS_EU"
        return "ES_PT_BAL"  # mainland + Baleares (07)
    if cc == "PT":
        return "ES_PT_BAL"  # peninsular
    if cc == "FR":
        return "FR" if is_retail else "CANARIAS_EU"
    # any other country
    return "INTL" if is_retail else "CANARIAS_EU"


def _weight_tier(scale: list, weight: float) -> Optional[dict]:
    """from-exclusive / to-inclusive; weight 0 falls in first tier."""
    for t in scale:
        lo = float(t["from_kg"])
        hi = float(t["to_kg"])
        if weight <= 0:
            return scale[0]
        if lo < weight <= hi:
            return t
    return None


async def get_shipping_config() -> dict:
    cfg = await db.shipping_config.find_one({"id": CONFIG_ID}, {"_id": 0})
    if not cfg:
        await db.shipping_config.insert_one({**DEFAULT_SHIPPING_CONFIG})
        cfg = {**DEFAULT_SHIPPING_CONFIG}
    return cfg


def evaluate_shipping(
    cfg: dict,
    *,
    customer_type: str,
    country: str,
    postal_code: str,
    subtotal_with_vat: float,
    subtotal_ex_vat: float,
    total_weight_kg: float,
    has_bulk: bool,
) -> dict:
    is_retail = customer_type != "professional"
    user_key = "retail" if is_retail else "professional"
    zone = detect_zone(country, postal_code, is_retail, cfg)
    role_subtotal = round(subtotal_with_vat if is_retail else subtotal_ex_vat, 2)

    base = {
        "zone": zone,
        "customer_type": customer_type,
        "subtotal": role_subtotal,
        "subtotal_with_vat": round(subtotal_with_vat, 2),
        "subtotal_ex_vat": round(subtotal_ex_vat, 2),
        "total_weight_kg": round(total_weight_kg, 3),
        "shipping_cost": 0.0,
        "total": role_subtotal,
        "free_shipping": False,
        "free_shipping_threshold": 0.0,
        "remaining_for_free_shipping": 0.0,
        "status": "ok",
        "method": None,
        "amount_basis": None,
        "message": "",
    }

    rule = (cfg.get("rules", {}).get(user_key, {}) or {}).get(zone)
    if not rule:
        base["status"] = "blocked" if is_retail else "manual_quote"
        base["method"] = "blocked" if is_retail else "manual_quote"
        base["shipping_cost"] = None
        base["total"] = None
        base["message"] = (
            "Por el momento no realizamos envíos a tu zona."
            if is_retail
            else "El coste de transporte se calculará manualmente."
        )
        return base

    method = rule["method"]
    base["method"] = method

    if method == "blocked":
        base["status"] = "blocked"
        base["shipping_cost"] = None
        base["total"] = None
        base["message"] = rule.get("message", "Envío no disponible para tu zona.")
        return base

    if method == "manual_quote":
        base["status"] = "manual_quote"
        base["shipping_cost"] = None
        base["total"] = None
        base["message"] = rule.get("message", "Coste de transporte pendiente de cálculo manual.")
        return base

    if method == "flat_with_free_threshold":
        threshold = float(rule["free_threshold"])
        amount = subtotal_with_vat if rule.get("amount_basis") == "total_with_vat" else subtotal_ex_vat
        base["amount_basis"] = rule.get("amount_basis")
        base["free_shipping_threshold"] = threshold
        if amount >= threshold:
            base["shipping_cost"] = 0.0
            base["free_shipping"] = True
            base["remaining_for_free_shipping"] = 0.0
        else:
            base["shipping_cost"] = round(float(rule["flat_fee"]), 2)
            base["remaining_for_free_shipping"] = round(threshold - amount, 2)
        base["total"] = round(role_subtotal + (base["shipping_cost"] or 0), 2)
        return base

    if method == "weight_scale_conditional_free":
        base["amount_basis"] = rule.get("free_amount_basis", "base_without_vat")
        free_min = float(rule.get("free_min_amount", 150.0))
        base["free_shipping_threshold"] = free_min
        # 1) Conditional free: only if NO bulk item AND base ex-VAT > min
        if (not has_bulk) and subtotal_ex_vat > free_min:
            base["shipping_cost"] = 0.0
            base["free_shipping"] = True
            base["total"] = round(role_subtotal, 2)
            base["message"] = "Portes gratuitos (pedido de detalle superior al mínimo)."
            return base
        # 2) Otherwise weight scale
        over = float(rule.get("over_max_weight_kg", 100.0))
        if total_weight_kg > over:
            base["status"] = "manual_quote"
            base["shipping_cost"] = None
            base["total"] = None
            base["message"] = f"Pedido superior a {over:.0f} kg: transporte calculado manualmente."
            return base
        tier = _weight_tier(rule.get("weight_scale", []), total_weight_kg)
        if tier is None:
            base["status"] = "manual_quote"
            base["shipping_cost"] = None
            base["total"] = None
            base["message"] = "Transporte calculado manualmente según peso."
            return base
        base["shipping_cost"] = round(float(tier["fee"]), 2)
        base["weight_tier"] = {"from_kg": tier["from_kg"], "to_kg": tier["to_kg"], "fee": tier["fee"]}
        if not has_bulk:
            base["remaining_for_free_shipping"] = round(max(0.0, free_min - subtotal_ex_vat), 2)
        base["total"] = round(role_subtotal + base["shipping_cost"], 2)
        return base

    # unknown method fallback
    base["status"] = "manual_quote"
    base["shipping_cost"] = None
    base["total"] = None
    base["message"] = "Coste de transporte pendiente."
    return base
