import { create } from "zustand";

type UiTheme = "light" | "dark";

interface ThemeState {
  theme: UiTheme;
  toggle: () => void;
}

const initialTheme =
  (localStorage.getItem("wordpaper-ui-theme") as UiTheme | null) ?? "light";

export const useThemeStore = create<ThemeState>((set) => ({
  theme: initialTheme,
  toggle: () =>
    set((state) => {
      const theme = state.theme === "light" ? "dark" : "light";
      localStorage.setItem("wordpaper-ui-theme", theme);
      return { theme };
    })
}));
