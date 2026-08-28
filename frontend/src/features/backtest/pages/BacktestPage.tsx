import { useState } from "react";
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
  Typography
} from "@mui/material";
import Grid from "@mui/material/Grid2";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { BacktestRunResponse, runBacktest } from "@/features/backtest/api/backtestApi";
import { PageHeader } from "@/shared/ui/PageHeader";
import { useToast } from "@/shared/ui/ToastProvider";

export function BacktestPage() {
  const [symbol, setSymbol] = useState("EUR/USD");
  const [strategyName, setStrategyName] = useState("rsi_mean_reversion");
  const [rsiOversold, setRsiOversold] = useState(30);
  const [rsiOverbought, setRsiOverbought] = useState(70);
  const [riskPct, setRiskPct] = useState(1);
  const [result, setResult] = useState<BacktestRunResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const { showToast } = useToast();

  const handleRun = async () => {
    setLoading(true);
    setResult(null);
    try {
      const response = await runBacktest({
        symbol,
        intervals: ["1min"],
        limit: 1000,
        strategy_name: strategyName,
        strategy_description: `RSI mean reversion: long below ${rsiOversold}, short above ${rsiOverbought}`,
        entry_long_rules: { match: "all", conditions: [{ field: "rsi_14", operator: "lt", value: rsiOversold }] },
        entry_short_rules: { match: "all", conditions: [{ field: "rsi_14", operator: "gt", value: rsiOverbought }] },
        initial_balance: 10000,
        risk_per_trade_pct: riskPct,
        spread_pips: 1.0,
        slippage_pips: 0.5,
        stop_loss_atr_multiple: 1.5,
        take_profit_atr_multiple: 3.0,
        max_holding_bars: 200
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
    let equity = 10000;
    return result.results[0].trades.map((trade, index) => {
      equity += trade.pnl;
      return { trade: index + 1, equity };
    });
  })();

  return (
    <Box sx={{ p: { xs: 2, sm: 4 }, display: "flex", flexDirection: "column", gap: 3 }}>
      <PageHeader title="Backtesting" subtitle="Test rule-based strategies against historical data" />
      <Card>
        <CardContent>
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField fullWidth label="Symbol" value={symbol} onChange={(e) => setSymbol(e.target.value)} />
            </Grid>
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField fullWidth label="Strategy name" value={strategyName} onChange={(e) => setStrategyName(e.target.value)} />
            </Grid>
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField
                fullWidth
                type="number"
                label="Risk per trade (%)"
                value={riskPct}
                onChange={(e) => setRiskPct(Number(e.target.value))}
              />
            </Grid>
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
              <Typography variant="h6">{intervalResult.interval} results</Typography>
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
                  <Tooltip />
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
            </CardContent>
          </Card>
        ))}
    </Box>
  );
}