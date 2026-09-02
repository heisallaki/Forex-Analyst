import { useEffect, useState } from "react";
import { Box, List, ListItem, ListItemText, Chip, Button, Typography, Tooltip } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { StrategyListItem, listStrategies } from "@/features/strategies/api/strategiesApi";
import { STRATEGY_PRESETS } from "@/features/strategies/strategyPresets";
import { PageHeader } from "@/shared/ui/PageHeader";
import { PageLoadingSkeleton } from "@/shared/ui/PageLoadingSkeleton";
import { useToast } from "@/shared/ui/useToast";

export function StrategiesPage() {
  const [dbStrategies, setDbStrategies] = useState<StrategyListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { showToast } = useToast();

  useEffect(() => {
    listStrategies()
      .then(setDbStrategies)
      .catch((err) => showToast((err as Error).message, "error"))
      .finally(() => setLoading(false));
  }, [showToast]);

  if (loading) {
    return <PageLoadingSkeleton variant="table" />;
  }

  return (
    <Box sx={{ p: { xs: 2, sm: 4 }, display: "flex", flexDirection: "column", gap: 2 }}>
      <PageHeader
        title="Strategies"
        subtitle="The full strategy library — genuinely implemented, partial, and not-yet-possible"
        action={
          <Button variant="contained" onClick={() => navigate("/backtest")}>
            Run a backtest
          </Button>
        }
      />
      <List>
        {STRATEGY_PRESETS.map((preset) => {
          const dbMatch = dbStrategies.find((strategy) => strategy.name === preset.strategyName);
          let statusLabel = "Not yet tested";
          let color: "success" | "warning" | "default" | "error" = "default";
          if (preset.status === "not_implemented") {
            statusLabel = "Not implemented";
            color = "error";
          } else if (dbMatch?.is_active) {
            statusLabel = "Active";
            color = "success";
          } else if (preset.status === "partial") {
            statusLabel = dbMatch ? "Active (partial)" : "Not yet tested (partial)";
            color = dbMatch ? "success" : "warning";
          }
          return (
            <ListItem key={preset.key} divider alignItems="flex-start">
              <ListItemText
                primary={preset.displayName}
                secondary={
                  <>
                    <Typography component="span" variant="body2" color="text.secondary">
                      {preset.description}
                    </Typography>
                    {preset.limitationNote && (
                      <Typography component="span" variant="caption" color="warning.main" sx={{ display: "block", mt: 0.5 }}>
                        {preset.limitationNote}
                      </Typography>
                    )}
                  </>
                }
              />
              <Tooltip title={preset.status === "not_implemented" ? preset.limitationNote ?? "" : ""}>
                <Chip label={statusLabel} color={color} />
              </Tooltip>
            </ListItem>
          );
        })}
      </List>
    </Box>
  );
}