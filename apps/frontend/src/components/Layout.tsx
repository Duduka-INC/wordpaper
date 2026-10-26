import { Moon, Sun } from "lucide-react";
import { useEffect } from "react";
import { Link, Outlet, useLocation } from "react-router-dom";

import { useLocaleStore } from "../locale";
import { useThemeStore } from "../theme";

export function Logo() {
  const { theme, toggle } = useThemeStore();
  const { locale, toggle: toggleLocale } = useLocaleStore();
  return (
    <div className="logo-wrap">
      <Link className="logo" to="/" aria-label="Wordpaper, на главную">
        wordpaper<span>.</span>
      </Link>
      <button
        className="theme-toggle"
        type="button"
        onClick={toggle}
        aria-label="Переключить тему интерфейса"
      >
        {theme === "light" ? <Sun size={14} /> : <Moon size={14} />}
      </button>
      <button
        className="theme-toggle locale-toggle"
        type="button"
        onClick={toggleLocale}
        aria-label={locale === "ru" ? "Switch to English" : "Переключить на русский"}
        title={locale === "ru" ? "English" : "Русский"}
      >
        {locale === "ru" ? "EN" : "RU"}
      </button>
    </div>
  );
}

export function Layout() {
  const theme = useThemeStore((state) => state.theme);
  const locale = useLocaleStore((state) => state.locale);
  const location = useLocation();

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  useEffect(() => {
    document.documentElement.lang = locale;
  }, [locale]);

  const studio = location.pathname.startsWith("/studio");
  return (
    <div className="app-shell">
      <header className={`site-header ${studio ? "site-header--studio" : ""}`}>
        <Logo />
        <nav className="site-nav" aria-label={locale === "ru" ? "Основная навигация" : "Main navigation"}>
          <Link to="/#gallery">{locale === "ru" ? "Галерея" : "Gallery"}</Link>
          <Link className="header-cta" to="/studio">
            {locale === "ru" ? "Создать" : "Create"}
          </Link>
        </nav>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
}
