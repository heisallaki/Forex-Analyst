import { useEffect, useState } from "react";
import {
  Box,
  TextField,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Typography,
  MenuItem,
  Chip,
  Tooltip
} from "@mui/material";
import Grid from "@mui/material/Grid2";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as ChartTooltip, ResponsiveContainer } from "recharts";
import { BacktestRunResponse, runBacktest } from "@/features/backtest/api/backtestApi";
import { getMarketStatus } from "@/features/market/api/marketApi";
import { STRATEGY_PRESETS } from "@/features/strategies/strategyPresets";
import { PageHeader } from "@/shared/ui/PageHeader";
import { useToast } from "@/shared/ui/useToast";

const SELECTABLE_PRESETS = STRATEGY_PRESETS.filter((preset) => preset.status !== "not_implemented");
const DISABLED_PRESETS = STRATEGY_PRESETS.filter((preset) => preset.status === "not_implemented");

export function BacktestPage() {
  const [instruments, setInstruments] = useState<string[]>([]);
  const [symbol, setSymbol] = useState("EUR/USD");
  const [presetKey, setPresetKey] = useState(SELECTABLE_PRESETS[0].key);
  const [rsiOversold, setRsiOversold] = useState(30);
  const [rsiOverbought, setRsiOverbought] = useState(70);
  const [result, setResult] = useState<BacktestRunResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const { showToast } = useToast();

  useEffect(() => {
    getMarketStatus()
      .then((status) => setInstruments(status.instruments))
      .catch(() => undefined);
  }, []);

  const activePreset = STRATEGY_PRESETS.find((preset) => preset.key === presetKey) ?? SELECTABLE_PRESETS[0];

  const handleRun = async () => {
    setLoading(true);
    setResult(null);
    try {
      const rules = activePreset.buildRuleGroups({ rsiOversold, rsiOverbought });
      const params = activePreset.buildParams();
      const response = await runBacktest({
        symbol,
        intervals: [activePreset.suggestedInterval],
        limit: 1000,
        strategy_name: activePreset.strategyName,
        strategy_description: activePreset.description,
        entry_long_rules: rules.long,
        entry_short_rules: rules.short,
        ...params
      });
      setResult(response);
      showToast("Backtest completed", "success");
    } catch (err) {
      showToast((err as Error).message, "error");
    } finally {
      setLoading(false);
    }
  };

  const equityCurve = (() => {
    if (!result || result.results.length === 0) {
      return [];
    }
    let equity = activePreset.buildParams().initial_balance;
    return result.results[0].trades.map((trade, index) => {
      equity += trade.pnl;
      return { trade: index + 1, equity };
    });
  })();

  return (
    <Box sx={{ p: { xs: 2, sm: 4 }, display: "flex", flexDirection: "column", gap: 3 }}>
      <PageHeader title="Backtesting" subtitle="Test genuinely implemented strategies against historical data" />
      <Card>
        <CardContent>
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField select fullWidth label="Symbol" value={symbol} onChange={(e) => setSymbol(e.target.value)}>
                {instruments.map((instrument) => (
                  <MenuItem key={instrument} value={instrument}>
                    {instrument}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid size={{ xs: 12, sm: 8 }}>
              <TextField select fullWidth label="Strategy" value={presetKey} onChange={(e) => setPresetKey(e.target.value)}>
                {SELECTABLE_PRESETS.map((preset) => (
                  <MenuItem key={preset.key} value={preset.key}>
                    {preset.displayName}
                    {preset.status === "partial" ? " (partial)" : ""}
                  </MenuItem>
                ))}
                {DISABLED_PRESETS.map((preset) => (
                  <MenuItem key={preset.key} value={preset.key} disabled>
                    {preset.displayName} — not yet implemented
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid size={{ xs: 12 }}>
              <Typography variant="body2" color="text.secondary">
                {activePreset.description}
              </Typography>
              {activePreset.limitationNote && (
                <Typography variant="caption" color="warning.main" sx={{ display: "block", mt: 0.5 }}>
                  Limitation: {activePreset.limitationNote}
                </Typography>
              )}
            </Grid>
            {activePreset.key === "range_mean_reversion" && (
              <>
                <Grid size={{ xs: 12, sm: 4 }}>
                  <TextField
                    fullWidth
                    type="number"
                    label="RSI oversold (long entry)"
                    value={rsiOversold}
                    onChange={(e) => setRsiOversold(Number(e.target.value))}
                  />
                </Grid>
                <Grid size={{ xs: 12, sm: 4 }}>
                  <TextField
                    fullWidth
                    type="number"
                    label="RSI overbought (short entry)"
                    value={rsiOverbought}
                    onChange={(e) => setRsiOverbought(Number(e.target.value))}
                  />
                </Grid>
              </>
            )}
            <Grid size={{ xs: 12, sm: 4 }} sx={{ display: "flex", alignItems: "center" }}>
              <Button variant="contained" onClick={handleRun} disabled={loading} fullWidth>
                {loading ? <CircularProgress size={22} color="inherit" /> : "Run backtest"}
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {result &&
        result.results.map((intervalResult) => (
          <Card key={intervalResult.interval}>
            <CardContent sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
              <Box sx={{ display: "flex", gap: 1, alignItems: "center", flexWrap: "wrap" }}>
                <Typography variant="h6">{intervalResult.interval} results</Typography>
                <Tooltip title="Strategy is now active on the Strategies page since it ran successfully against real data">
                  <Chip size="small" label="✅ activated" color="success" variant="outlined" />
                </Tooltip>
              </Box>
              <Grid container spacing={2}>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <Typography variant="body2" color="text.secondary">
                    Total trades
                  </Typography>
                  <Typography variant="h6">{intervalResult.statistics.total_trades}</Typography>
                </Grid>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <Typography variant="body2" color="text.secondary">
                    Win rate
                  </Typography>
                  <Typography variant="h6">
                    {intervalResult.statistics.win_rate !== null ? `${intervalResult.statistics.win_rate.toFixed(1)}%` : "—"}
                  </Typography>
                </Grid>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <Typography variant="body2" color="text.secondary">
                    Profit factor
                  </Typography>
                  <Typography variant="h6">
                    {intervalResult.statistics.profit_factor !== null
                      ? intervalResult.statistics.profit_factor.toFixed(2)
                      : "—"}
                  </Typography>
                </Grid>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <Typography variant="body2" color="text.secondary">
                    Max drawdown
                  </Typography>
                  <Typography variant="h6">{intervalResult.statistics.max_drawdown_pct.toFixed(1)}%</Typography>
                </Grid>
              </Grid>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={equityCurve}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="trade" />
                  <YAxis domain={["auto", "auto"]} />
                  <ChartTooltip />
                  <Line type="monotone" dataKey="equity" stroke="#2196f3" dot={false} />
                </LineChart>
              </ResponsiveContainer>
              <Box sx={{ overflowX: "auto" }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Side</TableCell>
                      <TableCell>Entry</TableCell>
                      <TableCell>Exit</TableCell>
                      <TableCell>PnL</TableCell>
                      <TableCell>R</TableCell>
                      <TableCell>Reason</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {intervalResult.trades.slice(0, 20).map((trade, index) => (
                      <TableRow key={index}>
                        <TableCell>{trade.side}</TableCell>
                        <TableCell>{trade.entry_price.toFixed(5)}</TableCell>
                        <TableCell>{trade.exit_price.toFixed(5)}</TableCell>
                        <TableCell>{trade.pnl.toFixed(2)}</TableCell>
                        <TableCell>{trade.r_multiple !== null ? trade.r_multiple.toFixed(2) : "—"}</TableCell>
                        <TableCell>{trade.exit_reason}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </Box>
              {intervalResult.trades.length === 0 && (
                <Typography color="text.secondary">
                  No trades were triggered in this window — the strategy still ran successfully and is now active.
                </Typography>
              )}
            </CardContent>
          </Card>
        ))}
    </Box>
  );
}