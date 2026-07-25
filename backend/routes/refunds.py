"""Refund system: admin-configurable reasons + order refunds with automatic
customer email and best-effort Stripe/PayPal provider refunds.

If payment-provider keys are not configured (or the order was not paid online),
the refund is recorded as a MANUAL refund (store returns money by hand) and the
customer is still notified by email.
"""
import base64
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from core.auth import require_admin
from core.config import (
    PAYPAL_API_BASE,
    PAYPAL_CLIENT_ID,
    PAYPAL_SECRET,
    STRIPE_API_KEY,
    db,
)
from core.mailer import send_refund_notification

logger = logging.getLogger("ecoandes.refunds")

router = APIRouter(prefix="/api/admin", tags=["refunds"])

DEFAULT_REASONS = [
    "Falta de stock",
    "Producto defectuoso o dañado",
    "Error en el pedido",
    "Cancelación a petición del cliente",
    "Retraso en el envío",
    "Otro motivo",
]


async def seed_refund_reasons() -> None:
    count = await db.refund_reasons.count_documents({})
    if count > 0:
        return
    now = datetime.now(timezone.utc).isoformat()
    for i, label in enumerate(DEFAULT_REASONS):
        await db.refund_reasons.insert_one({
            "id": str(uuid.uuid4()), "label": label, "active": True,
            "order": i, "created_at": now,
        })


# ---------- Refund reasons CRUD ----------
class ReasonIn(BaseModel):
    label: str = Field(..., min_length=2, max_length=120)
    active: bool = True


@router.get("/refund-reasons", dependencies=[Depends(require_admin)])
async def list_reasons():
    await seed_refund_reasons()
    reasons = await db.refund_reasons.find({}, {"_id": 0}).sort("order", 1).to_list(200)
    return {"reasons": reasons}


