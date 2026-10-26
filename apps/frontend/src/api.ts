import type {
  GalleryResponse,
  GenerationResponse,
  Meta,
  Wall,
  WallpaperSpec,
  WordLookup
} from "./types";

type ApiOptions = Omit<RequestInit, "body"> & { body?: unknown };

async function apiFetch<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const response = await fetch(path, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...options.headers
    },
    body: options.body === undefined ? undefined : JSON.stringify(options.body)
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(payload?.detail ?? `API error ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  meta: () => apiFetch<Meta>("/api/v1/meta"),
  lookupWord: (word: string) =>
    apiFetch<WordLookup>(`/api/v1/words/${encodeURIComponent(word)}?language=auto`),
  gallery: (params: URLSearchParams) =>
    apiFetch<GalleryResponse>(`/api/v1/gallery?${params.toString()}`),
  generate: (body: unknown) =>
    apiFetch<GenerationResponse>("/api/v1/generations", {
      method: "POST",
      body
    }),
  preview: (spec: WallpaperSpec) =>
    apiFetch<GenerationResponse["variants"][number]>("/api/v1/previews", {
      method: "POST",
      body: spec
    }),
  createWall: (spec: WallpaperSpec, visibility = "public") =>
    apiFetch<Wall>("/api/v1/walls", {
      method: "POST",
      body: { spec, visibility }
    }),
  wall: (wallId: string) => apiFetch<Wall>(`/api/v1/walls/${wallId}`),
  render: (
    wallId: string,
    body: { resolution: string; format: string; quality: number }
  ) =>
    apiFetch<Wall>(`/api/v1/walls/${wallId}/renders`, {
      method: "POST",
      body
    }),
  fork: (wallId: string) =>
    apiFetch<Wall>(`/api/v1/walls/${wallId}/fork`, { method: "POST" }),
  publish: (wallId: string) =>
    apiFetch<Wall>(`/api/v1/walls/${wallId}/publish`, { method: "POST" })
};
