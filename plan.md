# EcoAndes BIO — Plan de Continuación (UI → Blogs → Testing → Catálogo/Precios/IVA → Envíos → Pagos → SEO/GEO → Imágenes → **SEO Manual + Nombres Legacy + Redirecciones** → **UX/Operaciones (Lote 9)** → **Recuperación de Carritos (Lote 10)** → **Lote 11 (Splash + Recetas + Media links + Emails + Hero dots + 2º recordatorio + Links universales)**)

## 1) Objetivos

### Objetivos ya completados (iteración anterior)
- Modernizar la UI manteniendo identidad de marca (sage/terracotta/bone) con **bordes redondeados** y **micro‑animaciones** sin romper flujos. **(COMPLETADO)**
- Actualizar el **Blog**: mejorar 6 posts existentes y crear 6 nuevos (12 total) con imágenes WebP locales y fuentes citadas. **(COMPLETADO)**
- Ejecutar **testing end‑to‑end** para asegurar estabilidad (checkout/cupón/búsqueda/registro/blogs/UI). **(COMPLETADO)**

**Estado (sobre lo anterior):** UI + Blog listos.

### Objetivos del scope mayor (estado actual)
- **Fase 1 (P0): Catálogo + Precios + IVA (Excel‑driven)**
  - **Estado:** **COMPLETADO**.
- **Fase 2 (P0): Motor de envíos** por **tipo de usuario + zona + peso**, administrable vía JSON.
  - **Estado:** **COMPLETADO** + validado E2E.
- **Fase 3 (P1): Métodos de pago** por rol (sin contrareembolso) + scaffolding para credenciales futuras.
  - **Estado:** **COMPLETADO** (lógica + UI + validación server‑side). Credenciales **pendientes**.
- **Fase 4 (P1): SEO + GEO** por ficha de producto, con generación automática multi‑idioma y render en frontend.
  - **Estado:** **EN PROGRESO** (infra completada; protección por `manual=true`; pendiente spot-check y cierre).
- **Fase 5 (P1): Migración P0 de imágenes** a almacenamiento propio (WebP + resize + caché 1 año) una vez estabilizado el catálogo.
  - **Estado:** **PENDIENTE**.
- **Fase 6 (P0/P1): SEO Manual + Nombres Legacy + Redirecciones**
  - **Estado:** **COMPLETADO** (implementado + verificado).
- **Fase 7 (P0/P1): UX + Operaciones (Lote 9)**
  - **Estado:** **COMPLETADO** + validado E2E (**iteration_17 100%**).
- **Fase 12 (P0/P1): Recuperación de Carritos Abandonados (Lote 10)**
  - Recordatorio tras **4 h** de inactividad.
  - Email con incentivo **ECOBONUS**.
  - Página admin “Carritos abandonados”.
  - **Estado:** **COMPLETADO** + validado E2E (**iteration_18**).
- **Fase 13 (P0/P1): Lote 11 — Splash + Recetas + Media links + Emails + Hero dots + 2º recordatorio + Links universales**
  - 2º recordatorio de carrito **a las 24 h**.
  - Indicadores del Hero **verticales a la derecha** (desktop + móvil).
  - Splash screen con vídeo (mp4 + fallback webm) **una vez por sesión**.
  - Admin Archivos: **añadir por enlace** + filtro de vídeos + badges.
  - Sección Home “**Recetas con nuestros productos**” (3 vídeos verticales) + Admin.
  - Rediseño de emails automatizados con colores de marca.
  - **EXTENSIÓN:** opción **por enlace** universalizada en **todas** las ediciones de imágenes/PDF dentro del dashboard.
  - **Estado:** **COMPLETADO** + validado E2E (**iteration_19 100%**) y verificación manual adicional.

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
- Agrupación por producto base: **174 productos base**.

