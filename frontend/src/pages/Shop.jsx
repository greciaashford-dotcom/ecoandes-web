import React, { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../lib/api";
import ProductCard from "../components/ProductCard";
import SearchBar from "../components/SearchBar";
import Seo from "../components/Seo";

export default function Shop() {
  const { t, i18n } = useTranslation();
  const [params, setParams] = useSearchParams();
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const cat = params.get("cat") || "";
  const search = params.get("q") || "";

  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const { data: cats } = await api.get("/products/categories");
        setCategories(cats);
        const { data } = await api.get("/products", {
          params: { category: cat || undefined, search: search || undefined, limit: 200 },
        });
        setProducts(data);
      } finally {
        setLoading(false);
      }
    })();
  }, [cat, search, i18n.resolvedLanguage]);

  const chips = useMemo(
    () => [{ value: "", label: t("shop.all") }, ...categories.map((c) => ({ value: c.value, label: c.label }))],
    [categories, t]
  );

  const setCat = (value) => {
    setParams((prev) => {
      const n = new URLSearchParams(prev);
      if (value) n.set("cat", value);
      else n.delete("cat");
      return n;
    });
  };

  return (
    <div className="max-w-7xl mx-auto px-6 lg:px-12 py-16" data-testid="shop-page">
      <Seo
        title={t("shop.title", "Tienda")}
        description={t("shop.seoDesc", "Compra superalimentos, semillas, harinas, legumbres y especias ecológicas (BIO) a granel en EcoAndes. Formatos para hogar y profesionales.")}
        keywords={["tienda ecológica", "comprar bio a granel", "superalimentos", "semillas ecológicas", "harinas bio"]}
      />
      <div className="mb-10">
        <div className="overline mb-3">{t("shop.overline")}</div>
        <h1 className="font-heading text-4xl md:text-5xl font-light text-ink">{t("shop.title")}</h1>
        <p className="mt-4 text-sm text-ink-soft max-w-xl font-light">
          {t("shop.intro")}
        </p>
      </div>

      <div className="mb-6 max-w-xl" data-testid="shop-search-form">
        <SearchBar />
        {search && (
          <div className="mt-3 flex items-center gap-2 text-xs text-ink-soft" data-testid="shop-active-query">
            <span>{t("shop.resultsFor")}</span>
            <span className="text-sage-700 font-medium">“{search}”</span>
            <button
              type="button"
              onClick={() => setParams((prev) => { const n = new URLSearchParams(prev); n.delete("q"); return n; })}
              data-testid="shop-clear-query"
              className="text-sage-700 underline hover:text-sage-800"
            >
              {t("shop.clear")}
            </button>
          </div>
        )}
      </div>

      <div className="flex flex-wrap gap-2 mb-10" data-testid="category-chips">
        {chips.map((c) => {
          const active = (c.value || "") === (cat || "");
          return (
            <button
              key={c.value || "all"}
              onClick={() => setCat(c.value)}
              data-testid={`cat-chip-${c.value || "all"}`}
              className={`text-xs uppercase tracking-[0.18em] px-4 py-2 border rounded-sm transition ${
                active ? "bg-sage-500 text-white border-sage-500" : "bg-transparent text-ink border-bone-200 hover:border-sage-500"
              }`}
            >
              {c.label}
            </button>
          );
        })}
      </div>

      {loading ? (
        <div className="text-center py-20 text-ink-soft">{t("common.loading")}</div>
      ) : (
        <div className="lg:grid lg:grid-cols-[1fr_260px] lg:gap-10">
          <div>
            {products.length === 0 ? (
              <div className="text-center py-20 text-ink-soft" data-testid="no-products">{t("shop.noResults")}</div>
            ) : (
              <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-6 md:gap-8">
                {products.map((p) => (
                  <ProductCard key={p.id} product={p} />
                ))}
              </div>
            )}
          </div>

          {/* Right categories sidebar */}
          <aside className="hidden lg:block" data-testid="shop-categories-sidebar">
            <div className="sticky top-24 border border-bone-200 rounded-md bg-white p-5 flex flex-col max-h-[calc(100vh-8rem)]">
              <div className="overline mb-4">{t("shop.categoriesTitle", "Categorías")}</div>
              <ul className="space-y-1 overflow-y-auto eco-scroll pr-1 flex-1 min-h-0">
                {chips.map((c) => {
                  const active = (c.value || "") === (cat || "");
                  return (
                    <li key={c.value || "all"}>
                      <button
                        onClick={() => setCat(c.value)}
                        data-testid={`cat-side-${c.value || "all"}`}
                        className={`w-full text-left text-sm px-3 py-2 rounded-sm transition ${
                          active ? "bg-sage-100 text-sage-700 font-medium" : "text-ink-soft hover:bg-bone-100 hover:text-sage-700"
                        }`}
                      >
                        {c.label}
                      </button>
                    </li>
                  );
                })}
              </ul>
            </div>
          </aside>
        </div>
      )}
    </div>
  );
}
