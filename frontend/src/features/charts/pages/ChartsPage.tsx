import { useEffect, useState } from "react";
import { Box, TextField, MenuItem, Alert, Chip } from "@mui/material";
import { Time } from "lightweight-charts";
import { getCandles, getMarketStatus } from "@/features/market/api/marketApi";
import { CandlePoint, CandlestickChart } from "@/features/charts/components/CandlestickChart";
import { PageHeader } from "@/shared/ui/PageHeader";
import { PageLoadingSkeleton } from "@/shared/ui/PageLoadingSkeleton";
import { getPreference, setPreference } from "@/shared/utils/userPreferences";
import { useMarketSocket } from "@/features/market/hooks/useMarketSocket";

const INTERVALS = ["1min", "5min", "15min", "30min", "45min", "1h", "1day"];
const REFRESH_INTERVAL_MS = 30000;

export function ChartsPage() {
  const [instruments, setInstruments] = useState<string[]>([]);
  const [symbol, setSymbol] = useState(() => getPreference("charts_symbol", ""));
  const [interval, setInterval] = useState(() => getPreference("charts_interval", "1min"));
  const [data, setData] = useState<CandlePoint[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { ticks, status: socketStatus } = useMarketSocket();

  useEffect(() => {
    getMarketStatus()
      .then((status) => {
        setInstruments(status.instruments);
        if (!symbol && status.instruments.length > 0) {
          setSymbol(status.instruments[0]);
        }
      })
      .catch(() => setError("Could not load instruments"));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchCandles = () => {
    if (!symbol) {
      return;
    }
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
      .catch(() => setError("Could not load candles"));
  };

  useEffect(() => {
    if (!symbol) {
      return;
    }
    setLoading(true);
    setError(null);
    fetchCandles();
    setLoading(false);

    const intervalId = window.setInterval(fetchCandles, REFRESH_INTERVAL_MS);
    return () => window.clearInterval(intervalId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [symbol, interval]);

  const liveTick = symbol ? ticks[symbol] : undefined;
  const lastBar = data.length > 0 ? data[data.length - 1] : null;
  const liveBar: CandlePoint | null =
    liveTick && lastBar
      ? {
          time: lastBar.time,
          open: lastBar.open,
          high: Math.max(lastBar.high, Number(liveTick.price)),
          low: Math.min(lastBar.low, Number(liveTick.price)),
          close: Number(liveTick.price)
        }
      : null;

  const handleSymbolChange = (value: string) => {
    setSymbol(value);
    setPreference("charts_symbol", value);
  };

  const handleIntervalChange = (value: string) => {
    setInterval(value);
    setPreference("charts_interval", value);
  };

  return (
    <Box sx={{ p: { xs: 2, sm: 4 }, display: "flex", flexDirection: "column", gap: 3 }}>
      <PageHeader title="Charts" subtitle="Historical candles, with the current bar updated live" />
      <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap", alignItems: "center" }}>
        <TextField select label="Symbol" value={symbol} onChange={(e) => handleSymbolChange(e.target.value)} sx={{ minWidth: 160 }}>
          {instruments.map((instrument) => (
            <MenuItem key={instrument} value={instrument}>
              {instrument}
            </MenuItem>
          ))}
        </TextField>
        <TextField select label="Interval" value={interval} onChange={(e) => handleIntervalChange(e.target.value)} sx={{ minWidth: 140 }}>
          {INTERVALS.map((value) => (
            <MenuItem key={value} value={value}>
              {value}
            </MenuItem>
          ))}
        </TextField>
        <Chip
          size="small"
          label={liveTick ? "live" : socketStatus === "open" ? "connected, no ticks yet" : socketStatus}
          color={liveTick ? "success" : "default"}
        />
      </Box>
      {error && <Alert severity="error">{error}</Alert>}
      {loading ? <PageLoadingSkeleton variant="table" /> : <CandlestickChart data={data} liveBar={liveBar} />}
    </Box>
  );
}