#### 5.2 Reglas de catálogo (confirmadas e implementadas)
- Productos no presentes en Excel → archivado reversible.
- Productos presentes en Excel y no presentes en BD → creados.
- Productos presentes en ambos → sincronizados (categoría, origen, formatos, EAN, IVA, peso por variación).

#### 5.3 Entregables técnicos (implementados)
- Importador idempotente: `/app/backend/scripts/import_catalog.py`.
- Archivado reversible: `products_archive`.

#### 5.4 Cambios de modelo (implementados)
- Producto: `vat_rate`, `origin_country`, `seo`, `legacy_name_applied`, `slug_aliases`, `previous_name`.
- Variación: `weight_kg`, `is_bulk`, `ean`, `available_retail`, `available_professional`.

#### 5.5 Motor de precios / IVA (implementado)
- Backend: `_decorate` devuelve `display_price`/`display_price_ex_vat`.
- Frontend: carrito y checkout con desglose IVA y totales.

#### 5.6 Estado actual
- Catálogo: **174 productos activos / 390 formatos**.
- ~29 productos nuevos carecen de imagen (se resolverá en Fase 9).

#### 5.7 Bug crítico detectado y resuelto (stock)
- Stock por defecto a 999 en import.

---

### Fase 6 — Motor de Envíos — **COMPLETADO (P0)**
- Reglas B2C/B2B por zona + umbrales + escala por peso.
- Endpoints: quote público y config admin.
- Checkout integrado y validación server-side.

---

### Fase 7 — Métodos de Pago (por rol) — **COMPLETADO (P1)**
- Sin contrareembolso.
- Tarjeta/PayPal/Transferencia + “Otro (Confirming…)” (shipping) y restricción por pickup.
- Ajustes UI (Lote 9): “Pago con Tarjeta” + logos, PayPal logo, método confirming con texto solicitado.

**Pendiente:** credenciales/operativa real de pagos y transferencia.

---

### Fase 8 — SEO + GEO (multi‑idioma) — **EN PROGRESO (P1)**

#### 8.1 Backend (COMPLETADO)
- Generación SEO multi-idioma.
- Protección SEO manual: `manual=true` bloquea sobrescritura.

#### 8.2 Frontend (COMPLETADO)
- `Seo.jsx` con canonical/hreflang/metas y fix de título duplicado.

#### 8.3 Pendiente para cerrar la fase
- Spot-check 10–15 productos (ES/EN/FR) y correcciones manuales.

---

### Fase 9 — Migración P0 de Imágenes — **PENDIENTE (P1)**
- Migrar imágenes externas a WebP propio + caché 1 año.

---

### Fase 10 — SEO Manual + Nombres Legacy + Redirecciones — **COMPLETADO (P0/P1)**
- Editor SEO en admin (7 idiomas).
- Aplicación nombres legacy (162) + alias.
- Redirecciones (slug antiguo → canónico) y canonical.
- Blindaje para importador Excel.

---

### Fase 11 — Lote 9: UX + Operaciones — **COMPLETADO (2026-08)**
- Carrusel móvil (swipe + auto resume), ficha técnica responsive, hover B2B, spacing home.
- Welcome email newsletter (gate Resend), borrados CRM, registro UX/legal, checkout medios de pago.
- Testing: **iteration_17 100%**.

---

### Fase 12 — **Lote 10: Recuperación de Carritos Abandonados** — **COMPLETADO (2026-08)**

#### 12.1 Objetivo y decisiones del usuario
- Enviar **1 recordatorio** tras **4 horas** de inactividad.
- Incluir incentivo: **cupón ECOBONUS (5 €)**.
- Añadir página admin: **/admin/carritos**.

