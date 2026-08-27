import { useCallback, useEffect, useState } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  MenuItem,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Chip,
  Alert,
  CircularProgress
} from "@mui/material";
import Grid from "@mui/material/Grid2";
import {
  Portfolio,
  PortfolioPerformance,
  Trade,
  closeTrade,
  createPortfolio,
  getPortfolioPerformance,
  listPortfolios,
  listTrades,
  openTrade
} from "@/features/paper/api/paperApi";

export function PaperTradingPage() {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [selectedPortfolioId, setSelectedPortfolioId] = useState<string>("");
  const [performance, setPerformance] = useState<PortfolioPerformance | null>(null);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [newPortfolioName, setNewPortfolioName] = useState("Main Portfolio");
  const [newPortfolioBalance, setNewPortfolioBalance] = useState(10000);
  const [tradeSymbol, setTradeSymbol] = useState("EUR/USD");
  const [tradeSide, setTradeSide] = useState<"long" | "short">("long");
  const [riskAmount, setRiskAmount] = useState(100);
  const [stopLoss, setStopLoss] = useState<number | "">("");
  const [takeProfit, setTakeProfit] = useState<number | "">("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const loadPortfolios = useCallback(async () => {
    const result = await listPortfolios();
    setPortfolios(result);

    if (result.length > 0 && !selectedPortfolioId) {
    setSelectedPortfolioId(result[0].id);
    }
}, [selectedPortfolioId]);

