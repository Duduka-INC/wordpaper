import { useQuery } from "@tanstack/react-query";
import { ArrowDown, ArrowUpRight, Search } from "lucide-react";
import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";

import { api } from "../api";
import { StatusBlock } from "../components/StatusBlock";
import { WallpaperCard } from "../components/WallpaperCard";
import { useLocaleStore } from "../locale";

export function HomePage() {
  const locale = useLocaleStore((state) => state.locale);
  const ru = locale === "ru";
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
          <p className="eyebrow">{ru ? "Типографическая лаборатория" : "Typographic laboratory"}</p>
          <h1>
            {ru ? "Слова, которые" : "Words worth"}
            <br />
            {ru ? <>хочется <em>оставить.</em></> : <em>keeping.</em>}
          </h1>
          <p className="hero-lead">
            {ru
              ? "Превращайте определения, мысли и короткие фразы в обои. Выберите направление — остальное соберёт управляемая случайность."
              : "Turn definitions, thoughts and short phrases into wallpapers. Choose a direction and let controlled randomness compose the rest."}
          </p>
          <div className="hero-actions">
            <Link className="button button--dark" to="/studio">
              {ru ? "Открыть студию" : "Open studio"} <ArrowUpRight size={17} />
            </Link>
            <a className="text-link" href="#gallery">
              {ru ? "Смотреть галерею" : "View gallery"} <ArrowDown size={15} />
            </a>
          </div>
        </div>

        <div className="hero-stack" aria-label={ru ? "Примеры обоев" : "Wallpaper examples"}>
          {heroItems.length ? (
            heroItems.map((item, index) => (
              <Link
                key={item.wall_id}
                className={`hero-poster hero-poster--${index + 1}`}
                to={`/w/${item.wall_id}`}
              >
                <img src={item.cover_url} alt={ru ? `Обои со словом ${item.word}` : `Wallpaper featuring ${item.word}`} />
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
            <p className="eyebrow">{ru ? "Публичная коллекция" : "Public collection"}</p>
            <h2>{ru ? "Новые стены" : "Fresh walls"}</h2>
          </div>
          <p>
            {ru
              ? "Каждый объект хранит не только картинку, но и рецепт — его можно открыть, повторить и пересобрать под свой экран."
              : "Every piece keeps both the image and its recipe, ready to open, remix and rebuild for your screen."}
          </p>
        </div>

        <div className="gallery-tools">
          <form className="search-field" onSubmit={submitSearch}>
            <Search size={16} />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder={ru ? "Найти по wall_id" : "Find by wall_id"}
              aria-label={ru ? "Поиск по wall id" : "Search by wall id"}
            />
          </form>
          <div className="tool-group">
            <select value={sort} onChange={(event) => setSort(event.target.value)}>
              <option value="new">{ru ? "Сначала новые" : "Newest first"}</option>
              <option value="popular">{ru ? "Популярные" : "Popular"}</option>
            </select>
            <select value={theme} onChange={(event) => setTheme(event.target.value)}>
              <option value="">{ru ? "Любая тема" : "Any theme"}</option>
              <option value="light">{ru ? "Светлые" : "Light"}</option>
              <option value="dark">{ru ? "Тёмные" : "Dark"}</option>
            </select>
            <select
              value={hasText}
              onChange={(event) => setHasText(event.target.value)}
            >
              <option value="">{ru ? "Любой контент" : "Any content"}</option>
              <option value="true">{ru ? "С надписью" : "With text"}</option>
              <option value="false">{ru ? "Без надписи" : "Without text"}</option>
            </select>
          </div>
        </div>

        {gallery.isLoading ? (
          <StatusBlock label={ru ? "Открываем галерею" : "Opening gallery"} />
        ) : gallery.isError ? (
          <div className="empty-state">
            <h3>{ru ? "Галерея пока недоступна" : "Gallery is unavailable"}</h3>
            <p>{ru ? "Запустите FastAPI-бэкенд и обновите страницу." : "Start the API and refresh the page."}</p>
          </div>
        ) : items.length ? (
          <div className="gallery-grid">
            {items.map((item) => (
              <WallpaperCard key={item.wall_id} item={item} />
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <h3>{ru ? "Ничего не найдено" : "Nothing found"}</h3>
            <p>{ru ? "Попробуйте другой ID или снимите один из фильтров." : "Try another ID or clear one of the filters."}</p>
          </div>
        )}
      </section>
    </div>
  );
}
