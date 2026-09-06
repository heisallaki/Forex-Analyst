import { useCallback, useEffect, useState } from "react";
import {
  Box,
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
  Typography,
  Tooltip,
  IconButton
} from "@mui/material";
import Grid from "@mui/material/Grid2";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import {
  Portfolio,
  PortfolioPerformance,
  Trade,
  closeTrade,
  createPortfolio,
  getPortfolioPerformance,
  listPortfolios,
  listTrades,
  openTrade,
  partialCloseTrade
} from "@/features/paper/api/paperApi";
import { PageHeader } from "@/shared/ui/PageHeader";
import { PageLoadingSkeleton } from "@/shared/ui/PageLoadingSkeleton";
import { useToast } from "@/shared/ui/useToast";

export function PaperTradingPage() {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [selectedPortfolioId, setSelectedPortfolioId] = useState<string>("");
  const [performance, setPerformance] = useState<PortfolioPerformance | null>(null);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [newPortfolioName, setNewPortfolioName] = useState("Main Portfolio");
  const [newPortfolioBalance, setNewPortfolioBalance] = useState(10000);
  const [newPortfolioLeverage, setNewPortfolioLeverage] = useState(1);
  const [tradeSymbol, setTradeSymbol] = useState("EUR/USD");
  const [tradeSide, setTradeSide] = useState<"long" | "short">("long");
  const [riskAmount, setRiskAmount] = useState(100);
  const [stopLoss, setStopLoss] = useState<number | "">("");
  const [takeProfit, setTakeProfit] = useState<number | "">("");
  const [trailingStopDistance, setTrailingStopDistance] = useState<number | "">("");
  const [partialCloseQuantities, setPartialCloseQuantities] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const { showToast } = useToast();

  const loadPortfolios = async () => {
    const result = await listPortfolios();
    setPortfolios(result);
    if (result.length > 0 && !selectedPortfolioId) {
      setSelectedPortfolioId(result[0].id);
    }
  };

  useEffect(() => {
    loadPortfolios()
      .catch((err) => showToast((err as Error).message, "error"))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadPortfolioDetail = useCallback(
    async (portfolioId: string) => {
        const [performanceResult, tradesResult] = await Promise.all([
          getPortfolioPerformance(portfolioId),
          listTrades(portfolioId),
        ]);
      setPerformance(performanceResult);
      setTrades(tradesResult);
    },
    []
  );

  useEffect(() => {
      if (!selectedPortfolioId) return;

      loadPortfolioDetail(selectedPortfolioId).catch((err) =>
        showToast((err as Error).message, "error")
      );
  }, [selectedPortfolioId, loadPortfolioDetail, showToast]);

  const handleCreatePortfolio = async () => {
    try {
      const created = await createPortfolio(newPortfolioName, newPortfolioBalance, newPortfolioLeverage);
      await loadPortfolios();
      setSelectedPortfolioId(created.id);
      showToast("Portfolio created", "success");
    } catch (err) {
      showToast((err as Error).message, "error");
    }
  };

  const handleOpenTrade = async () => {
    if (!selectedPortfolioId || stopLoss === "") {
      showToast("Select a portfolio and provide a stop loss to size the trade by risk.", "warning");
      return;
    }
    try {
      await openTrade({
        portfolio_id: selectedPortfolioId,
        symbol: tradeSymbol,
        side: tradeSide,
        risk_amount: riskAmount,
        stop_loss: Number(stopLoss),
        take_profit: takeProfit === "" ? undefined : Number(takeProfit),
        trailing_stop_distance: trailingStopDistance === "" ? undefined : Number(trailingStopDistance)
      });
      await loadPortfolioDetail(selectedPortfolioId);
      showToast("Trade opened", "success");
    } catch (err) {
      showToast((err as Error).message, "error");
    }
  };

  const handleCloseTrade = async (tradeId: string) => {
    try {
      await closeTrade(tradeId);
      await loadPortfolioDetail(selectedPortfolioId);
      showToast("Trade closed", "success");
    } catch (err) {
      showToast((err as Error).message, "error");
    }
  };

  const handlePartialClose = async (tradeId: string) => {
    const raw = partialCloseQuantities[tradeId];
    const quantity = Number(raw);
    if (!raw || quantity <= 0) {
      showToast("Enter a valid partial close quantity", "warning");
      return;
    }
    try {
      await partialCloseTrade(tradeId, quantity);
      await loadPortfolioDetail(selectedPortfolioId);
      showToast("Partial close executed", "success");
    } catch (err) {
      showToast((err as Error).message, "error");
    }
  };

  if (loading) {
    return <PageLoadingSkeleton />;
  }

  return (
    <Box sx={{ p: { xs: 2, sm: 4 }, display: "flex", flexDirection: "column", gap: 3 }}>
      <PageHeader title="Paper Trading" subtitle="Simulate trades against live prices with a virtual portfolio" />

      <Card>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid size={{ xs: 12, sm: 4 }}>
              <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                <TextField
                  select
                  fullWidth
                  label="Portfolio"
                  value={selectedPortfolioId}
                  onChange={(e) => setSelectedPortfolioId(e.target.value)}
                >
                  {portfolios.map((portfolio) => (
                    <MenuItem key={portfolio.id} value={portfolio.id}>
                      {portfolio.name} (${portfolio.current_balance.toFixed(2)}, {portfolio.leverage}x)
                    </MenuItem>
                  ))}
                </TextField>
                <Tooltip title="A portfolio is a virtual account with its own starting balance and leverage. Every trade you open must belong to a portfolio, so create one first if the list is empty.">
                  <IconButton size="small" aria-label="What is a portfolio?">
                    <InfoOutlinedIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            </Grid>
            <Grid size={{ xs: 12, sm: 3 }}>
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
            <Grid size={{ xs: 6, sm: 1.5 }}>
              <TextField
                fullWidth
                type="number"
                label="Leverage"
                value={newPortfolioLeverage}
                onChange={(e) => setNewPortfolioLeverage(Number(e.target.value))}
                inputProps={{ min: 1, max: 100 }}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 1.5 }}>
              <Button variant="outlined" fullWidth onClick={handleCreatePortfolio}>
                Create
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {portfolios.length === 0 && (
        <Card>
          <CardContent>
            <Typography color="text.secondary">
              You don't have a portfolio yet — create one above to start paper trading.
            </Typography>
          </CardContent>
        </Card>
      )}

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
                  Available margin
                </Typography>
                <Typography variant="h6">${performance.available_margin.toFixed(2)}</Typography>
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
              <Tooltip title="If set, the stop loss ratchets favorably as price moves in your favor by this distance, and never moves backward.">
                <TextField
                  fullWidth
                  type="number"
                  label="Trailing stop (optional)"
                  value={trailingStopDistance}
                  onChange={(e) => setTrailingStopDistance(e.target.value === "" ? "" : Number(e.target.value))}
                />
              </Tooltip>
            </Grid>
            <Grid size={{ xs: 12 }}>
              <Button variant="contained" onClick={handleOpenTrade}>
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
          <Box sx={{ overflowX: "auto" }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Symbol</TableCell>
                  <TableCell>Side</TableCell>
                  <TableCell>Entry</TableCell>
                  <TableCell>Exit</TableCell>
                  <TableCell>Qty</TableCell>
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
                    <TableCell>{trade.quantity.toFixed(2)}</TableCell>
                    <TableCell>
                      {trade.pnl !== null
                        ? trade.pnl.toFixed(2)
                        : trade.realized_pnl !== 0
                          ? `${trade.realized_pnl.toFixed(2)} realized`
                          : "—"}
                    </TableCell>
                    <TableCell>
                      <Chip size="small" label={trade.status} color={trade.status === "open" ? "warning" : "default"} />
                    </TableCell>
                    <TableCell>
                      {trade.status === "open" && (
                        <Box sx={{ display: "flex", gap: 1, alignItems: "center" }}>
                          <TextField
                            size="small"
                            type="number"
                            placeholder="qty"
                            sx={{ width: 90 }}
                            value={partialCloseQuantities[trade.id] ?? ""}
                            onChange={(e) =>
                              setPartialCloseQuantities((prev) => ({ ...prev, [trade.id]: e.target.value }))
                            }
                          />
                          <Button size="small" onClick={() => handlePartialClose(trade.id)}>
                            Partial
                          </Button>
                          <Button size="small" onClick={() => handleCloseTrade(trade.id)}>
                            Close
                          </Button>
                        </Box>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Box>
          {trades.length === 0 && (
            <Typography color="text.secondary" sx={{ mt: 2 }}>
              No trades yet for this portfolio.
            </Typography>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}