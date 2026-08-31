import { useEffect, useState } from "react";
import { Box, Alert } from "@mui/material";
import { getMarketStatus } from "@/features/market/api/marketApi";
import { useMarketSocket } from "@/features/market/hooks/useMarketSocket";
import { PriceTicker } from "@/features/market/components/PriceTicker";
import { SessionBadge } from "@/features/market/components/SessionBadge";
import { MarketStatus } from "@/features/market/types";
import { PageHeader } from "@/shared/ui/PageHeader";
import { PageLoadingSkeleton } from "@/shared/ui/PageLoadingSkeleton";

export function MarketsPage() {
  const [status, setStatus] = useState<MarketStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { ticks, status: socketStatus } = useMarketSocket();

  useEffect(() => {
    getMarketStatus()
      .then(setStatus)
      .catch((err) => setError((err as Error).message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <PageLoadingSkeleton />;
  }

  if (error || !status) {
    return (
      <Box sx={{ p: { xs: 2, sm: 4 } }}>
        <Alert severity="error">{error || "Could not load market status."}</Alert>
      </Box>
    );
  }

  const hasAnyLiveTick = Object.keys(ticks).length > 0;

  return (
    <Box sx={{ p: { xs: 2, sm: 4 }, display: "flex", flexDirection: "column", gap: 3 }}>
      <PageHeader title="Markets" subtitle="Live prices across your configured instruments" />
      <SessionBadge activeSessions={status.active_sessions} />
      {socketStatus === "misconfigured" && (
        <Alert severity="error">
          Live price streaming is misconfigured — <code>VITE_WS_BASE_URL</code> is not set in{" "}
          <code>frontend/.env</code>. Add it and fully restart <code>npm run dev</code> (Vite doesn't hot-reload env
          files). See the browser console for details.
        </Alert>
      )}
      {socketStatus !== "misconfigured" && !hasAnyLiveTick && socketStatus === "open" && (
        <Alert severity="info">
          Connected, but no live ticks yet. Forex markets are closed on weekends, and free-tier data plans can limit
          how many symbols stream simultaneously. Historical candles and charts are unaffected.
        </Alert>
      )}
      <PriceTicker instruments={status.instruments} ticks={ticks} status={socketStatus} />
    </Box>
  );
}