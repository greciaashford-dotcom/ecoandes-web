import React from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Instagram, Facebook, Linkedin, Mail, Phone, MessageCircle, MapPin, Store, Clock } from "lucide-react";
import { STORE, STORE_HOURS, STORE_MAPS_URL, WAREHOUSE_MAPS_URL } from "../data/storeInfo";
import NewsletterForm from "./NewsletterForm";

const PHONE_DISPLAY = "918 30 72 66";
const PHONE_TEL = "+34918307266";
const WHATSAPP = "34696173094";
const WHATSAPP_DISPLAY = "+34 696 17 30 94";
const ADDRESS_LINE_1 = "C. Ferrocarril, 16, Edificio 12 Nave 4";
const ADDRESS_LINE_2 = "28880 Meco, Madrid";

export default function Footer() {
  const { t } = useTranslation();
  const waLink = `https://wa.me/${WHATSAPP}?text=${encodeURIComponent(
    "Hola, tengo una consulta sobre los productos Ecoandes."
  )}`;

  return (
    <footer className="bg-sage-800 text-bone-100 mt-20" data-testid="eco-footer">
      {/* Newsletter band */}
      <div className="border-b border-sage-700/50" data-testid="footer-newsletter">
        <div className="max-w-7xl mx-auto px-6 lg:px-12 py-12 grid md:grid-cols-2 gap-8 items-center">
          <div>
            <div className="overline text-sage-200 mb-2">{t("footer.newsletterTitle")}</div>
            <h3 className="font-heading text-2xl sm:text-3xl font-light text-bone-100">{t("newsletter.title")}</h3>
            <p className="text-sm text-sage-100/80 mt-2 max-w-md">{t("newsletter.subtitle")}</p>
          </div>
          <div>
            <NewsletterForm variant="footer" />
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 lg:px-12 py-16 sm:py-20 grid grid-cols-2 md:grid-cols-4 gap-10 sm:gap-12">
        <div className="col-span-2 md:col-span-2">
          <img
            src="/logo-ecoandes.png"
            alt="EcoAndes · Organic Ingredients"
            className="h-20 w-auto object-contain mb-6"
          />
          <p className="text-sm text-sage-100/80 max-w-md leading-relaxed font-light">
            {t("footer.tagline")}
          </p>
          <div className="mt-7 space-y-2.5 text-sm text-sage-100/90">
            <a
              href={WAREHOUSE_MAPS_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-start gap-2 hover:text-sage-200"
              data-testid="footer-address"
            >
              <MapPin size={14} className="mt-0.5 shrink-0" />
              <span>
                {ADDRESS_LINE_1}<br />
                {ADDRESS_LINE_2}
              </span>
            </a>
            <a href="mailto:info@productosecoandes.com" className="flex items-center gap-2 hover:text-sage-200" data-testid="footer-email">
              <Mail size={14} /> info@productosecoandes.com
            </a>
            <a href={`tel:${PHONE_TEL}`} className="flex items-center gap-2 hover:text-sage-200" data-testid="footer-phone">
              <Phone size={14} /> {PHONE_DISPLAY}
            </a>
            <a
              href={waLink}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 hover:text-sage-200"
              data-testid="footer-whatsapp"
            >
              <MessageCircle size={14} /> WhatsApp {WHATSAPP_DISPLAY}
            </a>
          </div>
          <div className="flex gap-3 mt-7" data-testid="footer-socials">
            <a
              href="https://www.facebook.com/EcoandesBio"
              target="_blank"
              rel="noopener noreferrer"
              className="w-10 h-10 rounded-full border border-sage-100/25 hover:border-sage-100 hover:bg-sage-100 hover:text-sage-800 flex items-center justify-center transition-all"
              data-testid="footer-facebook"
              aria-label="Facebook EcoAndes"
            >
              <Facebook size={16} />
            </a>
            <a
              href="https://www.instagram.com/ecoandesbio"
              target="_blank"
              rel="noopener noreferrer"
              className="w-10 h-10 rounded-full border border-sage-100/25 hover:border-sage-100 hover:bg-sage-100 hover:text-sage-800 flex items-center justify-center transition-all"
              data-testid="footer-instagram"
              aria-label="Instagram EcoAndes"
            >
              <Instagram size={16} />
            </a>
            <a
              href="https://www.linkedin.com/company/ecoandes-import-export-s-l-"
              target="_blank"
              rel="noopener noreferrer"
              className="w-10 h-10 rounded-full border border-sage-100/25 hover:border-sage-100 hover:bg-sage-100 hover:text-sage-800 flex items-center justify-center transition-all"
              data-testid="footer-linkedin"
              aria-label="LinkedIn EcoAndes"
            >
              <Linkedin size={16} />
            </a>
          </div>
        </div>

        <div>
          <div className="overline text-sage-200 mb-5">{t("footer.shop")}</div>
          <ul className="space-y-3 text-sm">
            <li><Link to="/tienda" className="hover:text-sage-200" data-testid="footer-link-shop">{t("footer.catalog")}</Link></li>
            <li><Link to="/profesional" className="hover:text-sage-200" data-testid="footer-link-pro">{t("footer.proAccount")}</Link></li>
            <li><Link to="/blog" className="hover:text-sage-200" data-testid="footer-link-blog">{t("footer.ourBlog")}</Link></li>
            <li><Link to="/certificaciones" className="hover:text-sage-200" data-testid="footer-link-cert">{t("footer.certifications")}</Link></li>
            <li><Link to="/sobre-nosotros" className="hover:text-sage-200" data-testid="footer-link-about">{t("footer.about")}</Link></li>
          </ul>
        </div>

        <div>
          <div className="overline text-sage-200 mb-5">{t("footer.customerArea")}</div>
          <ul className="space-y-3 text-sm">
            <li><Link to="/cuenta" className="hover:text-sage-200" data-testid="footer-link-account">{t("footer.myAccount")}</Link></li>
            <li><Link to="/cuenta" className="hover:text-sage-200" data-testid="footer-link-orders">{t("footer.myOrders")}</Link></li>
            <li><Link to="/lista-deseos" className="hover:text-sage-200" data-testid="footer-link-wishlist">{t("footer.wishlist")}</Link></li>
            <li><Link to="/atencion-cliente" className="hover:text-sage-200" data-testid="footer-link-returns">{t("footer.returns")}</Link></li>
            <li><Link to="/atencion-cliente" className="hover:text-sage-200" data-testid="footer-link-cs">{t("footer.customerService")}</Link></li>
            <li><Link to="/contacto" className="hover:text-sage-200" data-testid="footer-link-contact">{t("footer.contact")}</Link></li>
          </ul>
        </div>

        <div className="col-span-2 md:col-span-4 border-t border-sage-700/50 pt-10 grid grid-cols-1 md:grid-cols-2 gap-8" data-testid="footer-store">
          <div>
            <div className="flex items-center gap-2 overline text-sage-200 mb-4">
              <Store size={14} /> {t("store.name")}
            </div>
            <a
              href={STORE_MAPS_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-start gap-2 text-sm text-sage-100/90 hover:text-sage-200 transition-colors"
              data-testid="footer-store-address"
            >
              <MapPin size={15} className="mt-0.5 shrink-0" />
              <span>
                {STORE.market}<br />
                {STORE.addressLine1}<br />
                {STORE.addressLine2}<br />
                {STORE.addressLine3}
              </span>
            </a>
          </div>
          <div>
            <div className="flex items-center gap-2 overline text-sage-200 mb-4">
              <Clock size={14} /> {t("store.hoursTitle")}
            </div>
            <ul className="space-y-1.5 text-sm" data-testid="footer-store-hours">
              {STORE_HOURS.map((h) => (
                <li key={h.dayKey} className="flex items-center justify-between gap-4 max-w-sm">
                  <span className="text-sage-100/80">{t(`hours.days.${h.dayKey}`)}</span>
                  <span className={h.closed ? "text-sage-200/50" : "text-sage-100/95"}>{h.closed ? t("hours.closed") : h.value}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="col-span-2 md:col-span-4">
          <div className="overline text-sage-200 mb-5">{t("footer.legalInfo")}</div>
          <ul className="flex flex-wrap gap-x-6 gap-y-2 text-sm">
            <li><Link to="/legal/aviso-legal" className="hover:text-sage-200" data-testid="footer-link-aviso">{t("footer.legalNotice")}</Link></li>
            <li><Link to="/legal/politica-cookies" className="hover:text-sage-200" data-testid="footer-link-cookies">{t("footer.cookiePolicy")}</Link></li>
            <li><Link to="/legal/politica-privacidad" className="hover:text-sage-200" data-testid="footer-link-privacy">{t("footer.privacyPolicy")}</Link></li>
            <li><Link to="/legal/condiciones" className="hover:text-sage-200" data-testid="footer-link-terms">{t("footer.terms")}</Link></li>
          </ul>
        </div>
      </div>
      <div className="border-t border-sage-700/50 py-5 text-center text-[10px] sm:text-xs text-sage-200/70 tracking-[0.2em] uppercase px-4">
        © {new Date().getFullYear()} {t("footer.rights")}
      </div>
    </footer>
  );
}
