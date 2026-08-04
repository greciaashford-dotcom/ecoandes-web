# EcoAndes BIO — Plan de Continuación (UI → Blogs → Testing → Catálogo/Precios/IVA → Envíos → Pagos → SEO/GEO → Imágenes → **SEO Manual + Nombres Legacy + Redirecciones** → **UX/Operaciones (Lote 9)**)

## 1) Objetivos

### Objetivos ya completados (iteración anterior)
- Modernizar la UI manteniendo identidad de marca (sage/terracotta/bone) con **bordes redondeados** y **micro‑animaciones** sin romper flujos. **(COMPLETADO)**
- Actualizar el **Blog**: mejorar 6 posts existentes y crear 6 nuevos (12 total) con imágenes WebP locales y fuentes citadas. **(COMPLETADO)**
- Ejecutar **testing end‑to‑end** para asegurar estabilidad (checkout/cupón/búsqueda/registro/blogs/UI). **(COMPLETADO)**

**Estado (sobre lo anterior):** UI + Blog listos. Testing general anterior: **98.5% PASS** (Backend 36/37; Frontend 100%).

### Objetivos del scope mayor (estado actual)
- **Fase 1 (P0): Catálogo + Precios + IVA (Excel‑driven)**
  - Alinear productos existentes con los Excel, eliminar lo que no corresponda y crear lo que falte.
  - Modelar IVA, pesos y formatos para habilitar reglas de envíos y checkout correctos.
  - **Estado:** **COMPLETADO**.
- **Fase 2 (P0): Motor de envíos** por **tipo de usuario + zona + peso**, administrable vía JSON.
  - **Estado:** **COMPLETADO** + validado E2E.
- **Fase 3 (P1): Métodos de pago** por rol (sin contrareembolso) + scaffolding para credenciales futuras.
  - **Estado:** **COMPLETADO** (lógica + UI + validación server‑side). Credenciales **pendientes**.
- **Fase 4 (P1): SEO + GEO** por ficha de producto, con generación automática multi‑idioma y render en frontend.
  - **Estado:** **EN PROGRESO** (infraestructura completada; generación IA en background; protección por `manual=true`).
- **Fase 5 (P1): Migración P0 de imágenes** a almacenamiento propio (WebP + resize + caché 1 año) una vez estabilizado el catálogo.
  - **Estado:** **PENDIENTE**.
- **Fase 6 (P0/P1): SEO Manual + Nombres Legacy + Redirecciones**
  - Editor admin para **SEO manual por idioma (7 idiomas)**.
  - Aplicación de **nombres legacy** (nombre visible + slug/URL) para conservar SEO histórico.
  - Redirecciones de slugs antiguos → slugs nuevos (alias + replace en SPA).
  - Blindaje para que la auto‑reconciliación Excel no revierta los cambios.
  - **Estado:** **COMPLETADO** (implementado + verificado).
- **Fase 7 (P0/P1): UX + Operaciones (Lote 9)**
  - Mejoras móviles (carrusel y ficha técnica), ajustes de spacing, checkout UI, registro UX/legal, automatización email newsletter, y borrado CRM.
  - **Estado:** **COMPLETADO** + validado E2E (**iteration_17 100%**).

---

## 2) Pasos de Implementación

### Fase 1 — POC (Core UI Modernization) — **COMPLETADO**
**User stories (POC):**
1. Como usuario, quiero que botones y tarjetas respondan con animaciones sutiles.
2. Como usuario, quiero esquinas redondeadas en componentes clave.
3. Como usuario, quiero hovers fluidos sin CLS.
4. Como usuario, quiero rendimiento estable.
5. Como admin/usuario, quiero que nada funcional se rompa.

**Acciones ejecutadas:**
- Ajustado `--radius` en `/app/frontend/src/index.css`: `0.25rem → 0.85rem`.
- Tokens UI: `--shadow-sm/md/lg`, `--ease-soft`.
- Utilidades: `.hover-lift`, `.card-soft`, `.press`, `.reveal-fade`, `.reveal-scale`.
- `prefers-reduced-motion`.

---

### Fase 2 — Desarrollo V1 (UI Modernization completa) — **COMPLETADO**
**Cambios principales aplicados:**
- Botones pill, inputs redondeados y focus ring consistente.
- `ProductCard`, `Navbar`, `SearchBar`, `Blog` y `BlogPost` modernizados.

