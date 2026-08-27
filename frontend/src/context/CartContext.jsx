import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { toast } from "sonner";

const CartContext = createContext(null);
const STORAGE_KEY = "eco_cart_v1";

export function CartProvider({ children }) {
  // Lazy-initialize from localStorage synchronously to avoid a load/save effect race
  // that could clear the cart on refresh (esp. under React StrictMode double-invoke).
  const [items, setItems] = useState(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  });
  const [drawerOpen, setDrawerOpen] = useState(false);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  }, [items]);

  const lineKey = (productId, variationName) => `${productId}::${variationName || "default"}`;

  const addItem = useCallback((product, variation, quantity = 1, isPro = false) => {
    const variationName = variation ? variation.name : null;
    const src = variation || product;
    // Prefer backend display_price (role + VAT aware). Fallback to raw ex-VAT price.
    const unit_price =
      typeof src.display_price === "number"
        ? src.display_price
        : (isPro ? src.price_professional : src.price_retail);
    const unit_price_ex_vat =
      typeof src.display_price_ex_vat === "number"
        ? src.display_price_ex_vat
        : (isPro ? src.price_professional : src.price_retail);
    const vat_rate = typeof product.vat_rate === "number" ? product.vat_rate : 10;
    // Peso: usa weight_kg si existe; si no, deriva del formato del producto ("150 g", "1 kg")
    const parseWeightFromName = (name) => {
      if (!name) return 0;
      const m = String(name).toLowerCase().match(/(\d+(?:[.,]\d+)?)\s*(kg|kilos?|g|gr|gramos|ml|l|litros?)\b/);
      if (!m) return 0;
      const val = parseFloat(m[1].replace(",", "."));
      if (Number.isNaN(val)) return 0;
      return m[2].startsWith("k") || m[2].startsWith("l") ? val : val / 1000;
    };
    const weight_kg =
      typeof src.weight_kg === "number" && src.weight_kg > 0
        ? src.weight_kg
        : parseWeightFromName(variationName || product.name);
    const sku = variation ? variation.sku : product.sku;
    setItems((prev) => {
      const key = lineKey(product.id, variationName);
      const existing = prev.find((x) => lineKey(x.product_id, x.variation_name) === key);
      if (existing) {
        return prev.map((x) =>
          lineKey(x.product_id, x.variation_name) === key
            ? { ...x, quantity: x.quantity + quantity }
            : x
        );
      }
      return [
        ...prev,
        {
          product_id: product.id,
          sku,
          name: product.name,
          variation_name: variationName,
          unit_price,
          unit_price_ex_vat,
          vat_rate,
          weight_kg,
          quantity,
          image_url: product.image_url || "",
        },
      ];
    });
    toast.success("Añadido al carrito", {
      description: `${product.name}${variation ? " · " + variation.name : ""}`,
    });
    setDrawerOpen(true);
  }, []);

  const updateQuantity = (productId, variationName, quantity) => {
    setItems((prev) => {
      if (quantity <= 0) {
        return prev.filter(
          (x) => !(x.product_id === productId && (x.variation_name || null) === (variationName || null))
        );
      }
      return prev.map((x) =>
        x.product_id === productId && (x.variation_name || null) === (variationName || null)
          ? { ...x, quantity }
          : x
      );
    });
  };

  const removeItem = (productId, variationName) => {
    setItems((prev) =>
      prev.filter(
        (x) => !(x.product_id === productId && (x.variation_name || null) === (variationName || null))
      )
    );
  };

  const clearCart = () => setItems([]);

  const subtotal = items.reduce((acc, it) => acc + it.unit_price * it.quantity, 0);
  const subtotalExVat = items.reduce(
    (acc, it) => acc + (it.unit_price_ex_vat ?? it.unit_price) * it.quantity, 0
  );
  // VAT computed from each line's vat_rate (works for both B2C and B2B carts)
  const vatAmount = Math.round(
    items.reduce(
      (acc, it) => acc + (it.unit_price_ex_vat ?? it.unit_price) * it.quantity * ((it.vat_rate ?? 0) / 100),
      0
    ) * 100
  ) / 100;
  const subtotalWithVat = Math.round((subtotalExVat + vatAmount) * 100) / 100;
  const totalWeightKg = items.reduce((acc, it) => acc + (it.weight_kg || 0) * it.quantity, 0);
  const hasBulk = items.some((it) => (it.weight_kg || 0) > 1);
  const count = items.reduce((acc, it) => acc + it.quantity, 0);

  const value = {
    items,
    subtotal,
    subtotalExVat,
    subtotalWithVat,
    vatAmount,
    totalWeightKg,
    hasBulk,
    count,
    addItem,
    updateQuantity,
    removeItem,
    clearCart,
    drawerOpen,
    setDrawerOpen,
    openDrawer: () => setDrawerOpen(true),
    closeDrawer: () => setDrawerOpen(false),
  };
  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart debe usarse dentro de CartProvider");
  return ctx;
}
