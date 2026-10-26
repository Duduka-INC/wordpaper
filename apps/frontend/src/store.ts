import { create } from "zustand";

import type { ContentSpec, GeneratedVariant, WallpaperSpec } from "./types";

interface StudioState {
  content: ContentSpec;
  theme: "light" | "dark" | "auto";
  recipeId: string | null;
  intensity: number;
  aspectRatio: { width: number; height: number };
  locks: string[];
  variants: GeneratedVariant[];
  selectedIndex: number;
  seed: number | null;
  setContent: (patch: Partial<ContentSpec>) => void;
  setTheme: (theme: "light" | "dark" | "auto") => void;
  setRecipe: (recipeId: string | null) => void;
  setIntensity: (intensity: number) => void;
  setAspectRatio: (aspectRatio: { width: number; height: number }) => void;
  toggleLock: (lock: string) => void;
  setVariants: (variants: GeneratedVariant[], seed: number) => void;
  selectVariant: (index: number) => void;
  patchSelectedSpec: (patch: Partial<WallpaperSpec>) => void;
  replaceSelectedVariant: (variant: GeneratedVariant) => void;
}

export const useStudioStore = create<StudioState>((set) => ({
  content: {
    word: "consistency",
    transcription: "[kənˈsɪstənsi]",
    part_of_speech: "noun",
    language: "English",
    definition:
      "the ability to repeat a process with the same quality, over and over again."
  },
  theme: "auto",
  recipeId: null,
  intensity: 48,
  aspectRatio: { width: 16, height: 9 },
  locks: [],
  variants: [],
  selectedIndex: 0,
  seed: null,
  setContent: (patch) =>
    set((state) => ({ content: { ...state.content, ...patch } })),
  setTheme: (theme) => set({ theme }),
  setRecipe: (recipeId) => set({ recipeId }),
  setIntensity: (intensity) => set({ intensity }),
  setAspectRatio: (aspectRatio) => set({ aspectRatio }),
  toggleLock: (lock) =>
    set((state) => ({
      locks: state.locks.includes(lock)
        ? state.locks.filter((item) => item !== lock)
        : [...state.locks, lock]
    })),
  setVariants: (variants, seed) => set({ variants, seed, selectedIndex: 0 }),
  selectVariant: (selectedIndex) => set({ selectedIndex }),
  patchSelectedSpec: (patch) =>
    set((state) => ({
      variants: state.variants.map((variant, index) =>
        index === state.selectedIndex
          ? { ...variant, spec: { ...variant.spec, ...patch } }
          : variant
      )
    })),
  replaceSelectedVariant: (variant) =>
    set((state) => ({
      variants: state.variants.map((item, index) =>
        index === state.selectedIndex ? variant : item
      )
    }))
}));
