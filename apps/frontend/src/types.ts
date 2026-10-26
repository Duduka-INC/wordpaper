export type Theme = "light" | "dark";

export interface ContentSpec {
  word: string;
  transcription: string | null;
  part_of_speech: string | null;
  language: string | null;
  definition: string;
}

export interface AspectRatioSpec {
  width: number;
  height: number;
}

export interface WallpaperSpec {
  schema_version: number;
  seed: number;
  recipe_id: string;
  theme: Theme;
  content: ContentSpec;
  aspect_ratio: AspectRatioSpec;
  anchor: string;
  font_id: string;
  font_size_ratio: number;
  text_color: string;
  text_effect: "solid" | "liquid_glass";
  glass_intensity: number;
  background_color: string;
  background_asset_id: string | null;
  underline: boolean;
}

export interface GeneratedVariant {
  variant_id: string;
  spec: WallpaperSpec;
  preview_url: string;
}

export interface GenerationResponse {
  seed: number;
  variants: GeneratedVariant[];
}

export interface RenderResult {
  id: string;
  kind: string;
  width: number;
  height: number;
  format: string;
  status: string;
  url: string | null;
  download_url: string | null;
  byte_size: number | null;
  created_at: string;
}

export interface Wall {
  wall_id: string;
  visibility: string;
  revision: number;
  is_owner: boolean;
  spec: WallpaperSpec;
  cover_url: string | null;
  export_count: number;
  created_at: string;
  updated_at: string;
  renders: RenderResult[];
}

export interface GalleryItem {
  wall_id: string;
  theme: Theme;
  word: string;
  recipe_id: string;
  cover_url: string;
  aspect_ratio: AspectRatioSpec;
  export_count: number;
}

export interface GalleryResponse {
  items: GalleryItem[];
  next_cursor: string | null;
}

export interface MetaOption {
  id: string;
  label: string;
}

export interface Meta {
  fonts: MetaOption[];
  textures: MetaOption[];
  recipes: MetaOption[];
  anchors: MetaOption[];
  resolutions: MetaOption[];
}
