import { useAuthStore } from "@/features/auth/store/authStore";
import { refreshToken as refreshTokenRequest } from "@/features/auth/api/authApi";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL as string;

let refreshPromise: Promise<string | null> | null = null;

async function ensureFreshToken(): Promise<string | null> {
  const state = useAuthStore.getState();
  if (!state.refreshToken) {
    return null;
  }
  if (!refreshPromise) {
    refreshPromise = refreshTokenRequest(state.refreshToken)
      .then((response) => {
        useAuthStore.getState().setSession(response.user, response.access_token, response.refresh_token);
        return response.access_token;
      })
      .catch(() => {
        useAuthStore.getState().clearSession();
        return null;
      })
      .finally(() => {
        refreshPromise = null;
      });
  }
  return refreshPromise;
}

function authHeaders(): HeadersInit {
  const accessToken = useAuthStore.getState().accessToken;
  return accessToken ? { Authorization: `Bearer ${accessToken}` } : {};
}

async function request<T>(path: string, init: RequestInit): Promise<T> {
  let response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: { ...init.headers, ...authHeaders() }
  });

  if (response.status === 401) {
    const newAccessToken = await ensureFreshToken();
    if (newAccessToken) {
      response = await fetch(`${API_BASE_URL}${path}`, {
        ...init,
        headers: { ...init.headers, Authorization: `Bearer ${newAccessToken}` }
      });
    } else {
      window.location.href = "/login";
      throw new Error("Session expired. Please log in again.");
    }
  }

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export async function httpGet<T>(path: string): Promise<T> {
  return request<T>(path, { method: "GET" });
}

export async function httpPost<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
}