#### 12.2 Implementación (realizada)
**Backend**
- Nuevo módulo: `/app/backend/routes/carts.py`
  - `POST /api/cart/track` (público): snapshot de carrito por `cart_id` (uuid por dispositivo). Si `items=[]` marca `emptied`.
  - `GET /api/cart/admin/list` (admin): lista + stats (`active`, `reminded`, `converted`).
  - `DELETE /api/cart/admin/{cart_id}` (admin).
  - `process_abandoned_carts()`:
    - Idempotente por `reminder_sent_at`.
    - Selecciona carritos `active` con email y `updated_at` > 4h.
    - Envía email (si falla por Resend, se marca igual para evitar reintentos en bucle).
  - `mark_carts_converted(email, order_number)`:
    - Se llama al crear un pedido para marcar carritos del email como `converted`.
- Integración en pedidos: `routes/orders.py` llama a `mark_carts_converted` tras insertar el pedido.
- Scheduler: `/app/backend/core/scheduler.py` ejecuta `_maybe_abandoned_carts()` cada ~10 min.
- Router registrado en `backend/server.py`: `app.include_router(carts_router)`.

**Mailer (Resend)**
- `send_abandoned_cart_email(cart)` en `/app/backend/core/mailer.py`:
  - Tabla con productos y total.
  - Bloque con cupón ECOBONUS.
  - CTA “Recuperar mi carrito” → `https://productosecoandes.com/checkout`.

**Frontend**
- Componente global: `/app/frontend/src/components/CartTracker.jsx`.
- Checkout: al escribir email válido, guarda `eco_guest_email` y dispara `POST /api/cart/track`.
- Admin UI:
  - `/app/frontend/src/pages/admin/AdminAbandonedCarts.jsx`.
  - Ruta: `/admin/carritos` + link `admin-nav-carts`.

#### 12.3 Validación / Testing
- `testing_agent_v3` → `iteration_18`:
  - Backend: **100% (9/9)**
  - Frontend: **95% (17/18)**
  - Único fallo reportado: carga /tienda “Loading…” con `ERR_ABORTED` (transitorio del entorno del tester). Re-verificado OK.

#### 12.4 Caveats conocidos
- **Resend**: hasta verificar dominio, Resend bloquea envíos a destinatarios arbitrarios.

---

### Fase 13 — **Lote 11: Splash + Recetas + Media links + Emails + Hero dots + 2º recordatorio + Links universales** — **COMPLETADO (2026-08)**

#### 13.1 Objetivos del lote
1) 2º recordatorio de carrito a las **24h**.
2) Indicadores del Hero en vertical a la derecha (web + móvil).
3) Splash screen con vídeo de bienvenida.
4) Admin Archivos: opción subir archivo o pegar enlace (mejor performance).
5) Sección Home “Recetas con nuestros productos” (3 vídeos verticales) + Admin para CRUD/orden/metadescripción.
6) Emails automatizados: diseño más atractivo y con colores de marca.
7) **Extensión solicitada por usuario:** opción **por enlace** disponible en **TODOS** los puntos del dashboard donde se editan imágenes (y PDFs) — no solo en “Archivos”.

#### 13.2 Implementación (realizada)

**(1) 2º recordatorio carrito (24h)**
- `/app/backend/routes/carts.py`
  - `ABANDON_HOURS=4` (1º) + `ABANDON_HOURS_2ND=24` (2º).
  - Nuevos campos: `reminder2_sent_at`, `reminder_count`.
  - Si hay nueva actividad (`/cart/track`) se resetean `reminder_sent_at` y `reminder2_sent_at`.
  - Idempotencia garantizada: no reenvía si `reminder2_sent_at` ya existe.
- `/app/frontend/src/pages/admin/AdminAbandonedCarts.jsx`
  - Columna “Recordatorio”: muestra **1º** y **2º** con fecha.

**(2) Indicadores del Hero verticales derecha**
- `/app/frontend/src/components/HeroCarousel.jsx`
  - Dots movidos a `right-*` y dispuestos en columna.
  - Verificado por testing: desktop ~98.2% del ancho, móvil ~96.2%.

**(3) Splash screen con vídeo**
- Assets:
  - `/app/frontend/public/splash-bienvenida.mp4` (≈5.3MB) descargado del link del usuario.
  - `/app/frontend/public/splash-bienvenida.webm` (VP9 720p ≈1.1MB) generado para compatibilidad.
