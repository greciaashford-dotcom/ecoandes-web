# EcoAndes BIO — Plan de Continuación (UI → Blogs → Testing → Catálogo/Precios/IVA → Envíos → Pagos → SEO/GEO → Imágenes → **SEO Manual + Nombres Legacy + Redirecciones** → **UX/Operaciones (Lote 9)** → **Recuperación de Carritos (Lote 10)** → **Lote 11 (Splash + Recetas + Media links + Emails + Hero dots + 2º recordatorio + Links universales)** → **Fase 14 / Lote 12 (Blog Admin + Site Images Admin + Bug carrusel categorías)** → **Fase 15 / Lote 13 (Carrusel Coverflow 3D de categorías)** → **Fase 16 / Lote 14 (Envíos/Pagos/Reembolsos/Registro: v2)**)

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
- **Fase 2 (P0): Motor de envíos (V1)** por tipo de usuario + zona + peso, administrable vía JSON.
  - **Estado:** **COMPLETADO** (V1) + validado E2E.
- **Fase 3 (P1): Métodos de pago (V1)** por rol (sin contrareembolso) + scaffolding.
  - **Estado:** **COMPLETADO** (V1). Credenciales/operativa real: **pendiente de verificación**.
- **Fase 4 (P1): SEO + GEO** multi‑idioma.
  - **Estado:** **EN PROGRESO** (infra completada; pendiente spot-check y cierre).
- **Fase 5 (P1): Migración P0 de imágenes** a almacenamiento propio (WebP + resize + caché 1 año).
  - **Estado:** **PENDIENTE**.
- **Fase 6 (P0/P1): SEO Manual + Nombres Legacy + Redirecciones**
  - **Estado:** **COMPLETADO** (implementado + verificado).
- **Fase 7 (P0/P1): UX + Operaciones (Lote 9)**
  - **Estado:** **COMPLETADO** + validado E2E (**iteration_17 100%**).
- **Fase 12 (P0/P1): Recuperación de Carritos Abandonados (Lote 10)**
  - **Estado:** **COMPLETADO** + validado E2E (**iteration_18/19**).
- **Fase 13 (P0/P1): Lote 11 (Splash/Recetas/Emails/Links)**
  - **Estado:** **COMPLETADO** + validado E2E (**iteration_19 100%**).
- **Fase 14 (P0/P1): Blog Admin + Site Images Admin + bug carrusel categorías**
  - **Estado:** **COMPLETADO** + validado E2E (**iteration_20 100%**).
- **Fase 15 (P0/P1): Coverflow 3D categorías**
  - **Estado:** **COMPLETADO** + validado E2E (**iteration_21 100%**).

### Fase 16 / Lote 14 — Envíos/Pagos/Reembolsos/Registro (v2)
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
6) **Registro profesional**: mensaje opcional con placeholder solicitado, persistido y incluido en email interno.
7) **Revisión de integraciones** (test): Stripe OK en test; Resend restringido hasta verificar dominio; Verifactu no implementado.

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

#### 16.1 Reglas de negocio implementadas (fuente: conversación)
**Zonas cubiertas por cálculo automático (solo):**
- **España/Portugal peninsular + Baleares**.

**Retail (B2C):**
- Envío gratis desde **50€ (IVA incl.)**.
- Por debajo de 50€: **tarifa por peso del Excel**.

**Profesional verificado (B2B):**
- Envío gratis desde **150€ base imponible (sin IVA)**.
- Por debajo de 150€: **tarifa por peso del Excel**.

**Profesional NO verificado:**
- Compra con condiciones de **retail** (tipo efectivo retail para envíos y pagos).

**Canarias/Ceuta/Melilla y cualquier otro destino fuera de ES/PT peninsular+Baleares (incluye Francia y resto de países):**
- **Presupuesto manual** (peso/volumen/destino) y pedido **sin pago**.
- Flujo confirmado e implementado: estado **“Pendiente portes”** + `payment_status = awaiting_quote`.

**Tarifario Excel `portes_b2b.xlsx` (sin IVA):**
- 0–2 kg: 4
- >2–5 kg: 6
- >5–10 kg: 10
- >10–15 kg: 15
- >15–20 kg: 20
- >20–25 kg: 23
- >25–30 kg: 26
- >30–35 kg: 29
- >35 kg: 29 (porte máximo / cap)

**IVA del envío:** siempre **21%**.

**Peso para el cálculo:**
- Usa `weight_kg` si existe.
- Si falta, deriva del **formato** (parser para “150 g”, “1 kg”, “500 ml”…), implementado en backend + `CartContext`.

#### 16.2 Implementación técnica (backend) — COMPLETADO
1) `backend/core/shipping.py`
   - Shipping config v2 con reglas y escala Excel.
   - IVA del envío 21% (campos: `shipping_cost_ex_vat`, `shipping_vat`, `shipping_cost` (bruto)).
   - Detección de zonas:
     - Baleares (07) incluido en ES/PT/BAL.
     - Canarias (35/38), Ceuta (51), Melilla (52) → manual_quote.
     - FR y resto países → manual_quote.
   - Migración automática de config v1→v2 (`version: 2` verificada en DB).

2) `backend/routes/orders.py`
   - Métodos de pago permitidos por rol y delivery:
     - Retail/guest/pro no verificado: stripe + paypal.
     - Pro verificado: stripe + paypal + transfer + other.
     - Pickup: stripe + paypal.
   - Flujo manual_quote:
     - Pedido creado sin pago: `status = "Pendiente portes"`, `payment_method = "pending_quote"`, `payment_status = "awaiting_quote"`.
   - Endpoint admin para fijar portes:
     - `PATCH /api/orders/admin/{id}/shipping` con `shipping_cost_ex_vat`.
     - Recalcula total, aplica IVA 21% del envío, cambia estado a “Pendiente” y `payment_status` a “pending”.