**Checkpoint:** Home / Tienda / Blog / Post Blog: OK.

---

### Fase 3 — Blogs (12 posts en `blogPosts.js`) — **COMPLETADO**
- 12 entradas completas con `cover: "/blog/*.webp"`, `sources` (FAO/EFSA/USDA/NIH/Harvard/BEDCA), disclaimer y `related_query` exacto.
- `BlogPost.jsx` renderiza bloque “Fuentes” y productos relacionados.

---

### Fase 4 — Testing end‑to‑end (Phase G) — **COMPLETADO**
- `testing_agent_v3` (backend + frontend) → **98.5% PASS**.
- Incidencia menor preexistente: un producto sin campos opcionales `badges/web_rating/web_reviews` (LOW).

---

### Fase 5 — Catálogo + Precios + IVA (Excel‑driven) — **COMPLETADO (P0)**

#### 5.1 Fuente de datos (confirmado)
- **Excel PRO** = master: contiene `FAMILIA`, `Código (SKU)`, `Descripción`, `Formato`, `IVA`, `Origen*`, **precio profesional sin IVA**, EAN.
- **Excel WEB**: contiene `Código (SKU)`, `Descripción`, `Formato`, `Grupo (Retail/Granel)`, **PVP sin IVA**, EAN, **peso en kg**.
- Cobertura real tras análisis:
  - PRO: **388 SKUs**
  - WEB: **390 SKUs**
  - Intersección: **388**
  - WEB‑only: **AMG100**, **SGR100** (importados como retail-only).
- Agrupación por producto base: **174 productos base** (agrupando SKUs por prefijo; heurística: “quitar dígitos finales”).

#### 5.2 Reglas de catálogo (confirmadas e implementadas)
- Productos no presentes en Excel → **eliminados de tienda y dashboard** mediante archivado reversible.
- Productos presentes en Excel y no presentes en BD → **creados**.
- Productos presentes en ambos → **sincronizados**:
  - Nombre limpio (sin ruido de formato/pack), categoría (FAMILIA), origen.
  - Formatos/variaciones, EAN.
  - Precios B2C/B2B **sin IVA** + metadato `vat_rate`.
  - Peso por variación (`weight_kg`) + `is_bulk`.

#### 5.3 Entregables técnicos (implementados)
- Importador idempotente:
  - Ruta: `/app/backend/scripts/import_catalog.py`
  - Modo por defecto: **dry-run**; `--commit` aplica.
  - Agrupación: 390 SKUs → **174 productos**.
- Archivado reversible:
  - Colección: `products_archive`.
  - Resultado inicial: **42** productos legacy archivados (verificados como ausentes del Excel).

#### 5.4 Cambios de modelo (implementados)
- Producto:
  - `vat_rate` (4/10/21 y **2%** para sésamo pelado según Excel/cliente)
  - `origin_country`
  - `seo` (estructura: `meta_title`, `meta_description`, `keywords`, `geo_region`, `manual`)
  - `legacy_name_applied`, `slug_aliases`, `previous_name` (para migración SEO legacy)
- Variación:
  - `weight_kg`, `is_bulk`
  - `ean`
  - `available_retail`, `available_professional`

#### 5.5 Motor de precios / IVA (implementado)
- Backend (`/app/backend/routes/products.py`): `_decorate` devuelve:
  - `display_price` y `display_price_ex_vat` en producto y variaciones.
  - B2C: `display_price` **con IVA incluido**.
  - B2B (professional/admin): `display_price` **sin IVA**.
  - `price_includes_vat` para UI.
- Frontend:
  - `price.js` consume `display_price`.
  - `CartContext` guarda: `unit_price`, `unit_price_ex_vat`, `vat_rate`, `weight_kg`.
  - Exposición de totales: `subtotal`, `subtotalExVat`, `subtotalWithVat`, `vatAmount`, `totalWeightKg`, `hasBulk`.
  - Ficha de producto (`ProductDetail.jsx`) muestra nota: **IVA incluido** (B2C) / **Precio sin IVA** (B2B).

