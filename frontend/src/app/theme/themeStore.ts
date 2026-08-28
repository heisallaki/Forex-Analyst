import { create } from "zustand";
import { AccentColorKey } from "@/app/theme";

export type ThemeModePreference = "light" | "dark" | "system";

interface ThemeState {
  modePreference: ThemeModePreference;
  systemPrefersDark: boolean;
  accentColor: AccentColorKey;
  effectiveMode: () => "light" | "dark";
  setModePreference: (mode: ThemeModePreference) => void;
  toggleMode: () => void;
  setAccentColor: (color: AccentColorKey) => void;
}

function getStoredModePreference(): ThemeModePreference {
  const stored = localStorage.getItem("theme_mode_preference");
  if (stored === "light" || stored === "dark" || stored === "system") {
    return stored;
  }
  return "system";
}

function getStoredAccentColor(): AccentColorKey {
  const stored = localStorage.getItem("theme_accent_color");
  const valid: AccentColorKey[] = ["blue", "purple", "green", "orange", "yellow", "red", "pink", "cyan"];
  if (stored && valid.includes(stored as AccentColorKey)) {
    return stored as AccentColorKey;
  }
  return "blue";
}

function getSystemPrefersDark(): boolean {
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

export const useThemeStore = create<ThemeState>((set, get) => ({
  modePreference: getStoredModePreference(),
  systemPrefersDark: getSystemPrefersDark(),
  accentColor: getStoredAccentColor(),
  effectiveMode: () => {
    const { modePreference, systemPrefersDark } = get();
    if (modePreference === "system") {
      return systemPrefersDark ? "dark" : "light";
    }
    return modePreference;
  },
  setModePreference: (mode) => {
    localStorage.setItem("theme_mode_preference", mode);
    set({ modePreference: mode });
  },
  toggleMode: () => {
    const current = get().effectiveMode();
    const next = current === "dark" ? "light" : "dark";
    localStorage.setItem("theme_mode_preference", next);
    set({ modePreference: next });
  },
  setAccentColor: (color) => {
    localStorage.setItem("theme_accent_color", color);
    set({ accentColor: color });
  }
}));

if (typeof window !== "undefined") {
  const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
  mediaQuery.addEventListener("change", (event) => {
    useThemeStore.setState({ systemPrefersDark: event.matches });
  });
}