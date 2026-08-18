import React, { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api, resolveAsset } from "../lib/api";

// Carrusel infinito de categorías, editable desde el dashboard (/admin/carrusel).
// Auto-scroll continuo + arrastrable con el ratón o el dedo: al soltar, el
// movimiento automático se reanuda solo.

const AUTO_SPEED = 32; // px por segundo

function CategoryCard({ item, label, index }) {
  return (
    <Link
      to={item.cat ? `/tienda?cat=${encodeURIComponent(item.cat)}` : "/tienda"}
      className="group w-[140px] sm:w-[200px] lg:w-[220px] shrink-0 text-center select-none"
      draggable={false}
      data-testid={`category-carousel-item-${index}`}
    >
      <div className="aspect-square rounded-full overflow-hidden bg-white border border-bone-200 group-hover:border-sage-400 group-hover:shadow-[0_10px_28px_rgba(45,51,47,0.10)] transition-all duration-300">
        <img
          src={resolveAsset(item.img)}
          alt={label}
          loading="lazy"
          decoding="async"
          draggable={false}
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-[1.05] pointer-events-none"
        />
      </div>
      <div className="mt-3 text-[11.5px] uppercase tracking-[0.16em] text-ink group-hover:text-sage-700 transition-colors font-medium leading-snug px-1">
        {label}
      </div>
    </Link>
  );
}

