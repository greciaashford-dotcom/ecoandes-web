import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, formatEUR } from "../../lib/api";
import { StatusPill } from "./AdminDashboard";

const STATUSES = ["", "Pendiente", "Pagado", "Enviado", "Completado", "Cancelado"];

export default function AdminOrders() {
  const [orders, setOrders] = useState([]);
  const [filter, setFilter] = useState({ status: "", customer_type: "" });
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const { data } = await api.get("/orders/admin/list", {
        params: {
          status: filter.status || undefined,
          customer_type: filter.customer_type || undefined,
        },
      });
      setOrders(data);
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, [filter.status, filter.customer_type]);

  return (
    <div data-testid="admin-orders-page">
      <div className="overline mb-2">Gestión de pedidos</div>
      <h1 className="font-heading text-3xl font-light mb-6">Pedidos</h1>
      <div className="flex flex-wrap gap-3 mb-5" data-testid="orders-filters">
        <select className="input-eco max-w-xs" value={filter.status} onChange={(e) => setFilter((f) => ({ ...f, status: e.target.value }))} data-testid="orders-filter-status">
          {STATUSES.map((s) => <option key={s} value={s}>{s || "Todos los estados"}</option>)}
        </select>
        <select className="input-eco max-w-xs" value={filter.customer_type} onChange={(e) => setFilter((f) => ({ ...f, customer_type: e.target.value }))} data-testid="orders-filter-type">
          <option value="">Todos los clientes</option>
          <option value="retail">Retail</option>
          <option value="professional">Profesional</option>
        </select>
      </div>
      <div className="bg-white border border-bone-200 overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-xs uppercase tracking-[0.14em] text-ink-soft text-left border-b border-bone-200">
              <th className="p-4">Pedido</th>
              <th>Fecha</th>
              <th>Cliente</th>
              <th>Tipo</th>
              <th>Total</th>
              <th>Pago</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={7} className="py-10 text-center text-ink-soft">Cargando…</td></tr>
            ) : orders.length === 0 ? (
              <tr><td colSpan={7} className="py-10 text-center text-ink-soft" data-testid="orders-empty">Sin pedidos.</td></tr>
            ) : orders.map((o) => (
              <tr key={o.id} className="border-b border-bone-100 hover:bg-bone-100/40" data-testid={`order-row-${o.order_number}`}>
                <td className="p-4"><Link to={`/admin/pedidos/${o.id}`} className="text-sage-700 font-medium">{o.order_number}</Link></td>
                <td>{new Date(o.created_at).toLocaleDateString("es-ES")}</td>
                <td>{o.email}</td>
                <td className="capitalize">{o.customer_type}</td>
                <td>{formatEUR(o.total)}</td>
                <td className="capitalize">{o.payment_method} · {o.payment_status}</td>
                <td><StatusPill status={o.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
