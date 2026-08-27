import { useEffect, useState } from "react";
import { Box, Typography, List, ListItem, ListItemText, Chip, CircularProgress, Alert, Button } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { StrategyListItem, listStrategies } from "@/features/strategies/api/strategiesApi";

export function StrategiesPage() {
  const [strategies, setStrategies] = useState<StrategyListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    listStrategies()
      .then(setStrategies)
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
    <Box sx={{ p: 4, display: "flex", flexDirection: "column", gap: 2 }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <Typography variant="h4">Strategies</Typography>
        <Button variant="contained" onClick={() => navigate("/backtest")}>
          Run a new backtest
        </Button>
      </Box>
      {error && <Alert severity="error">{error}</Alert>}
      <List>
        {strategies.map((strategy) => (
          <ListItem key={strategy.id} divider>
            <ListItemText primary={strategy.name} secondary={strategy.description || "No description"} />
            <Chip label={strategy.is_active ? "active" : "inactive"} color={strategy.is_active ? "success" : "default"} />
          </ListItem>
        ))}
      </List>
      {strategies.length === 0 && (
        <Typography color="text.secondary">No strategies yet — run a backtest to create one.</Typography>
      )}
    </Box>
  );
}