3) `backend/routes/payments.py`
   - Bloqueo explícito de Stripe/PayPal si `payment_status == awaiting_quote`.

4) `backend/routes/refunds.py`
   - Se añade desglose fiscal de reembolso en el documento (`breakdown`).

5) `backend/routes/auth.py` + `backend/core/models.py`
   - Campo `message` opcional en registro profesional.

6) `backend/core/mailer.py`
   - Avisos de pedido/empresa adaptados para “Pendiente portes”.
   - Email interno de registro profesional incluye el mensaje opcional.

7) `backend/core/utils.py`
   - `calc_shipping` legacy neutralizado.
   - Parser `parse_weight_from_format()` añadido.

#### 16.3 Implementación técnica (frontend) — COMPLETADO
1) `frontend/src/pages/Checkout.jsx`
   - Visibilidad de pagos:
     - guest/retail/unverified pro → solo Tarjeta + PayPal.
     - verified pro → 4 métodos.
   - Manual quote (Canarias/outside):
     - Reemplaza métodos de pago por aviso.
     - CTA cambia a “Confirmar pedido (portes a presupuestar)”.
     - Resumen muestra “A presupuestar” y total “(sin portes)”.
   - Desglose IVA del envío mostrado (línea “Portes: base + IVA 21%”).

2) `frontend/src/components/CartDrawer.jsx`
   - Barra y mensaje de envío gratis por rol:
     - retail: 50€ (IVA incl.)
     - pro verificado: 150€ (base imponible).

3) `frontend/src/pages/Register.jsx`
   - Textarea de mensaje opcional para profesionales con placeholder solicitado.

4) `frontend/src/pages/PaymentSuccess.jsx`
   - Estado “quote” para pedidos sin pago (pendiente de portes).

5) `frontend/src/pages/CustomerService.jsx`
   - FAQ de envíos actualizada con reglas nuevas.

6) Admin
   - `AdminOrderDetail.jsx`: panel “Pendiente portes” + fijar portes + desglose fiscal de totales y reembolso.
   - Se corrige ruta de reembolso a `POST /api/admin/orders/{id}/refund`.
   - `AdminOrders.jsx` + `AdminDashboard.jsx/StatusPill`: nuevo estado “Pendiente portes”.

#### 16.4 Revisión de integraciones (punto 6 del lote) — COMPLETADO
- **Stripe:** activo en modo **TEST** (API OK, `livemode=false`).
- **Resend:** clave activa pero **restringida**; solo permite envíos de test a la cuenta propietaria hasta verificar dominio.
  - `SENDER_EMAIL` actual: `onboarding@resend.dev`.
  - Acción pendiente: verificar dominio en Resend para permitir envíos a clientes.
- **Verifactu:** **no implementado** (sin rutas/imports/variables detectadas). Requiere un lote específico si se desea integrar.
- **PayPal:** `PAYPAL_MODE=sandbox`, pero `PAYPAL_CLIENT_ID`/`PAYPAL_SECRET` están vacíos → pagos PayPal no operativos hasta configurar credenciales sandbox.

#### 16.5 Validación / Testing (obligatorio tras implementación) — COMPLETADO
- **iteration_22.json**:
  - Backend: **100% (60/60)**.
  - Frontend: verificado manualmente con Playwright:
    - Guest: 2 métodos de pago.
    - Desglose IVA del envío y tramo de peso visibles.
    - Canarias: aviso “Portes pendientes de presupuesto”, submit “Confirmar pedido…”, resumen “A presupuestar”.
- Nota: el supuesto problema de “cart persistence” fue un artefacto de automatización (overlay splash + toast intercepting). Persistencia real OK (`eco_cart_v1`).

---

## 3) Próximas Acciones (inmediatas)
1) **Cierre Fase 8 (SEO/GEO):** spot-check 10–15 productos (ES/EN/FR) y correcciones manuales.
2) **Fase 9 (P1): migración de imágenes** (WebP + caché 1 año) + completar productos sin foto.
3) **Operativa emails (Resend):** verificar dominio y actualizar `SENDER_EMAIL` a dominio verificado para permitir envíos a clientes.
4) **PayPal sandbox:** añadir `PAYPAL_CLIENT_ID` y `PAYPAL_SECRET` (sandbox) si se quiere habilitar PayPal en el entorno preview.
5) **Verifactu:** si se quiere integrar, definir alcance (endpoints, modos test/prod, mapeo de facturas/tickets, eventos desde pedidos/reembolsos).

---

## 4) Criterios de Éxito

**Se mantienen los criterios anteriores**, y se consolidan los de Fase 16 como cumplidos:
- Retail (ES/PT/BAL): envío gratis desde **50€ IVA incl**; por debajo, tarifa por peso Excel.
- Profesional verificado (ES/PT/BAL): envío gratis desde **150€ sin IVA**; por debajo, tarifa por peso Excel.
- Canarias/Ceuta/Melilla/FR/resto destinos: **pedido sin pago** + estado **“Pendiente portes”** + admin fija portes.
- IVA de envío: **21%** siempre (desglosado en reembolsos/admin).
- Checkout: métodos de pago visibles según reglas (2 vs 4) + bloqueo de pago si `awaiting_quote`.
- Registro profesional: mensaje opcional guardado y visible en notificación a la empresa.
- Integraciones: reporte honesto del estado de Stripe (test OK), Resend (restringido hasta verificar dominio), Verifactu (no integrado), PayPal sandbox (credenciales pendientes).
- Testing E2E: lote v2 cubierto (backend 100% + spot-check frontend).

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
