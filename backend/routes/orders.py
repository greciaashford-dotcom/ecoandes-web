"""Shipping calc + order creation + admin management."""
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pydantic import BaseModel

from core.auth import get_current_user_optional, require_admin
from core.config import db
from core.mailer import send_company_order_notice, send_order_confirmation
from core.models import (
    Order,
    OrderCreate,
    OrderStatusUpdate,
    ShippingQuote,
)
from core.shipping import evaluate_shipping, get_shipping_config, CONFIG_ID
from core.utils import calc_shipping

router = APIRouter(prefix="/api/orders", tags=["orders"])


class ShippingRequest(BaseModel):
    customer_type: str = "retail"
    country: str = "España"
    postal_code: str = ""
    subtotal_with_vat: float = 0.0
    subtotal_ex_vat: float = 0.0
    total_weight_kg: float = 0.0
    has_bulk: bool = False
    # legacy fallback
    subtotal: Optional[float] = None


class CouponRequest(BaseModel):
    code: str
    email: Optional[str] = None
    subtotal: float
    customer_type: str = "retail"


async def _has_previous_order(email: str) -> bool:
    """True if this email already placed an order (i.e. not a first order)."""
    if not email:
        return False
    existing = await db.orders.find_one({"email": email.lower()}, {"_id": 1})
    return existing is not None


async def evaluate_coupon(code: str, email: Optional[str], subtotal: float) -> dict:
    """Validate a coupon (DB-driven, managed from the admin panel).

    Returns: {valid, discount, message, code}
    """
    from routes.coupons import evaluate_coupon_db

    return await evaluate_coupon_db(code, email, subtotal)


@router.post("/validate-coupon")
async def validate_coupon(payload: CouponRequest):
    return await evaluate_coupon(payload.code, payload.email, payload.subtotal)


@router.post("/shipping-quote")
async def shipping_quote(payload: ShippingRequest):
    cfg = await get_shipping_config()
    swv = payload.subtotal_with_vat or payload.subtotal or 0.0
    sev = payload.subtotal_ex_vat or payload.subtotal or 0.0
    return evaluate_shipping(
        cfg,
        customer_type=payload.customer_type,
        country=payload.country,
        postal_code=payload.postal_code,
        subtotal_with_vat=swv,
        subtotal_ex_vat=sev,
        total_weight_kg=payload.total_weight_kg,
        has_bulk=payload.has_bulk,
    )


# ---------- Admin: shipping config ----------
@router.get("/shipping-config")
async def get_shipping_config_public():
    """Public read of shipping rules (zones/thresholds) for storefront info pages."""
    return await get_shipping_config()


@router.put("/shipping-config", dependencies=[Depends(require_admin)])
async def update_shipping_config(payload: dict):
    payload["id"] = CONFIG_ID
    await db.shipping_config.replace_one({"id": CONFIG_ID}, payload, upsert=True)
    return await get_shipping_config()


async def _register_buyer(order_doc: dict, user: Optional[dict]) -> None:
    """Track every purchasing email (registered or not) in the `buyers` collection.

    Classification: professional > registered > guest.
    """
    email = order_doc["email"]
    if user and user.get("role") in ("professional", "admin"):
        btype = "professional"
    elif order_doc.get("customer_type") == "professional":
        btype = "professional"
    elif order_doc.get("user_id"):
        btype = "registered"
    else:
        btype = "guest"
    name = order_doc.get("shipping_address", {}).get("full_name", "")
    now = order_doc["created_at"]
    await db.buyers.update_one(
        {"email": email},
        {
            "$set": {
                "email": email,
                "name": name or None,
                "type": btype,
                "registered": bool(order_doc.get("user_id")),
                "last_order_at": now,
                "last_order_number": order_doc.get("order_number"),
            },
            "$setOnInsert": {"first_order_at": now},
            "$inc": {"orders_count": 1, "total_spent": float(order_doc.get("total", 0.0))},
        },
        upsert=True,
    )


async def _next_order_number() -> str:
    counter = await db.counters.find_one_and_update(
        {"_id": "order"}, {"$inc": {"seq": 1}}, upsert=True, return_document=True
    )
    if counter is None:
        await db.counters.update_one({"_id": "order"}, {"$set": {"seq": 1000}}, upsert=True)
        return "ECO-1000"
    seq = counter.get("seq", 1000)
    return f"ECO-{seq}"


