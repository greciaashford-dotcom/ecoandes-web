"""Product routes (public + admin)."""
import asyncio
import re
import unicodedata
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from core.auth import get_current_user_optional, require_admin
from core.config import db
from core.models import Product, ProductCreate, ProductUpdate
from core.utils import slugify
from core.translator import (
    TARGET_LANGS,
    get_category_translations,
    generate_all_product_translations,
    generate_product_seo,
    STATUS as TRANSLATION_STATUS,
    SEO_STATUS,
)

router = APIRouter(prefix="/api/products", tags=["products"])

_TRANSLATABLE = ("name", "short_description", "description", "highlights")


def _norm(s: str) -> str:
    """Lowercase + strip accents for accent/case-insensitive matching."""
    s = unicodedata.normalize("NFKD", s or "")
    s = s.encode("ascii", "ignore").decode("ascii")
    return s.lower().strip()


def _term_level(term: str, text: str) -> int:
    """Match strength of `term` inside `text` (both normalized):
    3 = whole word, 2 = word-prefix, 1 = substring (mid-word), 0 = no match.
    """
    if not term or not text:
        return 0
    esc = re.escape(term)
    if re.search(rf"\b{esc}\b", text):
        return 3
    if re.search(rf"\b{esc}", text):
        return 2
    if term in text:
        return 1
    return 0


def _rank_search(products: List[dict], search: str, limit: int) -> List[dict]:
    """Relevance ranking so e.g. 'maca' returns 'Maca Negra' (whole word) and
    excludes 'Macarrones' (mere prefix) when a stronger match exists.

    Strategy: every query term must match each product; the product's level is
    the weakest term level. Only the strongest non-empty bucket is returned, so
    whole-word matches win over prefix/substring matches.
    """
    terms = [t for t in _norm(search).split() if t]
    if not terms:
        return products[:limit]
    scored = []
    for p in products:
        name = _norm(p.get("name", ""))
        tags = _norm(" ".join(p.get("tags", []) or []))
        sku = _norm(p.get("sku", ""))
        levels = []
        for t in terms:
            lv = max(_term_level(t, name), _term_level(t, tags), _term_level(t, sku))
            levels.append(lv)
        overall = min(levels) if levels else 0
        if overall == 0:
            continue
        starts = 1 if name.startswith(terms[0]) else 0
        scored.append((overall, starts, name, p))
    if not scored:
        return []
    top = max(s[0] for s in scored)
    bucket = [s for s in scored if s[0] == top]
    bucket.sort(key=lambda s: (-s[1], s[2]))
    return [s[3] for s in bucket][:limit]


def _apply_lang(p: dict, lang: Optional[str]) -> dict:
    """Overlay translated fields for the requested language (fallback to Spanish base)."""
    if lang and lang != "es" and lang in TARGET_LANGS:
        block = (p.get("translations") or {}).get(lang) or {}
        for f in _TRANSLATABLE:
            val = block.get(f)
            if val:
                p[f] = val
        # description blocks (nested)
        db_tr = block.get("description_blocks")
        if isinstance(db_tr, dict) and isinstance(p.get("description_blocks"), dict):
            merged = {**p["description_blocks"]}
            for k, v in db_tr.items():
                if v:
                    merged[k] = v
            p["description_blocks"] = merged
        # SEO/GEO block (per language)
        seo_tr = block.get("seo")
        if isinstance(seo_tr, dict) and seo_tr.get("meta_title"):
            p["seo"] = seo_tr
    p.pop("translations", None)
    return p


def _decorate(p: dict, user: Optional[dict], lang: Optional[str] = None) -> dict:
    """Add role/VAT-aware display prices and apply language overlay.

    Stored prices are SIN IVA. B2C (retail) sees prices WITH IVA included; B2B
    (professional/admin) sees prices SIN IVA (VAT shown separately at checkout).
    """
    is_pro = bool(user and (
        user.get("role") == "admin"
        or (user.get("role") == "professional" and user.get("approved"))
    ))
    p.pop("_id", None)
    vat = p.get("vat_rate", 10) or 0

    def disp(ex_vat: float) -> float:
        if ex_vat is None:
            return 0.0
        return round(ex_vat, 2) if is_pro else round(ex_vat * (1 + vat / 100), 2)

    base = p.get("price_professional") if is_pro else p.get("price_retail")
    p["display_price"] = disp(base or 0)
    p["display_price_ex_vat"] = round(base or 0, 2)
    p["price_includes_vat"] = (not is_pro)
    for v in (p.get("variations") or []):
        v_base = v.get("price_professional") if is_pro else v.get("price_retail")
        v["display_price"] = disp(v_base or 0)
        v["display_price_ex_vat"] = round(v_base or 0, 2)
    return _apply_lang(p, lang)


@router.get("")
async def list_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    featured: Optional[bool] = None,
    best_seller: Optional[bool] = None,
    lang: Optional[str] = None,
    limit: int = Query(100, le=500),
    user: Optional[dict] = Depends(get_current_user_optional),
):
    query: dict = {"active": True}
    if category:
        query["category"] = category
    if featured is not None:
        query["featured"] = featured
    if best_seller is not None:
        query["best_seller"] = best_seller
    if search:
        # Fetch candidates within the active (+category/flags) scope, then rank in
        # Python for precise, accent-insensitive, whole-word-first relevance.
        candidates = await db.products.find(query, {"_id": 0}).to_list(2000)
        items = _rank_search(candidates, search, limit)
        return [_decorate(p, user, lang) for p in items]
    items = await db.products.find(query, {"_id": 0}).limit(limit).to_list(limit)
    return [_decorate(p, user, lang) for p in items]