#### 5.6 Datos/estado actual (post‑fase)
- Catálogo en BD: **174 productos activos / 390 formatos**.
- IVA sésamo:
  - Sésamo crudo y negro: 4%
  - **Sésamo pelado: 2%** (confirmado por cliente y reflejado desde Excel)
- Imágenes:
  - ~29 productos nuevos carecen de imagen (se resuelve en Fase 9).

#### 5.7 Bug crítico detectado y resuelto (stock)
- Problema: el importador dejaba `stock=0` en productos/variaciones → el frontend deshabilitaba “Añadir al carrito”.
- Solución: stock por defecto **999** en producto y variaciones en el importador; re‑aplicado.
- Estado: **COMPLETADO**.

---

### Fase 6 — Motor de Envíos (zonas + reglas + escala por peso) — **COMPLETADO (P0)**

#### 6.1 Reglas B2C (implementadas)
- ES + PT peninsular + Baleares: ≥ 50€ (**con IVA**) → gratis; si no → 4,99€.
- Francia: ≥ 70€ (**con IVA**) → gratis; si no → 10€.
- Ceuta/Melilla/Canarias: envío bloqueado.
- Otros países (B2C): bloqueado.

#### 6.2 Reglas B2B (implementadas)
- ES + PT peninsular + Baleares:
  - Gratis si **base sin IVA > 150€** y el carrito contiene **solo formatos ≤ 1 kg**.
  - Si existe **cualquier ítem > 1 kg** → siempre coste por escala de peso.
  - Si base sin IVA ≤ 150€ → escala por peso.
  - Ítems < 1 kg: aplican al primer tramo (4€).
  - Límite superior > 100 kg → presupuesto manual.
- Canarias y resto de Europa: coste pendiente (presupuesto manual).

#### 6.3 Detección de zona (implementada)
- País + prefijo postal:
  - 07 Baleares
  - 35/38 Canarias
  - 51 Ceuta
  - 52 Melilla

#### 6.4 Estructura JSON en BD (implementada)
- Colección: `shipping_config` (documento versionado).
- Seed automático en primera llamada.

#### 6.5 Implementación (realizada)
- Motor en `/app/backend/core/shipping.py`:
  - `DEFAULT_SHIPPING_CONFIG`
  - `detect_zone` (por país + prefijo postal)
  - `evaluate_shipping` (flat/free/blocked/manual/escala por peso)
- Endpoint actualizado:
  - `POST /api/orders/shipping-quote` → usa motor y campos: `country`, `postal_code`, `subtotal_with_vat`, `subtotal_ex_vat`, `total_weight_kg`, `has_bulk`.
- Endpoints config:
  - `GET /api/orders/shipping-config` (público)
  - `PUT /api/orders/shipping-config` (admin)
- Pedido (`POST /api/orders`):
  - Recalcula server-side: `subtotal_ex_vat`, `vat_amount`, `subtotal_with_vat`, `total_weight_kg`, `has_bulk`.
  - Bloquea zonas restringidas (HTTP 400).
  - Persiste: `shipping_cost`, `shipping_status`, `shipping_zone`, `total_weight_kg`.
- Frontend Checkout:
  - Envía los datos al motor.
  - Muestra: desglose IVA, estados de envío (gratis/fijo/tramo/bloqueado/manual), y deshabilita el botón si está bloqueado.

#### 6.6 Validación
- Testing `iteration_6`: Backend **15/15 = 100%**, frontend verificado (IVA y checkout).
- Captura E2E confirmada: subtotal IVA incl., envío 4,99€, restante para envío gratis.

---

### Fase 7 — Métodos de Pago (por rol) — **COMPLETADO (P1)**

#### 7.1 Reglas (implementadas)
- Prohibición global: **sin contrareembolso**.
- **B2C (particulares):** Tarjeta (Stripe) / PayPal / Transferencia bancaria.
- **B2B (profesionales):** Tarjeta (Stripe) / PayPal / Transferencia bancaria / **Otro (domiciliación / confirming)**.
- **Restricción por entrega:** si `delivery_method = pickup` → solo **Stripe/PayPal**.

#### 7.2 Backend (implementado)
- `PaymentMethod` extendido: incluye `"other"`.
- Validación server-side en `POST /api/orders` según rol + entrega.
- Stripe/PayPal siguen usando variables de entorno (sin hardcode):
  - `STRIPE_API_KEY`
  - `PAYPAL_CLIENT_ID`, `PAYPAL_SECRET`

