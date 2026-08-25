import { Card, CardContent, Typography, Stack, Chip } from "@mui/material";
import { PriceTick } from "@/features/market/types";

interface PriceTickerProps {
  instruments: string[];
  ticks: Record<string, PriceTick>;
}

export function PriceTicker({ instruments, ticks }: PriceTickerProps) {
  return (
    <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
      {instruments.map((symbol) => {
        const tick = ticks[symbol];
        return (
          <Card key={symbol} sx={{ minWidth: 160 }}>
            <CardContent>
              <Typography variant="subtitle2">{symbol}</Typography>
              <Typography variant="h6">{tick ? tick.price : "—"}</Typography>
              <Chip
                size="small"
                label={tick ? "live" : "waiting"}
                color={tick ? "success" : "default"}
              />
            </CardContent>
          </Card>
        );
      })}
    </Stack>
  );
}