import { useEffect, useState } from "react";
import { Box, Typography, CircularProgress } from "@mui/material";
import { getMarketStatus } from "@/features/market/api/marketApi";
import { useMarketSocket } from "@/features/market/hooks/useMarketSocket";
import { PriceTicker } from "@/features/market/components/PriceTicker";
import { SessionBadge } from "@/features/market/components/SessionBadge";
import { MarketStatus } from "@/features/market/types";

export function MarketsPage() {
  const [status, setStatus] = useState<MarketStatus | null>(null);
  const ticks = useMarketSocket();

  useEffect(() => {
    getMarketStatus()
      .then(setStatus)
      .catch(() => setStatus(null));
  }, []);

  if (!status) {
    return (
      <Box sx={{ p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 4, display: "flex", flexDirection: "column", gap: 3 }}>
      <Typography variant="h4">Markets</Typography>
      <SessionBadge activeSessions={status.active_sessions} />
      <PriceTicker instruments={status.instruments} ticks={ticks} />
    </Box>
  );
}