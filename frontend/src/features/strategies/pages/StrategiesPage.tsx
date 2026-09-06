import { useCallback, useEffect, useState } from "react";
import { Box, List, ListItem, ListItemText, Chip, Button, Typography, Tooltip, IconButton } from "@mui/material";
import PowerSettingsNewIcon from "@mui/icons-material/PowerSettingsNew";
import DeleteIcon from "@mui/icons-material/Delete";
import { useNavigate } from "react-router-dom";
import {
  StrategyListItem,
  deactivateStrategy,
  deleteStrategy,
  listStrategies
} from "@/features/strategies/api/strategiesApi";
import { STRATEGY_PRESETS } from "@/features/strategies/strategyPresets";
import { PageHeader } from "@/shared/ui/PageHeader";
import { PageLoadingSkeleton } from "@/shared/ui/PageLoadingSkeleton";
import { ConfirmDialog } from "@/shared/ui/ConfirmDialog";
import { useToast } from "@/shared/ui/useToast";
import { useAuthStore } from "@/features/auth/store/authStore";

export function StrategiesPage() {
  const [dbStrategies, setDbStrategies] = useState<StrategyListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [pendingDelete, setPendingDelete] = useState<StrategyListItem | null>(null);
  const navigate = useNavigate();
  const { showToast } = useToast();
  const isAdmin = useAuthStore((state) => state.user?.role === "admin");

  const load = useCallback(
    () =>
      listStrategies()
        .then(setDbStrategies)
        .catch((err) => showToast((err as Error).message, "error")),
    [showToast]
  );
  useEffect(() => {
    load()
      .catch(() => undefined)
      .finally(() => setLoading(false));
  }, [load]);

  const handleDeactivate = async (strategy: StrategyListItem) => {
    try {
      await deactivateStrategy(strategy.id);
      showToast(`${strategy.name} deactivated`, "success");
      await load();
    } catch (err) {
      showToast((err as Error).message, "error");
    }
  };

  const handleDeleteConfirmed = async () => {
    if (!pendingDelete) {
      return;
    }
    try {
      await deleteStrategy(pendingDelete.id);
      showToast(`${pendingDelete.name} deleted`, "success");
      setPendingDelete(null);
      await load();
    } catch (err) {
      showToast((err as Error).message, "error");
    }
  };

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
            statusLabel = `Active (v${dbMatch.version})`;
            color = "success";
          } else if (dbMatch) {
            statusLabel = `Inactive (v${dbMatch.version})`;
            color = "default";
          } else if (preset.status === "partial") {
            statusLabel = "Not yet tested (partial)";
            color = "warning";
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
              <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                <Tooltip title={preset.status === "not_implemented" ? preset.limitationNote ?? "" : ""}>
                  <Chip label={statusLabel} color={color} />
                </Tooltip>
                {isAdmin && dbMatch && (
                  <>
                    {dbMatch.is_active && (
                      <Tooltip title="Deactivate">
                        <IconButton size="small" onClick={() => handleDeactivate(dbMatch)}>
                          <PowerSettingsNewIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )}
                    <Tooltip title="Delete permanently">
                      <IconButton size="small" color="error" onClick={() => setPendingDelete(dbMatch)}>
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </>
                )}
              </Box>
            </ListItem>
          );
        })}
      </List>

      <ConfirmDialog
        open={pendingDelete !== null}
        title="Delete this strategy?"
        description={`This permanently deletes "${pendingDelete?.name}" and its version history. Backtest results and signals already recorded stay in place but will no longer reference this strategy. This cannot be undone.`}
        confirmLabel="Delete permanently"
        destructive
        onConfirm={handleDeleteConfirmed}
        onCancel={() => setPendingDelete(null)}
      />
    </Box>
  );
}