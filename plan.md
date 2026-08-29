# EcoAndes BIO — Plan de Continuación (UI → Blogs → Testing → Catálogo/Precios/IVA → Envíos → Pagos → SEO/GEO → Imágenes → **SEO Manual + Nombres Legacy + Redirecciones** → **UX/Operaciones (Lote 9)** → **Recuperación de Carritos (Lote 10)** → **Lote 11 (Splash + Recetas + Media links + Emails + Hero dots + 2º recordatorio + Links universales)** → **Fase 14 / Lote 12 (Blog Admin + Site Images Admin + Bug carrusel categorías)** → **Fase 15 / Lote 13 (Carrusel Coverflow 3D de categorías)** → **Fase 16 / Lote 14 (Envíos/Pagos/Reembolsos/Registro: v2)** → **Fase 17 / Lote 15 (Carrito estilo Amazon + UX móvil + Mensajes a cliente)** → **Fase 18 / Lote 16 (Recomendados EcoAndes + UX móvil tienda/cartas + logout destacado)** → **Fase 19 / Lote 17 (Envíos retail v3 + verificación dirección + reembolsos tipo WooCommerce + solicitud factura + buscador + menú móvil + paginación tienda)**

## 1) Objetivos

### Objetivos ya completados (iteración anterior)
- Modernizar la UI manteniendo identidad de marca (sage/terracotta/bone) con **bordes redondeados** y **micro‑animaciones** sin romper flujos. **(COMPLETADO)**
- Actualizar el **Blog**: 12 posts mantenidos, ahora gestionables desde dashboard con SEO y JSON‑LD Article. **(COMPLETADO)**
- Ejecutar **testing end‑to‑end** para asegurar estabilidad (checkout/cupón/búsqueda/registro/blogs/UI). **(COMPLETADO)**
- **Carrusel categorías Coverflow 3D**: navegación por click + edición admin + descripciones auto/manual. **(COMPLETADO; iteration_21 100%)**
- **Carrito estilo Amazon**: confirmación dentro del drawer + carruseles + “Seguir comprando” + pagos por rol + panel de mensajes al cliente. **(COMPLETADO; iteration_23 100%)**
- **Recomendados por EcoAndes** en Home + tienda móvil 2 columnas + cards móvil + logout destacado. **(COMPLETADO; verificación visual)**

### Objetivos del scope mayor (estado actual)
- **Fase 1 (P0): Catálogo + Precios + IVA (Excel‑driven)**
  - **Estado:** **COMPLETADO**.
- **Fase 2 (P0): Motor de envíos (V1/V2/V3)** por tipo de usuario + zona + peso.
  - **Estado:** **COMPLETADO (V3)** + validado (shipping_config version=3).
- **Fase 3 (P1): Métodos de pago (V1/V2)** por rol (sin contrareembolso) + scaffolding.
  - **Estado:** **COMPLETADO (V2)**.
  - **Operativa real (pendiente de credenciales/dominio):**
    - PayPal sandbox sin credenciales.
    - Resend restringido hasta verificar dominio (solo permite envíos con dominio verificado).
- **Fase 4 (P1): SEO + GEO** multi‑idioma.
  - **Estado:** **EN PROGRESO** (infra completada; pendiente spot-check y cierre).
- **Fase 5 (P1): Migración P0 de imágenes** a almacenamiento propio (WebP + resize + caché 1 año).
  - **Estado:** **PENDIENTE**.
- **Fase 6 (P0/P1): SEO Manual + Nombres Legacy + Redirecciones**
  - **Estado:** **COMPLETADO**.

---

## 2) Pasos de Implementación

### Fase 1 — POC (Core UI Modernization) — **COMPLETADO**
(Se mantiene igual que en la versión anterior del plan.)

---

### Fase 2 — Desarrollo V1 (UI Modernization completa) — **COMPLETADO**
(Se mantiene igual que en la versión anterior del plan.)

---

### Fase 3 — Blogs (12 posts en `blogPosts.js`) — **COMPLETADO**
(Se mantiene igual que en la versión anterior del plan.)

---

### Fase 4 — Testing end‑to‑end (Phase G) — **COMPLETADO**
(Se mantiene igual que en la versión anterior del plan.)

