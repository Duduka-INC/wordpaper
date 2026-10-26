import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Copy, Download, ExternalLink, GitFork, LoaderCircle } from "lucide-react";
import { useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { api } from "../api";
import { StatusBlock } from "../components/StatusBlock";

export function WallPage() {
  const { wallId = "" } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [resolution, setResolution] = useState("1080p");
  const [format, setFormat] = useState("webp");
  const [copied, setCopied] = useState(false);

  const wall = useQuery({
    queryKey: ["wall", wallId],
    queryFn: () => api.wall(wallId),
    enabled: Boolean(wallId)
  });
  const render = useMutation({
    mutationFn: () => api.render(wallId, { resolution, format, quality: 92 }),
    onSuccess: (data) => queryClient.setQueryData(["wall", wallId], data)
  });
  const fork = useMutation({
    mutationFn: () => api.fork(wallId),
    onSuccess: (data) => navigate(`/studio?wall_id=${data.wall_id}`)
  });

  const latestExport = useMemo(
    () => wall.data?.renders.find((item) => item.kind === "export" && item.status === "ready"),
    [wall.data]
  );

  if (wall.isLoading) return <div className="page-status"><StatusBlock label="Открываем обои" /></div>;
  if (wall.isError || !wall.data) {
    return <div className="page-status empty-state"><h2>Обои не найдены</h2><Link to="/">Вернуться в галерею</Link></div>;
  }

  const item = wall.data;
  const ratio = `${item.spec.aspect_ratio.width} / ${item.spec.aspect_ratio.height}`;
  const previewUrl = latestExport?.url ?? item.cover_url;

  async function copyId() {
    await navigator.clipboard.writeText(item.wall_id);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1400);
  }

  return (
    <div className="wall-page">
      <div className="wall-page__topline">
        <Link to="/" className="text-link"><ArrowLeft size={15} /> Галерея</Link>
        <span className="mono">{item.spec.recipe_id.replaceAll("_", " ")}</span>
      </div>

      <section className="wall-viewer">
        <div className="wall-viewer__image" style={{ aspectRatio: ratio }}>
          {previewUrl && <img src={previewUrl} alt={`Обои ${item.wall_id}`} />}
        </div>
        <div className="wall-viewer__index mono">{item.spec.seed}</div>
      </section>

      <aside className="export-panel">
        <p className="eyebrow">Готовые обои</p>
        <h1>{item.spec.content.word || "Без надписи"}</h1>
        <button className="wall-id" type="button" onClick={copyId}>
          <span className="mono">{item.wall_id}</span>
          {copied ? "Скопировано" : <Copy size={15} />}
        </button>

        <div className="export-controls">
          <label className="field">
            <span>Разрешение</span>
            <select value={resolution} onChange={(event) => setResolution(event.target.value)}>
              <option value="1080p">Full HD · 1080p</option>
              <option value="2k">QHD · 2K</option>
              <option value="4k">Ultra HD · 4K</option>
              <option value="8k">Ultra HD · 8K</option>
            </select>
          </label>
          <label className="field">
            <span>Формат</span>
            <select value={format} onChange={(event) => setFormat(event.target.value)}>
              <option value="webp">WebP</option>
              <option value="png">PNG</option>
              <option value="jpeg">JPEG</option>
            </select>
          </label>
        </div>

        <button
          className="button button--dark button--wide"
          type="button"
          onClick={() => render.mutate()}
          disabled={render.isPending}
        >
          {render.isPending ? <LoaderCircle className="spin" size={16} /> : <ExternalLink size={16} />}
          {render.isPending ? "Рендерим…" : "Создать рендер"}
        </button>

        {latestExport?.download_url && (
          <a className="button button--accent button--wide" href={latestExport.download_url}>
            <Download size={16} /> Скачать {latestExport.width}×{latestExport.height}
          </a>
        )}

        <button
          className="button button--ghost button--wide"
          type="button"
          onClick={() => fork.mutate()}
          disabled={fork.isPending}
        >
          <GitFork size={16} /> Создать свою версию
        </button>

        <dl className="render-facts">
          <div><dt>Рецепт</dt><dd>{item.spec.recipe_id.replaceAll("_", " ")}</dd></div>
          <div><dt>Шрифт</dt><dd>{item.spec.font_id.replaceAll("_", " ")}</dd></div>
          <div><dt>Экспортов</dt><dd>{item.export_count}</dd></div>
          <div><dt>Видимость</dt><dd>{item.visibility}</dd></div>
        </dl>
      </aside>
    </div>
  );
}
