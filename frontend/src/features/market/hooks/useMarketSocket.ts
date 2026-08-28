import { useEffect, useRef, useState } from "react";
import { PriceTick } from "@/features/market/types";
import { useAuthStore } from "@/features/auth/store/authStore";

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL as string;

export type MarketSocketStatus = "connecting" | "open" | "closed" | "error";

export function useMarketSocket() {
  const [ticks, setTicks] = useState<Record<string, PriceTick>>({});
  const [status, setStatus] = useState<MarketSocketStatus>("connecting");
  const accessToken = useAuthStore((state) => state.accessToken);
  const reconnectAttempt = useRef(0);
  const socketRef = useRef<WebSocket | null>(null);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!accessToken) {
      return;
    }

    let cancelled = false;

    const connect = () => {
      setStatus("connecting");
      const socket = new WebSocket(`${WS_BASE_URL}/market/ws/prices?token=${accessToken}`);
      socketRef.current = socket;

      socket.onopen = () => {
        reconnectAttempt.current = 0;
        setStatus("open");
      };

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

      socket.onerror = () => {
        setStatus("error");
      };

      socket.onclose = () => {
        if (cancelled) {
          return;
        }
        setStatus("closed");
        const delay = Math.min(1000 * 2 ** reconnectAttempt.current, 15000);
        reconnectAttempt.current += 1;
        timeoutRef.current = setTimeout(connect, delay);
      };
    };

    connect();

    return () => {
      cancelled = true;
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      socketRef.current?.close();
    };
  }, [accessToken]);

  return { ticks, status };
}