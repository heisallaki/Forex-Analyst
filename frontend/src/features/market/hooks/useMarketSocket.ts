import { useEffect, useRef, useState } from "react";
import { PriceTick } from "@/features/market/types";
import { useAuthStore } from "@/features/auth/store/authStore";

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL as string;

export function useMarketSocket() {
  const [ticks, setTicks] = useState<Record<string, PriceTick>>({});
  const socketRef = useRef<WebSocket | null>(null);
  const accessToken = useAuthStore((state) => state.accessToken);

  useEffect(() => {
    if (!accessToken) {
      return;
    }
    const socket = new WebSocket(`${WS_BASE_URL}/market/ws/prices?token=${accessToken}`);
    socketRef.current = socket;

    socket.onmessage = (event) => {
      try {
        const tick: PriceTick = JSON.parse(event.data);
        if (tick.symbol) {
          setTicks((previous) => ({ ...previous, [tick.symbol]: tick }));
        }
      } catch {
        return;
      }
    };

    return () => {
      socket.close();
    };
  }, [accessToken]);

  return ticks;
}