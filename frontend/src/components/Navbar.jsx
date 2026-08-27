import React, { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { ShoppingBag, User, Menu, X, LogOut, LayoutDashboard, Search, Heart, Scale } from "lucide-react";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
import { useWishlist } from "../context/WishlistContext";
import SearchBar from "./SearchBar";
import LanguageSwitcher from "./LanguageSwitcher";

export default function Navbar() {
  const { t } = useTranslation();
  const { count, openDrawer } = useCart();
  const { user, logout } = useAuth();
  const { wishlistCount, compareCount } = useWishlist();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [mobileSearchOpen, setMobileSearchOpen] = useState(false);
  const nav = useNavigate();

  const linkCls = ({ isActive }) =>
    `text-xs uppercase tracking-[0.22em] font-medium transition-colors whitespace-nowrap ${
      isActive ? "text-sage-600" : "text-ink hover:text-sage-600"
    }`;

  return (
    <header
      data-testid="eco-navbar"
      className="sticky top-0 z-40 bg-bone-100/95 backdrop-blur-md border-b border-bone-200"
    >
      {/* Top row */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-12 py-3 sm:py-4 flex items-center justify-between gap-3 sm:gap-6">
        <button
          className="lg:hidden text-ink shrink-0"
          onClick={() => setMobileOpen(true)}
          data-testid="nav-mobile-toggle"
          aria-label={t("nav.openMenu")}
        >
          <Menu size={22} />
        </button>

        <Link to="/" data-testid="nav-brand" className="flex items-center shrink-0">
          <img src="/logo-ecoandes.png" alt="EcoAndes · Organic Ingredients" className="h-14 sm:h-16 md:h-[72px] w-auto object-contain" />
        </Link>

        {/* Desktop search bar - persistent */}
        <div className="hidden lg:block flex-1 max-w-xl mx-4">
          <SearchBar />
        </div>

        <div className="flex items-center gap-2 sm:gap-4 lg:gap-6 shrink-0">
          {/* Mobile search toggle */}
          <button
            className="lg:hidden text-ink hover:text-sage-600 p-1"
            onClick={() => setMobileSearchOpen((v) => !v)}
            data-testid="nav-mobile-search-toggle"
            aria-label={t("nav.search")}
          >
            <Search size={20} />
          </button>

          {user?.role === "admin" && (
            <button
              onClick={() => nav("/admin")}
              data-testid="nav-admin-btn"
              className="hidden md:inline-flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-sage-600 hover:text-sage-700"
            >
              <LayoutDashboard size={16} /> {t("nav.admin")}
            </button>
          )}
          {user ? (
            <div className="relative group hidden md:block">
              <Link
                to="/cuenta"
                className="flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-ink hover:text-sage-600"
                data-testid="nav-user-btn"
              >
                <User size={16} /> {user.first_name}
              </Link>
              <div className="absolute right-0 top-full mt-2 w-48 bg-white border border-bone-200 shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 rounded-xl overflow-hidden">
                <Link to="/cuenta" className="block px-4 py-3 text-sm text-ink hover:bg-sage-50 transition-colors" data-testid="nav-account-link">
                  {t("nav.account")}
                </Link>
                {user.role === "admin" && (
                  <Link to="/admin" className="block px-4 py-3 text-sm text-ink hover:bg-sage-50 transition-colors" data-testid="nav-admin-link">
                    {t("nav.adminDashboard")}
                  </Link>
                )}
                <button
                  onClick={() => { logout(); nav("/"); }}
                  className="w-full text-left px-4 py-3 text-sm text-ink hover:bg-sage-50 transition-colors flex items-center gap-2"
                  data-testid="nav-logout-btn"
                >
                  <LogOut size={14} /> {t("nav.logout")}
                </button>
              </div>
            </div>
          ) : (
            <Link
              to="/login"
              data-testid="nav-login-link"
              className="hidden md:flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-ink hover:text-sage-600"
            >
              <User size={16} /> {t("nav.login")}
            </Link>
          )}
          <LanguageSwitcher />
          <Link
            to="/comparar"
            data-testid="nav-compare-btn"
            className="relative hidden sm:flex items-center text-ink hover:text-sage-600 transition-colors"
            aria-label={t("nav.compare")}
          >
            <Scale size={20} />
            {compareCount > 0 && (
              <span data-testid="compare-count" className="absolute -top-2 -right-2 bg-sage-500 text-white text-[10px] h-4 min-w-[16px] px-1 rounded-full flex items-center justify-center font-medium">{compareCount}</span>
            )}
          </Link>
          <Link
            to="/lista-deseos"
            data-testid="nav-wishlist-btn"
            className="relative hidden md:flex items-center text-ink hover:text-sage-600 transition-colors"
            aria-label={t("nav.wishlist")}
          >
            <Heart size={20} />
            {wishlistCount > 0 && (
              <span data-testid="wishlist-count" className="absolute -top-2 -right-2 bg-terracotta text-white text-[10px] h-4 min-w-[16px] px-1 rounded-full flex items-center justify-center font-medium">{wishlistCount}</span>
            )}
          </Link>
          {/* Móvil: icono de cuenta (persona). Verde con punto cuando hay sesión iniciada. */}
          <Link
            to={user ? "/cuenta" : "/login"}
            data-testid="nav-mobile-account"
            className={`relative flex md:hidden items-center transition-colors ${user ? "text-sage-600" : "text-ink hover:text-sage-600"}`}
            aria-label={user ? t("nav.account") : t("nav.login")}
          >
            <User size={20} />
            {user && (
              <span
                data-testid="nav-mobile-account-dot"
                className="absolute -top-1 -right-1 h-2.5 w-2.5 rounded-full bg-sage-500 border-2 border-bone-100"
              />
            )}
          </Link>
          <button
            onClick={openDrawer}
            data-testid="nav-cart-btn"
            className="relative flex items-center gap-2 text-ink hover:text-sage-600 transition-colors"
            aria-label={t("nav.openCart")}
          >
            <ShoppingBag size={20} />
            {count > 0 && (
              <span
                data-testid="cart-count"
                className="absolute -top-2 -right-2 bg-sage-500 text-white text-[10px] h-4 min-w-[16px] px-1 rounded-full flex items-center justify-center font-medium"
              >
                {count}
              </span>
            )}
          </button>
        </div>
      </div>

      {/* Mobile search bar (toggle) */}
      {mobileSearchOpen && (
        <div className="lg:hidden border-t border-bone-200 px-4 sm:px-6 py-3 bg-bone-100" data-testid="nav-mobile-search">
          <SearchBar compact onNavigate={() => setMobileSearchOpen(false)} />
        </div>
      )}

      {/* Bottom row: navigation links (desktop) */}
      <div className="hidden lg:block border-t border-bone-200/70 bg-bone-100">
        <nav className="max-w-7xl mx-auto px-6 lg:px-12 py-3 flex items-center justify-center gap-10">
          <NavLink to="/" className={linkCls} data-testid="nav-link-home" end>{t("nav.home")}</NavLink>
          <NavLink to="/tienda" className={linkCls} data-testid="nav-link-shop">{t("nav.shop")}</NavLink>
          <NavLink to="/blog" className={linkCls} data-testid="nav-link-blog">{t("nav.blog")}</NavLink>
          <NavLink to="/profesional" className={linkCls} data-testid="nav-link-pro">{t("nav.pro")}</NavLink>
          <NavLink to="/contacto" className={linkCls} data-testid="nav-link-contact">{t("nav.contact")}</NavLink>
        </nav>
      </div>

      {/* Mobile drawer menu */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 bg-bone-100" data-testid="mobile-menu">
          <div className="flex items-center justify-between px-5 py-4 border-b border-bone-200 bg-bone-100">
            <img src="/logo-ecoandes.png" alt="EcoAndes" className="h-9 w-auto object-contain" />
            <button onClick={() => setMobileOpen(false)} data-testid="mobile-close" aria-label={t("nav.close")} className="text-ink p-1">
              <X size={22} />
            </button>
          </div>
          <div className="px-5 py-5 bg-bone-100 border-b border-bone-200">
            <SearchBar compact onNavigate={() => setMobileOpen(false)} />
          </div>
          <nav className="flex flex-col bg-white">
            {[
              ["/", t("nav.home")],
              ["/tienda", t("nav.shop")],
              ["/blog", t("nav.blog")],
              ["/profesional", t("nav.pro")],
              ["/contacto", t("nav.contact")],
              ["/lista-deseos", t("nav.wishlist")],
              ["/comparar", t("nav.compare")],
              [user ? "/cuenta" : "/login", user ? t("nav.account") : t("nav.login")],
            ].map(([to, label]) => (
              <Link
                key={to}
                to={to}
                onClick={() => setMobileOpen(false)}
                data-testid={`mobile-link-${to.replace(/\//g, "") || "home"}`}
                className="text-base text-ink uppercase tracking-[0.2em] font-medium px-5 py-4 border-b border-bone-200 hover:bg-sage-50 transition-colors"
              >
                {label}
              </Link>
            ))}
            {user?.role === "admin" && (
              <Link
                to="/admin"
                onClick={() => setMobileOpen(false)}
                data-testid="mobile-link-admin"
                className="text-base text-sage-700 uppercase tracking-[0.2em] font-medium px-5 py-4 border-b border-bone-200 hover:bg-sage-50 transition-colors bg-sage-50/50"
              >
                {t("nav.adminDashboard")}
              </Link>
            )}
            {user && (
              <button
                onClick={() => { logout(); setMobileOpen(false); nav("/"); }}
                data-testid="mobile-logout"
                className="text-base text-ink uppercase tracking-[0.2em] font-medium px-5 py-4 text-left flex items-center gap-2 hover:bg-sage-50 transition-colors"
              >
                <LogOut size={16} /> {t("nav.logout")}
              </button>
            )}
          </nav>
        </div>
      )}
    </header>
  );
}