#### 7.3 Frontend (implementado)
- Checkout:
  - Transferencia disponible para **B2C y B2B** (solo envío a domicilio).
  - Método **Other** (confirming) visible **solo con envío**.
  - Al seleccionar recogida se resetean `transfer/other` → `stripe`.
- Flujo offline:
  - `transfer` y `other` redirigen a `/pago/success?offline=1&method={transfer|other}`.
  - `PaymentSuccess` muestra mensaje específico para `other`.

#### 7.4 Ajuste aplicado en Lote 9 (UI/Operaciones)
- Etiqueta del método 1: **"Pago con Tarjeta"** (antes “Tarjeta (Stripe)”).
- Logos (sin peticiones externas): **Visa/MasterCard/Amex** inline SVG.
- PayPal con logo inline SVG.
- Nuevo método en UI: **"Otro (Confirming, solo para clientes que llegan a un acuerdo con EcoAndes)"** debajo de Transferencia.
- Validación backend actualizada: `other` permitido en envío a domicilio (no pickup) para todos los roles.

#### 7.5 Pendiente de completar cuando el cliente entregue credenciales/datos
- Stripe: API keys (live/test según entorno).
- PayPal: client id/secret.
- Transferencia: IBAN, beneficiario, banco, concepto y plantilla de email.
- Operativa “Other”: flujo de aprobación/admin, textos legales y comunicación.

---

### Fase 8 — SEO + GEO (multi‑idioma) — **EN PROGRESO (P1)**

#### 8.1 Backend (COMPLETADO)
- `translator.py`:
  - `generate_product_seo(only_missing, batch_size)`.
  - Estado `SEO_STATUS`.
  - Persistencia:
    - ES: `product.seo`
    - Idiomas: `translations.{lang}.seo`
  - **Protección SEO manual:**
    - Si `seo.manual == true` (ES) o `translations.{lang}.seo.manual == true`, ese idioma se **excluye** de la generación IA.
- `products.py`:
  - `_apply_lang` superpone `seo` por idioma.
  - Endpoints admin:
    - `POST /api/products/seo/run?only_missing=true`
    - `GET /api/products/seo/status`

#### 8.2 Frontend (COMPLETADO)
- Componente `/app/frontend/src/components/Seo.jsx` (sin dependencias):
  - `<title>`, metas, OpenGraph/Twitter, canonical, hreflang, JSON‑LD opcional.
  - Fix: evita duplicar “EcoAndes” si el título ya lo contiene.
- Integración:
  - `ProductDetail.jsx`: JSON‑LD Product + Offer/AggregateOffer + `countryOfOrigin`.
  - `Home.jsx`: JSON‑LD Organization.
  - `Shop.jsx`: SEO base de tienda.

#### 8.3 Estado actual de generación (EN CURSO)
- Generación IA arrancada y corriendo en background.
- Nota tras aplicar nombres legacy:
  - Algunos `meta_title/meta_description` generados anteriormente pueden contener nombres antiguos.
  - Se corrigen con el editor manual o re-lanzando IA (respetará `manual=true`).

#### 8.4 Pendiente (para cerrar la fase)
- Esperar a que `SEO_STATUS.running=false` y `done=7/7`.
- Revisión aleatoria de calidad (10–15 productos) en ES/EN/FR.

---

### Fase 9 — Migración P0 de Imágenes (tras SEO estable) — **PENDIENTE (P1)**
**Contexto actual:**
- Parte del catálogo aún usa imágenes externas (hotlink) y ~29 productos nuevos no tienen imagen.

**Objetivo:**
- Descargar imágenes externas → convertir a **WebP** + redimensionar → subir a object storage (`/api/files/...`) → actualizar `image_url`/`gallery`.

**Caché:**
- Subir cache de `/api/files/` a 1 año (`max-age=31536000, immutable`).

**Salvaguarda:**
- Guardar `legacy_image_url` para reversión.

---

### Fase 10 — **SEO Manual (Admin) + Nombres Legacy + Redirecciones 301** — **COMPLETADO (P0/P1)**

