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
      className="group w-[190px] sm:w-[220px] shrink-0 text-center select-none"
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

  const onPointerDown = (e) => {
    draggingRef.current = true;
    movedRef.current = 0;
    dragStartX.current = e.clientX;
    dragStartOffset.current = offsetRef.current;
    e.currentTarget.setPointerCapture?.(e.pointerId);
  };
  const onPointerMove = (e) => {
    if (!draggingRef.current) return;
    const dx = e.clientX - dragStartX.current;
    movedRef.current = Math.max(movedRef.current, Math.abs(dx));
    offsetRef.current = dragStartOffset.current + dx;
  };
  const endDrag = () => {
    // al soltar, el auto-scroll se reanuda solo (draggingRef vuelve a false)
    draggingRef.current = false;
  };
  const onClickCapture = (e) => {
    // si el usuario arrastró, no interpretar como click en la categoría
    if (movedRef.current > 6) {
      e.preventDefault();
      e.stopPropagation();
    }
  };

  if (items.length === 0) return null;

  return (
    <section className="py-16 overflow-hidden" data-testid="category-carousel">
      <div className="max-w-7xl mx-auto px-6 lg:px-12 mb-10 text-center">
        <div className="overline mb-3">{t("categoryCarousel.overline")}</div>
        <h2 className="font-heading text-3xl md:text-4xl font-light">{t("categoryCarousel.title")}</h2>
      </div>
      <div
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
        <div ref={trackRef} className="flex gap-5 w-max px-2.5 items-start will-change-transform">
          {doubled.map((item, i) => (
            <CategoryCard key={`${item.id || item.cat}-${i}`} item={item} label={labels[item.cat] || item.title} index={i} />
          ))}
        </div>
      </div>
    </section>
  );
}
