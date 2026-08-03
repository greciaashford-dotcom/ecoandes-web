# EcoAndes BIO — Plan de Continuación (UI → Blogs → Testing → Catálogo/Precios/IVA → Envíos → Pagos → SEO/GEO → Imágenes → **SEO Manual + Nombres Legacy + Redirecciones**)

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
  - **Estado:** **EN PROGRESO** (infraestructura completada y verificada; generación IA corriendo en background).
- **Fase 5 (P1): Migración P0 de imágenes** a almacenamiento propio (WebP + resize + caché 1 año) una vez estabilizado el catálogo.
  - **Estado:** **PENDIENTE**.
- **Fase 6 (P0/P1): SEO Manual + Nombres Legacy + Redirecciones**
  - Editor admin para **SEO manual por idioma (7 idiomas)**.
  - Aplicación de **nombres legacy** (nombre visible + slug/URL) para conservar SEO histórico.
  - Redirecciones de slugs antiguos → slugs nuevos.
  - Blindaje para que la auto‑reconciliación Excel no revierta los cambios.
  - **Estado:** **EN PROGRESO** (confirmado por usuario; pendiente de implementación).

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
  - `seo` (estructura: `meta_title`, `meta_description`, `keywords`, `geo_region`)
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
  - Método **Other** visible solo para profesionales y solo con envío.
  - Al seleccionar recogida se resetean `transfer/other` → `stripe`.
- Flujo offline:
  - `transfer` y `other` redirigen a `/pago/success?offline=1&method={transfer|other}`.
  - `PaymentSuccess` muestra mensaje específico para `other`.

#### 7.4 Pendiente de completar cuando el cliente entregue credenciales/datos
- Stripe: API keys (live/test según entorno).
- PayPal: client id/secret.
- Transferencia: IBAN, beneficiario, banco, concepto y plantilla de email.
- Operativa “Other”: flujo de aprobación/admin, textos legales y comunicación.

---

### Fase 8 — SEO + GEO (multi‑idioma) — **EN PROGRESO (P1)**

#### 8.1 Backend (COMPLETADO)
- `translator.py`:
  - Añadido `generate_product_seo(only_missing, batch_size)`.
  - Estado `SEO_STATUS`.
  - Prompt `_SEO_RULES` GEO-aware: incluye país de origen, marca EcoAndes, BIO, “a granel”, keywords localizadas.
  - Persistencia:
    - ES: `product.seo`
    - Idiomas: `translations.{lang}.seo`
- `products.py`:
  - `_apply_lang` ahora superpone `seo` por idioma.
  - Endpoints admin:
    - `POST /api/products/seo/run?only_missing=true`
    - `GET /api/products/seo/status`

#### 8.2 Frontend (COMPLETADO)
- Nuevo componente `/app/frontend/src/components/Seo.jsx` (sin dependencias):
  - `<title>`
  - meta description/keywords
  - OpenGraph/Twitter
  - canonical
  - hreflang alternates (**7 idiomas + x-default**)
  - JSON‑LD opcional
- Integración:
  - `ProductDetail.jsx`: JSON‑LD Product + Offer/AggregateOffer + `countryOfOrigin`.
  - `Home.jsx`: JSON‑LD Organization.
  - `Shop.jsx`: SEO base de tienda.

#### 8.3 Estado actual de generación (EN CURSO)
- Generación IA arrancada y corriendo en background.
- Progreso observado (ejemplo): **ES 96/174** ya con `seo.meta_title` (y aumentando) y continuará para los 6 idiomas restantes.
- Calidad validada en muestra: incluye origen (Perú/Colombia), “BIO”, “a granel” y keywords localizadas.
- Fallback temporal (hasta que llegue el SEO IA por producto): algunos productos usan `short_description` heredado como `meta_description`.

#### 8.4 Pendiente (para cerrar la fase)
- Esperar a que `SEO_STATUS.running=false` y `done=7/7`.
- Revisión aleatoria de calidad (10–15 productos) en ES/EN/FR.
- (Antes era opcional) **Ahora requerido**: editor admin para SEO manual multi‑idioma (ver Fase 10).

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

### Fase 10 — **SEO Manual (Admin) + Nombres Legacy + Redirecciones 301** — **EN PROGRESO (P0/P1)**

#### 10.1 Editor SEO manual (Admin) — **P0**
**Objetivo:** editar por producto y por idioma (7 tabs):
- `meta_title`
- `meta_description`
- `keywords` (lista)
- `geo_region`

