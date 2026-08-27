# EcoAndes BIO — Plan de Continuación (UI → Blogs → Testing → Catálogo/Precios/IVA → Envíos → Pagos → SEO/GEO → Imágenes → **SEO Manual + Nombres Legacy + Redirecciones** → **UX/Operaciones (Lote 9)** → **Recuperación de Carritos (Lote 10)** → **Lote 11 (Splash + Recetas + Media links + Emails + Hero dots + 2º recordatorio + Links universales)** → **Fase 14 / Lote 12 (Blog Admin + Site Images Admin + Bug carrusel categorías)** → **Fase 15 / Lote 13 (Carrusel Coverflow 3D de categorías)** → **Fase 16 / Lote 14 (Envíos/Pagos/Reembolsos/Registro: v2)** → **Fase 17 / Lote 15 (Carrito estilo Amazon + UX móvil + Mensajes a cliente)**)

## 1) Objetivos

### Objetivos ya completados (iteración anterior)
- Modernizar la UI manteniendo identidad de marca (sage/terracotta/bone) con **bordes redondeados** y **micro‑animaciones** sin romper flujos. **(COMPLETADO)**
- Actualizar el **Blog**: 12 posts mantenidos, ahora gestionables desde dashboard con SEO y JSON‑LD Article. **(COMPLETADO)**
- Ejecutar **testing end‑to‑end** para asegurar estabilidad (checkout/cupón/búsqueda/registro/blogs/UI). **(COMPLETADO)**
- **Carrusel categorías Coverflow 3D**: navegación por click + edición admin + descripciones auto/manual. **(COMPLETADO; iteration_21 100%)**

**Estado (sobre lo anterior):** UI + Blog + Operaciones listos.

### Objetivos del scope mayor (estado actual)
- **Fase 1 (P0): Catálogo + Precios + IVA (Excel‑driven)**
  - **Estado:** **COMPLETADO**.
- **Fase 2 (P0): Motor de envíos (V1/V2)** por tipo de usuario + zona + peso.
  - **Estado:** **COMPLETADO (V2)** + validado.
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
- **Fase 7 (P0/P1): UX + Operaciones (Lote 9)**
  - **Estado:** **COMPLETADO**.
- **Fase 12 (P0/P1): Recuperación de Carritos Abandonados (Lote 10)**
  - **Estado:** **COMPLETADO**.
- **Fase 13 (P0/P1): Lote 11 (Splash/Recetas/Emails/Links)**
  - **Estado:** **COMPLETADO**.
- **Fase 14 (P0/P1): Blog Admin + Site Images Admin + bug carrusel categorías**
  - **Estado:** **COMPLETADO**.
- **Fase 15 (P0/P1): Coverflow 3D categorías**
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
- **Nota:** esta fase se considera completada en su V1.

**Actualización v2 (Lote 14) — COMPLETADA:** ver Fase 16.

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
- El cálculo de portes por peso no subía en algunos casos porque ciertas variaciones carecían de `weight_kg`. Se hizo backfill total (389/389 variaciones) + migración de carritos guardados + fallback parser (formato “150 g”, “1 kg”, “500 ml”…). **(COMPLETADO)**

---

### Fase 17 — Lote 15: Carrito estilo Amazon + UX móvil + Mensajes a cliente — **COMPLETADO (2026-08)**
> **Estado:** **COMPLETADO (implementado + validado; pendiente confirmación de usuario)**.

#### 17.1 Objetivo UX: “Añadir al carrito” estilo Amazon — **COMPLETADO**
**Decisión confirmada:** mantener el **panel lateral deslizante** (CartDrawer), sin redirección a una página aislada.

**Entregado (UX):**
- Confirmación en el propio panel: **bloque verde “Añadido al carrito”** con miniatura y nombre del producto (`cart-added-confirmation`).
- Se eliminó el **toast** de “Añadido al carrito” para evitar que tape botones del drawer.
- Nuevo estado `lastAdded` en `CartContext` para renderizar la confirmación contextual.

#### 17.2 Backend (FastAPI) — recomendaciones para el panel — **COMPLETADO**
**Nuevo endpoint:**
- `GET /api/products/recommendations?product_id=...&viewed=...&limit=...`

**Respuesta:**
```json
{
  "category": "...",
  "related": [...],
  "recommended": [...],
  "explore": [...],
  "offers": [...]
}
```

**Heurística (v1):**
- `related` (cross‑sell): misma categoría, prioriza `best_seller`/`featured`.
- `recommended` (up‑sell): si usuario logueado, categorías de compras previas; fallback `featured` + `best_seller` + top por rating.
- `explore`: historial `viewed` (localStorage `eco_recent_views`) + populares (`best_seller`) + top rating.
- **De-duplicación cross-sección** (un producto no aparece en varias filas) y exclusión del producto seed.

