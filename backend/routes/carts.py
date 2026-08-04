"""Carritos abandonados: tracking público + recordatorio automático por email + CRM admin.

Colección `abandoned_carts` (un doc por cart_id de dispositivo):
{ cart_id, email, items[], subtotal, status: active|reminded|converted|emptied,
  created_at, updated_at, reminder_sent_at, converted_order, converted_at }

Flujo: el frontend envía snapshots del carrito (usuarios logueados siempre; invitados
en cuanto escriben su email en el checkout). El scheduler llama a
`process_abandoned_carts()` cada ~10 min y envía el recordatorio (cupón ECOBONUS)
a los carritos con email inactivos más de ABANDON_HOURS. Al crear un pedido, los
carritos de ese email se marcan como convertidos.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from core.auth import require_admin
from core.config import db

logger = logging.getLogger("ecoandes.carts")

router = APIRouter(prefix="/api/cart", tags=["cart"])

ABANDON_HOURS = 4  # horas de inactividad antes del recordatorio (elección del usuario)


class CartItemIn(BaseModel):
    product_id: str
    name: str
    variation_name: Optional[str] = None
    quantity: int = 1
    unit_price: float = 0
    image_url: Optional[str] = ""


class CartTrackIn(BaseModel):
    cart_id: str = Field(min_length=8, max_length=64)
    email: Optional[str] = None
    items: List[CartItemIn] = []
    subtotal: float = 0


@router.post("/track")
async def track_cart(payload: CartTrackIn):
    """Snapshot del carrito. Sin auth: el cart_id es un uuid por dispositivo."""
    now = datetime.now(timezone.utc).isoformat()
    email = (payload.email or "").strip().lower() or None
    if not payload.items:
        # carrito vaciado: no hay nada que recordar
        await db.abandoned_carts.update_one(
            {"cart_id": payload.cart_id},
            {"$set": {"items": [], "subtotal": 0, "status": "emptied", "updated_at": now}},
        )
        return {"ok": True, "status": "emptied"}
    update = {
        "$set": {
            "items": [i.model_dump() for i in payload.items][:50],
            "subtotal": round(payload.subtotal, 2),
            "status": "active",
            "updated_at": now,
            # actividad nueva -> el recordatorio vuelve a estar disponible
            "reminder_sent_at": None,
        },
        "$setOnInsert": {"created_at": now},
    }
    if email:
        update["$set"]["email"] = email
    await db.abandoned_carts.update_one({"cart_id": payload.cart_id}, update, upsert=True)
    return {"ok": True, "status": "active"}


@router.get("/admin/list", dependencies=[Depends(require_admin)])
async def list_abandoned_carts(limit: int = 200):
    carts = (
        await db.abandoned_carts.find({}, {"_id": 0})
        .sort("updated_at", -1)
        .to_list(min(limit, 500))
    )
    stats = {
        "active": await db.abandoned_carts.count_documents({"status": "active", "items.0": {"$exists": True}}),
        "reminded": await db.abandoned_carts.count_documents({"status": "reminded"}),
        "converted": await db.abandoned_carts.count_documents({"status": "converted"}),
    }
    return {"carts": carts, "stats": stats}


@router.delete("/admin/{cart_id}", dependencies=[Depends(require_admin)])
async def delete_abandoned_cart(cart_id: str):
    res = await db.abandoned_carts.delete_one({"cart_id": cart_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Carrito no encontrado")
    return {"ok": True}


async def mark_carts_converted(email: str, order_number: str) -> None:
    """Llamado al crear un pedido: los carritos de ese email dejan de ser abandonados."""
    now = datetime.now(timezone.utc).isoformat()
    await db.abandoned_carts.update_many(
        {"email": email.lower(), "status": {"$in": ["active", "reminded"]}},
        {"$set": {"status": "converted", "converted_order": order_number, "converted_at": now}},
    )


async def process_abandoned_carts() -> int:
    """Envía el recordatorio a carritos con email inactivos > ABANDON_HOURS.

    Devuelve el nº de recordatorios enviados. Idempotente: usa reminder_sent_at.
    """
    from core.mailer import send_abandoned_cart_email

    cutoff = (datetime.now(timezone.utc) - timedelta(hours=ABANDON_HOURS)).isoformat()
    cursor = db.abandoned_carts.find(
        {
            "status": "active",
            "email": {"$nin": [None, ""]},
            "items.0": {"$exists": True},
            "updated_at": {"$lt": cutoff},
            "reminder_sent_at": None,
        },
        {"_id": 0},
    ).limit(50)
    sent = 0
    now = datetime.now(timezone.utc).isoformat()
    async for cart in cursor:
        try:
            await send_abandoned_cart_email(cart)
        except Exception as e:  # noqa: BLE001
            # el envío puede fallar (p.ej. dominio Resend sin verificar): se marca
            # igualmente para no reintentar en bucle cada 10 minutos
            logger.warning("Abandoned-cart email failed for %s: %s", cart.get("email"), e)
        await db.abandoned_carts.update_one(
            {"cart_id": cart["cart_id"]},
            {"$set": {"status": "reminded", "reminder_sent_at": now}},
        )
        sent += 1
    if sent:
        logger.info("Abandoned-cart reminders processed: %s", sent)
    return sent