useEffect(() => {
  loadPortfolios()
    .catch((err) => setError((err as Error).message))
    .finally(() => setLoading(false));
}, [loadPortfolios]);

  const loadPortfolioDetail = async (portfolioId: string) => {
    const [performanceResult, tradesResult] = await Promise.all([
      getPortfolioPerformance(portfolioId),
      listTrades(portfolioId)
    ]);
    setPerformance(performanceResult);
    setTrades(tradesResult);
  };

  useEffect(() => {
    if (selectedPortfolioId) {
      loadPortfolioDetail(selectedPortfolioId).catch((err) => setError((err as Error).message));
    }
  }, [selectedPortfolioId]);

  const handleCreatePortfolio = async () => {
    setError(null);
    try {
      const created = await createPortfolio(newPortfolioName, newPortfolioBalance);
      await loadPortfolios();
      setSelectedPortfolioId(created.id);
    } catch (err) {
      setError((err as Error).message);
    }
  };

  const handleOpenTrade = async () => {
    if (!selectedPortfolioId || stopLoss === "") {
      setError("Select a portfolio and provide a stop loss to size the trade by risk.");
      return;
    }
    setError(null);
    try {
      await openTrade({
        portfolio_id: selectedPortfolioId,
        symbol: tradeSymbol,
        side: tradeSide,
        risk_amount: riskAmount,
        stop_loss: Number(stopLoss),
        take_profit: takeProfit === "" ? undefined : Number(takeProfit)
      });
      await loadPortfolioDetail(selectedPortfolioId);
    } catch (err) {
      setError((err as Error).message);
    }
  };

  const handleCloseTrade = async (tradeId: string) => {
    setError(null);
    try {
      await closeTrade(tradeId);
      await loadPortfolioDetail(selectedPortfolioId);
    } catch (err) {
      setError((err as Error).message);
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 4, display: "flex", flexDirection: "column", gap: 3 }}>
      <Typography variant="h4">Paper Trading</Typography>
      {error && <Alert severity="error">{error}</Alert>}

      <Card>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField
                select
                fullWidth
                label="Portfolio"
                value={selectedPortfolioId}
                onChange={(e) => setSelectedPortfolioId(e.target.value)}
              >
                {portfolios.map((portfolio) => (
                  <MenuItem key={portfolio.id} value={portfolio.id}>
                    {portfolio.name} (${portfolio.current_balance.toFixed(2)})
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField
                fullWidth
                label="New portfolio name"
                value={newPortfolioName}
                onChange={(e) => setNewPortfolioName(e.target.value)}
              />
            </Grid>
            <Grid size={{ xs: 6, sm: 2 }}>
              <TextField
                fullWidth
                type="number"
                label="Balance"
                value={newPortfolioBalance}
                onChange={(e) => setNewPortfolioBalance(Number(e.target.value))}
              />
            </Grid>
            <Grid size={{ xs: 6, sm: 2 }}>
              <Button variant="outlined" fullWidth onClick={handleCreatePortfolio}>
                Create
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {performance && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Performance
            </Typography>
            <Grid container spacing={2}>
              <Grid size={{ xs: 6, sm: 3 }}>
                <Typography variant="body2" color="text.secondary">
                  Balance
                </Typography>
                <Typography variant="h6">${performance.current_balance.toFixed(2)}</Typography>
              </Grid>
              <Grid size={{ xs: 6, sm: 3 }}>
                <Typography variant="body2" color="text.secondary">
                  Return
                </Typography>
                <Typography variant="h6">{performance.return_pct.toFixed(2)}%</Typography>
              </Grid>
              <Grid size={{ xs: 6, sm: 3 }}>
                <Typography variant="body2" color="text.secondary">
                  Win rate
                </Typography>
                <Typography variant="h6">
                  {performance.win_rate !== null ? `${performance.win_rate.toFixed(1)}%` : "—"}
                </Typography>
              </Grid>
              <Grid size={{ xs: 6, sm: 3 }}>
                <Typography variant="body2" color="text.secondary">
                  Open trades
                </Typography>
                <Typography variant="h6">{performance.open_trades}</Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Open a trade
          </Typography>
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, sm: 2 }}>
              <TextField fullWidth label="Symbol" value={tradeSymbol} onChange={(e) => setTradeSymbol(e.target.value)} />
            </Grid>
            <Grid size={{ xs: 12, sm: 2 }}>
              <TextField
                select
                fullWidth
                label="Side"
                value={tradeSide}
                onChange={(e) => setTradeSide(e.target.value as "long" | "short")}
              >
                <MenuItem value="long">Long</MenuItem>
                <MenuItem value="short">Short</MenuItem>
              </TextField>
            </Grid>
            <Grid size={{ xs: 12, sm: 2 }}>
              <TextField
                fullWidth
                type="number"
                label="Risk amount"
                value={riskAmount}
                onChange={(e) => setRiskAmount(Number(e.target.value))}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 2 }}>
              <TextField
                fullWidth
                type="number"
                label="Stop loss"
                value={stopLoss}
                onChange={(e) => setStopLoss(e.target.value === "" ? "" : Number(e.target.value))}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 2 }}>
              <TextField
                fullWidth
                type="number"
                label="Take profit"
                value={takeProfit}
                onChange={(e) => setTakeProfit(e.target.value === "" ? "" : Number(e.target.value))}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 2 }}>
              <Button variant="contained" fullWidth onClick={handleOpenTrade}>
                Open trade
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Trade journal
          </Typography>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Symbol</TableCell>
                <TableCell>Side</TableCell>
                <TableCell>Entry</TableCell>
                <TableCell>Exit</TableCell>
                <TableCell>PnL</TableCell>
                <TableCell>Status</TableCell>
                <TableCell />
              </TableRow>
            </TableHead>
            <TableBody>
              {trades.map((trade) => (
                <TableRow key={trade.id}>
                  <TableCell>{trade.symbol}</TableCell>
                  <TableCell>{trade.side}</TableCell>
                  <TableCell>{trade.entry_price.toFixed(5)}</TableCell>
                  <TableCell>{trade.exit_price !== null ? trade.exit_price.toFixed(5) : "—"}</TableCell>
                  <TableCell>{trade.pnl !== null ? trade.pnl.toFixed(2) : "—"}</TableCell>
                  <TableCell>
                    <Chip size="small" label={trade.status} color={trade.status === "open" ? "warning" : "default"} />
                  </TableCell>
                  <TableCell>
                    {trade.status === "open" && (
                      <Button size="small" onClick={() => handleCloseTrade(trade.id)}>
                        Close
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </Box>
  );
}