#### 17.3 Frontend — carruseles “Amazon‑like” en el drawer — **COMPLETADO**
**Nuevo componente:**
- `frontend/src/components/CartRecommendations.jsx`

**Entregado (UI):**
- 3 carruseles horizontales modernos (scroll‑snap) dentro del drawer:
  1) Productos relacionados
  2) Recomendado para ti
  3) Explorar más artículos
- Click en una mini‑card navega al producto y **cierra el drawer** (flujo rápido).
- Historial de navegación implementado en `ProductDetail` con localStorage `eco_recent_views`.

#### 17.4 Ofertas para ti en [Categoría] — preparado para el futuro — **COMPLETADO (preparación)**
**Decisión del usuario:** omitir la sección por ahora, y que aparezca automáticamente cuando existan descuentos.

**Preparación entregada:**
- Campo opcional `compare_at_price` (precio anterior) añadido al modelo de producto.
- El endpoint devuelve `offers` solo si existen productos con `compare_at_price > precio retail actual`.
- Las mini-cards soportan badge de % y precio tachado cuando `offers` empiece a tener datos.

#### 17.5 UX móvil: icono de cuenta + reubicación favoritos — **COMPLETADO**
- En móvil se muestra icono **persona** (`nav-mobile-account`), verde con punto cuando hay sesión (`nav-mobile-account-dot`).
- El icono **corazón/favoritos** se oculta en el top bar en móvil y queda accesible por menú hamburguesa.

#### 17.6 Carrito: botón “SEGUIR COMPRANDO” — **COMPLETADO**
- En el footer del drawer:
  - Botón **SEGUIR COMPRANDO** (`cart-continue-shopping-btn`) encima de
  - **FINALIZAR COMPRA** (`cart-checkout-btn`).

#### 17.7 Catálogo/UI: cards y home — **COMPLETADO**
- **ProductCard:** eliminada la etiqueta de categoría.
- **Home (Destacados):** grid a **2 columnas en móvil**.

#### 17.8 Admin: mensaje personalizado al cliente — **COMPLETADO**
- En `AdminOrderDetail` se añadió panel **“Mensaje al cliente”** con asunto opcional + textarea.
- Endpoint: `POST /api/orders/admin/{id}/message`.
- Envío por email con plantilla corporativa (`send_custom_customer_message` en `core/mailer.py`).
- Registro en `order.customer_messages[]` + listado en UI.
- Si Resend está restringido, la UI informa (mensaje se registra igualmente con `sent=false`).

#### 17.9 i18n — **COMPLETADO**
- Nuevas claves en 7 idiomas (`es,en,fr,it,pt,ja,zh`) bajo `cart.*`:
  - `addedToCart`, `continueShopping`, `related`, `recommended`, `explore`, `offersIn`.

#### 17.10 Testing / Evidencia — **COMPLETADO**
- Testing agent: `iteration_23.json` — **backend 100% (10/10)** y **frontend 100%**, sin action items.
- Verificación visual: drawer desktop (confirmación + carruseles) y móvil (icono persona + 2 columnas).
- Datos de prueba limpiados.

---

## 3) Próximas Acciones (inmediatas)
1) **Cierre Fase 8 (SEO/GEO):** spot-check 10–15 productos (ES/EN/FR) y correcciones manuales.
2) **Fase 9 (P1): migración de imágenes** (WebP + caché 1 año).
3) **Operativa emails (Resend):** verificar dominio y actualizar `SENDER_EMAIL` a dominio verificado.
4) **PayPal sandbox:** añadir `PAYPAL_CLIENT_ID` y `PAYPAL_SECRET` (sandbox) si se quiere habilitar PayPal en el entorno preview.
5) **Verifactu:** definir alcance y estrategia de integración.
6) **Descuentos/ofertas (futuro):** añadir UI de admin para `compare_at_price` y activar sección “Ofertas” del drawer automáticamente.

---

## 4) Criterios de Éxito

**Se mantienen los criterios anteriores**, y se confirman los de Fase 17 (ya implementados):
- “Añadir al carrito” no redirige: confirmación y recomendaciones dentro del panel.
- Carruseles muestran productos válidos, sin duplicados y excluyendo el producto seed.
- UX móvil mejorada (persona visible, favoritos accesibles desde menú).
- Carrito con “Seguir comprando” + “Finalizar compra”.
- ProductCard sin categoría.
- Home destacados a 2 columnas en móvil.
- Admin permite enviar mensaje personalizado al cliente y registrar el envío (sent true/false según Resend).

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
