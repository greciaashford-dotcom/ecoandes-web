"""Resend email sender."""
import asyncio
import logging
from typing import Optional

import resend

from core.config import RESEND_API_KEY, SENDER_EMAIL, ADMIN_NOTIFICATION_EMAIL, STORE_NOTIFICATION_EMAIL

logger = logging.getLogger(__name__)


def _order_email_html(order: dict) -> str:
    rows = "".join(
        f"""
        <tr>
          <td style="padding:10px 0;border-bottom:1px solid #EAE6DF;">
            <div style="color:#2D332F;font-size:14px;">{it.get('name', '')}{' · ' + it['variation_name'] if it.get('variation_name') else ''}</div>
            <div style="color:#606962;font-size:12px;">SKU: {it.get('sku', '')}</div>
          </td>
          <td style="padding:10px 0;border-bottom:1px solid #EAE6DF;text-align:right;color:#2D332F;font-size:14px;">
            {it.get('quantity', 0)} × {it.get('unit_price', 0):.2f} €
          </td>
        </tr>
        """
        for it in order.get("items", [])
    )
    addr = order.get("shipping_address", {}) or {}
    return f"""
    <div style="font-family:Manrope,Arial,sans-serif;background:#F9F8F6;padding:40px 20px;color:#2D332F;">
      <div style="max-width:560px;margin:0 auto;background:#FFFFFF;padding:40px;">
        <div style="text-align:center;margin-bottom:24px;">
          <div style="font-family:Outfit,Arial,sans-serif;font-size:28px;letter-spacing:0.12em;color:#2D332F;font-weight:300;">ECOANDES</div>
          <div style="color:#6B826E;font-size:11px;letter-spacing:0.3em;text-transform:uppercase;margin-top:4px;">Natural · BIO</div>
        </div>
        <h2 style="font-family:Outfit,Arial,sans-serif;font-weight:300;color:#2D332F;margin:24px 0 8px;">Gracias por tu pedido</h2>
        <p style="color:#606962;font-size:14px;line-height:1.6;">
          Hemos recibido tu pedido <strong>#{order.get('order_number', '')}</strong>.
          Pronto recibirás otro email cuando sea enviado.
        </p>
        <table style="width:100%;border-collapse:collapse;margin-top:24px;">
          {rows}
        </table>
        <table style="width:100%;margin-top:16px;">
          <tr><td style="color:#606962;font-size:13px;padding:4px 0;">Subtotal</td>
              <td style="text-align:right;font-size:13px;color:#2D332F;">{order.get('subtotal', 0):.2f} €</td></tr>
          <tr><td style="color:#606962;font-size:13px;padding:4px 0;">Envío</td>
              <td style="text-align:right;font-size:13px;color:#2D332F;">{order.get('shipping_cost', 0):.2f} €</td></tr>
          <tr><td style="color:#2D332F;font-size:16px;padding:12px 0;border-top:1px solid #EAE6DF;"><strong>Total</strong></td>
              <td style="text-align:right;font-size:16px;color:#2D332F;border-top:1px solid #EAE6DF;padding:12px 0;"><strong>{order.get('total', 0):.2f} €</strong></td></tr>
        </table>
        <h3 style="font-family:Outfit,Arial,sans-serif;font-weight:400;color:#2D332F;margin-top:32px;">Envío a</h3>
        <p style="color:#606962;font-size:13px;line-height:1.6;">
          {addr.get('full_name', '')}<br/>
          {addr.get('street', '')}<br/>
          {addr.get('postal_code', '')} {addr.get('city', '')}, {addr.get('province', '')}<br/>
          {addr.get('country', '')}
        </p>
        <p style="color:#9BA39D;font-size:11px;text-align:center;margin-top:40px;letter-spacing:0.1em;">
          Ecoandes · Productos ecológicos de los Andes
        </p>
      </div>
    </div>
    """


async def send_order_confirmation(order: dict) -> Optional[str]:
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not configured; skipping order email.")
        return None
    resend.api_key = RESEND_API_KEY
    recipients = [order["email"]]
    bcc = [ADMIN_NOTIFICATION_EMAIL] if ADMIN_NOTIFICATION_EMAIL else []
    params = {
        "from": SENDER_EMAIL,
        "to": recipients,
        "subject": f"Confirmación de pedido #{order.get('order_number', '')} · Ecoandes",
        "html": _order_email_html(order),
    }
    if bcc:
        params["bcc"] = bcc
    try:
        resp = await asyncio.to_thread(resend.Emails.send, params)
        return resp.get("id") if isinstance(resp, dict) else None
    except Exception as e:
        logger.exception("Failed to send order email: %s", e)
        return None


