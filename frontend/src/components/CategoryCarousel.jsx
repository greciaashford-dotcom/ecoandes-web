import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../lib/api";

// Carrusel infinito de categorías: cada imagen enlaza a la tienda
// filtrada por su categoría real de la base de datos (?cat=...).
const CATEGORY_ITEMS = [
  { title: "CEREALES EN GRANO", cat: "PSEUDOCEREALES Y CEREALES EN GRANO", img: "https://assets.zyrosite.com/w7wEiJrqV2hbSrVN/cereales-en-grano-nvN4HZZDlUud1P7E.png" },
  { title: "SUPER ALIMENTOS", cat: "SUPERALIMENTOS EN POLVO U HOJA", img: "https://assets.zyrosite.com/w7wEiJrqV2hbSrVN/superalimentos-cuL4v4KFXGJdYA83.png" },
  { title: "ARROCES", cat: "ARROCES", img: "https://assets.zyrosite.com/w7wEiJrqV2hbSrVN/arroces-c0rZdaWC9njktmzt.png" },
  { title: "AZÚCARES Y ENDULZANTES", cat: "AZUCARES Y ENDULZANTES", img: "https://assets.zyrosite.com/w7wEiJrqV2hbSrVN/azucares-y-endulzantes-X3Y6m6GRLw4EKlMp.png" },
  { title: "CACAO Y DERIVADOS", cat: "CACAO Y DERIVADOS", img: "https://assets.zyrosite.com/w7wEiJrqV2hbSrVN/cacao-y-derivados-kW3mfwsnGSMmBDZ9.png" },
  { title: "COPOS", cat: "COPOS", img: "https://assets.zyrosite.com/w7wEiJrqV2hbSrVN/copos-Ha6zriYnCD5hsKyc.png" },
  { title: "ESPECIAS", cat: "ESPECIAS Y CONDIMENTOS", img: "https://assets.zyrosite.com/w7wEiJrqV2hbSrVN/especias-UPhOHHOvtQnLOuMR.png" },
  { title: "SEMILLAS", cat: "SEMILLAS", img: "https://assets.zyrosite.com/w7wEiJrqV2hbSrVN/semillas-wLokHer8QfRzl1L0.png" },
  { title: "FRUTOS SECOS", cat: "FRUTOS SECOS", img: "https://assets.zyrosite.com/w7wEiJrqV2hbSrVN/frutos-secos-cvXFfd8j2BynRD0R.png" },
  { title: "HARINAS", cat: "HARINAS", img: "https://assets.zyrosite.com/w7wEiJrqV2hbSrVN/harinas-PKEQ39X53eDRxXPh.png" },
  { title: "HINCHADOS", cat: "HINCHADOS y MUESLIS", img: "https://assets.zyrosite.com/w7wEiJrqV2hbSrVN/hinchados-VzCmOzf0TBU5aAGU.png" },
  { title: "LEGUMBRES", cat: "LEGUMBRES", img: "https://assets.zyrosite.com/w7wEiJrqV2hbSrVN/legunbres-HqdovJLrgEPM7t90.png" },
  { title: "ALMIDONES Y ESPESANTES", cat: "ALMIDONES y ESPESANTES", img: "https://assets.zyrosite.com/w7wEiJrqV2hbSrVN/almidones-y-espezantes-Y5mIqThw5z9KDtqF.png" },
  { title: "FRUTA DESHIDRATADA", cat: "FRUTA DESHIDRATADA", img: "https://assets.zyrosite.com/w7wEiJrqV2hbSrVN/fruta-deshidratada-pUTD6MmhXkp8iefs.png" },
  { title: "TEXTURIZADOS Y PROTEÍNAS", cat: "PROTEÍNAS", img: "https://assets.zyrosite.com/w7wEiJrqV2hbSrVN/texturizados-y-proteinas-kLTsjYFc5z2c9RJv.png" },
];

function CategoryCard({ item, label, index }) {
  return (
    <Link
      to={`/tienda?cat=${encodeURIComponent(item.cat)}`}
      className="group w-[190px] sm:w-[220px] shrink-0 text-center"
      data-testid={`category-carousel-item-${index}`}
    >
      <div className="aspect-square rounded-full overflow-hidden bg-white border border-bone-200 group-hover:border-sage-400 group-hover:shadow-[0_10px_28px_rgba(45,51,47,0.10)] transition-all duration-300">
        <img
          src={item.img}
          alt={label}
          loading="lazy"
          decoding="async"
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-[1.05]"
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

  // Translate category titles using the store's category translations
  useEffect(() => {
    const lng = (i18n.resolvedLanguage || "es").slice(0, 2);
    if (lng === "es") {
      setLabels({});
      return;
    }
    api
      .get("/categories", { params: { lang: lng } })
      .then(({ data }) => {
        const map = {};
        (data || []).forEach((c) => { map[c.value] = c.label; });
        setLabels(map);
      })
      .catch(() => setLabels({}));
  }, [i18n.resolvedLanguage]);

  const doubled = [...CATEGORY_ITEMS, ...CATEGORY_ITEMS];

  return (
    <section className="py-16 overflow-hidden" data-testid="category-carousel">
      <div className="max-w-7xl mx-auto px-6 lg:px-12 mb-10 text-center">
        <div className="overline mb-3">{t("categoryCarousel.overline")}</div>
        <h2 className="font-heading text-3xl md:text-4xl font-light">{t("categoryCarousel.title")}</h2>
      </div>
      <div className="marquee-row" style={{ "--marquee-duration": "90s" }}>
        <div className="marquee-track items-start">
          {doubled.map((item, i) => (
            <CategoryCard key={`${item.cat}-${i}`} item={item} label={labels[item.cat] || item.title} index={i} />
          ))}
        </div>
      </div>
    </section>
  );
}
