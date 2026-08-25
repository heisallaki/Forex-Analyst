import { MarketStatus } from "@/features/market/types";
import { useAuthStore } from "@/features/auth/store/authStore";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL as string;

export async function getMarketStatus(): Promise<MarketStatus> {
  const accessToken = useAuthStore.getState().accessToken;
  const response = await fetch(`${API_BASE_URL}/market/status`, {
    headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : undefined
  });
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }
  return response.json() as Promise<MarketStatus>;
}