- Frontend:
  - `/app/frontend/src/components/SplashScreen.jsx` (montado en `App.js`).
  - Aparece **una vez por sesión** (`sessionStorage eco_splash_seen`).
  - Botón **Saltar**.
  - Autocierre al terminar el vídeo (~8.2s) + failsafe a 11s.
  - Fix importante: `onError` no está en `<video>` (evita cierre prematuro cuando falla un `<source>` pero hay otro reproducible); se usa en el último `<source>`.

**(4) Archivos por enlace (CDN/nube del cliente)**
- Backend: `/app/backend/routes/files.py`
  - `POST /api/admin/files/external` (admin): registra `external:true`, hace `HEAD` para `content-type/size` si es posible.
  - `GET /api/admin/files?kind=video` añadido.
  - `list_files` retorna `url` externo si `external:true`.
- Frontend: `/app/frontend/src/pages/admin/AdminFiles.jsx`
  - Botón **Añadir por enlace** + diálogo.
  - Pestaña **Vídeos**.
  - Badges: **Vídeo** / **Enlace**.
  - Preview de vídeo en tarjeta.

**(5) Sección Recetas + Admin**
- Backend: `/app/backend/routes/recipes.py`
  - Config en `site_config` con `_id=recipe_videos`.
  - `GET /api/recipes` público + `GET/PUT /api/recipes/admin` (admin).
- Frontend:
  - `Home.jsx` inserta `<RecipesSection />` **después de** productos destacados.
  - `/app/frontend/src/components/RecipesSection.jsx`:
    - Hasta 3 vídeos verticales (aspect 9:16) + metadescripción.
    - Layout centrado (flex) para 1–3 vídeos.
    - JSON‑LD `VideoObject`.
  - Admin:
    - `/app/frontend/src/pages/admin/AdminRecipes.jsx` (CRUD/orden/activo/metadescripción máx 300).
    - Ruta `/admin/recetas` + link sidebar `admin-nav-recipes`.
  - Nota: queda 1 item **DEMO** (“Receta demo” con `/splash-bienvenida.mp4`) para que el usuario lo sustituya por sus 3 vídeos reales.

**(6) Emails automatizados rediseñados**
- `/app/backend/core/mailer.py`
  - `_wrap(...)` renovado:
    - Cabecera verde **#72A638**.
    - Banda de confianza (certificación/envío/pago seguro).
    - Footer oscuro con dirección real.
  - Impacto: afecta a **todos** los correos automáticos (bienvenida newsletter, carritos, pedidos, etc.).

**(7) Links universales en TODOS los editores de imágenes/PDF (EXTENSIÓN)**
- **Objetivo:** que el usuario pueda editar/establecer imágenes desde el dashboard **por enlace** en **cada lugar** donde se edita una imagen o PDF.
- **Solución técnica:** rework de `/app/frontend/src/pages/admin/UploadButton.jsx` para incluir un control dividido:
  - **Subir** (archivo desde dispositivo)
  - **🔗 Enlace** (diálogo para pegar URL)
- **Comportamiento del diálogo:**
  - Valida URL http/https.
  - Llama a `POST /api/admin/files/external` (registra en biblioteca).
  - Ejecuta el mismo callback `onUploaded({url, filename, ...})` usado por el resto del dashboard, por lo que **no requiere cambios** en cada pantalla.
- **Cobertura efectiva (heredado automáticamente por todos los usos existentes):**
  - Editor de producto: imagen principal, galería, imágenes por formato, ficha técnica (PDF).
  - Portada/Hero: imagen web + móvil de cada slide.
  - Carrusel categorías: imagen por item.
  - Archivos (además del botón “Añadir por enlace”).
