import { useEffect, useState } from "react";
import { Box, Typography, Card, CardContent, Chip, CircularProgress, Alert } from "@mui/material";
import Grid from "@mui/material/Grid2";
import { useNavigate } from "react-router-dom";
import { getMarketStatus } from "@/features/market/api/marketApi";
import { MarketStatus } from "@/features/market/types";
import { SignalListItem, listSignals } from "@/features/signals/api/signalsApi";
import { Portfolio, PortfolioPerformance, getPortfolioPerformance, listPortfolios } from "@/features/paper/api/paperApi";

export function DashboardPage() {
  const [marketStatus, setMarketStatus] = useState<MarketStatus | null>(null);
  const [signals, setSignals] = useState<SignalListItem[]>([]);
  const [performance, setPerformance] = useState<PortfolioPerformance | null>(null);
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([getMarketStatus(), listSignals(null, 5), listPortfolios()])
      .then(async ([statusResult, signalsResult, portfoliosResult]) => {
        setMarketStatus(statusResult);
        setSignals(signalsResult);
        if (portfoliosResult.length > 0) {
          setPortfolio(portfoliosResult[0]);
          const performanceResult = await getPortfolioPerformance(portfoliosResult[0].id);
          setPerformance(performanceResult);
        }
      })
      .catch((err) => setError((err as Error).message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <Box sx={{ p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 4, display: "flex", flexDirection: "column", gap: 3 }}>
      <Typography variant="h4">Dashboard</Typography>
      {error && <Alert severity="error">{error}</Alert>}

      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card sx={{ cursor: "pointer" }} onClick={() => navigate("/markets")}>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                Active sessions
              </Typography>
              <Box sx={{ display: "flex", gap: 1, mt: 1, flexWrap: "wrap" }}>
                {marketStatus?.active_sessions.map((session) => (
                  <Chip key={session} label={session} size="small" color="primary" variant="outlined" />
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card sx={{ cursor: "pointer" }} onClick={() => navigate("/paper")}>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                {portfolio ? portfolio.name : "No portfolio yet"}
              </Typography>
              <Typography variant="h5">{performance ? `$${performance.current_balance.toFixed(2)}` : "—"}</Typography>
              {performance && (
                <Typography variant="body2" color={performance.return_pct >= 0 ? "success.main" : "error.main"}>
                  {performance.return_pct.toFixed(2)}% return
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card sx={{ cursor: "pointer" }} onClick={() => navigate("/signals")}>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                Recent signals
              </Typography>
              <Typography variant="h5">{signals.length}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Latest signals
          </Typography>
          {signals.map((signal) => (
            <Box
              key={signal.id}
              sx={{ display: "flex", gap: 2, alignItems: "center", py: 1, borderBottom: "1px solid rgba(255,255,255,0.08)" }}
            >
              <Typography sx={{ minWidth: 100 }}>{signal.symbol}</Typography>
              <Chip
                size="small"
                label={signal.direction}
                color={signal.direction === "long" ? "success" : signal.direction === "short" ? "error" : "default"}
              />
              <Typography variant="body2" color="text.secondary">
                {(signal.confidence * 100).toFixed(0)}% confidence
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ ml: "auto" }}>
                {new Date(signal.created_at).toLocaleString()}
              </Typography>
            </Box>
          ))}
          {signals.length === 0 && <Typography color="text.secondary">No signals yet.</Typography>}
        </CardContent>
      </Card>
    </Box>
  );
}