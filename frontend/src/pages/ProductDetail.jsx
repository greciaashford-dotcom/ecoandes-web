import React, { useEffect, useState, useMemo } from "react";
import { useParams, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { motion } from "framer-motion";
import {
  Minus, Plus, ChevronRight, Heart, Scale, MessageCircle, Share2,
  Check, Leaf, FileDown, AlertCircle,
} from "lucide-react";
import { api, formatEUR, resolveAsset } from "../lib/api";
import { getPriceRange, sortVariations, variationPrice } from "../lib/price";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
import { useWishlist } from "../context/WishlistContext";
import { toast } from "sonner";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../components/ui/tabs";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "../components/ui/select";
import ProductGallery from "../components/ProductGallery";
import TrustBadges from "../components/TrustBadges";
import ProductCarousel from "../components/ProductCarousel";
import ProductReviews from "../components/ProductReviews";
import StarRating from "../components/StarRating";
import Seo from "../components/Seo";

const WHATSAPP = "34696173094";

// Organic-farming certification badges shown on every product (ES-ECO-023-MA).
const CERTIFICATIONS = [
  "/certifications/cert-1.svg",
  "/certifications/cert-2.svg",
  "/certifications/cert-3.svg",
  "/certifications/cert-4.svg",
];

export default function ProductDetail() {
  const { t, i18n } = useTranslation();
  const { slug } = useParams();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedVariation, setSelectedVariation] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [related, setRelated] = useState([]);
  const [bestSellers, setBestSellers] = useState([]);
  const [allCategories, setAllCategories] = useState([]);
  const { addItem } = useCart();
  const { user } = useAuth();
  const { isWished, isCompared, toggleWishlist, toggleCompare } = useWishlist();
  const isPro = user?.role === "professional" || user?.role === "admin";

  useEffect(() => {
    let alive = true;
    (async () => {
      setLoading(true);
      try {
        const { data } = await api.get(`/products/slug/${slug}`);
        if (!alive) return;
        setProduct(data);
        const sorted = sortVariations(data.variations || []);
        setSelectedVariation(sorted.length ? sorted[0] : null);
        setQuantity(1);
        // cross-sell
        const [rel, bs] = await Promise.all([
          api.get("/products", { params: { category: data.category, limit: 12 } }),
          api.get("/products", { params: { best_seller: true, limit: 12 } }),
        ]);
        if (!alive) return;
        setRelated((rel.data || []).filter((p) => p.id !== data.id).slice(0, 10));
        setBestSellers((bs.data || []).filter((p) => p.id !== data.id).slice(0, 10));
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => { alive = false; };
  }, [slug, i18n.resolvedLanguage]);

  useEffect(() => {
    let alive = true;
    api.get("/products/categories").then(({ data }) => { if (alive) setAllCategories(data || []); }).catch(() => {});
    return () => { alive = false; };
  }, [i18n.resolvedLanguage]);

  const sortedVariations = useMemo(() => {
    const seen = new Set();
    const uniq = (product?.variations || []).filter((v) => {
      if (v.active === false) return false;  // hide disabled formats from storefront
      if (seen.has(v.sku)) return false;
      seen.add(v.sku);
      return true;
    });
    return sortVariations(uniq);
  }, [product]);
  const range = useMemo(() => getPriceRange(product, isPro), [product, isPro]);

  if (loading) {
    return <div className="max-w-7xl mx-auto px-6 py-24 text-center text-ink-soft">{t("product.loading")}</div>;
  }
  if (!product) {
    return (
      <div className="max-w-7xl mx-auto px-6 py-24 text-center">
        <p>{t("product.notFound")}</p>
        <Link to="/tienda" className="btn-outline mt-6 inline-block">{t("product.backToShop")}</Link>
      </div>
    );
  }

  const currentPrice = selectedVariation
    ? variationPrice(selectedVariation, isPro)
    : (isPro ? product.price_professional : product.price_retail);
  const inStock = selectedVariation ? (selectedVariation.stock ?? 1) !== 0 : (product.stock ?? 1) !== 0;
  const blocks = product.description_blocks || {};
  const blockOrder = ["ingredients", "origin", "benefits", "usage", "storage", "certifications"];
  const hasBlocks = blockOrder.some((k) => blocks[k]);
  const nutrition = product.nutrition || [];
  const techUrl = product.tech_sheet?.url ? resolveAsset(product.tech_sheet.url) : "";
  const categories = (product.category || "").split(",").map((c) => c.trim()).filter(Boolean);

  const handleAdd = () => {
    if (!inStock) return;
    addItem(product, selectedVariation, quantity, isPro);
  };

  const handleShare = async () => {
    const url = window.location.href;
    try {
      if (navigator.share) {
        await navigator.share({ title: product.name, url });
      } else {
        await navigator.clipboard.writeText(url);
        toast.success(t("product.shareCopied"));
      }
    } catch { /* cancelled */ }
  };

  const askLink = `https://wa.me/${WHATSAPP}?text=${encodeURIComponent(
    `Hola, tengo una pregunta sobre: ${product.name} (SKU ${product.sku})`
  )}`;

  const secondaryBtn = "inline-flex items-center gap-2 text-xs uppercase tracking-[0.16em] px-3 py-2 rounded-sm border border-bone-200 bg-white text-ink hover:border-sage-500 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sage-500";

  // --- SEO / GEO ---
  const seo = product.seo || {};
  const seoTitle = seo.meta_title || product.name;
  const seoDesc = seo.meta_description || product.short_description || product.description || `${product.name} ecológico (BIO) a granel en EcoAndes.`;
  const seoImage = product.image_url ? resolveAsset(product.image_url) : (product.gallery && product.gallery[0] ? resolveAsset(product.gallery[0]) : "");
  const offerPrices = (product.variations || []).map((v) => variationPrice(v, isPro)).filter((p) => p > 0);
  const productJsonLd = {
    "@context": "https://schema.org",
    "@type": "Product",
    name: product.name,
    description: seoDesc,
    sku: product.sku,
    category: product.category,
    ...(seoImage ? { image: [seoImage] } : {}),
    brand: { "@type": "Brand", name: "EcoAndes" },
    ...(product.origin_country ? { countryOfOrigin: product.origin_country } : {}),
    ...(offerPrices.length
      ? {
          offers: {
            "@type": "AggregateOffer",
            priceCurrency: "EUR",
            lowPrice: Math.min(...offerPrices).toFixed(2),
            highPrice: Math.max(...offerPrices).toFixed(2),
            offerCount: offerPrices.length,
            availability: inStock ? "https://schema.org/InStock" : "https://schema.org/OutOfStock",
          },
        }
      : currentPrice > 0
      ? {
          offers: {
            "@type": "Offer",
            priceCurrency: "EUR",
            price: currentPrice.toFixed(2),
            availability: inStock ? "https://schema.org/InStock" : "https://schema.org/OutOfStock",
          },
        }
      : {}),
  };

  return (
    <div className="bg-bone-100 pb-10">
      <Seo
        title={seoTitle}
        description={seoDesc}
        keywords={seo.keywords}
        image={seoImage}
        type="product"
        jsonLd={productJsonLd}
      />
      {/* Breadcrumbs */}
      <div className="max-w-[72rem] mx-auto px-4 sm:px-6 lg:px-8 py-5 text-xs text-ink-soft uppercase tracking-[0.16em] flex items-center gap-2 flex-wrap" data-testid="breadcrumbs">
        <Link to="/" className="hover:text-sage-600">{t("product.breadcrumbHome")}</Link>
        <ChevronRight size={12} />
        <Link to="/tienda" className="hover:text-sage-600">{t("product.breadcrumbShop")}</Link>
        <ChevronRight size={12} />
        <span className="text-ink normal-case tracking-normal">{product.name}</span>
      </div>

      {/* Hero */}
      <div className="max-w-[72rem] mx-auto px-4 sm:px-6 lg:px-8 lg:grid lg:grid-cols-12 lg:gap-x-10">
        <div className="lg:col-span-7">
          <ProductGallery
            mainImage={product.image_url}
            gallery={product.gallery || []}
            variations={sortedVariations}
            selectedSku={selectedVariation?.sku}
            onSelectVariation={(v) => setSelectedVariation(v)}
            name={product.name}
          />
        </div>

        <div className="lg:col-span-5 mt-8 lg:mt-0">
          <div className="overline text-sage-600">{product.category}</div>
          <h1 className="font-heading text-3xl sm:text-4xl font-light text-ink mt-2 leading-tight">{product.name}</h1>

          {product.web_rating > 0 && (
            <div className="flex items-center gap-2 mt-3">
              <StarRating value={product.web_rating} readOnly size={15} />
              {product.web_reviews > 0 && <span className="text-xs text-ink-muted">({product.web_reviews})</span>}
            </div>
          )}

          {product.highlights && (
            <p className="text-ink-soft mt-4 leading-relaxed">{product.highlights}</p>
          )}

          <TrustBadges badges={product.badges} className="mt-5" />

          {/* Price */}
          <div className="mt-6 flex items-baseline gap-3 flex-wrap">
            <span className="font-heading text-3xl font-light text-ink" data-testid="product-price">
              {currentPrice > 0 ? formatEUR(currentPrice) : t("common.consult")}
            </span>
            {range.min !== range.max && (
              <span className="text-sm text-ink-muted">
                {t("product.priceRange")}: {formatEUR(range.min)} – {formatEUR(range.max)}
              </span>
            )}
            {isPro && currentPrice > 0 && (
              <span className="text-xs uppercase tracking-[0.18em] text-terracotta">{t("product.proPrice")}</span>
            )}
          </div>
          {currentPrice > 0 && (
            <div className="mt-1.5 text-xs text-ink-muted" data-testid="product-vat-note">
              {isPro
                ? `Precio sin IVA · IVA ${product.vat_rate ?? 10}% no incluido`
                : `IVA (${product.vat_rate ?? 10}%) incluido`}
            </div>
          )}
          {!isPro && product.price_professional > 0 && (
            <Link to="/login" className="text-xs uppercase tracking-[0.18em] text-sage-600 hover:text-sage-700 mt-1 inline-block" data-testid="pdp-login-b2b">
              {t("product.accessB2B")}
            </Link>
          )}

          {/* Variation selector */}
          {sortedVariations.length > 0 && (
            <div className="mt-6">
              <div className="overline mb-2">{t("product.format")}</div>
              <Select
                value={selectedVariation?.sku}
                onValueChange={(sku) => setSelectedVariation(sortedVariations.find((v) => v.sku === sku))}
              >
                <SelectTrigger className="w-full bg-white" data-testid="product-variant-select">
                  <SelectValue placeholder={t("product.format")} />
                </SelectTrigger>
                <SelectContent>
                  {sortedVariations.map((v) => (
                    <SelectItem key={v.sku} value={v.sku} data-testid={`variant-option-${v.sku}`}>
                      {v.name} — {formatEUR(variationPrice(v, isPro))}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}

          {/* Availability */}
          <div className="mt-5">
            <span
              data-testid="product-availability"
              className={`inline-flex items-center gap-1.5 text-xs uppercase tracking-[0.16em] px-3 py-1.5 rounded-full border ${
                inStock ? "text-sage-700 bg-sage-50 border-sage-200" : "text-terracotta bg-bone-100 border-bone-200"
              }`}
            >
              {inStock ? <Check size={13} /> : <AlertCircle size={13} />}
              {inStock ? t("product.inStock") : t("product.outOfStock")}
            </span>
          </div>

          {/* Quantity + Add to cart */}
          <div className="mt-5 flex flex-col sm:flex-row gap-3">
            <div className="inline-flex items-stretch rounded-sm border border-bone-200 bg-white">
              <button onClick={() => setQuantity((q) => Math.max(1, q - 1))} aria-label="-" data-testid="quantity-decrement-button" className="px-3 text-ink hover:bg-bone-100 transition-colors">
                <Minus size={16} />
              </button>
              <input
                type="number" min={1} value={quantity}
                onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value || "1", 10)))}
                data-testid="quantity-input"
                className="w-14 text-center border-x border-bone-200 bg-transparent outline-none text-ink"
              />
              <button onClick={() => setQuantity((q) => q + 1)} aria-label="+" data-testid="quantity-increment-button" className="px-3 text-ink hover:bg-bone-100 transition-colors">
                <Plus size={16} />
              </button>
            </div>
            <button onClick={handleAdd} disabled={!inStock || currentPrice <= 0} className="btn-primary flex-1 disabled:opacity-50" data-testid="add-to-cart-button">
              {t("product.addToCart")}
            </button>
          </div>

          {/* Secondary actions */}
          <div className="mt-4 flex flex-wrap gap-2" data-testid="secondary-actions">
            <button onClick={() => toggleWishlist(product)} className={`${secondaryBtn} ${isWished(product.id) ? "border-terracotta text-terracotta" : ""}`} data-testid="wishlist-button">
              <Heart size={15} fill={isWished(product.id) ? "currentColor" : "none"} /> {t("product.addToWishlist")}
            </button>
            <button onClick={() => toggleCompare(product)} className={`${secondaryBtn} ${isCompared(product.id) ? "border-sage-600 text-sage-700" : ""}`} data-testid="compare-button">
              <Scale size={15} /> {t("product.compare")}
            </button>
            <a href={askLink} target="_blank" rel="noopener noreferrer" className={secondaryBtn} data-testid="ask-about-product-button">
              <MessageCircle size={15} /> {t("product.ask")}
            </a>
            <button onClick={handleShare} className={secondaryBtn} data-testid="share-button">
              <Share2 size={15} /> {t("product.share")}
            </button>
          </div>

          {/* Metadata */}
          <div className="mt-6 pt-4 border-t border-bone-200 flex flex-wrap gap-x-6 gap-y-2 text-xs text-ink-muted">
            <span data-testid="product-sku">{t("product.sku")}: {product.sku}</span>
            <span data-testid="product-categories">{t("product.categories")}: {product.category}</span>
          </div>

          {/* Organic certifications (all products) */}
          <div className="mt-5 pt-4 border-t border-bone-200" data-testid="product-certifications">
            <p className="text-xs text-ink-soft leading-relaxed">
              {t("product.certificationLabel")}
            </p>
            <div className="mt-3 flex flex-wrap items-center gap-3">
              {CERTIFICATIONS.map((c, i) => (
                <div
                  key={i}
                  className="h-16 w-16 sm:h-[72px] sm:w-[72px] rounded-md border border-bone-200 bg-white p-2 flex items-center justify-center shrink-0"
                  title={t("product.certificationLabel")}
                  data-testid={`certification-badge-${i + 1}`}
                >
                  <img
                    src={c}
                    alt="Certificación Agricultura Ecológica ES-ECO-023-MA"
                    className="max-h-full max-w-full object-contain"
                    loading="lazy"
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Explore categories (right column, easy cross-navigation) */}
          {allCategories.length > 0 && (
            <div className="mt-5 pt-4 border-t border-bone-200" data-testid="pdp-categories">
              <div className="overline mb-3">Explora más categorías</div>
              <div className="flex flex-wrap gap-2">
                {allCategories.map((c) => (
                  <Link
                    key={c.value}
                    to={`/tienda?cat=${encodeURIComponent(c.value)}`}
                    data-testid={`pdp-cat-${c.value}`}
                    className={`text-[11px] uppercase tracking-[0.14em] px-3 py-1.5 rounded-sm border transition ${
                      categories.includes(c.value) ? "bg-sage-50 border-sage-300 text-sage-700" : "border-bone-200 text-ink-soft hover:border-sage-500 hover:text-sage-700"
                    }`}
                  >
                    {c.label}
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="max-w-[72rem] mx-auto px-4 sm:px-6 lg:px-8 mt-12">
        <Tabs defaultValue="description">
          <TabsList className="w-full justify-start gap-2 overflow-x-auto eco-scroll bg-transparent p-0 h-auto flex-wrap">
            <TabsTrigger value="description" className="rounded-full border border-bone-200 bg-white px-4 py-2 text-xs uppercase tracking-[0.16em] data-[state=active]:border-sage-500 data-[state=active]:text-sage-700" data-testid="tab-description">{t("product.tabDescription")}</TabsTrigger>
            <TabsTrigger value="nutrition" className="rounded-full border border-bone-200 bg-white px-4 py-2 text-xs uppercase tracking-[0.16em] data-[state=active]:border-sage-500 data-[state=active]:text-sage-700" data-testid="tab-nutrition">{t("product.tabNutrition")}</TabsTrigger>
            <TabsTrigger value="techsheet" className="rounded-full border border-bone-200 bg-white px-4 py-2 text-xs uppercase tracking-[0.16em] data-[state=active]:border-sage-500 data-[state=active]:text-sage-700" data-testid="tab-techsheet">{t("product.tabTechSheet")}</TabsTrigger>
            <TabsTrigger value="reviews" className="rounded-full border border-bone-200 bg-white px-4 py-2 text-xs uppercase tracking-[0.16em] data-[state=active]:border-sage-500 data-[state=active]:text-sage-700" data-testid="tab-reviews">{t("product.tabReviews")}</TabsTrigger>
          </TabsList>

          {/* Description */}
          <TabsContent value="description" className="mt-6" data-testid="product-description-tab">
            {hasBlocks ? (
              <div className="space-y-6">
                {blockOrder.filter((k) => blocks[k]).map((k) => (
                  <div key={k} className="grid gap-2 lg:grid-cols-12">
                    <div className="lg:col-span-3 overline pt-1">{t(`product.blocks.${k}`)}</div>
                    <div className="lg:col-span-9 text-sm sm:text-base text-ink leading-relaxed whitespace-pre-line">{blocks[k]}</div>
                  </div>
                ))}
              </div>
            ) : product.description ? (
              <div className="text-sm sm:text-base text-ink leading-relaxed whitespace-pre-line">{product.description}</div>
            ) : (
              <div className="text-ink-muted text-sm">—</div>
            )}
          </TabsContent>

          {/* Nutrition */}
          <TabsContent value="nutrition" className="mt-6" data-testid="product-nutrition-tab">
            {nutrition.length > 0 ? (
              <div className="overflow-hidden rounded-md border border-bone-200 bg-white max-w-xl">
                <table className="w-full text-sm">
                  <thead className="bg-bone-100">
                    <tr>
                      <th className="text-left px-4 py-3 text-xs uppercase tracking-[0.16em] text-ink-muted font-medium">{t("product.nutritionColNutrient")}</th>
                      <th className="text-right px-4 py-3 text-xs uppercase tracking-[0.16em] text-ink-muted font-medium">{t("product.nutritionColValue")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {nutrition.map((n, i) => (
                      <tr key={i} className="border-t border-bone-200 hover:bg-sage-50/60 transition-colors">
                        <td className="px-4 py-2.5 text-ink">{n.label}</td>
                        <td className="px-4 py-2.5 text-right text-ink">{n.value}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="rounded-md border border-bone-200 bg-white p-8 text-center max-w-xl" data-testid="nutrition-empty-state">
                <Leaf className="mx-auto text-sage-400 mb-3" size={26} />
                <p className="text-ink-soft text-sm">{t("product.nutritionEmpty")}</p>
                <a href={askLink} target="_blank" rel="noopener noreferrer" className="btn-outline inline-block mt-4">{t("product.ask")}</a>
              </div>
            )}
          </TabsContent>

          {/* Tech sheet */}
          <TabsContent value="techsheet" className="mt-6" data-testid="product-technical-sheet-tab">
            {techUrl ? (
              <div className="rounded-md border border-bone-200 bg-white p-6 max-w-xl flex items-center justify-between gap-4">
                <div>
                  <div className="font-heading text-lg text-ink">{t("product.techSheetTitle")}</div>
                  <p className="text-sm text-ink-soft mt-1">{t("product.techSheetDesc")}</p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <a href={techUrl} target="_blank" rel="noopener noreferrer" className="btn-outline inline-flex items-center gap-2" data-testid="technical-sheet-view-button">
                    <FileDown size={15} /> Ver Documento
                  </a>
                  <a href={techUrl} target="_blank" rel="noopener noreferrer" download className="btn-primary inline-flex items-center gap-2" data-testid="technical-sheet-download-button">
                    <FileDown size={15} /> {t("product.downloadPdf")}
                  </a>
                </div>
              </div>
            ) : (
              <div className="rounded-md border border-bone-200 bg-white p-8 text-center max-w-xl" data-testid="techsheet-empty-state">
                <FileDown className="mx-auto text-sage-400 mb-3" size={26} />
                <p className="text-ink-soft text-sm">{t("product.techSheetEmpty")}</p>
                <a href={askLink} target="_blank" rel="noopener noreferrer" className="btn-outline inline-block mt-4">{t("product.ask")}</a>
              </div>
            )}
          </TabsContent>

          {/* Reviews */}
          <TabsContent value="reviews" className="mt-2" data-testid="product-reviews-tab">
            <ProductReviews productId={product.id} />
          </TabsContent>
        </Tabs>
      </div>

      {/* Cross-selling */}
      {related.length > 0 && (
        <ProductCarousel overline={t("shop.title") || ""} title={t("product.relatedTitle")} products={related} testid="related-products-carousel" />
      )}
      {bestSellers.length > 0 && (
        <ProductCarousel title={t("product.bestSellersTitle")} products={bestSellers} testid="best-sellers-carousel" />
      )}

      {/* Mobile sticky add-to-cart */}
      <div className="lg:hidden fixed bottom-0 inset-x-0 z-40 bg-white border-t border-bone-200 px-4 py-3 flex items-center gap-3" style={{ boxShadow: "0 -12px 30px rgba(45,51,47,0.08)" }} data-testid="sticky-add-to-cart-bar">
        <div className="min-w-0 flex-1">
          <div className="text-sm text-ink truncate">{product.name}</div>
          <div className="text-sm font-medium text-ink">{currentPrice > 0 ? formatEUR(currentPrice) : t("common.consult")}</div>
        </div>
        <button onClick={handleAdd} disabled={!inStock || currentPrice <= 0} className="btn-primary disabled:opacity-50" data-testid="sticky-add-to-cart-button">
          {t("product.addToCartShort")}
        </button>
      </div>
    </div>
  );
}