**Backend (a implementar):**
- `GET /api/products/{id}/seo` (admin):
  - Devuelve SEO ES y `translations.{lang}.seo` para `en, zh, fr, ja, it, pt`.
  - Devuelve flags `manual: true/false` por idioma (y/o por bloque SEO).
- `PUT /api/products/{id}/seo` (admin):
  - Permite actualizar SEO por idioma.
  - Guarda `manual=true` cuando el admin edita.
- Blindaje IA:
  - `generate_product_seo(...)` debe **respetar** `manual=true` y **no sobrescribir** ese idioma.
  - Incluso con `force` (si se usa en el futuro), no debe pisar manual salvo operación explícita de “reset”.

**Frontend (a implementar):**
- Integrar en `ProductEditorModal.jsx` un nuevo tab “SEO” con:
  - Sub‑tabs por idioma (ES, EN, ZH, FR, JA, IT, PT).
  - Contadores de caracteres y recomendaciones.
  - Botón “Guardar” que llama al `PUT /api/products/{id}/seo`.

#### 10.2 Aplicar nombres legacy (nombre visible + slug) — **P0**
**Regla confirmada por usuario:**
- El **nombre visible** y el **slug/URL** pasan al **nombre legacy exacto**.

**Fuente:**
- `/app/backend/data/seo_name_mapping.json`
  - `mapping` (162 pares actuales→legacy)
  - `sin_equivalente` (3 legacy sin equivalente: Albahaca, Harina de Chía, Soja texturizada extra fina)

**Backend (a implementar):**
- `POST /api/products/legacy-names/apply` (admin)
  - Soporta `dry_run=true|false`.
  - Aplica sobre los **162** productos mapeados:
    - `name = legacy_name`
    - `slug = slugify(legacy_name)` (asegurando unicidad)
    - `slug_aliases`: añade el slug anterior.
    - Metadatos de auditoría: `legacy_name_applied=true`, `previous_name`, `previous_slug`, `legacy_name`.
- Resolver slugs antiguos:
  - Ampliar `GET /api/products/slug/{slug}` para:
    - Buscar primero por `slug`.
    - Si no existe, buscar por `slug_aliases`.
    - Si viene por alias, devolver el producto canónico + `redirected_from: <slug_antiguo>` + `canonical_slug: <slug_nuevo>`.

**Frontend (a implementar):**
- `ProductDetail.jsx`:
  - Si la API devuelve `redirected_from`, hacer `navigate(`/producto/${canonical_slug}`, { replace: true })`.
  - Mantener `<Seo>` con canonical correcto (URL final tras replace).

#### 10.3 Blindaje contra auto‑reconciliación Excel — **P0**
**Problema a evitar:** `import_catalog.py` vuelve a poner `name` desde Excel y puede revertir nombres legacy.

**Solución (a implementar):**
- En `/app/backend/scripts/import_catalog.py`:
  - Si `prior.legacy_name_applied == true`:
    - Preservar `name` y `slug` actuales.
    - Preservar `slug_aliases`, `previous_name`, `previous_slug`, `legacy_name`, `legacy_name_applied`.
  - Seguir sincronizando:
    - precios, IVA, variaciones, pesos, disponibilidad, etc.
  - Preservar también `translations` y `seo` existentes (ya lo hace para `seo`/`translations` si existen).

#### 10.4 Ejecución + verificación — **P1**
- Ejecutar:
  - `POST /api/products/legacy-names/apply?dry_run=true` (reporte)
  - `POST /api/products/legacy-names/apply?dry_run=false` (aplicar)
- Verificar con curl:
  - Producto antes/después: slug antiguo retorna 200 con `redirected_from` y `canonical_slug`.
  - Navegación SPA reemplaza URL.
- Ejecutar `testing_agent_v3`:
  - Acceso por slug antiguo y redirección.
  - SEO head tags y canonical.
  - Admin editor SEO (guardar y re‑leer).

---

## 3) Próximas Acciones (inmediatas)
1. **Implementar Fase 10.1**: endpoints SEO manual + UI admin (7 idiomas con pestañas) + flag `manual`.
2. **Implementar Fase 10.2**: aplicar nombres legacy con `dry_run` + persistencia de `slug_aliases` + resolución de slugs antiguos.
3. **Implementar Fase 10.3**: blindaje del importador Excel para no revertir `name/slug` legacy.
4. **Aplicar mapeo legacy** (162 productos) y verificar en frontend.
5. **Testing E2E** completo del cambio (incluye redirección y SEO manual).
6. Retomar Fase 9 (imágenes) cuando el catálogo y SEO queden estables.

