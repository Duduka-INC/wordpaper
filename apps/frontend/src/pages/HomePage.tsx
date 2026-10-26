import { useQuery } from "@tanstack/react-query";
import { ArrowDown, ArrowUpRight, Search } from "lucide-react";
import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";

import { api } from "../api";
import { StatusBlock } from "../components/StatusBlock";
import { WallpaperCard } from "../components/WallpaperCard";

export function HomePage() {
  const [search, setSearch] = useState("");
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState("new");
  const [theme, setTheme] = useState("");
  const [hasText, setHasText] = useState("");

  const params = new URLSearchParams({ sort, limit: "24" });
  if (query) params.set("q", query);
  if (theme) params.set("theme", theme);
  if (hasText) params.set("has_text", hasText);

  const gallery = useQuery({
    queryKey: ["gallery", params.toString()],
    queryFn: () => api.gallery(params)
  });

  const items = gallery.data?.items ?? [];
  const heroItems = items.slice(0, 3);

  function submitSearch(event: FormEvent) {
    event.preventDefault();
    setQuery(search.trim());
    document.getElementById("gallery")?.scrollIntoView({ behavior: "smooth" });
  }

  return (
    <div className="home-page">
      <section className="hero-section">
        <div className="hero-copy">
          <p className="eyebrow">Типографическая лаборатория</p>
          <h1>
            Слова, которые
            <br />
            хочется <em>оставить.</em>
          </h1>
          <p className="hero-lead">
            Превращайте определения, мысли и короткие фразы в обои. Выберите
            направление — остальное соберёт управляемая случайность.
          </p>
          <div className="hero-actions">
            <Link className="button button--dark" to="/studio">
              Открыть студию <ArrowUpRight size={17} />
            </Link>
            <a className="text-link" href="#gallery">
              Смотреть галерею <ArrowDown size={15} />
            </a>
          </div>
        </div>

        <div className="hero-stack" aria-label="Примеры обоев">
          {heroItems.length ? (
            heroItems.map((item, index) => (
              <Link
                key={item.wall_id}
                className={`hero-poster hero-poster--${index + 1}`}
                to={`/w/${item.wall_id}`}
              >
                <img src={item.cover_url} alt={`Обои со словом ${item.word}`} />
              </Link>
            ))
          ) : (
            <div className="hero-placeholder">
              <span>wordpaper</span>
            </div>
          )}
        </div>
        <div className="hero-index mono">01 — GENERATED WITH INTENT</div>
      </section>

      <section className="gallery-section" id="gallery">
        <div className="gallery-heading">
          <div>
            <p className="eyebrow">Публичная коллекция</p>
            <h2>Новые стены</h2>
          </div>
          <p>
            Каждый объект хранит не только картинку, но и рецепт — его можно
            открыть, повторить и пересобрать под свой экран.
          </p>
        </div>

        <div className="gallery-tools">
          <form className="search-field" onSubmit={submitSearch}>
            <Search size={16} />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Найти по wall_id"
              aria-label="Поиск по wall id"
            />
          </form>
          <div className="tool-group">
            <select value={sort} onChange={(event) => setSort(event.target.value)}>
              <option value="new">Сначала новые</option>
              <option value="popular">Популярные</option>
            </select>
            <select value={theme} onChange={(event) => setTheme(event.target.value)}>
              <option value="">Любая тема</option>
              <option value="light">Светлые</option>
              <option value="dark">Тёмные</option>
            </select>
            <select
              value={hasText}
              onChange={(event) => setHasText(event.target.value)}
            >
              <option value="">Любой контент</option>
              <option value="true">С надписью</option>
              <option value="false">Без надписи</option>
            </select>
          </div>
        </div>

        {gallery.isLoading ? (
          <StatusBlock label="Открываем галерею" />
        ) : gallery.isError ? (
          <div className="empty-state">
            <h3>Галерея пока недоступна</h3>
            <p>Запустите FastAPI-бэкенд и обновите страницу.</p>
          </div>
        ) : items.length ? (
          <div className="gallery-grid">
            {items.map((item) => (
              <WallpaperCard key={item.wall_id} item={item} />
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <h3>Ничего не найдено</h3>
            <p>Попробуйте другой ID или снимите один из фильтров.</p>
          </div>
        )}
      </section>
    </div>
  );
}
