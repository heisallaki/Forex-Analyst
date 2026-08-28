import { useEffect, useState } from "react";
import { Box, Card, CardContent, Chip, Alert } from "@mui/material";
import Grid from "@mui/material/Grid2";
import { useNavigate } from "react-router-dom";
import { getMarketStatus } from "@/features/market/api/marketApi";
import { MarketStatus } from "@/features/market/types";
import { SignalListItem, listSignals } from "@/features/signals/api/signalsApi";
import { Portfolio, PortfolioPerformance, getPortfolioPerformance, listPortfolios } from "@/features/paper/api/paperApi";
import { PageHeader } from "@/shared/ui/PageHeader";
import { PageLoadingSkeleton } from "@/shared/ui/PageLoadingSkeleton";
import { Box as MuiBox, Typography } from "@mui/material";

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
    return <PageLoadingSkeleton />;
  }

  const goTo = (path: string) => () => navigate(path);
  const onEnterKey = (path: string) => (event: React.KeyboardEvent) => {
    if (event.key === "Enter" || event.key === " ") {
      navigate(path);
    }
  };

  return (
    <Box sx={{ p: { xs: 2, sm: 4 }, display: "flex", flexDirection: "column", gap: 3 }}>
      <PageHeader title="Dashboard" subtitle="Your trading command center" />
      {error && <Alert severity="error">{error}</Alert>}

      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card sx={{ cursor: "pointer" }} onClick={goTo("/markets")} onKeyDown={onEnterKey("/markets")} role="button" tabIndex={0}>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                Active sessions
              </Typography>
              <MuiBox sx={{ display: "flex", gap: 1, mt: 1, flexWrap: "wrap" }}>
                {marketStatus?.active_sessions.map((session) => (
                  <Chip key={session} label={session} size="small" color="primary" variant="outlined" />
                ))}
                {marketStatus?.active_sessions.length === 0 && (
                  <Typography variant="body2" color="text.secondary">
                    No sessions currently open
                  </Typography>
                )}
              </MuiBox>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card sx={{ cursor: "pointer" }} onClick={goTo("/paper")} onKeyDown={onEnterKey("/paper")} role="button" tabIndex={0}>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                {portfolio ? portfolio.name : "No portfolio yet"}
              </Typography>
              <Typography variant="h5">{performance ? `$${performance.current_balance.toFixed(2)}` : "—"}</Typography>
              {performance && (
                <Chip
                  size="small"
                  sx={{ mt: 1 }}
                  color={performance.return_pct >= 0 ? "success" : "error"}
                  label={`${performance.return_pct >= 0 ? "+" : ""}${performance.return_pct.toFixed(2)}%`}
                />
              )}
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card sx={{ cursor: "pointer" }} onClick={goTo("/signals")} onKeyDown={onEnterKey("/signals")} role="button" tabIndex={0}>
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
            <MuiBox
              key={signal.id}
              sx={{
                display: "flex",
                gap: 2,
                alignItems: "center",
                py: 1.2,
                flexWrap: "wrap",
                borderBottom: "1px solid",
                borderColor: "divider"
              }}
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
              <Typography variant="body2" color="text.secondary" sx={{ ml: { sm: "auto" } }}>
                {new Date(signal.created_at).toLocaleString()}
              </Typography>
            </MuiBox>
          ))}
          {signals.length === 0 && (
            <Typography color="text.secondary">No signals yet — run a backtest or check AI Analysis to generate one.</Typography>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}