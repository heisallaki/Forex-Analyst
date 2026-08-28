import { useAuthStore } from "@/features/auth/store/authStore";

function keyFor(key: string): string {
  const userId = useAuthStore.getState().user?.id ?? "anonymous";
  return `pref:${userId}:${key}`;
}

export function getPreference<T>(key: string, fallback: T): T {
  const raw = localStorage.getItem(keyFor(key));
  if (raw === null) {
    return fallback;
  }
  try {
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

export function setPreference<T>(key: string, value: T): void {
  localStorage.setItem(keyFor(key), JSON.stringify(value));
}