import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Package, ShoppingBag, Heart, ArrowRight } from "lucide-react";
import { api, formatEUR } from "../lib/api";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";

export default function Account() {
  const { user, logout } = useAuth();
  const { count, openDrawer } = useCart();
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    (async () => {
      try {
        const { data } = await api.get("/orders/mine");
        setOrders(data);
      } catch {}
    })();
  }, []);

  const myProducts = useMemo(() => {
    const map = new Map();
    orders.forEach((o) => {
      (o.items || []).forEach((it) => {
        const key = `${it.product_id}:${it.variation_name || ""}`;
        const prev = map.get(key);
        if (prev) {
          prev.quantity += it.quantity;
          prev.last_ordered = o.created_at > prev.last_ordered ? o.created_at : prev.last_ordered;
        } else {
          map.set(key, { ...it, quantity: it.quantity, last_ordered: o.created_at });
        }
      });
    });
    return Array.from(map.values()).sort((a, b) => (b.last_ordered > a.last_ordered ? 1 : -1));
  }, [orders]);

  const totalOrders = orders.length;
  const totalSpent = orders.reduce((acc, o) => acc + (o.total || 0), 0);

  if (!user) {
    return (
      <div className="max-w-xl mx-auto py-20 px-6 text-center">
        <p className="text-ink-soft">Debes iniciar sesión.</p>
        <Link to="/login" className="btn-outline mt-6 inline-block">Acceder</Link>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-6 lg:px-12 py-12 sm:py-14" data-testid="account-page">
      <div className="overline mb-3">Mi cuenta</div>
      <h1 className="font-heading text-3xl sm:text-4xl md:text-5xl font-light">Hola, {user.first_name}</h1>
      <div className="flex items-center gap-3 mt-3 text-sm text-ink-soft flex-wrap">
        <span>{user.email}</span>
        <span>·</span>
        <span className="text-sage-700 uppercase tracking-[0.18em] text-xs">
          {user.role === "professional" ? "Cuenta B2B" : user.role === "admin" ? "Administrador" : "Retail"}
        </span>
      </div>

      {/* 3 tarjetas: Mis Productos · Mis Pedidos · Carrito */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6 mt-10" data-testid="account-quick-cards">
        <a href="#mis-productos" data-testid="account-card-products" className="group bg-white border border-bone-200 hover:border-sage-300 hover:shadow-[0_8px_30px_rgba(0,0,0,0.06)] transition-all p-6 flex flex-col">
          <div className="flex items-center justify-between mb-5">
            <div className="w-11 h-11 rounded-sm bg-sage-100 flex items-center justify-center text-sage-700">
              <Heart size={20} />
            </div>
            <span className="overline">Mis productos</span>
          </div>
          <div className="font-heading text-3xl font-light" data-testid="card-products-count">{myProducts.length}</div>
          <div className="text-sm text-ink-soft mt-1">Productos comprados al menos una vez</div>
          <div className="mt-auto pt-5 text-xs uppercase tracking-[0.2em] text-sage-700 inline-flex items-center gap-2 group-hover:gap-3 transition-all">
            Ver listado <ArrowRight size={12} />
          </div>
        </a>
        <a href="#mis-pedidos" data-testid="account-card-orders" className="group bg-white border border-bone-200 hover:border-sage-300 hover:shadow-[0_8px_30px_rgba(0,0,0,0.06)] transition-all p-6 flex flex-col">
          <div className="flex items-center justify-between mb-5">
            <div className="w-11 h-11 rounded-sm bg-sage-100 flex items-center justify-center text-sage-700">
              <Package size={20} />
            </div>
            <span className="overline">Mis pedidos</span>
          </div>
          <div className="font-heading text-3xl font-light" data-testid="card-orders-count">{totalOrders}</div>
          <div className="text-sm text-ink-soft mt-1">Total invertido: {formatEUR(totalSpent)}</div>
          <div className="mt-auto pt-5 text-xs uppercase tracking-[0.2em] text-sage-700 inline-flex items-center gap-2 group-hover:gap-3 transition-all">
            Ver pedidos <ArrowRight size={12} />
          </div>
        </a>
        <button
          type="button"
          onClick={openDrawer}
          data-testid="account-card-cart"
          className="text-left group bg-white border border-bone-200 hover:border-sage-300 hover:shadow-[0_8px_30px_rgba(0,0,0,0.06)] transition-all p-6 flex flex-col"
        >
          <div className="flex items-center justify-between mb-5">
            <div className="w-11 h-11 rounded-sm bg-sage-100 flex items-center justify-center text-sage-700">
              <ShoppingBag size={20} />
            </div>
            <span className="overline">Carrito</span>
          </div>
          <div className="font-heading text-3xl font-light" data-testid="card-cart-count">{count}</div>
          <div className="text-sm text-ink-soft mt-1">{count === 0 ? "Sin productos en cesta" : "Productos en tu cesta"}</div>
          <div className="mt-auto pt-5 text-xs uppercase tracking-[0.2em] text-sage-700 inline-flex items-center gap-2 group-hover:gap-3 transition-all">
            Abrir cesta <ArrowRight size={12} />
          </div>
        </button>
      </div>

      {/* Mis productos */}
      <section id="mis-productos" className="mt-16" data-testid="account-products-section">
        <div className="flex items-end justify-between mb-5 gap-3">
          <h2 className="font-heading text-2xl sm:text-3xl font-light">Mis productos comprados</h2>
          <Link to="/tienda" className="text-xs uppercase tracking-[0.2em] text-sage-700 whitespace-nowrap">Seguir comprando →</Link>
        </div>
        {myProducts.length === 0 ? (
          <div className="bg-white border border-bone-200 p-8 text-ink-soft text-sm text-center">
            Aún no has comprado productos. <Link to="/tienda" className="text-sage-700">Descubre el catálogo</Link>.
          </div>
        ) : (
          <div className="bg-white border border-bone-200 divide-y divide-bone-100">
            {myProducts.map((it, i) => (
              <div key={i} className="p-4 sm:p-5 flex gap-4 items-center" data-testid={`my-product-${it.sku}`}>
                <div className="w-14 h-14 sm:w-16 sm:h-16 bg-bone-100 overflow-hidden shrink-0">
                  {it.image_url && <img src={it.image_url} alt={it.name} className="w-full h-full object-cover" />}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm sm:text-base text-ink truncate">{it.name}</div>
                  <div className="text-xs text-ink-soft">
                    {it.variation_name && <span>{it.variation_name} · </span>}
                    SKU {it.sku}
                  </div>
                  <div className="text-xs text-ink-muted mt-1">Comprado {it.quantity} {it.quantity === 1 ? "vez" : "veces"} · último pedido {new Date(it.last_ordered).toLocaleDateString("es-ES")}</div>
                </div>
                <div className="hidden sm:block text-sm text-ink-soft">{formatEUR(it.unit_price)}</div>
                <Link to={`/tienda?q=${encodeURIComponent(it.name)}`} className="btn-outline py-2.5 px-4 text-[10px] hidden md:inline-block whitespace-nowrap">
                  Volver a comprar
                </Link>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Mis pedidos */}
      <section id="mis-pedidos" className="mt-16" data-testid="account-orders-section">
        <h2 className="font-heading text-2xl sm:text-3xl font-light mb-5">Tus pedidos</h2>
        {orders.length === 0 ? (
          <div className="bg-white border border-bone-200 p-8 text-ink-soft text-sm text-center">Aún no tienes pedidos.</div>
        ) : (
          <div className="space-y-4" data-testid="account-orders-list">
            {orders.map((o) => (
              <div key={o.id} className="bg-white border border-bone-200 p-5 flex flex-wrap items-center gap-5 justify-between" data-testid={`account-order-${o.order_number}`}>
                <div>
                  <div className="text-xs text-ink-soft uppercase tracking-[0.18em]">{new Date(o.created_at).toLocaleDateString("es-ES")}</div>
                  <div className="font-heading text-lg mt-1">Pedido {o.order_number}</div>
                </div>
                <div className="flex gap-6 text-sm">
                  <div><div className="text-ink-soft text-xs">Total</div><div>{formatEUR(o.total)}</div></div>
                  <div><div className="text-ink-soft text-xs">Estado</div><div className="text-sage-700">{o.status}</div></div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      <div className="mt-14">
        <button onClick={logout} className="btn-outline" data-testid="account-logout-btn">Cerrar sesión</button>
      </div>
    </div>
  );
}
