import { httpGet, httpPost } from "@/shared/api/httpClient";

export interface AppUser {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

async function httpPatch<T>(path: string, body: unknown): Promise<T> {
  return httpPost<T>(path, body, "PATCH");
}

export async function listUsers(): Promise<AppUser[]> {
  return httpGet<AppUser[]>("/users");
}

export async function updateUserRole(userId: string, role: string): Promise<AppUser> {
  return httpPatch<AppUser>(`/users/${userId}/role`, { role });
}

export async function updateUserStatus(userId: string, isActive: boolean): Promise<AppUser> {
  return httpPatch<AppUser>(`/users/${userId}/status`, { is_active: isActive });
}