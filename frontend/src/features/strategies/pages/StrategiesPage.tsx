import { useEffect, useState } from "react";
import { Box, List, ListItem, ListItemText, Chip, Button, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { StrategyListItem, listStrategies } from "@/features/strategies/api/strategiesApi";
import { PageHeader } from "@/shared/ui/PageHeader";
import { PageLoadingSkeleton } from "@/shared/ui/PageLoadingSkeleton";
import { useToast } from "@/shared/ui/ToastProvider";

export function StrategiesPage() {
  const [strategies, setStrategies] = useState<StrategyListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { showToast } = useToast();

  useEffect(() => {
    listStrategies()
      .then(setStrategies)
      .catch((err) => showToast((err as Error).message, "error"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <PageLoadingSkeleton variant="table" />;
  }

  return (
    <Box sx={{ p: { xs: 2, sm: 4 }, display: "flex", flexDirection: "column", gap: 2 }}>
      <PageHeader
        title="Strategies"
        subtitle="Every strategy created through backtesting"
        action={
          <Button variant="contained" onClick={() => navigate("/backtest")}>
            Run a new backtest
          </Button>
        }
      />
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