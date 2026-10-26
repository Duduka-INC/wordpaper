import * as Slider from "@radix-ui/react-slider";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  Check,
  ChevronDown,
  Dice5,
  Download,
  Lock,
  RefreshCw,
  Sparkles
} from "lucide-react";
import { useEffect, useRef } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import { api } from "../api";
import { AnchorGrid } from "../components/AnchorGrid";
import { StatusBlock } from "../components/StatusBlock";
import { useStudioStore } from "../store";
import type { GeneratedVariant } from "../types";

const THEMES = [
  ["auto", "Авто"],
  ["light", "Светлая"],
  ["dark", "Тёмная"]
] as const;

const RATIOS = [
  [{ width: 16, height: 9 }, "16:9"],
  [{ width: 9, height: 16 }, "9:16"],
  [{ width: 4, height: 3 }, "4:3"]
] as const;

export function StudioPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const sourceWallId = searchParams.get("wall_id");
  const initialized = useRef(false);
  const store = useStudioStore();
  const selected = store.variants[store.selectedIndex];

  const meta = useQuery({ queryKey: ["meta"], queryFn: api.meta });
  const sourceWall = useQuery({
    queryKey: ["wall", sourceWallId],
    queryFn: () => api.wall(sourceWallId!),
    enabled: Boolean(sourceWallId)
  });

  const generation = useMutation({
    mutationFn: () =>
      api.generate({
        content: store.content,
        theme: store.theme,
        recipe_id: store.recipeId,
        aspect_ratio: store.aspectRatio,
        count: 4,
        intensity: store.intensity,
        seed: null,
        locks: store.locks,
        base_spec: selected?.spec ?? null
      }),
    onSuccess: (data) => store.setVariants(data.variants, data.seed)
  });

  const preview = useMutation({
    mutationFn: api.preview,
    onSuccess: (variant) => store.replaceSelectedVariant(variant)
  });

  const saveWall = useMutation({
    mutationFn: () => api.createWall(selected.spec, "public"),
    onSuccess: (wall) => navigate(`/w/${wall.wall_id}`)
  });

  useEffect(() => {
    if (initialized.current) return;
    if (sourceWall.data?.cover_url) {
      const variant: GeneratedVariant = {
        variant_id: sourceWall.data.wall_id,
        spec: sourceWall.data.spec,
        preview_url: sourceWall.data.cover_url
      };
      store.setVariants([variant], sourceWall.data.spec.seed);
      initialized.current = true;
    } else if (!sourceWallId) {
      initialized.current = true;
      generation.mutate();
    }
  }, [sourceWall.data, sourceWallId]);

  function regenerate() {
    generation.mutate();
  }

  function applySelectedPatch(
    patch: Partial<GeneratedVariant["spec"]>,
    lock?: string
  ) {
    if (!selected) return;
    const nextSpec = { ...selected.spec, ...patch };
    store.patchSelectedSpec(patch);
    if (lock && !store.locks.includes(lock)) store.toggleLock(lock);
    preview.mutate(nextSpec);
  }

  const activeAnchor = selected?.spec.anchor ?? "bottom_left";
  const previewRatio = selected
    ? `${selected.spec.aspect_ratio.width} / ${selected.spec.aspect_ratio.height}`
    : "16 / 9";

  return (
    <div className="studio-page">
      <aside className="studio-panel studio-panel--left">
        <div className="panel-title-row">
          <div>
            <p className="eyebrow">Параметры</p>
            <h1>Студия</h1>
          </div>
          <span className="save-status"><Check size={12} /> локально</span>
        </div>

        <section className="control-section">
          <h2>Содержание</h2>
          <label className="field">
            <span>Слово или фраза</span>
            <input
              value={store.content.word}
              onChange={(event) => store.setContent({ word: event.target.value })}
            />
          </label>
          <div className="field-row">
            <label className="field">
              <span>Транскрипция</span>
              <input
                value={store.content.transcription ?? ""}
                onChange={(event) =>
                  store.setContent({ transcription: event.target.value || null })
                }
              />
            </label>
            <label className="field field--short">
              <span>Часть речи</span>
              <input
                value={store.content.part_of_speech ?? ""}
                onChange={(event) =>
                  store.setContent({ part_of_speech: event.target.value || null })
                }
              />
            </label>
          </div>
          <label className="field">
            <span>Определение</span>
            <textarea
              value={store.content.definition}
              onChange={(event) =>
                store.setContent({ definition: event.target.value })
              }
              rows={4}
            />
          </label>
        </section>

        <section className="control-section">
          <h2>Характер</h2>
          <div className="segmented">
            {THEMES.map(([id, label]) => (
              <button
                key={id}
                type="button"
                className={store.theme === id ? "is-active" : ""}
                onClick={() => store.setTheme(id)}
              >
                {label}
              </button>
            ))}
          </div>
          <label className="field">
            <span>Рецепт</span>
            <div className="select-wrap">
              <select
                value={store.recipeId ?? ""}
                onChange={(event) => store.setRecipe(event.target.value || null)}
              >
                <option value="">Подобрать автоматически</option>
                {meta.data?.recipes.map((recipe) => (
                  <option key={recipe.id} value={recipe.id}>{recipe.label}</option>
                ))}
              </select>
              <ChevronDown size={14} />
            </div>
          </label>
          <div className="range-label">
            <span>Спокойно</span><span>Экспериментально</span>
          </div>
          <Slider.Root
            className="slider-root"
            value={[store.intensity]}
            max={100}
            step={1}
            onValueChange={([value]) => store.setIntensity(value)}
          >
            <Slider.Track className="slider-track"><Slider.Range className="slider-range" /></Slider.Track>
            <Slider.Thumb className="slider-thumb" aria-label="Степень экспериментальности" />
          </Slider.Root>
        </section>

        <section className="control-section">
          <h2>Холст</h2>
          <div className="ratio-options">
            {RATIOS.map(([ratio, label]) => (
              <button
                key={label}
                type="button"
                className={
                  store.aspectRatio.width === ratio.width &&
                  store.aspectRatio.height === ratio.height
                    ? "is-active"
                    : ""
                }
                onClick={() => store.setAspectRatio({ ...ratio })}
              >
                <i style={{ aspectRatio: `${ratio.width}/${ratio.height}` }} />
                {label}
              </button>
            ))}
          </div>
        </section>

        <section className="control-section">
          <h2>Оформление</h2>
          <label className="field">
            <span>Шрифт</span>
            <div className="select-wrap">
              <select
                value={selected?.spec.font_id ?? ""}
                disabled={!selected || preview.isPending}
                onChange={(event) =>
                  applySelectedPatch({ font_id: event.target.value }, "font")
                }
              >
                {meta.data?.fonts.map((font) => (
                  <option key={font.id} value={font.id}>{font.label}</option>
                ))}
              </select>
              <ChevronDown size={14} />
            </div>
          </label>
          <label className="field">
            <span>Текстура фона</span>
            <div className="select-wrap">
              <select
                value={selected?.spec.background_asset_id ?? ""}
                disabled={!selected || preview.isPending}
                onChange={(event) =>
                  applySelectedPatch(
                    { background_asset_id: event.target.value || null },
                    "background"
                  )
                }
              >
                <option value="">Без текстуры</option>
                {meta.data?.textures.map((texture) => (
                  <option key={texture.id} value={texture.id}>{texture.label}</option>
                ))}
              </select>
              <ChevronDown size={14} />
            </div>
          </label>
          <label className="field">
            <span>Эффект текста</span>
            <div className="select-wrap">
              <select
                value={selected?.spec.text_effect ?? "solid"}
                disabled={!selected || preview.isPending}
                onChange={(event) =>
                  applySelectedPatch(
                    { text_effect: event.target.value as "solid" | "liquid_glass" },
                    "effect"
                  )
                }
              >
                <option value="solid">Обычная заливка</option>
                <option value="liquid_glass">Liquid glass</option>
              </select>
              <ChevronDown size={14} />
            </div>
          </label>
          <label className="field">
            <span>Цвет текста / оттенок стекла</span>
            <div className="color-field">
              <input
                type="color"
                value={selected?.spec.text_color ?? "#111111"}
                disabled={!selected || preview.isPending}
                onChange={(event) =>
                  applySelectedPatch({ text_color: event.target.value }, "font")
                }
              />
              <code>{selected?.spec.text_color ?? "#111111"}</code>
            </div>
          </label>
          {selected?.spec.text_effect === "liquid_glass" && (
            <div className="field">
              <span>Интенсивность Liquid Glass</span>
              <div className="range-label">
                <span>Мягко</span>
                <strong>
                  {Math.round((selected.spec.glass_intensity ?? 0.72) * 100)}%
                </strong>
                <span>Выразительно</span>
              </div>
              <Slider.Root
                className="slider-root"
                value={[
                  Math.round((selected.spec.glass_intensity ?? 0.72) * 100)
                ]}
                max={100}
                step={1}
                onValueChange={([value]) =>
                  store.patchSelectedSpec({ glass_intensity: value / 100 })
                }
                onValueCommit={([value]) =>
                  applySelectedPatch(
                    { glass_intensity: value / 100 },
                    "effect"
                  )
                }
              >
                <Slider.Track className="slider-track">
                  <Slider.Range className="slider-range" />
                </Slider.Track>
                <Slider.Thumb
                  className="slider-thumb"
                  aria-label="Интенсивность Liquid Glass"
                />
              </Slider.Root>
            </div>
          )}
        </section>
      </aside>

      <section className="studio-canvas-area">
        <div className="studio-toolbar">
          <span className="mono">{selected?.spec.recipe_id ?? "new composition"}</span>
          <div>
            <button className="icon-button" type="button" onClick={regenerate} aria-label="Перемешать">
              <RefreshCw size={16} />
            </button>
            <button
              className="button button--dark button--small"
              type="button"
              disabled={!selected || saveWall.isPending}
              onClick={() => saveWall.mutate()}
            >
              <Download size={15} /> Сохранить в галерею
            </button>
          </div>
        </div>

        <div className="canvas-stage">
          {generation.isPending || sourceWall.isLoading ? (
            <StatusBlock />
          ) : selected ? (
            <div className="canvas-frame" style={{ aspectRatio: previewRatio }}>
              <img src={selected.preview_url} alt="Предпросмотр обоев" />
              <span className="canvas-seed mono">SEED {selected.spec.seed}</span>
            </div>
          ) : (
            <div className="empty-state"><h3>Не удалось собрать варианты</h3></div>
          )}
        </div>

        <div className="canvas-bottom-bar">
          <div>
            <span className="eyebrow">Позиция</span>
            <AnchorGrid
              value={activeAnchor}
              onChange={(anchor) => {
                applySelectedPatch({ anchor }, "layout");
              }}
            />
          </div>
          <p>Позиция будет точно пересчитана при сохранении или следующей генерации.</p>
        </div>
      </section>

      <aside className="studio-panel studio-panel--right">
        <div className="panel-title-row">
          <div><p className="eyebrow">Генератор</p><h2>Варианты</h2></div>
          <Dice5 size={19} />
        </div>

        <div className="variant-grid">
          {store.variants.map((variant, index) => (
            <button
              key={variant.variant_id}
              type="button"
              className={index === store.selectedIndex ? "is-active" : ""}
              onClick={() => store.selectVariant(index)}
            >
              <img src={variant.preview_url} alt={`Вариант ${index + 1}`} />
              <span>{String(index + 1).padStart(2, "0")}</span>
            </button>
          ))}
        </div>

        <button
          className="button button--accent button--wide"
          type="button"
          onClick={regenerate}
          disabled={generation.isPending}
        >
          <Sparkles size={16} /> Создать 4 варианта
        </button>

        <section className="locks-section">
          <div className="locks-heading"><Lock size={14} /><span>Зафиксировать</span></div>
          <div className="lock-chips">
            {["font", "background", "layout", "effect"].map((lock) => (
              <button
                key={lock}
                type="button"
                className={store.locks.includes(lock) ? "is-active" : ""}
                onClick={() => store.toggleLock(lock)}
              >
                {lock === "font" && "Шрифт"}
                {lock === "background" && "Фон"}
                {lock === "layout" && "Позиция"}
                {lock === "effect" && "Эффект"}
              </button>
            ))}
          </div>
        </section>

        {selected && (
          <div className="variant-details">
            <div><span>Шрифт</span><strong>{selected.spec.font_id.replaceAll("_", " ")}</strong></div>
            <div><span>Эффект</span><strong>{selected.spec.text_effect.replaceAll("_", " ")}</strong></div>
            <div><span>Тема</span><strong>{selected.spec.theme}</strong></div>
          </div>
        )}
      </aside>
    </div>
  );
}
