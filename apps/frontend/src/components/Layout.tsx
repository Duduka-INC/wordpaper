import { Moon, Sun } from "lucide-react";
import { useEffect } from "react";
import { Link, Outlet, useLocation } from "react-router-dom";

import { useThemeStore } from "../theme";

export function Logo() {
  const { theme, toggle } = useThemeStore();
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
    </div>
  );
}

export function Layout() {
  const theme = useThemeStore((state) => state.theme);
  const location = useLocation();

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  const studio = location.pathname.startsWith("/studio");
  return (
    <div className="app-shell">
      <header className={`site-header ${studio ? "site-header--studio" : ""}`}>
        <Logo />
        <nav className="site-nav" aria-label="Основная навигация">
          <Link to="/#gallery">Галерея</Link>
          <Link className="header-cta" to="/studio">
            Создать
          </Link>
        </nav>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
}
