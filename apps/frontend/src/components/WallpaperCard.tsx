import { Link } from "react-router-dom";

import type { GalleryItem } from "../types";

export function WallpaperCard({ item }: { item: GalleryItem }) {
  const ratio = `${item.aspect_ratio.width} / ${item.aspect_ratio.height}`;
  return (
    <Link
      className="wall-card"
      to={`/w/${item.wall_id}`}
      aria-label={`Открыть обои ${item.wall_id}, ${item.word}`}
    >
      <div className="wall-card__image" style={{ aspectRatio: ratio }}>
        <img src={item.cover_url} alt="" loading="lazy" />
      </div>
      <div className="wall-card__meta">
        <span>{item.word || "Без надписи"}</span>
        <span className="mono">{item.wall_id}</span>
      </div>
    </Link>
  );
}
