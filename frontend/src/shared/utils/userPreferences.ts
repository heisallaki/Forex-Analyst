import { useAuthStore } from "@/features/auth/store/authStore";

const STORAGE_KEY = "fx-analyst-user-preferences";

const getUserId = () => useAuthStore.getState().user?.id ?? "guest";

const getAllPreferences = (): Record<string, Record<string, string>> => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as Record<string, Record<string, string>>) : {};
  } catch {
    return {};
  }
};

export const getPreference = <T extends string>(key: string, fallback: T): T => {
  const prefs = getAllPreferences()[getUserId()] ?? {};
  const value = prefs[key];
  return (value ?? fallback) as T;
};

export const setPreference = <T extends string>(key: string, value: T): void => {
  const allPrefs = getAllPreferences();
  const userPrefs = allPrefs[getUserId()] ?? {};
  userPrefs[key] = value;
  allPrefs[getUserId()] = userPrefs;

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(allPrefs));
  } catch {
    // noop
  }
};