---

### Fase 5 — Catálogo + Precios + IVA (Excel‑driven) — **COMPLETADO (P0)**
(Se mantiene igual que en la versión anterior del plan.)

---

### Fase 6 — Motor de Envíos (V1) — **COMPLETADO (P0)**
- Existe `core/shipping.py` con detección de zonas y reglas.

**Actualización v2 (Lote 14) — COMPLETADA:** ver Fase 16.

**Actualización v3 (Lote 17) — COMPLETADA:** ver Fase 19.

---

### Fase 7 — Métodos de Pago (V1) — **COMPLETADO (P1)**
- Existe lógica de métodos de pago + UI.

**Actualización v2 (Lote 14) — COMPLETADA:** ver Fase 16.

---

### Fase 8 — SEO + GEO (multi‑idioma) — **EN PROGRESO (P1)**
(Se mantiene igual que en la versión anterior del plan.)

---

### Fase 9 — Migración P0 de Imágenes — **PENDIENTE (P1)**
(Se mantiene igual que en la versión anterior del plan.)

---

### Fase 10 — SEO Manual + Nombres Legacy + Redirecciones — **COMPLETADO (P0/P1)**
(Se mantiene igual que en la versión anterior del plan.)

---

### Fase 11 — Lote 9: UX + Operaciones — **COMPLETADO (2026-08)**
(Se mantiene igual que en la versión anterior del plan.)

---

### Fase 12 — Lote 10: Recuperación de Carritos Abandonados — **COMPLETADO (2026-08)**
(Se mantiene igual que en la versión anterior del plan.)

---

### Fase 13 — Lote 11 — **COMPLETADO (2026-08)**
(Se mantiene igual que en la versión anterior del plan.)

---

### Fase 14 — Lote 12 — **COMPLETADO (2026-08)**
(Se mantiene igual que en la versión anterior del plan.)

---

### Fase 15 — Lote 13 — **COMPLETADO (2026-08)**
(Se mantiene igual que en la versión anterior del plan.)

---

### Fase 16 — Lote 14: Envíos/Pagos/Reembolsos/Registro (v2) — **COMPLETADO (2026-08)**
> **Estado:** **COMPLETADO (implementado + validado)**.

Entregables principales (v2):
1) **Reglas de envío B2C/B2B** con umbrales diferenciados:
   - Retail: envío gratis desde **50€ (IVA incl.)** en ES/PT peninsular + Baleares.
   - Profesional verificado: envío gratis desde **150€ base imponible (sin IVA)** en ES/PT peninsular + Baleares.
2) **Tarifas por peso desde Excel** `portes_b2b.xlsx` (importe neto, sin IVA) + **IVA envío 21%** siempre.
3) **Manual quote** para Canarias/Ceuta/Melilla/Francia y resto de países: pedido **sin pago** (“Pendiente portes”) con flujo admin.
4) **Métodos de pago** por rol/validación server-side:
   - Retail / invitado / profesional NO verificado: **Tarjeta (Stripe) + PayPal**.
   - Profesional verificado: **4 métodos** (Tarjeta, PayPal, Transferencia, Otro/Confirming).
   - Pickup: siempre **Tarjeta + PayPal**.
5) **Reembolsos** con desglose fiscal (productos vs envío, envío 21%) + corrección de ruta en frontend.
6) **Registro profesional**: mensaje opcional con placeholder solicitado.
7) **Revisión de integraciones** (test): Stripe OK en test; Resend restringido hasta verificar dominio; Verifactu no implementado.

**Nota post‑v2 (bug real detectado y corregido):**
- El cálculo de portes por peso no subía en algunos casos porque ciertas variaciones carecían de `weight_kg`. Se hizo backfill total (389/389 variaciones) + migración de carritos guardados + fallback parser. **(COMPLETADO)**

---

### Fase 17 — Lote 15: Carrito estilo Amazon + UX móvil + Mensajes a cliente — **COMPLETADO (2026-08)**
> **Estado:** **COMPLETADO (implementado + validado; pendiente confirmación de usuario)**.

(Se mantiene igual que en la versión anterior del plan.)

---

