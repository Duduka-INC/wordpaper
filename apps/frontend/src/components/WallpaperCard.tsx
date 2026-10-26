import { Link } from "react-router-dom";

import type { GalleryItem } from "../types";
import { useLocaleStore } from "../locale";

export function WallpaperCard({ item }: { item: GalleryItem }) {
  const locale = useLocaleStore((state) => state.locale);
  const ru = locale === "ru";
  const ratio = `${item.aspect_ratio.width} / ${item.aspect_ratio.height}`;
  return (
    <Link
      className="wall-card"
      to={`/w/${item.wall_id}`}
      aria-label={ru ? `Открыть обои ${item.wall_id}, ${item.word}` : `Open wallpaper ${item.wall_id}, ${item.word}`}
    >
      <div className="wall-card__image" style={{ aspectRatio: ratio }}>
        <img src={item.cover_url} alt="" loading="lazy" />
      </div>
      <div className="wall-card__meta">
        <span>{item.word || (ru ? "Без надписи" : "No text")}</span>
        <span className="mono">{item.wall_id}</span>
      </div>
    </Link>
  );
}