def _pickup_email_html(order: dict) -> str:
    rows = "".join(
        f"""
        <tr>
          <td style="padding:8px 0;border-bottom:1px solid #EAE6DF;color:#2D332F;font-size:14px;">
            {it.get('name', '')}{' · ' + it['variation_name'] if it.get('variation_name') else ''}
            <span style="color:#9BA39D;"> (SKU: {it.get('sku', '')})</span>
          </td>
          <td style="padding:8px 0;border-bottom:1px solid #EAE6DF;text-align:right;color:#2D332F;font-size:14px;">
            x{it.get('quantity', 0)}
          </td>
        </tr>
        """
        for it in order.get("items", [])
    )
    addr = order.get("shipping_address", {}) or {}
    return f"""
    <div style="font-family:Manrope,Arial,sans-serif;background:#F9F8F6;padding:32px 20px;color:#2D332F;">
      <div style="max-width:560px;margin:0 auto;background:#FFFFFF;padding:36px;border-top:4px solid #6B826E;">
        <div style="color:#6B826E;font-size:11px;letter-spacing:0.3em;text-transform:uppercase;">Recogida en tienda</div>
        <h2 style="font-family:Outfit,Arial,sans-serif;font-weight:400;color:#2D332F;margin:8px 0 4px;">Nuevo pedido para recoger</h2>
        <p style="color:#606962;font-size:14px;line-height:1.6;">
          Pedido <strong>#{order.get('order_number', '')}</strong> pagado por adelantado.
          El cliente pasará a recogerlo por la tienda.
        </p>
        <table style="width:100%;border-collapse:collapse;margin-top:16px;">{rows}</table>
        <table style="width:100%;margin-top:12px;">
          <tr><td style="color:#2D332F;font-size:15px;padding:10px 0;border-top:1px solid #EAE6DF;"><strong>Total pagado</strong></td>
              <td style="text-align:right;font-size:15px;color:#2D332F;border-top:1px solid #EAE6DF;padding:10px 0;"><strong>{order.get('total', 0):.2f} €</strong></td></tr>
        </table>
        <h3 style="font-family:Outfit,Arial,sans-serif;font-weight:400;color:#2D332F;margin-top:24px;">Datos del cliente</h3>
        <p style="color:#606962;font-size:13px;line-height:1.6;">
          {addr.get('full_name', '')}<br/>
          {('Tel: ' + addr.get('phone')) if addr.get('phone') else ''}<br/>
          Email: {order.get('email', '')}
        </p>
      </div>
    </div>
    """


async def send_pickup_notification(order: dict) -> Optional[str]:
    """Notify the physical store that a paid pickup order is ready to prepare."""
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not configured; skipping pickup notification.")
        return None
    if not STORE_NOTIFICATION_EMAIL:
        logger.warning("STORE_NOTIFICATION_EMAIL not configured; skipping pickup notification.")
        return None
    resend.api_key = RESEND_API_KEY
    params = {
        "from": SENDER_EMAIL,
        "to": [STORE_NOTIFICATION_EMAIL],
        "subject": f"🛍️ Recogida en tienda · Pedido #{order.get('order_number', '')} · Ecoandes",
        "html": _pickup_email_html(order),
    }
    try:
        resp = await asyncio.to_thread(resend.Emails.send, params)
        return resp.get("id") if isinstance(resp, dict) else None
    except Exception as e:
        logger.exception("Failed to send pickup notification: %s", e)
        return None



# ---------- Generic branded wrapper ----------
def _wrap(title: str, body_html: str, accent: str = "#6B826E") -> str:
    return f"""
    <div style="font-family:Manrope,Arial,sans-serif;background:#F9F8F6;padding:40px 20px;color:#2D332F;">
      <div style="max-width:560px;margin:0 auto;background:#FFFFFF;padding:40px;border-top:4px solid {accent};">
        <div style="text-align:center;margin-bottom:16px;">
          <div style="font-family:Outfit,Arial,sans-serif;font-size:26px;letter-spacing:0.12em;color:#2D332F;font-weight:300;">ECOANDES</div>
          <div style="color:#6B826E;font-size:11px;letter-spacing:0.3em;text-transform:uppercase;margin-top:4px;">Natural · BIO</div>
        </div>
        <h2 style="font-family:Outfit,Arial,sans-serif;font-weight:400;color:#2D332F;margin:20px 0 10px;">{title}</h2>
        {body_html}
        <p style="color:#9BA39D;font-size:11px;text-align:center;margin-top:36px;letter-spacing:0.1em;">
          Ecoandes · Productos ecológicos de los Andes
        </p>
      </div>
    </div>
    """


