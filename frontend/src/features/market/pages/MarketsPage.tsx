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
  const ticks = useMarketSocket();

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

  return (
    <Box sx={{ p: { xs: 2, sm: 4 }, display: "flex", flexDirection: "column", gap: 3 }}>
      <PageHeader title="Markets" subtitle="Live prices across your configured instruments" />
      <SessionBadge activeSessions={status.active_sessions} />
      <PriceTicker instruments={status.instruments} ticks={ticks} />
    </Box>
  );
}