import { create } from "zustand";
import { AuthUser } from "@/features/auth/types";

interface AuthState {
  user: AuthUser | null;
  accessToken: string | null;
  refreshToken: string | null;
  setSession: (user: AuthUser, accessToken: string, refreshToken: string) => void;
  clearSession: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: JSON.parse(localStorage.getItem("auth_user") || "null"),
  accessToken: localStorage.getItem("auth_access_token"),
  refreshToken: localStorage.getItem("auth_refresh_token"),
  setSession: (user, accessToken, refreshToken) => {
    localStorage.setItem("auth_user", JSON.stringify(user));
    localStorage.setItem("auth_access_token", accessToken);
    localStorage.setItem("auth_refresh_token", refreshToken);
    set({ user, accessToken, refreshToken });
  },
  clearSession: () => {
    localStorage.removeItem("auth_user");
    localStorage.removeItem("auth_access_token");
    localStorage.removeItem("auth_refresh_token");
    set({ user: null, accessToken: null, refreshToken: null });
  }
}));