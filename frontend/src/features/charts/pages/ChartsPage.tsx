import { useEffect, useState } from "react";
import { Box, TextField, MenuItem, Alert } from "@mui/material";
import { Time } from "lightweight-charts";
import { getCandles, getMarketStatus } from "@/features/market/api/marketApi";
import { CandlePoint, CandlestickChart } from "@/features/charts/components/CandlestickChart";
import { PageHeader } from "@/shared/ui/PageHeader";
import { PageLoadingSkeleton } from "@/shared/ui/PageLoadingSkeleton";

const INTERVALS = ["1min", "5min", "15min", "1h", "1day"];

export function ChartsPage() {
  const [instruments, setInstruments] = useState<string[]>([]);
  const [symbol, setSymbol] = useState("");
  const [interval, setInterval] = useState("1min");
  const [data, setData] = useState<CandlePoint[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getMarketStatus()
      .then((status) => {
        setInstruments(status.instruments);
        if (status.instruments.length > 0) {
          setSymbol(status.instruments[0]);
        }
      })
      .catch(() => setError("Could not load instruments"));
  }, []);

  useEffect(() => {
    if (!symbol) {
      return;
    }
    setLoading(true);
    setError(null);
    getCandles(symbol, interval, 300)
      .then((candles) => {
        setData(
          candles.map((candle) => ({
            time: Math.floor(new Date(candle.timestamp).getTime() / 1000) as Time,
            open: candle.open,
            high: candle.high,
            low: candle.low,
            close: candle.close
          }))
        );
      })
      .catch(() => setError("Could not load candles"))
      .finally(() => setLoading(false));
  }, [symbol, interval]);

  return (
    <Box sx={{ p: { xs: 2, sm: 4 }, display: "flex", flexDirection: "column", gap: 3 }}>
      <PageHeader title="Charts" subtitle="Historical candlestick data for any configured instrument" />
      <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
        <TextField select label="Symbol" value={symbol} onChange={(e) => setSymbol(e.target.value)} sx={{ minWidth: 160 }}>
          {instruments.map((instrument) => (
            <MenuItem key={instrument} value={instrument}>
              {instrument}
            </MenuItem>
          ))}
        </TextField>
        <TextField select label="Interval" value={interval} onChange={(e) => setInterval(e.target.value)} sx={{ minWidth: 140 }}>
          {INTERVALS.map((value) => (
            <MenuItem key={value} value={value}>
              {value}
            </MenuItem>
          ))}
        </TextField>
      </Box>
      {error && <Alert severity="error">{error}</Alert>}
      {loading ? <PageLoadingSkeleton variant="table" /> : <CandlestickChart data={data} />}
    </Box>
  );
}