def _allowed_payment_methods(delivery_method: str, is_pro: bool) -> list:
    """Payment methods allowed per delivery + role. No cash on delivery anywhere."""
    if delivery_method == "pickup":
        return ["stripe", "paypal"]  # pay now to collect
    methods = ["stripe", "paypal", "transfer"]
    if is_pro:
        methods.append("other")  # domiciliación / confirming (B2B only)
    return methods


@router.post("")
async def create_order(
    payload: OrderCreate,
    background: BackgroundTasks,
    user: Optional[dict] = Depends(get_current_user_optional),
):
    if not payload.items:
        raise HTTPException(status_code=400, detail="El carrito está vacío")

    # Recalculate prices from DB to prevent tampering (stored prices are SIN IVA)
    recomputed_items: List[dict] = []
    subtotal_ex_vat = 0.0
    vat_amount = 0.0
    total_weight_kg = 0.0
    has_bulk = False
    is_pro = payload.customer_type == "professional" and user and (
        user.get("role") == "admin"
        or (user.get("role") == "professional" and user.get("approved"))
    )
    # Validate payment method against role + delivery (no COD anywhere)
    allowed_methods = _allowed_payment_methods(payload.delivery_method, bool(is_pro))
    if payload.payment_method not in allowed_methods:
        raise HTTPException(
            status_code=400,
            detail=f"Método de pago no disponible para tu tipo de pedido. Permitidos: {', '.join(allowed_methods)}",
        )
    for item in payload.items:
        product = await db.products.find_one({"id": item.product_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=400, detail=f"Producto no encontrado: {item.name}")
        vat_rate = int(product.get("vat_rate", 10) or 0)
        # resolve variation price + weight
        unit_ex_vat = product["price_professional"] if is_pro else product["price_retail"]
        weight_kg = 0.0
        variation_sku = item.sku
        if item.variation_name and product.get("variations"):
            for v in product["variations"]:
                if v["name"] == item.variation_name or v["sku"] == item.sku:
                    unit_ex_vat = v["price_professional"] if is_pro else v["price_retail"]
                    weight_kg = float(v.get("weight_kg", 0) or 0)
                    variation_sku = v["sku"]
                    break
        qty = max(1, int(item.quantity))
        line_ex_vat = round(unit_ex_vat * qty, 2)
        line_vat = round(line_ex_vat * vat_rate / 100, 2)
        subtotal_ex_vat += line_ex_vat
        vat_amount += line_vat
        total_weight_kg += weight_kg * qty
        if weight_kg > 1.0:
            has_bulk = True
        # unit price as charged/displayed: retail incl. VAT, pro ex VAT
        unit_charged = round(unit_ex_vat * (1 + vat_rate / 100), 2) if not is_pro else round(unit_ex_vat, 2)
        recomputed_items.append(
            {
                "product_id": product["id"],
                "sku": variation_sku or product.get("sku", ""),
                "name": product["name"],
                "variation_name": item.variation_name,
                "unit_price": unit_charged,
                "unit_price_ex_vat": round(unit_ex_vat, 2),
                "vat_rate": vat_rate,
                "weight_kg": weight_kg,
                "quantity": qty,
                "image_url": product.get("image_url", ""),
            }
        )

    subtotal_ex_vat = round(subtotal_ex_vat, 2)
    vat_amount = round(vat_amount, 2)
    subtotal_with_vat = round(subtotal_ex_vat + vat_amount, 2)
    # subtotal used for coupon + display follows role basis
    role_subtotal = subtotal_with_vat if not is_pro else subtotal_ex_vat

    # ---- Shipping via engine ----
    addr = payload.shipping_address
    cfg = await get_shipping_config()
    ship = evaluate_shipping(
        cfg,
        customer_type=payload.customer_type,
        country=addr.country,
        postal_code=addr.postal_code,
        subtotal_with_vat=subtotal_with_vat,
        subtotal_ex_vat=subtotal_ex_vat,
        total_weight_kg=total_weight_kg,
        has_bulk=has_bulk,
    )
    shipping_status = ship.get("status", "ok")
    if payload.delivery_method == "pickup":
        # Click & Collect: no shipping cost
        shipping_cost = 0.0
        shipping_status = "ok"
    elif shipping_status == "blocked":
        raise HTTPException(status_code=400, detail=ship.get("message", "Envío no disponible para tu zona."))
    elif shipping_status == "manual_quote":
        shipping_cost = 0.0  # to be set by admin afterwards
    else:
        shipping_cost = float(ship.get("shipping_cost") or 0.0)

    # Apply coupon server-side (re-validated against DB rules). Stacks with free shipping.
    discount = 0.0
    applied_coupon = None
    if payload.coupon_code:
        result = await evaluate_coupon(payload.coupon_code, payload.email, role_subtotal)
        if result["valid"]:
            discount = result["discount"]
            applied_coupon = result.get("code") or payload.coupon_code.strip().upper()
    total = round(subtotal_with_vat + shipping_cost - discount, 2)
    if total < 0:
        total = 0.0

    order_number = await _next_order_number()
    import uuid

    order_doc = {
        "id": str(uuid.uuid4()),
        "order_number": order_number,
        "email": payload.email.lower(),
        "user_id": user["id"] if user else None,
        "customer_type": payload.customer_type,
        "items": recomputed_items,
        "shipping_address": payload.shipping_address.model_dump(),
        "billing_address": payload.billing_address.model_dump() if payload.billing_address else None,
        "subtotal": subtotal_with_vat,
        "subtotal_ex_vat": subtotal_ex_vat,
        "vat_amount": vat_amount,
        "shipping_cost": shipping_cost,
        "shipping_status": shipping_status,
        "shipping_zone": ship.get("zone"),
        "total_weight_kg": round(total_weight_kg, 3),
        "discount": discount,
        "coupon_code": applied_coupon,
        "total": total,
        "currency": "EUR",
        "status": "Pendiente",
        "payment_method": payload.payment_method,
        "delivery_method": payload.delivery_method,
        "payment_status": "pending",
        "payment_session_id": None,
        "payment_id": None,
        "notes": payload.notes,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    # First-touch traffic attribution (connects orders with the analytics dashboard)
    acq_raw = payload.acquisition or {}
    from routes.analytics import classify_traffic

    acq_source, acq_medium, acq_ref_host = classify_traffic(
        acq_raw.get("referrer", "") or "",
        acq_raw.get("utm_source") or None,
        acq_raw.get("utm_medium") or None,
    )
    order_doc["acquisition"] = {
        "source": acq_source,
        "medium": acq_medium,
        "referrer_host": acq_ref_host,
        "utm_source": (acq_raw.get("utm_source") or "")[:100],
        "utm_campaign": (acq_raw.get("utm_campaign") or "")[:150],
        "landing_page": (acq_raw.get("landing_page") or "")[:300],
    }
    await db.orders.insert_one(order_doc)
    order_doc.pop("_id", None)
    # Register coupon redemption (usage counter for admin panel)
    if applied_coupon:
        from routes.coupons import register_coupon_use

        await register_coupon_use(applied_coupon)
    # Track buyer email (registered or guest) for first-order coupon control + marketing
    await _register_buyer(order_doc, user)
    # Send confirmation email in background (non-blocking, even for B2B bank transfers)
    background.add_task(send_order_confirmation, order_doc)
    # Aviso interno a la empresa: nuevo pedido recibido
    background.add_task(send_company_order_notice, order_doc)
    return order_doc


@router.get("/by-number/{order_number}")
async def get_by_number(order_number: str):
    order = await db.orders.find_one({"order_number": order_number}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return order


@router.get("/mine")
async def my_orders(user: dict = Depends(get_current_user_optional)):
    if not user:
        return []
    orders = (
        await db.orders.find({"user_id": user["id"]}, {"_id": 0})
        .sort("created_at", -1)
        .to_list(200)
    )
    return orders


# ---------- Admin ----------
@router.get("/admin/list", dependencies=[Depends(require_admin)])
async def admin_list_orders(
    status: Optional[str] = None,
    customer_type: Optional[str] = None,
    search: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    source: Optional[str] = None,
    registered: Optional[str] = None,
    limit: int = Query(200, le=1000),
):
    import re as _re

    query: dict = {}
    if status:
        query["status"] = status
    if customer_type:
        query["customer_type"] = customer_type
    if source:
        query["acquisition.source"] = source
    if registered == "1":
        query["user_id"] = {"$ne": None}
    elif registered == "0":
        query["user_id"] = None
    if date_from or date_to:
        rng: dict = {}
        if date_from:
            rng["$gte"] = f"{date_from}T00:00:00"
        if date_to:
            rng["$lte"] = f"{date_to}T23:59:59.999999+00:00"
        query["created_at"] = rng
    if search:
        rx = _re.compile(_re.escape(search.strip()), _re.IGNORECASE)
        query["$or"] = [
            {"order_number": rx},
            {"email": rx},
            {"shipping_address.full_name": rx},
        ]
    orders = await db.orders.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return orders


ORDER_STATUSES = ["Pendiente", "Pagado", "Enviado", "Completado", "Cancelado"]


@router.get("/admin/status-counts", dependencies=[Depends(require_admin)])
async def admin_status_counts():
    """Counts per status for the WooCommerce-style quick filter tabs."""
    counts = {"all": await db.orders.count_documents({})}
    for s in ORDER_STATUSES:
        counts[s] = await db.orders.count_documents({"status": s})
    return counts


class BulkStatusUpdate(BaseModel):
    ids: List[str]
    status: str


@router.post("/admin/bulk-status", dependencies=[Depends(require_admin)])
async def admin_bulk_status(payload: BulkStatusUpdate):
    if payload.status not in ORDER_STATUSES:
        raise HTTPException(status_code=400, detail="Estado no válido")
    if not payload.ids:
        raise HTTPException(status_code=400, detail="Sin pedidos seleccionados")
    result = await db.orders.update_many(
        {"id": {"$in": payload.ids}},
        {"$set": {"status": payload.status, "updated_at": datetime.now(timezone.utc).isoformat()}},
    )
    return {"updated": result.modified_count}


@router.get("/admin/stats", dependencies=[Depends(require_admin)])
async def admin_stats():
    total = await db.orders.count_documents({})
    pending = await db.orders.count_documents({"status": "Pendiente"})
    paid = await db.orders.count_documents({"status": "Pagado"})
    shipped = await db.orders.count_documents({"status": "Enviado"})
    completed = await db.orders.count_documents({"status": "Completado"})
    pipeline = [
        {"$match": {"payment_status": "paid"}},
        {"$group": {"_id": None, "total": {"$sum": "$total"}}},
    ]
    cursor = db.orders.aggregate(pipeline)
    revenue = 0.0
    async for r in cursor:
        revenue = r.get("total", 0.0)
    customers = await db.users.count_documents({})
    products_count = await db.products.count_documents({"active": True})
    return {
        "orders_total": total,
        "orders_pending": pending,
        "orders_paid": paid,
        "orders_shipped": shipped,
        "orders_completed": completed,
        "revenue": round(revenue, 2),
        "customers": customers,
        "products": products_count,
    }


@router.get("/admin/buyers", dependencies=[Depends(require_admin)])
async def admin_buyers(
    type: Optional[str] = None,
    limit: int = Query(500, le=2000),
):
    """All purchasing emails (registered or guest), with classification + totals."""
    query: dict = {}
    if type in ("guest", "registered", "professional"):
        query["type"] = type
    buyers = (
        await db.buyers.find(query, {"_id": 0})
        .sort("last_order_at", -1)
        .limit(limit)
        .to_list(limit)
    )
    stats = {
        "total": await db.buyers.count_documents({}),
        "guest": await db.buyers.count_documents({"type": "guest"}),
        "registered": await db.buyers.count_documents({"type": "registered"}),
        "professional": await db.buyers.count_documents({"type": "professional"}),
    }
    return {"buyers": buyers, "stats": stats}


@router.get("/admin/{order_id}", dependencies=[Depends(require_admin)])
async def admin_get_order(order_id: str):
    order = await db.orders.find_one({"id": order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return order


@router.patch("/admin/{order_id}/status", dependencies=[Depends(require_admin)])
async def admin_update_status(order_id: str, payload: OrderStatusUpdate):
    result = await db.orders.update_one(
        {"id": order_id},
        {"$set": {"status": payload.status, "updated_at": datetime.now(timezone.utc).isoformat()}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    order = await db.orders.find_one({"id": order_id}, {"_id": 0})
    return order
