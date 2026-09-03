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
  const connectingRef = useRef(false);

  useEffect(() => {
    if (!accessToken) {
      return;
    }

    if (!WS_BASE_URL) {
      console.error(
        "VITE_WS_BASE_URL is not set. Add it to frontend/.env (e.g. wss://your-backend-host/api/v1) and fully restart/rebuild — Vite does not hot-reload env files."
      );
      setStatus("misconfigured");
      return;
    }

    let cancelled = false;

    const closeSocketSafely = (socket: WebSocket | null) => {
      if (!socket) {
        return;
      }
      if (socket.readyState === WebSocket.CONNECTING) {
        socket.onopen = () => socket.close();
      } else if (socket.readyState === WebSocket.OPEN) {
        socket.close();
      }
    };

    const connect = (tokenOverride?: string) => {
      if (cancelled || connectingRef.current) {
        return;
      }
      const tokenToUse = tokenOverride ?? useAuthStore.getState().accessToken;
      if (!tokenToUse) {
        setStatus("closed");
        return;
      }

      connectingRef.current = true;
      setStatus("connecting");
      const socket = new WebSocket(`${WS_BASE_URL}/market/ws/prices?token=${tokenToUse}`);
      socketRef.current = socket;

      socket.onopen = () => {
        connectingRef.current = false;
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
        connectingRef.current = false;
        if (cancelled || socketRef.current !== socket) {
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
          if (cancelled) {
            return;
          }
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
      connectingRef.current = false;
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      closeSocketSafely(socketRef.current);
    };
  }, [accessToken]);

  return { ticks, status };
}