#### 10.1 Editor SEO manual (Admin) — **COMPLETADO (P0)**
**Objetivo:** editar por producto y por idioma (7 tabs):
- `meta_title` (con contador recomendado /65)
- `meta_description` (con contador recomendado /170)
- `keywords`
- `geo_region`

**Backend (implementado):**
- `GET /api/products/{id}/seo` (admin)
- `PUT /api/products/{id}/seo` (admin)
  - Guarda `manual=true` para bloquear sobrescritura por IA.

**Frontend (implementado):**
- En `/admin/productos`, botón lápiz junto al punto SEO abre modal `SeoEditorModal`:
  - 7 pestañas: `es,en,fr,it,pt,zh,ja`
  - Guardado por idioma
  - Feedback con toast “SEO guardado · protegido frente a la IA”

#### 10.2 Aplicar nombres legacy (nombre visible + slug) — **COMPLETADO (P0)**
**Regla (confirmada por usuario):**
- El **nombre visible** y el **slug/URL** pasan al **nombre legacy exacto**.

**Fuente:**
- `/app/backend/data/seo_name_mapping.json`
  - `mapping`: 162 pares actuales→legacy
  - `sin_equivalente`: 3 legacy sin equivalente (Albahaca, Harina de Chía, Soja texturizada extra fina)

**Backend (implementado):**
- `POST /api/products/legacy-names/apply` (admin)
  - Soporta `dry_run=true|false`
  - **Aplicado en BD:** 162 renombrados
  - Idempotente (2ª llamada: `applied=0`, `skipped=162`)

**Admin UI (implementado):**
- Botón “Aplicar nombres legacy” en `/admin/productos` para re-ejecución (idempotente).

#### 10.3 Redirecciones (slug antiguo → canónico) — **COMPLETADO (P0)**
**Backend (implementado):**
- `GET /api/products/slug/{slug}`:
  - Busca por `slug`
  - Si no existe, busca por `slug_aliases`
  - Si entra por alias: añade `redirected_from` y `canonical_slug`

**Frontend (implementado):**
- `ProductDetail.jsx`:
  - Si la API devuelve `redirected_from`, hace `navigate(..., { replace: true })` al slug canónico.

#### 10.4 Blindaje contra auto‑reconciliación Excel — **COMPLETADO (P0)**
- `/app/backend/scripts/import_catalog.py`:
  - Si `prior.legacy_name_applied == true`, preserva `name` legacy.
  - Preserva `slug_aliases` y `previous_name`.
  - Dry-run verificado: **162/174** con legacy preservado; **0** a archivar.

#### 10.5 Validación / Testing — **COMPLETADO (P1)**
- `testing_agent_v3` → `iteration_16` sin bugs críticos reales.
- Verificado manualmente (ES): PDP / tienda / búsqueda / admin muestran nombres legacy.

---

### Fase 11 — **Lote 9: UX + Operaciones (8 mejoras)** — **COMPLETADO (2026-08)**

#### 11.1 Alcance
1) Carrusel móvil “Nuestras categorías”: swipe libre con el dedo + reanuda auto-scroll al soltar.
2) Ficha técnica: responsive móvil (botón “DESCARGAR PDF” no se sale) + rediseño estético.
3) Hover del CTA “ABRIR CUENTA B2B”: color hover = `#72a638`.
4) Ajuste de espaciado entre secciones de la home.
5) Email de bienvenida newsletter automático.
6) Borrado desde CRM: clientes, compradores y leads WhatsApp.
7) Registro: textos de botones, orden de campos B2B, aviso AEAT, checkbox privacidad.
8) Checkout: labels y logos de métodos de pago + método “Otro (Confirming…)”.

#### 11.2 Implementación (realizada)
- **(1) Carrusel móvil (CategoryCarousel):**
  - Touch listeners nativos (`touchstart/move/end`) con `passive:false` para bloquear scroll cuando el gesto es horizontal.
  - Bloqueo direccional (si gesto vertical → no secuestra scroll de página).
  - `draggingRef` pausa auto-scroll durante el toque y lo reanuda al soltar.
  - Pointer events quedan para ratón (evita conflictos con touch).
- **(2) Ficha técnica (ProductDetail):**
  - Tarjeta `rounded-2xl` con icono.
  - Botones apilados `flex-col` en móvil (`w-full`) y `flex-row` en desktop.
  - Verificado dentro de 390px.
