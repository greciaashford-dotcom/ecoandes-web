import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import { useAuth } from "../context/AuthContext";
import PasswordInput from "../components/PasswordInput";

const BUSINESS_TYPES = [
  "Tienda a Granel",
  "Ecotienda",
  "Herbolario",
  "Grupo de Consumo",
  "HORECA (Hostelería/Restauración)",
  "Obrador / Pastelería",
  "Distribuidor",
  "Otro",
];

export default function Register() {
  const { t } = useTranslation();
  const { register } = useAuth();
  const nav = useNavigate();
  const [form, setForm] = useState({
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    role: "retail",
    company: "",
    tax_id: "",
    business_type: "",
    phone: "",
  });
  const [loading, setLoading] = useState(false);
  const [pendingPro, setPendingPro] = useState(false);

  const onChange = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = { ...form };
      if (payload.role === "retail") {
        delete payload.company;
        delete payload.tax_id;
        delete payload.business_type;
      }
      const u = await register(payload);
      if (form.role === "professional") {
        // Professional accounts require manual admin approval.
        setPendingPro(true);
        window.scrollTo({ top: 0, behavior: "smooth" });
      } else {
        toast.success(t("register.created"), { description: `${t("register.welcome")} ${u.first_name}` });
        nav("/");
      }
    } catch (err) {
      toast.error(t("register.error"), { description: err?.response?.data?.detail || t("register.checkData") });
    } finally {
      setLoading(false);
    }
  };

  if (pendingPro) {
    return (
      <div className="max-w-2xl mx-auto px-6 py-20 text-center" data-testid="register-pro-pending">
        <div className="w-16 h-16 rounded-full bg-sage-100 text-sage-700 flex items-center justify-center mx-auto mb-6">
          <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>
        </div>
        <h1 className="font-heading text-3xl font-light">Solicitud en revisión</h1>
        <p className="mt-4 text-ink-soft leading-relaxed">
          Tu petición para acceder como <strong>profesional</strong> dentro de la plataforma está
          siendo revisada. En un plazo de <strong>24 horas</strong> validaremos tu cuenta y tendrás
          acceso a los precios y condiciones profesionales.
        </p>
        <p className="mt-3 text-ink-soft leading-relaxed">
          Te hemos enviado un correo de confirmación a <strong>{form.email}</strong> con esta misma
          información.
        </p>
        <div className="mt-8 flex gap-3 justify-center">
          <button onClick={() => nav("/")} className="btn-primary" data-testid="pro-pending-home">Ir al inicio</button>
          <button onClick={() => nav("/tienda")} className="btn-outline" data-testid="pro-pending-shop">Ver la tienda</button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-16" data-testid="register-page">
      <div className="overline mb-3">{t("register.overline")}</div>
      <h1 className="font-heading text-4xl font-light">{t("register.title")}</h1>
      <p className="mt-3 text-ink-soft text-sm font-light">{t("register.subtitle")}</p>

      <div className="mt-6 flex gap-2" data-testid="register-role-tabs">
        {["retail", "professional"].map((r) => (
          <button
            key={r}
            type="button"
            onClick={() => setForm((f) => ({ ...f, role: r }))}
            data-testid={`register-role-${r}`}
            className={`text-xs uppercase tracking-[0.22em] px-5 py-3 border rounded-sm transition ${
              form.role === r ? "bg-sage-500 text-white border-sage-500" : "border-bone-200 text-ink hover:border-sage-500"
            }`}
          >
            {r === "retail" ? t("register.retail") : t("register.professional")}
          </button>
        ))}
      </div>

      <form onSubmit={submit} className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4" data-testid="register-form">
        <input className="input-eco" placeholder={t("register.firstName")} required value={form.first_name} onChange={onChange("first_name")} data-testid="register-first-name" />
        <input className="input-eco" placeholder={t("register.lastName")} required value={form.last_name} onChange={onChange("last_name")} data-testid="register-last-name" />
        <input className="input-eco md:col-span-2" type="email" placeholder={t("register.email")} required value={form.email} onChange={onChange("email")} data-testid="register-email" />
        <PasswordInput className="md:col-span-2" placeholder={t("register.password")} minLength={6} required value={form.password} onChange={onChange("password")} testid="register-password" />
        <input className="input-eco" placeholder={t("register.phone")} value={form.phone} onChange={onChange("phone")} data-testid="register-phone" />
        {form.role === "professional" && (
          <>
            <p className="md:col-span-2 text-xs text-ink-soft bg-sage-50 border border-sage-200 rounded-sm px-3 py-2" data-testid="register-pro-note">
              Las cuentas profesionales requieren aprobación manual del equipo. Tras registrarte, tu
              solicitud quedará en revisión (máx. 24 h) y recibirás un correo cuando se active.
            </p>
            <input className="input-eco" placeholder={t("register.company")} required value={form.company} onChange={onChange("company")} data-testid="register-company" />
            <input className="input-eco" placeholder={t("register.taxId")} required value={form.tax_id} onChange={onChange("tax_id")} data-testid="register-tax-id" />
            <select
              className="input-eco md:col-span-2 text-ink"
              required
              value={form.business_type}
              onChange={onChange("business_type")}
              data-testid="register-business-type"
            >
              <option value="" disabled>{t("register.businessType")}</option>
              {BUSINESS_TYPES.map((b) => (
                <option key={b} value={b}>{b}</option>
              ))}
            </select>
          </>
        )}
        <button type="submit" disabled={loading} className="btn-primary md:col-span-2 w-full" data-testid="register-submit">
          {loading ? t("register.creating") : t("register.submit")}
        </button>
      </form>

      <p className="mt-6 text-sm text-ink-soft">
        {t("register.haveAccount")} <Link to="/login" className="text-sage-600 hover:text-sage-700" data-testid="register-to-login">{t("register.login")}</Link>
      </p>
    </div>
  );
}
