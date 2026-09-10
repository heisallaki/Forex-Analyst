import { useEffect, useRef, useState } from "react";
import { useAuthStore } from "@/features/auth/store/authStore";

export type MarketSocketStatus = "connecting" | "open" | "closed" | "misconfigured";

export type MarketTick = {
  symbol: string;
  price: string;
  timestamp: number;
};

export function useMarketSocket() {
  const [status, setStatus] = useState<MarketSocketStatus>("connecting");
  const [ticks, setTicks] = useState<Record<string, MarketTick>>({});
  const socketRef = useRef<WebSocket | null>(null);
  const accessToken = useAuthStore((state) => state.accessToken);

  useEffect(() => {
    if (!accessToken) {
      setStatus("closed");
      return;
    }

    const wsBaseUrl = import.meta.env.VITE_WS_BASE_URL ?? "ws://localhost:8000/api/v1";
    const socket = new WebSocket(`${wsBaseUrl}/market/ws/prices?token=${accessToken}`);
    socketRef.current = socket;
    setStatus("connecting");

    socket.onopen = () => setStatus("open");
    socket.onclose = () => setStatus("closed");
    socket.onerror = () => setStatus("closed");
    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data) as { event?: string; symbol?: string; price?: string };
        if (payload.event === "price" && payload.symbol && payload.price) {
          const { symbol, price } = payload;
          setTicks((current) => ({
            ...current,
            [symbol]: {
              symbol,
              price,
              timestamp: Date.now(),
            },
          }));
        }
      } catch {
        // Ignore malformed WebSocket messages.
      }
    };

    return () => {
      socketRef.current = null;
      if (socket.readyState === WebSocket.OPEN) {
        socket.close();
      } else {
        socket.onopen = () => socket.close();
      }
    };
  }, [accessToken]);

  return { status, ticks };
}