@router.post("/refund-reasons", dependencies=[Depends(require_admin)])
async def create_reason(payload: ReasonIn):
    count = await db.refund_reasons.count_documents({})
    doc = {
        "id": str(uuid.uuid4()), "label": payload.label.strip(),
        "active": payload.active, "order": count,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.refund_reasons.insert_one(dict(doc))
    doc.pop("_id", None)
    return doc


@router.put("/refund-reasons/{reason_id}", dependencies=[Depends(require_admin)])
async def update_reason(reason_id: str, payload: ReasonIn):
    res = await db.refund_reasons.update_one(
        {"id": reason_id}, {"$set": {"label": payload.label.strip(), "active": payload.active}}
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Motivo no encontrado")
    return await db.refund_reasons.find_one({"id": reason_id}, {"_id": 0})


@router.delete("/refund-reasons/{reason_id}", dependencies=[Depends(require_admin)])
async def delete_reason(reason_id: str):
    res = await db.refund_reasons.delete_one({"id": reason_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Motivo no encontrado")
    return {"ok": True}


# ---------- Provider refunds (best-effort) ----------
async def _stripe_refund(order: dict, amount: float) -> dict:
    """Refund a paid Stripe order. Returns {ok, provider, id, manual, error}."""
    if not STRIPE_API_KEY:
        return {"ok": False, "manual": True, "error": "Stripe no configurado"}
    session_id = order.get("payment_session_id")
    if not session_id:
        return {"ok": False, "manual": True, "error": "Sin sesión de pago"}
    try:
        import stripe
        stripe.api_key = STRIPE_API_KEY
        session = await __import__("asyncio").to_thread(stripe.checkout.Session.retrieve, session_id)
        payment_intent = session.get("payment_intent") if isinstance(session, dict) else getattr(session, "payment_intent", None)
        if not payment_intent:
            return {"ok": False, "manual": True, "error": "Sin payment_intent"}
        refund = await __import__("asyncio").to_thread(
            stripe.Refund.create,
            payment_intent=payment_intent,
            amount=int(round(amount * 100)),
        )
        rid = refund.get("id") if isinstance(refund, dict) else getattr(refund, "id", None)
        return {"ok": True, "provider": "stripe", "id": rid, "manual": False}
    except Exception as e:  # noqa: BLE001
        logger.exception("Stripe refund failed: %s", e)
        return {"ok": False, "manual": True, "error": str(e)}


async def _paypal_refund(order: dict, amount: float) -> dict:
    if not PAYPAL_CLIENT_ID or not PAYPAL_SECRET:
        return {"ok": False, "manual": True, "error": "PayPal no configurado"}
    session_id = order.get("payment_session_id")
    if not session_id:
        return {"ok": False, "manual": True, "error": "Sin orden PayPal"}
    try:
        auth = base64.b64encode(f"{PAYPAL_CLIENT_ID}:{PAYPAL_SECRET}".encode()).decode()
        async with httpx.AsyncClient(timeout=20.0) as cx:
            tok = await cx.post(
                f"{PAYPAL_API_BASE}/v1/oauth2/token",
                headers={"Authorization": f"Basic {auth}"},
                data={"grant_type": "client_credentials"},
            )
            token = tok.json()["access_token"]
            # find capture id from the order
            od = await cx.get(
                f"{PAYPAL_API_BASE}/v2/checkout/orders/{session_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
            capture_id = None
            data = od.json()
            for pu in data.get("purchase_units", []):
                for cap in (pu.get("payments", {}) or {}).get("captures", []):
                    capture_id = cap.get("id")
                    break
            if not capture_id:
                return {"ok": False, "manual": True, "error": "Sin captura PayPal"}
            rf = await cx.post(
                f"{PAYPAL_API_BASE}/v2/payments/captures/{capture_id}/refund",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"amount": {"value": f"{amount:.2f}", "currency_code": order.get("currency", "EUR")}},
            )
            if rf.status_code >= 300:
                return {"ok": False, "manual": True, "error": rf.text}
            return {"ok": True, "provider": "paypal", "id": rf.json().get("id"), "manual": False}
    except Exception as e:  # noqa: BLE001
        logger.exception("PayPal refund failed: %s", e)
        return {"ok": False, "manual": True, "error": str(e)}


# ---------- Refund an order ----------
class RefundIn(BaseModel):
    reason: str = Field(..., min_length=2)
    amount: Optional[float] = None  # default = full order total
    restock: bool = False           # optionally set the products out of stock note (info only)
    notify: bool = True


@router.post("/orders/{order_id}/refund", dependencies=[Depends(require_admin)])
async def refund_order(order_id: str, payload: RefundIn):
    order = await db.orders.find_one({"id": order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if order.get("status") == "Reembolsado":
        raise HTTPException(status_code=400, detail="Este pedido ya fue reembolsado")

    amount = float(payload.amount) if payload.amount is not None else float(order.get("total", 0))
    amount = round(max(0.0, min(amount, float(order.get("total", 0)))), 2)

    # Attempt provider refund only for paid online orders
    result = {"ok": False, "manual": True, "error": None}
    if order.get("payment_status") == "paid":
        if order.get("payment_method") == "stripe":
            result = await _stripe_refund(order, amount)
        elif order.get("payment_method") == "paypal":
            result = await _paypal_refund(order, amount)
        else:
            result = {"ok": False, "manual": True, "error": "Método sin reembolso automático"}
    else:
        result = {"ok": False, "manual": True, "error": "Pedido no pagado online"}

    now = datetime.now(timezone.utc).isoformat()
    refund_doc = {
        "id": str(uuid.uuid4()),
        "order_id": order_id,
        "order_number": order.get("order_number"),
        "email": order.get("email"),
        "amount": amount,
        "reason": payload.reason,
        "provider": result.get("provider") or order.get("payment_method"),
        "provider_refund_id": result.get("id"),
        "manual": bool(result.get("manual")),
        "provider_ok": bool(result.get("ok")),
        "provider_error": result.get("error"),
        "created_at": now,
    }
    await db.refunds.insert_one(dict(refund_doc))
    refund_doc.pop("_id", None)

    await db.orders.update_one(
        {"id": order_id},
        {"$set": {
            "status": "Reembolsado",
            "payment_status": "refunded",
            "refund": {
                "amount": amount, "reason": payload.reason,
                "manual": refund_doc["manual"], "provider": refund_doc["provider"],
                "provider_refund_id": refund_doc["provider_refund_id"],
                "created_at": now,
            },
            "updated_at": now,
        }},
    )

    email_id = None
    if payload.notify:
        email_id = await send_refund_notification(order, refund_doc)

    return {
        "ok": True,
        "refund": refund_doc,
        "provider_result": result,
        "email_sent": bool(email_id),
        "email_configured": email_id is not None,
    }


@router.get("/refunds", dependencies=[Depends(require_admin)])
async def list_refunds():
    refunds = await db.refunds.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)
    return {"refunds": refunds, "total": len(refunds)}