async def _send(to: str, subject: str, html: str) -> Optional[str]:
    """Low-level send helper. No-op (logged) when RESEND_API_KEY is missing."""
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not configured; skipping email to %s (%s)", to, subject)
        return None
    if not to:
        return None
    resend.api_key = RESEND_API_KEY
    params = {"from": SENDER_EMAIL, "to": [to], "subject": subject, "html": html}
    try:
        resp = await asyncio.to_thread(resend.Emails.send, params)
        return resp.get("id") if isinstance(resp, dict) else None
    except Exception as e:  # noqa: BLE001
        logger.exception("Failed to send email (%s): %s", subject, e)
        return None


# ---------- Professional account: under review ----------
async def send_professional_review(user: dict) -> Optional[str]:
    name = user.get("first_name", "")
    body = f"""
      <p style="color:#606962;font-size:14px;line-height:1.7;">
        Hola {name}, hemos recibido tu solicitud para acceder como <strong>profesional (B2B)</strong>
        en EcoAndes.
      </p>
      <p style="color:#606962;font-size:14px;line-height:1.7;">
        Tu petición está siendo revisada por nuestro equipo. En un plazo de
        <strong>24 horas</strong> validaremos tu cuenta y te avisaremos por email cuando
        tengas acceso a los precios y condiciones profesionales.
      </p>
      <p style="color:#606962;font-size:14px;line-height:1.7;">
        Mientras tanto, puedes navegar por la tienda con normalidad. Gracias por tu confianza.
      </p>
    """
    return await _send(user.get("email"), "Tu solicitud profesional está en revisión · Ecoandes",
                       _wrap("Solicitud en revisión", body))


async def send_professional_approved(user: dict) -> Optional[str]:
    name = user.get("first_name", "")
    body = f"""
      <p style="color:#606962;font-size:14px;line-height:1.7;">
        ¡Buenas noticias, {name}! Tu cuenta <strong>profesional (B2B)</strong> ha sido
        <strong style="color:#6B826E;">aprobada</strong>.
      </p>
      <p style="color:#606962;font-size:14px;line-height:1.7;">
        Ya puedes iniciar sesión y disfrutar de los precios y condiciones profesionales
        en toda la tienda.
      </p>
    """
    return await _send(user.get("email"), "Tu cuenta profesional ha sido aprobada · Ecoandes",
                       _wrap("Cuenta aprobada", body))


# ---------- Refund notification ----------
async def send_refund_notification(order: dict, refund: dict) -> Optional[str]:
    addr = order.get("shipping_address", {}) or {}
    name = addr.get("full_name", "")
    reason = refund.get("reason", "")
    amount = float(refund.get("amount", order.get("total", 0)) or 0)
    method = refund.get("provider") or order.get("payment_method", "")
    manual = refund.get("manual")
    method_line = (
        "El importe se devolverá manualmente a tu método de pago original."
        if manual else
        f"El reembolso se ha procesado a través de {method}. Puede tardar unos días en reflejarse."
    )
    body = f"""
      <p style="color:#606962;font-size:14px;line-height:1.7;">
        Hola {name}, te confirmamos el <strong>reembolso</strong> de tu pedido
        <strong>#{order.get('order_number', '')}</strong>.
      </p>
      <table style="width:100%;margin-top:16px;border-collapse:collapse;">
        <tr><td style="color:#606962;font-size:13px;padding:6px 0;">Importe reembolsado</td>
            <td style="text-align:right;font-size:15px;color:#2D332F;"><strong>{amount:.2f} €</strong></td></tr>
        <tr><td style="color:#606962;font-size:13px;padding:6px 0;border-top:1px solid #EAE6DF;">Motivo</td>
            <td style="text-align:right;font-size:13px;color:#2D332F;border-top:1px solid #EAE6DF;">{reason}</td></tr>
      </table>
      <p style="color:#606962;font-size:14px;line-height:1.7;margin-top:16px;">{method_line}</p>
      <p style="color:#606962;font-size:14px;line-height:1.7;">Lamentamos las molestias y gracias por tu comprensión.</p>
    """
    return await _send(order.get("email"), f"Reembolso de tu pedido #{order.get('order_number','')} · Ecoandes",
                       _wrap("Reembolso procesado", body, accent="#B0654F"))