---

## 4) Criterios de Éxito
- **UI**: radios redondeados coherentes, hover/focus modernos, animaciones sutiles; sin degradación de rendimiento. **(Cumplido)**
- **Blog**: 12 posts completos con imágenes WebP locales y fuentes; productos relacionados funcionan. **(Cumplido)**
- **Catálogo**: BD coincide con Excel: **174 productos / 390 formatos**; archivado reversible de legacy; categorías y origen cargados; pesos por variación; stock operable. **(Cumplido)**
- **IVA**: cálculo dinámico consistente y visualización B2C con IVA / B2B sin IVA; desglose en checkout y persistencia en pedido. **(Cumplido)**
- **Envíos**: reglas por rol y zona + escala por peso correctas (incluye excepciones B2B y zonas restringidas) + bloqueo/quote manual. **(Cumplido)**
- **Pagos**: métodos por rol, sin COD; validación backend + UI; credenciales desacopladas. **(Cumplido; credenciales pendientes)**
- **SEO/GEO**: metadatos multi‑idioma generados y renderizados; canonical + hreflang + JSON‑LD correcto. **(En progreso)**
- **SEO Manual (nuevo):** admin puede editar SEO en 7 idiomas; `manual=true` evita sobrescritura por IA. **(Pendiente)**
- **Legacy names + redirect (nuevo):** nombre + slug actualizados a legacy; slugs antiguos resuelven y redirigen a canónico en SPA; canonical correcto. **(Pendiente)**
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
- **Stripe**: claves test del cliente configuradas; sesión de checkout real + endpoint de estado OK (fix: estado consultado vía SDK oficial de Stripe por incompatibilidad pydantic del wrapper).
- **Analítica propia (first-party)**: `routes/analytics.py` + `lib/tracking.js` — pageviews por ruta, clasificación de fuentes (orgánico/social/IA/referencia/directo/UTM), geolocalización por IP (headers CDN + ip-api con caché en `db.geoip`), colección `db.visits`.
- **Dashboard admin renovado**: filtro global de fechas (presets + rango custom), 4 KPIs, gráfico de evolución, mapa mundial interactivo (d3-geo + world-atlas, tooltip por país), ranking de países con banderas, resumen de adquisición con % y medios, páginas más vistas, últimos pedidos con Origen.
- **Pedidos estilo WooCommerce**: pestañas por estado con contadores, acciones en lote (cambio de estado masivo), filtros (fechas, canal de venta, cliente registrado, B2C/B2B), buscador, tabla con checkbox / #pedido+cliente+ojo (modal vista previa) / fecha / badge estado / total € / Origen (atribución first-touch guardada en `order.acquisition`).
- **Productos**: columna SEO con puntos rojo/naranja/verde (score 0-100 sobre meta título, descripción, keywords, contenido e imagen) + tooltip con desglose.
- **Archivos**: subida múltiple simultánea de imágenes y PDFs con progreso.
- Testing E2E iteración 13: Backend 14/14 (100%), Frontend 100%.

---

## 7) Lote de 12 mejoras (2026-07) — COMPLETADO
1. Carrusel "Nuestras categorías" editable desde /admin/carrusel (añadir/eliminar/reordenar/ocultar/cambiar imagen y enlace) · sección movida justo tras el hero · arrastrable con reanudación del auto-scroll al soltar.
2. Color principal cambiado #2C402E → #72A638 (sage-800 en tailwind).
3. Logo blanco en el footer (/logo-ecoandes-white.png).
4. Sidebar de categorías de la Tienda con scroll independiente (sticky + max-height + overflow).
5. Validación NIF/CIF con API BeeL (core/beel.py): checksum oficial + censo AEAT → auto / manual (24h) / failed con el mensaje exacto pedido en /registro. Key en .env (BEEL_API_KEY).
6. Emails automatizados (core/mailer.py + core/scheduler.py): registro (cliente+empresa con estado de verificación), pedidos (cliente+aviso interno), reembolsos (ambas partes), reporte diario de estadísticas a las 8:00 (Europe/Madrid) a info@productosecoandes.com e info@destacaenlinea.com. NOTA: entregas a clientes requieren verificar dominio en Resend.
7. /admin/seo: análisis SEO con IA (Gemini) semanal automático + botón "Analizar ahora"; informes en db.seo_reports.
8. /admin/legal: editor de Aviso Legal, Cookies, Privacidad y Condiciones (db.legal_pages); páginas públicas renderizadas desde la API.
9. 154 productos enriquecidos desde las fichas técnicas PDF (scripts/enrich_from_pdfs.py): tech_sheet + tabla nutricional + bloques (ingredientes, origen, beneficios, uso, conservación, certificaciones) + descripciones; matching determinista + IA (154/159 PDFs, 3 duplicados y 2 sin producto en catálogo: Harina de Chía y Guaraná).
10. Selector de formato en ficha de producto como botones pill de un click; rango de precios con flecha →.
11. Enriquecimiento persistido en /app/backend/data/product_enrichment.json + seed automático al arrancar (core/enrichment_seed.py) → los datos viajan con el código a nuevos entornos.
12. Botón compartir con menú (WhatsApp, Facebook, X, LinkedIn, Telegram, Pinterest, copiar enlace).
- Testing E2E iteración 14: Backend 100% (20/20), Frontend 95%, sin bugs.

