import { useEffect, useState } from "react";
import { Box, Typography, Card, CardContent, TextField, MenuItem, CircularProgress, Alert } from "@mui/material";
import Grid from "@mui/material/Grid2";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { Portfolio, PortfolioPerformance, getPortfolioPerformance, listPortfolios } from "@/features/paper/api/paperApi";

export function AnalyticsPage() {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [selectedPortfolioId, setSelectedPortfolioId] = useState("");
  const [performance, setPerformance] = useState<PortfolioPerformance | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listPortfolios()
      .then((result) => {
        setPortfolios(result);
        if (result.length > 0) {
          setSelectedPortfolioId(result[0].id);
        }
      })
      .catch((err) => setError((err as Error).message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (selectedPortfolioId) {
      getPortfolioPerformance(selectedPortfolioId)
        .then(setPerformance)
        .catch((err) => setError((err as Error).message));
    }
  }, [selectedPortfolioId]);

  if (loading) {
    return (
      <Box sx={{ p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  const chartData = performance
    ? [
        { label: "Gross profit", value: performance.gross_profit },
        { label: "Gross loss", value: performance.gross_loss }
      ]
    : [];

  return (
    <Box sx={{ p: 4, display: "flex", flexDirection: "column", gap: 3 }}>
      <Typography variant="h4">Analytics</Typography>
      {error && <Alert severity="error">{error}</Alert>}
      <TextField
        select
        label="Portfolio"
        value={selectedPortfolioId}
        onChange={(e) => setSelectedPortfolioId(e.target.value)}
        sx={{ maxWidth: 300 }}
      >
        {portfolios.map((portfolio) => (
          <MenuItem key={portfolio.id} value={portfolio.id}>
            {portfolio.name}
          </MenuItem>
        ))}
      </TextField>

      {performance && (
        <>
          <Grid container spacing={2}>
            <Grid size={{ xs: 6, sm: 3 }}>
              <Card>
                <CardContent>
                  <Typography variant="body2" color="text.secondary">
                    Total P&L
                  </Typography>
                  <Typography variant="h5">{performance.total_pnl.toFixed(2)}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={{ xs: 6, sm: 3 }}>
              <Card>
                <CardContent>
                  <Typography variant="body2" color="text.secondary">
                    Profit factor
                  </Typography>
                  <Typography variant="h5">
                    {performance.profit_factor !== null ? performance.profit_factor.toFixed(2) : "—"}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={{ xs: 6, sm: 3 }}>
              <Card>
                <CardContent>
                  <Typography variant="body2" color="text.secondary">
                    Total trades
                  </Typography>
                  <Typography variant="h5">{performance.total_trades}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={{ xs: 6, sm: 3 }}>
              <Card>
                <CardContent>
                  <Typography variant="body2" color="text.secondary">
                    Return
                  </Typography>
                  <Typography variant="h5">{performance.return_pct.toFixed(2)}%</Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Gross profit vs loss
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="label" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#2196f3" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </>
      )}
      {portfolios.length === 0 && (
        <Typography color="text.secondary">Create a portfolio in Paper Trading to see analytics.</Typography>
      )}
    </Box>
  );
}