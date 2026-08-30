import { LoginPayload, RegisterPayload, TokenResponse } from "@/features/auth/types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL as string;

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function login(payload: LoginPayload): Promise<TokenResponse> {
  return postJson<TokenResponse>("/auth/login", payload);
}

export function register(payload: RegisterPayload): Promise<TokenResponse> {
  return postJson<TokenResponse>("/auth/register", payload);
}

export function refreshToken(refresh_token: string): Promise<TokenResponse> {
  return postJson<TokenResponse>("/auth/refresh", { refresh_token });
}

export function logout(refresh_token: string): Promise<void> {
  return fetch(`${API_BASE_URL}/auth/logout`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token })
  }).then(() => undefined);
}

export interface MessageResponse {
  message: string;
}

export function forgotPassword(email: string): Promise<MessageResponse> {
  return postJson<MessageResponse>("/auth/forgot-password", { email });
}

export function resetPassword(email: string, code: string, newPassword: string): Promise<MessageResponse> {
  return postJson<MessageResponse>("/auth/reset-password", { email, code, new_password: newPassword });
}