---

## 8) Lote de 7 mejoras (mensaje 338) — **COMPLETADO (2026-08)**
1. **Dashboard:** scroll independiente en el sidebar (`overflow-y: auto`) sin desplazar el contenido principal.
2. **Home / Nuestras Categorías:** carrusel igual de funcional en móvil (viewport 390×844), con drag táctil y responsive; sin overflow horizontal.
3. **Home / COLECCIÓN PRINCIPAL:** imagen reemplazada y optimizada:
   - `/app/frontend/public/coleccion-principal.webp` (~197KB)
   - fallback `/app/frontend/public/coleccion-principal.jpg` (~293KB)
4. **Home / CANAL PROFESIONAL:** overlay verde eliminado → overlay neutro muy ligero (observado `rgba(0,0,0,0.3)`), manteniendo legibilidad.
5. **Footer:** rediseño completo mobile-first:
   - banda superior newsletter,
   - layout responsive (4 columnas en desktop),
   - barra inferior legal/copyright,
   - enlaces funcionan y envío de newsletter muestra feedback (toast/mensaje).
   - Implementación: `/app/frontend/src/components/Footer.jsx` + `/app/frontend/src/components/Footer.css`.
6. **Persistencia/migración:** snapshot exportable/restaurable:
   - Export: `/app/backend/scripts/export_site_snapshot.py` → `/app/backend/data/site_snapshot.json`
   - Restore: `/app/backend/core/snapshot_seed.py` aplicado en el arranque (server.py)
   - Cobertura export reportada: hero + 15 items carrusel + 4 páginas legales + 177 registros de archivos.
   - **Caveat**: el snapshot preserva registros/configuración, pero la disponibilidad de los **binarios** en object storage debe validarse en el entorno destino.
7. **SEO (migración de nombres legacy):** mapeo completo **165/165** en:
   - `/app/backend/data/seo_name_mapping.json`
   - Resultado: **162 mapeados** + **3 marcados `sin_equivalente`** por decisión del usuario (opción b):
     - `Albahaca`
     - `Harina de Chía`
     - `Soja texturizada extra fina`
   - Ajuste del script `/app/backend/scripts/seo_name_mapping.py`: pasada de **coincidencia exacta normalizada** antes del fuzzy para evitar colisiones (p.ej. “Clavo de olor” vs “Clavo de olor en polvo”).

**Validación (testing):**
- `testing_agent_v3` → `iteration_15`:
  - Backend: **97.3% (71/73)**
  - Frontend desktop/móvil/admin: **100%**
  - Sin bugs críticos; sin action items.

---

## 9) Lote 8 — **Editor SEO Manual + Aplicar Nombres Legacy + Redirecciones** — **EN PROGRESO (2026-08)**

### 9.1 Alcance confirmado por usuario
- Al aplicar legacy:
  - **Nombre visible + slug/URL** pasan al **nombre legacy exacto**.
- Redirecciones:
  - No hay listado de URLs antiguas; se generarán **slugs nuevos** desde nombres legacy y se redirigirá **slug actual → slug nuevo**.
- Editor SEO:
  - Editable en **los 7 idiomas** con pestañas.

### 9.2 Entregables
- Admin: editor SEO multi‑idioma (7 tabs) con guardado persistente.
- Backend: aplicar nombres legacy (162 productos), mantener `slug_aliases`, resolver alias.
- Frontend: redirección SPA `replace` cuando se entra por slug antiguo; canonical consistente.
- Blindaje importador Excel para preservar renombres legacy.

### 9.3 Estado
- Diseño y reglas: **confirmadas**.
- Implementación: **pendiente**.
- Testing: **pendiente**.
