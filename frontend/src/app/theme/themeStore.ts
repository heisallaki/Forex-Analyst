import { create } from "zustand";

type ThemeMode = "light" | "dark";

interface ThemeState {
  mode: ThemeMode;
  toggleMode: () => void;
}

function getInitialMode(): ThemeMode {
  const stored = localStorage.getItem("theme_mode");
  if (stored === "light" || stored === "dark") {
    return stored;
  }
  return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
}

export const useThemeStore = create<ThemeState>((set, get) => ({
  mode: getInitialMode(),
  toggleMode: () => {
    const next = get().mode === "dark" ? "light" : "dark";
    localStorage.setItem("theme_mode", next);
    set({ mode: next });
  }
}));