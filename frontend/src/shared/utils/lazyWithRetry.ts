import { ComponentType, lazy } from "react";

export function lazyWithRetry<T extends ComponentType<unknown>>(
  factory: () => Promise<{ default: T }>
): ReturnType<typeof lazy<T>> {
  return lazy(async () => {
    const storageKey = "chunk-load-retried";
    try {
      const module = await factory();
      window.sessionStorage.removeItem(storageKey);
      return module;
    } catch (error) {
      const alreadyRetried = window.sessionStorage.getItem(storageKey);
      if (!alreadyRetried) {
        window.sessionStorage.setItem(storageKey, "true");
        window.location.reload();
        return new Promise<{ default: T }>(() => {});
      }
      window.sessionStorage.removeItem(storageKey);
      throw error;
    }
  });
}