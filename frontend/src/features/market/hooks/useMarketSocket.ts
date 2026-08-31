import { useEffect, useRef, useState } from "react";
import { PriceTick } from "@/features/market/types";
import { useAuthStore } from "@/features/auth/store/authStore";
import { refreshAccessToken } from "@/shared/api/httpClient";

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL as string | undefined;
const AUTH_CLOSE_CODES = [4401, 4403];
const MAX_RECONNECT_DELAY_MS = 20000;

export type MarketSocketStatus = "connecting" | "open" | "closed" | "misconfigured";

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

    if (!WS_BASE_URL) {
      console.error(
        "VITE_WS_BASE_URL is not set. Add it to frontend/.env (e.g. ws://localhost:8000/api/v1) and fully restart `npm run dev` — Vite does not hot-reload env files."
      );
      setStatus("misconfigured");
      return;
    }

    let cancelled = false;

    const connect = (tokenOverride?: string) => {
      if (cancelled) {
        return;
      }
      const tokenToUse = tokenOverride ?? useAuthStore.getState().accessToken;
      if (!tokenToUse) {
        setStatus("closed");
        return;
      }

      setStatus("connecting");
      const socket = new WebSocket(`${WS_BASE_URL}/market/ws/prices?token=${tokenToUse}`);
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
        if (import.meta.env.DEV) {
          console.warn("Market WebSocket error event fired (a close event will follow with the real reason)");
        }
      };

      socket.onclose = (event) => {
        if (cancelled) {
          return;
        }
        if (import.meta.env.DEV) {
          console.warn(`Market WebSocket closed: code=${event.code} reason="${event.reason || "none"}"`);
        }
        setStatus("closed");

        const delay = Math.min(1000 * 2 ** reconnectAttempt.current, MAX_RECONNECT_DELAY_MS);
        reconnectAttempt.current += 1;
        const isAuthFailure = AUTH_CLOSE_CODES.includes(event.code);

        timeoutRef.current = setTimeout(async () => {
          if (isAuthFailure) {
            const freshToken = await refreshAccessToken();
            if (freshToken) {
              connect(freshToken);
            } else {
              setStatus("closed");
            }
          } else {
            connect();
          }
        }, delay);
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