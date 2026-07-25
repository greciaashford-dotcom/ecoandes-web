import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, formatEUR } from "../../lib/api";
import { toast } from "sonner";
import { StatusPill } from "./AdminDashboard";

const STATUSES = ["Pendiente", "Pagado", "Enviado", "Completado", "Cancelado", "Reembolsado"];

export default function AdminOrderDetail() {
  const { id } = useParams();
  const [order, setOrder] = useState(null);
  const [updating, setUpdating] = useState(false);
  const [reasons, setReasons] = useState([]);
  const [refundReason, setRefundReason] = useState("");
  const [refundAmount, setRefundAmount] = useState("");
  const [refunding, setRefunding] = useState(false);

  const load = async () => {
    const { data } = await api.get(`/orders/admin/${id}`);
    setOrder(data);
    setRefundAmount(String(data.total ?? ""));
  };

  useEffect(() => { load(); }, [id]);
  useEffect(() => {
    api.get("/admin/refund-reasons").then(({ data }) => {
      const active = (data.reasons || []).filter((r) => r.active);
      setReasons(active);
      if (active.length) setRefundReason(active[0].label);
    }).catch(() => {});
  }, []);

  const updateStatus = async (status) => {
    setUpdating(true);
    try {
      const { data } = await api.patch(`/orders/admin/${id}/status`, { status });
      setOrder(data);
      toast.success("Estado actualizado");
    } catch (e) {
      toast.error("Error", { description: e?.response?.data?.detail });
    } finally { setUpdating(false); }
  };

  const doRefund = async () => {
    if (!refundReason) { toast.error("Selecciona un motivo"); return; }
    if (!window.confirm(`¿Reembolsar ${refundAmount}€ del pedido ${order.order_number}?`)) return;
    setRefunding(true);
    try {
      const { data } = await api.post(`/orders/admin/${id}/refund`, {
        reason: refundReason,
        amount: refundAmount === "" ? null : Number(refundAmount),
        notify: true,
      });
      const emailNote = data.email_sent ? " · email enviado al cliente" : " · email no enviado (falta configurar Resend)";
      const provNote = data.provider_result?.ok ? `Reembolso procesado vía ${data.refund.provider}` : "Registrado como reembolso manual";
      toast.success("Reembolso registrado", { description: provNote + emailNote });
      load();
    } catch (e) {
      toast.error("Error al reembolsar", { description: e?.response?.data?.detail });
    } finally { setRefunding(false); }
  };

  if (!order) return <div className="text-ink-soft">Cargando pedido…</div>;
  const addr = order.shipping_address || {};
  return (
    <div data-testid="admin-order-detail">
      <Link to="/admin/pedidos" className="text-sm text-sage-700" data-testid="back-to-orders">← Volver a pedidos</Link>
      <div className="flex flex-wrap items-center justify-between gap-4 mt-4">
        <div>
          <div className="overline mb-1">Pedido</div>
          <h1 className="font-heading text-3xl font-light">{order.order_number}</h1>
          <div className="text-sm text-ink-soft mt-1">{new Date(order.created_at).toLocaleString("es-ES")}</div>
        </div>
        <StatusPill status={order.status} />
      </div>

      <div className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white border border-bone-200 p-6">
          <h2 className="font-heading text-xl font-normal mb-4">Productos</h2>
          <ul className="divide-y divide-bone-100">
            {order.items.map((it, i) => (
              <li key={i} className="py-4 flex gap-4 items-start" data-testid={`order-item-${it.sku}`}>
                <div className="w-16 h-16 bg-bone-100 overflow-hidden shrink-0">
                  {it.image_url && <img src={it.image_url} alt={it.name} className="w-full h-full object-cover" />}
                </div>
                <div className="flex-1">
                  <div className="text-sm text-ink">{it.name}</div>
                  {it.variation_name && <div className="text-xs text-ink-soft">{it.variation_name}</div>}
                  <div className="text-xs text-ink-soft">SKU: {it.sku}</div>
                </div>
                <div className="text-sm">{it.quantity} × {formatEUR(it.unit_price)}</div>
                <div className="text-sm font-medium">{formatEUR(it.unit_price * it.quantity)}</div>
              </li>
            ))}
          </ul>
          <div className="mt-6 border-t border-bone-200 pt-4 text-sm space-y-1.5 max-w-xs ml-auto">
            <div className="flex justify-between"><span className="text-ink-soft">Subtotal</span><span>{formatEUR(order.subtotal)}</span></div>
            <div className="flex justify-between"><span className="text-ink-soft">Envío</span><span>{formatEUR(order.shipping_cost)}</span></div>
            <div className="flex justify-between text-base font-medium pt-2 border-t border-bone-200"><span>Total</span><span>{formatEUR(order.total)}</span></div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white border border-bone-200 p-6">
            <h3 className="overline mb-3">Cliente</h3>
            <div className="text-sm text-ink">{addr.full_name}</div>
            <div className="text-sm text-ink-soft">{order.email}</div>
            {addr.phone && <div className="text-sm text-ink-soft">{addr.phone}</div>}
            <div className="text-xs uppercase tracking-[0.18em] text-sage-700 mt-2">{order.customer_type}</div>
          </div>
          <div className="bg-white border border-bone-200 p-6">
            <h3 className="overline mb-3">Envío</h3>
            <div className="text-sm text-ink-soft leading-relaxed">
              {addr.street}<br />
              {addr.postal_code} {addr.city}<br />
              {addr.province}, {addr.country}
            </div>
            {addr.notes && <div className="text-xs text-ink-muted mt-3">Notas: {addr.notes}</div>}
          </div>
          <div className="bg-white border border-bone-200 p-6">
            <h3 className="overline mb-3">Pago</h3>
            <div className="text-sm capitalize">{order.payment_method}</div>
            <div className="text-xs text-ink-soft">Estado: {order.payment_status}</div>
          </div>
          <div className="bg-white border border-bone-200 p-6">
            <h3 className="overline mb-3">Cambiar estado</h3>
            <select
              className="input-eco"
              value={order.status}
              onChange={(e) => updateStatus(e.target.value)}
              disabled={updating}
              data-testid="order-status-select"
            >
              {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>

          {/* Refund */}
          <div className="bg-white border border-bone-200 p-6" data-testid="order-refund-panel">
            <h3 className="overline mb-3">Reembolso</h3>
            {order.status === "Reembolsado" || order.payment_status === "refunded" ? (
              <div className="text-sm" data-testid="order-refunded-note">
                <div className="inline-flex items-center gap-1.5 text-sage-700 bg-sage-50 border border-sage-200 rounded-full px-3 py-1 text-xs uppercase tracking-wide">Reembolsado</div>
                {order.refund && (
                  <div className="text-ink-soft mt-3 leading-relaxed">
                    {formatEUR(order.refund.amount)} · {order.refund.reason}<br />
                    {order.refund.manual ? "Reembolso manual" : `Vía ${order.refund.provider}`}
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-3">
                <label className="block text-xs text-ink-soft">Motivo del reembolso
                  <select className="input-eco mt-1" value={refundReason} onChange={(e) => setRefundReason(e.target.value)} data-testid="refund-reason-select">
                    {reasons.length === 0 && <option value="">(Configura motivos en Reembolsos)</option>}
                    {reasons.map((r) => <option key={r.id} value={r.label}>{r.label}</option>)}
                  </select>
                </label>
                <label className="block text-xs text-ink-soft">Importe a reembolsar (€)
                  <input type="number" step="0.01" className="input-eco mt-1" value={refundAmount} onChange={(e) => setRefundAmount(e.target.value)} data-testid="refund-amount-input" />
                </label>
                <button onClick={doRefund} disabled={refunding || !refundReason} className="btn-primary w-full disabled:opacity-60" data-testid="refund-submit-btn">
                  {refunding ? "Procesando…" : "Reembolsar y avisar al cliente"}
                </button>
                <p className="text-[11px] text-ink-muted">Se intentará el reembolso automático (Stripe/PayPal) si el pedido se pagó online; en caso contrario quedará como reembolso manual. Se enviará un email al cliente.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