export default function CategoryCarousel() {
  const { t, i18n } = useTranslation();
  const [labels, setLabels] = useState({});
  const [items, setItems] = useState([]);

  const trackRef = useRef(null);
  const rowRef = useRef(null);
  const offsetRef = useRef(0);
  const halfRef = useRef(1);
  const draggingRef = useRef(false);
  const movedRef = useRef(0);
  const dragStartX = useRef(0);
  const dragStartOffset = useRef(0);

  // Items editables desde el dashboard
  useEffect(() => {
    api
      .get("/carousel-categories")
      .then(({ data }) => setItems(data.items || []))
      .catch(() => setItems([]));
  }, []);

  // Traducción de los títulos con las traducciones de categorías de la tienda
  useEffect(() => {
    const lng = (i18n.resolvedLanguage || "es").slice(0, 2);
    if (lng === "es") {
      setLabels({});
      return;
    }
    api
      .get("/products/categories", { params: { lang: lng } })
      .then(({ data }) => {
        const map = {};
        (data || []).forEach((c) => { map[c.value] = c.label; });
        setLabels(map);
      })
      .catch(() => setLabels({}));
  }, [i18n.resolvedLanguage]);

  const doubled = useMemo(() => [...items, ...items], [items]);

  // Medir la mitad del track (una vuelta completa) para el bucle infinito
  useEffect(() => {
    const measure = () => {
      if (trackRef.current) halfRef.current = Math.max(1, trackRef.current.scrollWidth / 2);
    };
    measure();
    const ro = typeof ResizeObserver !== "undefined" ? new ResizeObserver(measure) : null;
    if (ro && trackRef.current) ro.observe(trackRef.current);
    window.addEventListener("resize", measure);
    return () => {
      if (ro) ro.disconnect();
      window.removeEventListener("resize", measure);
    };
  }, [doubled.length]);

  // Bucle de animación: auto-scroll continuo salvo mientras se arrastra
  useEffect(() => {
    if (doubled.length === 0) return undefined;
    let raf;
    let last = performance.now();
    const reduced = window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches;
    const tick = (now) => {
      const dt = Math.min(0.1, (now - last) / 1000);
      last = now;
      if (!draggingRef.current && !reduced) {
        offsetRef.current -= AUTO_SPEED * dt;
      }
      const half = halfRef.current;
      if (offsetRef.current <= -half) offsetRef.current += half;
      if (offsetRef.current > 0) offsetRef.current -= half;
      if (trackRef.current) trackRef.current.style.transform = `translate3d(${offsetRef.current}px,0,0)`;
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [doubled.length]);

  const capturedRef = useRef(false);

  const onPointerDown = (e) => {
    if (e.pointerType === "touch") return; // el táctil se gestiona con listeners nativos
    draggingRef.current = true;
    capturedRef.current = false;
    movedRef.current = 0;
    dragStartX.current = e.clientX;
    dragStartOffset.current = offsetRef.current;
    // IMPORTANTE: no capturar el puntero aquí. Con setPointerCapture en pointerdown,
    // el click posterior se dispara en el contenedor y NO en el <Link> de la
    // categoría, rompiendo la navegación. Solo se captura cuando hay arrastre real.
  };
  const onPointerMove = (e) => {
    if (e.pointerType === "touch") return;
    if (!draggingRef.current) return;
    const dx = e.clientX - dragStartX.current;
    movedRef.current = Math.max(movedRef.current, Math.abs(dx));
    if (movedRef.current > 6 && !capturedRef.current) {
      try { e.currentTarget.setPointerCapture?.(e.pointerId); capturedRef.current = true; } catch { /* ignore */ }
    }
    offsetRef.current = dragStartOffset.current + dx;
  };
  const endDrag = () => {
    // al soltar, el auto-scroll se reanuda solo (draggingRef vuelve a false)
    draggingRef.current = false;
  };

  // Táctil (móvil): listeners nativos con passive:false para poder bloquear el
  // scroll vertical cuando el gesto es horizontal. Deslizamiento libre en ambas
  // direcciones y reanudación automática del movimiento al levantar el dedo.
  useEffect(() => {
    const el = rowRef.current;
    if (!el) return undefined;
    let startX = 0;
    let startY = 0;
    let startOffset = 0;
    let active = false;
    let horizontal = null; // null = sin decidir, true = arrastre del carrusel
    const onTouchStart = (e) => {
      const t = e.touches[0];
      active = true;
      horizontal = null;
      startX = t.clientX;
      startY = t.clientY;
      startOffset = offsetRef.current;
      movedRef.current = 0;
      draggingRef.current = true; // pausa el auto-scroll mientras el dedo toca
    };
    const onTouchMove = (e) => {
      if (!active) return;
      const t = e.touches[0];
      const dx = t.clientX - startX;
      const dy = t.clientY - startY;
      if (horizontal === null && (Math.abs(dx) > 5 || Math.abs(dy) > 5)) {
        horizontal = Math.abs(dx) >= Math.abs(dy);
        if (!horizontal) {
          // gesto vertical: dejar que la página haga scroll y soltar el carrusel
          active = false;
          draggingRef.current = false;
          return;
        }
      }
      if (horizontal) {
        if (e.cancelable) e.preventDefault(); // bloquea el scroll de la página
        movedRef.current = Math.max(movedRef.current, Math.abs(dx));
        offsetRef.current = startOffset + dx;
      }
    };
    const onTouchEnd = () => {
      active = false;
      draggingRef.current = false; // el movimiento automático continúa solo
    };
    el.addEventListener("touchstart", onTouchStart, { passive: true });
    el.addEventListener("touchmove", onTouchMove, { passive: false });
    el.addEventListener("touchend", onTouchEnd, { passive: true });
    el.addEventListener("touchcancel", onTouchEnd, { passive: true });
    return () => {
      el.removeEventListener("touchstart", onTouchStart);
      el.removeEventListener("touchmove", onTouchMove);
      el.removeEventListener("touchend", onTouchEnd);
      el.removeEventListener("touchcancel", onTouchEnd);
    };
  }, []);

  const onClickCapture = (e) => {
    // si el usuario arrastró, no interpretar como click en la categoría
    if (movedRef.current > 6) {
      e.preventDefault();
      e.stopPropagation();
    }
  };

  if (items.length === 0) return null;

  return (
    <section className="py-10 md:py-12 overflow-hidden" data-testid="category-carousel">
      <div className="max-w-7xl mx-auto px-6 lg:px-12 mb-7 sm:mb-8 text-center">
        <div className="overline mb-3">{t("categoryCarousel.overline")}</div>
        <h2 className="font-heading text-2xl sm:text-3xl md:text-4xl font-light">{t("categoryCarousel.title")}</h2>
      </div>
      <div
        ref={rowRef}
        className="marquee-row cursor-grab active:cursor-grabbing"
        style={{ touchAction: "pan-y" }}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={endDrag}
        onPointerCancel={endDrag}
        onPointerLeave={endDrag}
        onClickCapture={onClickCapture}
        data-testid="category-carousel-draggable"
      >
        <div ref={trackRef} className="flex gap-4 sm:gap-5 w-max px-2.5 items-start will-change-transform">
          {doubled.map((item, i) => (
            <CategoryCard key={`${item.id || item.cat}-${i}`} item={item} label={labels[item.cat] || item.title} index={i} />
          ))}
        </div>
      </div>
    </section>
  );
}