### Fase 18 — Lote 16: Recomendados EcoAndes + UX móvil tienda/cartas + logout destacado — **COMPLETADO (2026-08)**
> **Estado:** **COMPLETADO (implementado + validado; pendiente confirmación de usuario)**.

(Se mantiene igual que en la versión anterior del plan.)

---

### Fase 19 — Lote 17: Envíos retail v3 + verificación dirección + reembolsos tipo WooCommerce + solicitar factura + buscador + menú móvil + paginación tienda — **COMPLETADO (2026-08)**
> **Estado:** **COMPLETADO** (implementado + validado; iteration_24 backend 100% 13/13; frontend 15/16, issue LOW confirmado como falso negativo por verificación manual).

> **Nota de scope:** la **barra inferior fija de iconos en móvil fue descartada** por el usuario.

#### 19.1 Envíos retail v3 (cambio de regla) — **COMPLETADO**
**Regla (confirmada e implementada):**
- Particulares (retail):
  - Si el pedido (IVA incl.) es **< 50€** → **porte único**: **4,12€ (sin IVA)** → **4,99€** con IVA 21%.
  - Si el pedido es **≥ 50€** → **envío gratis**.
  - **Se elimina la tabla por kilos para particulares** (tabla Excel queda solo para profesionales).
- Profesionales verificados:
  - Se mantiene: envío gratis desde **150€ base imponible** (península/Baleares) y **tabla por peso Excel** por debajo.
- Canarias / destinos fuera península:
  - Se mantiene **presupuesto manual** y orden sin pago hasta cotización.

**Implementación realizada:**
- `backend/core/shipping.py`:
  - Migración config `version: 2 → 3`.
  - Retail ES/PT/BAL pasa a `flat_with_free_threshold` con `flat_fee = 4.12` (net) y `free_min_amount = 50` (basis `total_with_vat`).
- Textos/FAQ actualizados.

#### 19.2 Verificación de dirección en Checkout — **COMPLETADO**
**Objetivo:** reducir direcciones inválidas sin bloquear pedidos por falsos negativos.

**Implementación realizada:**
- `frontend/src/lib/esPostal.js`:
  - Mapa de provincias por prefijo CP (01–52).
  - Validación CP español.
  - Autocompletado de provincia por CP.
- `frontend/src/pages/Checkout.jsx`:
  - **Bloqueo** por entradas claramente inválidas:
    - CP ES inválido.
    - Teléfono con menos de 9 dígitos.
    - Calle demasiado corta.
  - **Verificación soft** (no bloqueante) con Nominatim:
    - `GET /api/orders/verify-address`.
    - Si `found=false` → warning amber + requiere **segundo click de confirmación**.
- `backend/routes/orders.py`:
  - `GET /api/orders/verify-address` proxy hacia Nominatim (User-Agent EcoAndes).

#### 19.3 Reembolsos tipo WooCommerce (cliente y admin, por producto) — **COMPLETADO**
**Requisito (confirmado e implementado):**
- Cliente: botón visible por pedido “Solicitar reembolso” → modal para:
  - todo el pedido, o
  - 1/varios productos con cantidad,
  - motivo opcional.
  - Solicitud llega a EcoAndes para revisión (no reembolso automático).
- Admin: reembolso por líneas (sku/qty/importes editables), múltiples reembolsos parciales por pedido.
- **Envío solo se devuelve automáticamente** en reembolso total del pedido (aún editable/forzable por admin).

**Implementación realizada:**
- `POST /api/orders/{id}/refund-request` (owner auth): crea `order.refund_request` con status pending; evita duplicados; email interno.
- `POST /api/admin/orders/{id}/refund`:
  - acepta `items[]` por sku/qty/amount + flags de envío.
  - guarda `order.refunds[]`, `order.refunded_total`, `order.partially_refunded`.
  - status `Reembolsado` solo cuando el total del pedido está reembolsado.
  - si había solicitud pendiente → la marca como `processed`.
- UI:
  - `/cuenta`: modal de solicitud por pedido.
  - `AdminOrderDetail`: UI por producto con qty e importes, envío editable, historial de reembolsos, alert de solicitud del cliente con botón “Precargar esta selección”.

