import React, { useEffect, useState } from "react";
import { api, formatEUR } from "../../lib/api";
import { ShoppingCart, Users, Package, TrendingUp } from "lucide-react";
import { Link } from "react-router-dom";

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [recent, setRecent] = useState([]);

  useEffect(() => {
    (async () => {
      try {
        const [{ data }, { data: orders }] = await Promise.all([
          api.get("/orders/admin/stats"),
          api.get("/orders/admin/list", { params: { limit: 5 } }),
        ]);
        setStats(data);
        setRecent(orders);
      } catch (e) { console.error(e); }
    })();
  }, []);

  const cards = stats ? [
    { i: ShoppingCart, t: "Pedidos totales", v: stats.orders_total, sub: `${stats.orders_pending} pendientes` },
    { i: TrendingUp, t: "Ingresos (pagados)", v: formatEUR(stats.revenue), sub: `${stats.orders_paid} pagados` },
    { i: Users, t: "Clientes", v: stats.customers, sub: "Registrados" },
    { i: Package, t: "Productos", v: stats.products, sub: "Activos" },
  ] : [];

  return (
    <div data-testid="admin-dashboard">
      <div className="overline mb-2">Panel principal</div>
      <h1 className="font-heading text-3xl font-light mb-8">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        {cards.map((c) => (
          <div key={c.t} className="bg-white border border-bone-200 p-6 rounded-sm" data-testid={`stat-${c.t.toLowerCase().replace(/ /g, '-')}`}>
            <c.i className="text-sage-600" size={18} />
            <div className="overline mt-4 mb-1">{c.t}</div>
            <div className="font-heading text-2xl font-normal text-ink">{c.v}</div>
            <div className="text-xs text-ink-soft mt-1">{c.sub}</div>
          </div>
        ))}
      </div>

      <div className="mt-10 bg-white border border-bone-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-heading text-xl font-normal">Últimos pedidos</h2>
          <Link to="/admin/pedidos" className="text-xs uppercase tracking-[0.2em] text-sage-700">Ver todos →</Link>
        </div>
        {recent.length === 0 ? (
          <div className="text-ink-soft text-sm py-6 text-center">Aún no hay pedidos.</div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-xs uppercase tracking-[0.14em] text-ink-soft text-left border-b border-bone-200">
                <th className="py-3">Pedido</th>
                <th>Cliente</th>
                <th>Tipo</th>
                <th>Total</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              {recent.map((o) => (
                <tr key={o.id} className="border-b border-bone-100" data-testid={`recent-order-${o.order_number}`}>
                  <td className="py-3"><Link className="text-sage-700" to={`/admin/pedidos/${o.id}`}>{o.order_number}</Link></td>
                  <td>{o.email}</td>
                  <td className="capitalize">{o.customer_type}</td>
                  <td>{formatEUR(o.total)}</td>
                  <td><StatusPill status={o.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export function StatusPill({ status }) {
  const map = {
    Pendiente: "bg-terracotta/15 text-terracotta",
    Pagado: "bg-sage-100 text-sage-700",
    Enviado: "bg-sage-500/15 text-sage-700",
    Completado: "bg-sage-200 text-sage-800",
    Cancelado: "bg-red-100 text-red-700",
  };
  return (
    <span className={`text-[10px] uppercase tracking-[0.18em] px-2 py-1 rounded-sm ${map[status] || "bg-bone-200 text-ink"}`}>
      {status}
    </span>
  );
}