- **(3) Hover CTA B2B (Home):**
  - `hover:bg-sage-800 hover:text-white` (equivalente `#72a638`).
- **(4) Spacing home (Home + CategoryCarousel):**
  - Reducción de espacios grandes: `py-20 → py-10/12`, `mt-20 → mt-6/8`, etc.
- **(5) Bienvenida newsletter (backend):**
  - `send_newsletter_welcome` en `core/mailer.py`.
  - Disparo async en `POST /api/newsletter/subscribe`.
  - **Gate conocido:** Resend restringe envíos a emails “own address” hasta verificar dominio.
- **(6) Borrados CRM:**
  - `DELETE /api/admin/users/{user_id}` con protecciones (no self-delete, no admins).
  - `DELETE /api/orders/admin/buyers/{email}` (solo ficha CRM; no borra pedidos).
  - Leads WhatsApp: delete ya existía; se añadió feedback con toasts.
  - UI: iconos papelera + confirm en `AdminCustomers` y `AdminBuyers`.
- **(7) Registro (Register + i18n):**
  - Botones: “SOY PARTICULAR” y “SOY PROFESIONAL B2B”.
  - Profesional: empieza con “Nombre de la Empresa” + “CIF/NIF” al lado, luego “Tipo de Negocio”, luego aviso AEAT.
  - Checkbox requerido “Acepto la Política de Privacidad de EcoAndes” (submit deshabilitado si no está marcado).
  - Textos actualizados en 7 idiomas.
- **(8) Checkout (Checkout + backend payments):**
  - “Pago con Tarjeta” + logos Visa/MasterCard/Amex (SVG inline).
  - PayPal con logo (SVG inline).
  - Método “Otro (Confirming…)” añadido debajo de Transferencia.
  - Backend: `_allowed_payment_methods` actualizado (other permitido en shipping; pickup sigue solo Stripe/PayPal).

#### 11.3 Validación
- `testing_agent_v3` → `iteration_17`:
  - Backend **100% (12/12)**
  - Frontend móvil **100% (8/8)**
  - Frontend desktop **100% (11/11)**
  - Cero bugs.
- Limpieza post-testing:
  - Eliminados: suscriptores test, pedido **ECO-4** de test, buyers de test.

---

## 3) Próximas Acciones (inmediatas)
1. **Cerrar Fase 8 (SEO/GEO):** esperar fin de generación IA + spot-check + corregir manualmente lo que sea necesario (ya existe editor 7 idiomas).
2. **Fase 9 (P1): migración de imágenes** (P0) una vez se congelen los productos finales.
3. **Operativa newsletter (Resend):** verificar dominio de envío para habilitar el email de bienvenida a cualquier destinatario.
4. (Opcional) Reporte admin de “productos con SEO manual” + botón “reset manual” por idioma.
5. Testing E2E adicional tras migración de imágenes y/o tras finalizar SEO IA.

---

## 4) Criterios de Éxito
- **UI**: radios redondeados coherentes, hover/focus modernos, animaciones sutiles; sin degradación de rendimiento. **(Cumplido)**
- **Blog**: 12 posts completos con imágenes WebP locales y fuentes; productos relacionados funcionan. **(Cumplido)**
- **Catálogo**: BD coincide con Excel: **174 productos / 390 formatos**; archivado reversible de legacy; categorías y origen cargados; pesos por variación; stock operable. **(Cumplido)**
- **IVA**: cálculo dinámico consistente y visualización B2C con IVA / B2B sin IVA; desglose en checkout y persistencia en pedido. **(Cumplido)**
- **Envíos**: reglas por rol y zona + escala por peso correctas (incluye excepciones B2B y zonas restringidas) + bloqueo/quote manual. **(Cumplido)**
- **Pagos**: métodos por rol, sin COD; validación backend + UI. **(Cumplido; credenciales pendientes)**
- **Checkout UX**: labels claros y logos de métodos; método “Confirming” disponible según regla; pickup restringe métodos. **(Cumplido)**
- **SEO/GEO**: metadatos multi‑idioma generados y renderizados; canonical + hreflang + JSON‑LD correcto. **(En progreso; infra OK)**
- **SEO Manual:** admin puede editar SEO en 7 idiomas; `manual=true` evita sobrescritura por IA. **(Cumplido)**
- **Legacy names + redirect:** nombre + slug actualizados a legacy; slugs antiguos resuelven y redirigen a canónico en SPA; canonical correcto. **(Cumplido)**
- **Registro UX/legal:** roles claros, orden de campos profesional correcto, aviso AEAT presente, checkbox privacidad obligatorio. **(Cumplido)**
- **Operaciones CRM:** borrado de clientes/compradores/leads disponible con protecciones y confirm. **(Cumplido)**
- **Imágenes**: assets propios (WebP) + caché 1 año; no dependencia externa; productos nuevos con imagen. **(Pendiente)**
- **Portabilidad**: semillas/snapshots restauran contenido de UI/Legal/Archivos en entornos nuevos; binarios de storage verificados. **(Parcial: snapshot OK, binarios por validar)**