@router.post("/by-ids")
async def products_by_ids(payload: dict, lang: Optional[str] = None,
                          user: Optional[dict] = Depends(get_current_user_optional)):
    ids = payload.get("ids") or []
    if not ids:
        return []
    items = await db.products.find({"id": {"$in": ids}, "active": True}, {"_id": 0}).to_list(500)
    order = {pid: i for i, pid in enumerate(ids)}
    items.sort(key=lambda d: order.get(d["id"], 999))
    return [_decorate(p, user, lang) for p in items]


@router.get("/categories")
async def list_categories(lang: Optional[str] = None):
    cats = sorted([c for c in await db.products.distinct("category", {"active": True}) if c])
    mapping = {}
    if lang and lang != "es" and lang in TARGET_LANGS:
        all_tr = await get_category_translations()
        mapping = all_tr.get(lang, {})
    return [{"value": c, "label": mapping.get(c, c)} for c in cats]


@router.get("/slug/{slug}")
async def get_by_slug(
    slug: str,
    lang: Optional[str] = None,
    user: Optional[dict] = Depends(get_current_user_optional),
):
    product = await db.products.find_one({"slug": slug, "active": True}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return _decorate(product, user, lang)


@router.get("/{product_id}")
async def get_product(
    product_id: str,
    lang: Optional[str] = None,
    user: Optional[dict] = Depends(get_current_user_optional),
):
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return _decorate(product, user, lang)


# ---------- Admin ----------
@router.post("", dependencies=[Depends(require_admin)])
async def create_product(payload: ProductCreate):
    from uuid import uuid4

    now = datetime.now(timezone.utc).isoformat()
    slug = payload.slug or slugify(payload.name)
    # ensure unique slug
    existing = await db.products.find_one({"slug": slug}, {"_id": 0})
    if existing:
        slug = f"{slug}-{uuid4().hex[:5]}"
    doc = payload.model_dump()
    doc["id"] = str(uuid4())
    doc["slug"] = slug
    doc["created_at"] = now
    doc["updated_at"] = now
    await db.products.insert_one(doc)
    doc.pop("_id", None)
    return doc


@router.patch("/{product_id}", dependencies=[Depends(require_admin)])
async def update_product(product_id: str, payload: ProductUpdate):
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="Sin cambios")
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    result = await db.products.update_one({"id": product_id}, {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    doc = await db.products.find_one({"id": product_id}, {"_id": 0})
    return doc


@router.patch("/{product_id}/stock", dependencies=[Depends(require_admin)])
async def update_stock(product_id: str, payload: dict):
    """Update product-level and/or per-variation stock."""
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    set_fields = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if "stock" in payload and payload["stock"] is not None:
        set_fields["stock"] = int(payload["stock"])
    await db.products.update_one({"id": product_id}, {"$set": set_fields})
    # per-variation stock
    for v in (payload.get("variations") or []):
        if "sku" in v and "stock" in v:
            await db.products.update_one(
                {"id": product_id},
                {"$set": {"variations.$[el].stock": int(v["stock"])}},
                array_filters=[{"el.sku": v["sku"]}],
            )
    doc = await db.products.find_one({"id": product_id}, {"_id": 0, "translations": 0})
    return doc


@router.delete("/{product_id}", dependencies=[Depends(require_admin)])
async def delete_product(product_id: str):
    await db.products.update_one({"id": product_id}, {"$set": {"active": False}})
    return {"ok": True}


# ---------- Translations (admin) ----------
@router.post("/translations/run", dependencies=[Depends(require_admin)])
async def run_translations(only_missing: bool = True):
    """Kick off generation of product + category translations in a separate
    process (never blocks the API)."""
    from core.jobs import content_jobs_status, spawn_content_generation

    jobs = await content_jobs_status()
    if jobs.get("running"):
        return {"started": False, "reason": "already_running", "status": jobs}
    ok = spawn_content_generation(translations=True, seo=False, force=not only_missing)
    return {"started": ok, "status": await content_jobs_status()}


@router.get("/translations/status", dependencies=[Depends(require_admin)])
async def translations_status():
    from core.jobs import content_jobs_status

    jobs = await content_jobs_status()
    # keep legacy in-process status as fallback detail
    return {**TRANSLATION_STATUS, "job": jobs}


# ---------- SEO / GEO (admin) ----------
@router.post("/seo/run", dependencies=[Depends(require_admin)])
async def run_seo(only_missing: bool = True):
    """Kick off generation of SEO/GEO metadata in a separate process
    (never blocks the API)."""
    from core.jobs import content_jobs_status, spawn_content_generation

    jobs = await content_jobs_status()
    if jobs.get("running"):
        return {"started": False, "reason": "already_running", "status": jobs}
    ok = spawn_content_generation(translations=False, seo=True, force=not only_missing)
    return {"started": ok, "status": await content_jobs_status()}


@router.get("/seo/status", dependencies=[Depends(require_admin)])
async def seo_status():
    from core.jobs import content_jobs_status

    jobs = await content_jobs_status()
    return {**SEO_STATUS, "job": jobs}