#### 19.4 Profesionales: “Solicitar factura” — **COMPLETADO**
- `/cuenta` (profesional): botón “Solicitar Factura” por pedido.
- `POST /api/orders/{id}/invoice-request`:
  - solo profesional (o admin), owner check.
  - guarda `order.invoice_request` pending y envía aviso interno.
- Admin: badge “Factura solicitada” en detalle pedido.

#### 19.5 Buscador frontend (móvil y UX) — **COMPLETADO**
- Placeholder: “¿Qué buscas hoy?” (7 idiomas).
- Móvil: buscador **siempre visible** bajo la barra superior.
- Anti-zoom iOS: input `font-size: 16px` en móvil.

#### 19.6 Menú lateral móvil (estética) — **COMPLETADO**
- Menú hamburger rediseñado con:
  - panel lateral con backdrop,
  - tarjeta de usuario / acciones login+registro,
  - enlaces agrupados con iconos y badges,
  - botón logout terracota.
- Fix técnico: render por `createPortal(document.body)` para evitar clipping por `backdrop-blur` del header.

#### 19.7 Tienda: categorías en desplegable móvil + paginación global — **COMPLETADO**
- Móvil: categorías en desplegable (`shop-categories-toggle` + panel).
- Todas las vistas: paginación 28 productos/página (≈7 páginas con el catálogo actual), reset con filtros/búsqueda y scroll-to-top.
- Escritorio: se mantienen chips + sidebar.

---

## 3) Próximas Acciones (inmediatas)
1) **Cierre Fase 8 (SEO/GEO):** spot-check 10–15 productos (ES/EN/FR) y correcciones manuales.
2) **Fase 9 (P1): migración de imágenes** (WebP + caché 1 año).
3) **Operativa emails (Resend):** verificar dominio y actualizar `SENDER_EMAIL` a dominio verificado.
4) **PayPal sandbox:** añadir `PAYPAL_CLIENT_ID` y `PAYPAL_SECRET` (sandbox) si se quiere habilitar PayPal en el entorno preview.
5) **Verifactu:** definir alcance y estrategia de integración.
6) **Descuentos/ofertas (futuro):**
   - Añadir UI de admin para `compare_at_price`.
   - Activar automáticamente “Ofertas para ti en [Categoría]” del drawer al existir descuentos.

---

## 4) Criterios de Éxito

**Se mantienen los criterios anteriores**, y se consolidan los de Fase 19 (ya cumplidos):
- Retail shipping v3:
  - <50€ → 4,99€ (IVA incl.)
  - ≥50€ → gratis
  - sin tabla por peso para retail.
- Checkout:
  - bloquea CP/teléfono claramente inválidos,
  - advierte direcciones no encontradas y permite continuar con doble confirmación.
- Reembolsos:
  - Cliente puede solicitar por producto o pedido completo.
  - Admin puede ejecutar parcial/total; envío solo se devuelve automáticamente en reembolso total.
  - Montos editables por admin; reembolsos múltiples por pedido.
- Profesionales: botón “Solicitar factura” por pedido con aviso a info@productosecoandes.com.
- Buscador móvil siempre visible, placeholder correcto y sin zoom al escribir.
- Menú lateral móvil mejorado y sin clipping.
- Tienda:
  - categorías en desplegable móvil,
  - paginación 28/página en todas las vistas.

---

## 5) Clonación a nuevo entorno (2026-07) — COMPLETADO
(Se mantiene igual que en la versión anterior del plan.)

---

## 6) Mejoras Dashboard + Credenciales (2026-07) — COMPLETADO
(Se mantiene igual que en la versión anterior del plan.)

---

## 7) Lote de 12 mejoras (2026-07) — COMPLETADO
(Se mantiene igual que en la versión anterior del plan.)

---

## 8) Lote de 7 mejoras (mensaje 338) — **COMPLETADO (2026-08)**
(Se mantiene igual que en la versión anterior del plan.)

---

## 9) Lote 8 — **Editor SEO Manual + Aplicar Nombres Legacy + Redirecciones** — **COMPLETADO (2026-08)**
(Se mantiene igual que en la versión anterior del plan.)