---

## 5) Clonación a nuevo entorno (2026-07) — COMPLETADO
- Repo clonado desde GitHub a este entorno (código exacto, sin cambios funcionales).
- `.env` backend reconstruido (MONGO_URL/DB_NAME preservados, JWT_SECRET, EMERGENT_LLM_KEY, STRIPE_API_KEY=sk_test_emergent; PayPal/Resend/Cloudinary vacíos por decisión del usuario).
- Auto-reconciliación de catálogo OK al arrancar: 174 productos / 390 formatos desde Excel. Admin seed + hero (5 slides) + worker de traducciones/SEO en background.
- Testing E2E (iteraciones 11-12): Backend 100% (83/83), Frontend 95%+.
- Fixes aplicados durante la clonación:
  1. `CategoryCarousel.jsx`: endpoint corregido `/categories` → `/products/categories` (labels traducidos del carrusel de categorías en Home).
  2. `CookieBanner.jsx`: añadido botón X para cerrar el banner rápidamente (sesión actual, sin registrar consentimiento; RGPD intacto).
- Flujo de compra verificado end-to-end: PDP → carrito → checkout (envío 4,99€ Madrid) → pago transferencia → pedido ECO-1 visible en admin.
- Credenciales test: admin@ecoandes.com / Admin123!

---

## 6) Mejoras Dashboard + Credenciales (2026-07) — COMPLETADO
- **Resend**: API key del cliente configurada y probada (email de confirmación enviado OK).
- **Stripe**: claves test del cliente configuradas; sesión de checkout real + endpoint de estado OK.
- **Analítica propia (first-party)**: `routes/analytics.py` + `lib/tracking.js`.
- **Dashboard admin renovado** + **Pedidos estilo WooCommerce** + **SEO score** + **Archivos multi-upload**.
- Testing E2E iteración 13: Backend 14/14 (100%), Frontend 100%.

---

## 7) Lote de 12 mejoras (2026-07) — COMPLETADO
(Se mantiene igual que en la versión anterior del plan.)

---

## 8) Lote de 7 mejoras (mensaje 338) — **COMPLETADO (2026-08)**
(Se mantiene igual que en la versión anterior del plan.)

---

## 9) Lote 8 — **Editor SEO Manual + Aplicar Nombres Legacy + Redirecciones** — **COMPLETADO (2026-08)**

### 9.1 Alcance confirmado por usuario
- Legacy:
  - **Nombre visible + slug/URL** pasan al **nombre legacy exacto**.
- Redirecciones:
  - Slugs nuevos generados desde el nombre legacy.
  - Redirigir **slug actual → slug nuevo** automáticamente.
- Editor SEO:
  - Editable en **los 7 idiomas** con pestañas.

### 9.2 Entregables (implementados)
- Admin: editor SEO multi‑idioma (7 tabs) con guardado persistente y `manual=true`.
- Backend: nombres legacy aplicados (162) + `slug_aliases` + endpoint idempotente.
- Frontend: redirección SPA `replace` al slug canónico, canonical correcto.
- Importador Excel: preserva legacy para no revertir en reconciliaciones.

### 9.3 Validación
- Redirección verificada en navegador: slug antiguo → canónico.
- Admin modal SEO verificado (captura + toast).
- `iteration_16` sin bugs críticos reales; el problema de nombres se debía a `lang=en`.
