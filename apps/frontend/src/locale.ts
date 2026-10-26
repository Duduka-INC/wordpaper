import { create } from "zustand";

export type UiLocale = "ru" | "en";

interface LocaleState {
  locale: UiLocale;
  toggle: () => void;
}

const initialLocale =
  (localStorage.getItem("wordpaper-ui-locale") as UiLocale | null) ?? "ru";

export const useLocaleStore = create<LocaleState>((set) => ({
  locale: initialLocale,
  toggle: () =>
    set((state) => {
      const locale = state.locale === "ru" ? "en" : "ru";
      localStorage.setItem("wordpaper-ui-locale", locale);
      return { locale };
    })
}));