- **Verificación:**
  - Compilación: `esbuild` OK.
  - E2E manual con capturas: flujo completo en editor de producto (diálogo → registro externo → preview actualizado + toast “Enlace aplicado”), presencia confirmada en Portada/Carrusel/Ficha técnica/Variaciones.
  - Endpoint `files/external` ya validado en `iteration_19`.

#### 13.3 Validación / Testing
- `testing_agent_v3` → `iteration_19`:
  - Backend: **100% (9/9)**
  - Frontend: **100%**
  - Única nota: fallos de envío a `example.com` (Resend) **esperados**; la lógica de recordatorio y marcado funciona.
- Extensión links universales: verificación manual adicional (capturas + no se guardó ningún producto real).

#### 13.4 Caveats conocidos
- **Resend**: entrega real a destinatarios arbitrarios requiere dominio verificado.
- `ffmpeg` se utilizó para generar el `.webm`; el asset ya queda persistente en `public/`.

---

## 3) Próximas Acciones (inmediatas)
1. **Cerrar Fase 8 (SEO/GEO):** spot-check 10–15 productos (ES/EN/FR) y correcciones manuales.
2. **Fase 9 (P1): migración de imágenes** (WebP + caché 1 año) + completar productos sin foto.
3. **Operativa emails (Resend):** verificar dominio de envío para habilitar entrega real:
   - bienvenida newsletter
   - carritos abandonados (1º + 2º)
   - emails de pedidos / devoluciones
4. Recetas:
   - Reemplazar el vídeo demo por los 3 vídeos reales (URLs cloud/CDN) y ajustar títulos/descripciones.
5. (Opcional) Admin Carritos:
   - filtro por estado + búsqueda por email
   - botón “marcar como ignorado”

---

## 4) Criterios de Éxito
- **UI**: radios redondeados coherentes, hover/focus modernos, animaciones sutiles. **(Cumplido)**
- **Blog**: 12 posts completos con WebP locales + fuentes. **(Cumplido)**
- **Catálogo**: BD coincide con Excel (174/390). **(Cumplido)**
- **IVA**: cálculo dinámico consistente B2C/B2B. **(Cumplido)**
- **Envíos**: reglas correctas y validadas. **(Cumplido)**
- **Pagos**: métodos por rol, sin COD; UI clara con logos. **(Cumplido; credenciales pendientes)**
- **SEO/GEO**: metadatos multi‑idioma generados y renderizados; canonical/hreflang/JSON‑LD. **(En progreso; infra OK)**
- **SEO Manual:** editable 7 idiomas, protegido contra IA. **(Cumplido)**
- **Legacy names + redirect:** aplicado + alias + canonical. **(Cumplido)**
- **Registro UX/legal:** roles claros, campos pro ordenados, aviso AEAT, checkbox privacidad. **(Cumplido)**
- **Operaciones CRM:** borrado clientes/compradores/leads. **(Cumplido)**
- **Carritos abandonados:** tracking server-side (logueados + invitados con email), **1º recordatorio 4h + 2º 24h**, conversión marcada por email al crear pedido, CRM admin con stats y borrado. **(Cumplido)**
- **Splash screen:** se muestra 1 vez por sesión, reproduce vídeo, botón saltar, autocierre y fallback webm. **(Cumplido)**
- **Recetas:** sección home visible solo si hay vídeos activos, hasta 3, admin CRUD + metadescripción. **(Cumplido)**
- **Archivos por enlace:** admin permite subir o pegar enlace, con filtros y preview. **(Cumplido)**
- **Links universales en dashboard:** cada punto de edición de imágenes/PDF ofrece opción por enlace con el mismo flujo. **(Cumplido)**
- **Emails:** plantilla coherente y atractiva con colores de marca. **(Cumplido; entrega real sujeta a dominio Resend)**
- **Imágenes**: assets propios (WebP) + caché 1 año; productos sin foto resueltos. **(Pendiente)**
- **Portabilidad**: snapshot/seed restauran contenido; binarios de storage por validar. **(Parcial)**

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
