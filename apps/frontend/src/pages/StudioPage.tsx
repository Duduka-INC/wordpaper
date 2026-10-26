import * as Slider from "@radix-ui/react-slider";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  Check,
  ChevronDown,
  Dice5,
  Download,
  Lock,
  RefreshCw,
  Sparkles,
  WandSparkles
} from "lucide-react";
import { useEffect, useRef } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import { api } from "../api";
import { AnchorGrid } from "../components/AnchorGrid";
import { StatusBlock } from "../components/StatusBlock";
import { useLocaleStore } from "../locale";
import { useStudioStore } from "../store";
import type { GeneratedVariant } from "../types";

const RATIOS = [
  [{ width: 16, height: 9 }, "16:9"],
  [{ width: 9, height: 16 }, "9:16"],
  [{ width: 4, height: 3 }, "4:3"]
] as const;

export function StudioPage() {
  const locale = useLocaleStore((state) => state.locale);
  const ru = locale === "ru";
  const themes = [
    ["auto", ru ? "Авто" : "Auto"],
    ["light", ru ? "Светлая" : "Light"],
    ["dark", ru ? "Тёмная" : "Dark"]
  ] as const;
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

  const lookup = useMutation({
    mutationFn: api.lookupWord,
    onSuccess: (entry) =>
      store.setContent({
        word: entry.word,
        transcription: entry.transcription,
        part_of_speech: entry.part_of_speech,
        language: entry.language,
        definition: entry.definition,
        source_name: entry.source_name,
        source_url: entry.source_url,
        source_license: entry.source_license
      })
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
            <p className="eyebrow">{ru ? "Параметры" : "Parameters"}</p>
            <h1>{ru ? "Студия" : "Studio"}</h1>
          </div>
          <span className="save-status"><Check size={12} /> {ru ? "локально" : "local"}</span>
        </div>

        <section className="control-section">
          <h2>{ru ? "Содержание" : "Content"}</h2>
          <label className="field">
            <span>{ru ? "Слово или фраза" : "Word or phrase"}</span>
            <div className="input-action">
              <input
                value={store.content.word}
                onChange={(event) => store.setContent({ word: event.target.value })}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && store.content.word.trim()) {
                    lookup.mutate(store.content.word);
                  }
                }}
              />
              <button
                type="button"
                onClick={() => lookup.mutate(store.content.word)}
                disabled={!store.content.word.trim() || lookup.isPending}
                aria-label={ru ? "Заполнить из словаря" : "Auto-fill from dictionary"}
                title={ru ? "Найти транскрипцию и определение" : "Find pronunciation and definition"}
              >
                {lookup.isPending ? <RefreshCw className="spin" size={15} /> : <WandSparkles size={15} />}
              </button>
            </div>
          </label>
          {lookup.isError && (
            <p className="field-message field-message--error">
              {lookup.error instanceof Error ? lookup.error.message : ru ? "Слово не найдено" : "Word not found"}
            </p>
          )}
          <div className="field-row">
            <label className="field">
              <span>{ru ? "Транскрипция" : "Pronunciation"}</span>
              <input
                value={store.content.transcription ?? ""}
                onChange={(event) =>
                  store.setContent({ transcription: event.target.value || null })
                }
              />
            </label>
            <label className="field field--short">
              <span>{ru ? "Часть речи" : "Part of speech"}</span>
              <input
                value={store.content.part_of_speech ?? ""}
                onChange={(event) =>
                  store.setContent({ part_of_speech: event.target.value || null })
                }
              />
            </label>
          </div>
          <label className="field">
            <span>{ru ? "Определение" : "Definition"}</span>
            <textarea
              value={store.content.definition}
              onChange={(event) =>
                store.setContent({ definition: event.target.value })
              }
              rows={4}
            />
          </label>
          {store.content.source_url && (
            <p className="lookup-source">
              {ru ? "Источник" : "Source"}: <a href={store.content.source_url} target="_blank" rel="noreferrer">{store.content.source_name ?? store.content.source_url}</a>
              {store.content.source_license && ` · ${store.content.source_license}`}
            </p>
          )}
        </section>

        <section className="control-section">
          <h2>{ru ? "Характер" : "Character"}</h2>
          <div className="segmented">
            {themes.map(([id, label]) => (
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
            <span>{ru ? "Рецепт" : "Recipe"}</span>
            <div className="select-wrap">
              <select
                value={store.recipeId ?? ""}
                onChange={(event) => store.setRecipe(event.target.value || null)}
              >
                <option value="">{ru ? "Подобрать автоматически" : "Choose automatically"}</option>
                {meta.data?.recipes.map((recipe) => (
                  <option key={recipe.id} value={recipe.id}>{recipe.label}</option>
                ))}
              </select>
              <ChevronDown size={14} />
            </div>
          </label>
          <div className="range-label">
            <span>{ru ? "Спокойно" : "Calm"}</span><span>{ru ? "Экспериментально" : "Experimental"}</span>
          </div>
          <Slider.Root
            className="slider-root"
            value={[store.intensity]}
            max={100}
            step={1}
            onValueChange={([value]) => store.setIntensity(value)}
          >
            <Slider.Track className="slider-track"><Slider.Range className="slider-range" /></Slider.Track>
            <Slider.Thumb className="slider-thumb" aria-label={ru ? "Степень экспериментальности" : "Experiment intensity"} />
          </Slider.Root>
        </section>

        <section className="control-section">
          <h2>{ru ? "Холст" : "Canvas"}</h2>
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
          <h2>{ru ? "Оформление" : "Appearance"}</h2>
          <label className="field">
            <span>{ru ? "Шрифт" : "Typeface"}</span>
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
            <span>{ru ? "Текстура фона" : "Background texture"}</span>
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
                <option value="">{ru ? "Без текстуры" : "No texture"}</option>
                {meta.data?.textures.map((texture) => (
                  <option key={texture.id} value={texture.id}>{texture.label}</option>
                ))}
              </select>
              <ChevronDown size={14} />
            </div>
          </label>
          <label className="field">
            <span>{ru ? "Эффект текста" : "Text effect"}</span>
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
                <option value="solid">{ru ? "Обычная заливка" : "Solid fill"}</option>
                <option value="liquid_glass">Liquid glass</option>
              </select>
              <ChevronDown size={14} />
            </div>
          </label>
          <label className="field">
            <span>{ru ? "Цвет текста / оттенок стекла" : "Text color / glass tint"}</span>
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
              <span>{ru ? "Интенсивность Liquid Glass" : "Liquid Glass intensity"}</span>
              <div className="range-label">
                <span>{ru ? "Мягко" : "Soft"}</span>
                <strong>
                  {Math.round((selected.spec.glass_intensity ?? 0.72) * 100)}%
                </strong>
                <span>{ru ? "Выразительно" : "Bold"}</span>
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
                  aria-label={ru ? "Интенсивность Liquid Glass" : "Liquid Glass intensity"}
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
            <button className="icon-button" type="button" onClick={regenerate} aria-label={ru ? "Перемешать" : "Shuffle"}>
              <RefreshCw size={16} />
            </button>
            <button
              className="button button--dark button--small"
              type="button"
              disabled={!selected || saveWall.isPending}
              onClick={() => saveWall.mutate()}
            >
              <Download size={15} /> {ru ? "Сохранить в галерею" : "Save to gallery"}
            </button>
          </div>
        </div>

        <div className="canvas-stage">
          {generation.isPending || sourceWall.isLoading ? (
            <StatusBlock />
          ) : selected ? (
            <div className="canvas-frame" style={{ aspectRatio: previewRatio }}>
              <img src={selected.preview_url} alt={ru ? "Предпросмотр обоев" : "Wallpaper preview"} />
              <span className="canvas-seed mono">SEED {selected.spec.seed}</span>
            </div>
          ) : (
            <div className="empty-state"><h3>{ru ? "Не удалось собрать варианты" : "Could not create variants"}</h3></div>
          )}
        </div>

        <div className="canvas-bottom-bar">
          <div>
            <span className="eyebrow">{ru ? "Позиция" : "Position"}</span>
            <AnchorGrid
              value={activeAnchor}
              onChange={(anchor) => {
                applySelectedPatch({ anchor }, "layout");
              }}
            />
          </div>
          <p>{ru ? "Позиция будет точно пересчитана при сохранении или следующей генерации." : "Position is recalculated precisely on save or the next generation."}</p>
        </div>
      </section>

      <aside className="studio-panel studio-panel--right">
        <div className="panel-title-row">
          <div><p className="eyebrow">{ru ? "Генератор" : "Generator"}</p><h2>{ru ? "Варианты" : "Variants"}</h2></div>
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
              <img src={variant.preview_url} alt={`${ru ? "Вариант" : "Variant"} ${index + 1}`} />
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
          <Sparkles size={16} /> {ru ? "Создать 4 варианта" : "Create 4 variants"}
        </button>

        <section className="locks-section">
          <div className="locks-heading"><Lock size={14} /><span>{ru ? "Зафиксировать" : "Lock"}</span></div>
          <div className="lock-chips">
            {["font", "background", "layout", "effect"].map((lock) => (
              <button
                key={lock}
                type="button"
                className={store.locks.includes(lock) ? "is-active" : ""}
                onClick={() => store.toggleLock(lock)}
              >
                {lock === "font" && (ru ? "Шрифт" : "Font")}
                {lock === "background" && (ru ? "Фон" : "Background")}
                {lock === "layout" && (ru ? "Позиция" : "Position")}
                {lock === "effect" && (ru ? "Эффект" : "Effect")}
              </button>
            ))}
          </div>
        </section>

        {selected && (
          <div className="variant-details">
            <div><span>{ru ? "Шрифт" : "Font"}</span><strong>{selected.spec.font_id.replaceAll("_", " ")}</strong></div>
            <div><span>{ru ? "Эффект" : "Effect"}</span><strong>{selected.spec.text_effect.replaceAll("_", " ")}</strong></div>
            <div><span>{ru ? "Тема" : "Theme"}</span><strong>{selected.spec.theme}</strong></div>
          </div>
        )}
      </aside>
    </div>
  );
}
