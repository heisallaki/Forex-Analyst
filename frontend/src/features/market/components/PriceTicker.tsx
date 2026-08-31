import { Card, CardContent, Typography, Stack, Chip } from "@mui/material";
import { PriceTick } from "@/features/market/types";
import { MarketSocketStatus } from "@/features/market/hooks/useMarketSocket";

interface PriceTickerProps {
  instruments: string[];
  ticks: Record<string, PriceTick>;
  status: MarketSocketStatus;
}

function badgeFor(hasTick: boolean, status: MarketSocketStatus): { label: string; color: "success" | "warning" | "default" | "error" } {
  if (hasTick) {
    return { label: "live", color: "success" };
  }
  if (status === "misconfigured") {
    return { label: "config error", color: "error" };
  }
  if (status === "connecting") {
    return { label: "connecting", color: "default" };
  }
  if (status === "closed") {
    return { label: "reconnecting", color: "warning" };
  }
  return { label: "no data yet", color: "warning" };
}

export function PriceTicker({ instruments, ticks, status }: PriceTickerProps) {
  return (
    <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
      {instruments.map((symbol) => {
        const tick = ticks[symbol];
        const badge = badgeFor(!!tick, status);
        return (
          <Card key={symbol} sx={{ minWidth: 160 }}>
            <CardContent>
              <Typography variant="subtitle2">{symbol}</Typography>
              <Typography variant="h6">{tick ? tick.price : "—"}</Typography>
              <Chip size="small" label={badge.label} color={badge.color} />
            </CardContent>
          </Card>
        );
      })}
    </Stack>
  );
}