import React from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Heart, Scale, Plus } from "lucide-react";
import { formatEUR, resolveAsset } from "../lib/api";
import { getPriceRange } from "../lib/price";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
import { useWishlist } from "../context/WishlistContext";
import StarRating from "./StarRating";

export default function ProductCard({ product }) {
  const { t } = useTranslation();
  const { addItem } = useCart();
  const { user } = useAuth();
  const { isWished, isCompared, toggleWishlist, toggleCompare } = useWishlist();
  const isPro = user?.role === "professional" || user?.role === "admin";

  const { min, max } = getPriceRange(product, isPro);
  const hasVariations = (product.variations || []).length > 0;
  const rating = product.web_rating || 0;
  const reviews = product.web_reviews || 0;
  const img = resolveAsset(product.image_url) || resolveAsset((product.gallery || [])[0]);

  const priceLabel =
    min <= 0
      ? t("common.consult")
      : min !== max
      ? `${formatEUR(min)} – ${formatEUR(max)}`
      : formatEUR(min);

  const onAdd = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (hasVariations) return; // go to detail to pick format
    addItem(product, null, 1, isPro);
  };

  const iconBtn =
    "h-9 w-9 rounded-full bg-white/95 backdrop-blur border flex items-center justify-center transition-all duration-200 hover:scale-110 active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sage-500";

  return (
    <Link
      to={`/producto/${product.slug}`}
      data-testid={`product-card-${product.id}`}
      className="group block bg-white border border-bone-200 rounded-2xl overflow-hidden hover-lift focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sage-500 focus-visible:ring-offset-2"
    >
      <div className="relative aspect-square bg-bone-100 overflow-hidden">
        {img ? (
          <img
            src={img}
            alt={product.name}
            loading="lazy"
            className="h-full w-full object-contain p-4 transition-transform duration-500 group-hover:scale-[1.06]"
          />
        ) : (
          <div className="h-full w-full flex items-center justify-center text-ink-muted text-xs">EcoAndes</div>
        )}
        {product.best_seller && (
          <span className="absolute top-3 left-3 bg-terracotta text-white text-[10px] uppercase tracking-[0.18em] px-2.5 py-1 rounded-full shadow-sm">
            {t("productCard.bestSeller")}
          </span>
        )}
        <div className="absolute top-3 right-3 flex flex-col gap-2 opacity-100 lg:opacity-0 lg:translate-x-1 lg:group-hover:opacity-100 lg:group-hover:translate-x-0 transition-all duration-300">
          <button
            type="button"
            onClick={(e) => { e.preventDefault(); e.stopPropagation(); toggleWishlist(product); }}
            aria-label={t("productCard.wishlist")}
            data-testid={`product-card-wishlist-${product.id}`}
            className={`${iconBtn} ${isWished(product.id) ? "border-terracotta text-terracotta" : "border-bone-200 text-ink hover:border-sage-500"}`}
          >
            <Heart size={15} fill={isWished(product.id) ? "currentColor" : "none"} />
          </button>
          <button
            type="button"
            onClick={(e) => { e.preventDefault(); e.stopPropagation(); toggleCompare(product); }}
            aria-label={t("productCard.compare")}
            data-testid={`product-card-compare-${product.id}`}
            className={`${iconBtn} ${isCompared(product.id) ? "border-sage-600 text-sage-700" : "border-bone-200 text-ink hover:border-sage-500"}`}
          >
            <Scale size={15} />
          </button>
        </div>
      </div>

      <div className="p-4">
        <div className="overline text-sage-600 mb-1.5 line-clamp-1">{product.category}</div>
        <h3 className="font-heading text-base text-ink leading-snug line-clamp-2 min-h-[2.6rem] transition-colors duration-200 group-hover:text-sage-700">{product.name}</h3>
        {rating > 0 && (
          <div className="flex items-center gap-1.5 mt-1.5">
            <StarRating value={rating} readOnly size={12} />
            {reviews > 0 && <span className="text-[11px] text-ink-muted">({reviews})</span>}
          </div>
        )}
        <div className="flex items-center justify-between mt-2.5">
          <span className="text-sm text-ink" data-testid={`product-card-price-${product.id}`}>{priceLabel}</span>
          {hasVariations ? (
            <span className="text-[11px] uppercase tracking-[0.18em] text-sage-600 transition-transform duration-200 group-hover:translate-x-0.5">{t("product.viewProduct")}</span>
          ) : (
            min > 0 && (
              <button
                type="button"
                onClick={onAdd}
                aria-label={t("productCard.addToCart")}
                data-testid={`product-card-add-${product.id}`}
                className="h-9 w-9 rounded-full bg-sage-500 text-white hover:bg-sage-600 transition-all duration-200 hover:scale-110 active:scale-95 flex items-center justify-center shadow-sm"
              >
                <Plus size={16} />
              </button>
            )
          )}
        </div>
      </div>
    </Link>
  );
}
