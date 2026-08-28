import { useEffect, useState } from "react";
import {
  Box,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Chip,
  Typography,
  Checkbox,
  Button,
  FormControlLabel,
  Switch,
  Tooltip
} from "@mui/material";
import {
  SignalListItem,
  deleteSignals,
  hideSignals,
  listSignals,
  unhideSignals
} from "@/features/signals/api/signalsApi";
import { PageHeader } from "@/shared/ui/PageHeader";
import { PageLoadingSkeleton } from "@/shared/ui/PageLoadingSkeleton";
import { ConfirmDialog } from "@/shared/ui/ConfirmDialog";
import { useToast } from "@/shared/ui/ToastProvider";

export function SignalsPage() {
  const [signals, setSignals] = useState<SignalListItem[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [showHidden, setShowHidden] = useState(false);
  const [loading, setLoading] = useState(true);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const { showToast } = useToast();

  const load = async () => {
    const result = await listSignals(null, 100, showHidden);
    setSignals(result);
    setSelected([]);
  };

  useEffect(() => {
    setLoading(true);
    load()
      .catch((err) => showToast((err as Error).message, "error"))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showHidden]);

  const toggleSelected = (id: string) => {
    setSelected((prev) => (prev.includes(id) ? prev.filter((value) => value !== id) : [...prev, id]));
  };

  const selectableIds = signals.filter((signal) => signal.is_owner).map((signal) => signal.id);
  const allSelected = selectableIds.length > 0 && selectableIds.every((id) => selected.includes(id));

  const toggleSelectAll = () => {
    setSelected(allSelected ? [] : selectableIds);
  };

  const reportSkipped = (skipped: string[]) => {
    if (skipped.length > 0) {
      showToast(`${skipped.length} signal(s) were skipped — you can only manage signals you generated, or be an admin.`, "warning");
    }
  };

  const handleHide = async () => {
    try {
      const response = await hideSignals(selected);
      reportSkipped(response.skipped);
      showToast(`Hid ${response.succeeded.length} signal(s)`, "success");
      await load();
    } catch (err) {
      showToast((err as Error).message, "error");
    }
  };

  const handleUnhide = async () => {
    try {
      const response = await unhideSignals(selected);
      reportSkipped(response.skipped);
      showToast(`Restored ${response.succeeded.length} signal(s)`, "success");
      await load();
    } catch (err) {
      showToast((err as Error).message, "error");
    }
  };

  const handleDeleteConfirmed = async () => {
    setConfirmOpen(false);
    try {
      const response = await deleteSignals(selected);
      reportSkipped(response.skipped);
      showToast(`Permanently deleted ${response.succeeded.length} signal(s)`, "success");
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
      <PageHeader title="Signals" subtitle="Every recommendation and backtest signal generated so far" />

      <Box sx={{ display: "flex", gap: 2, alignItems: "center", flexWrap: "wrap" }}>
        <FormControlLabel
          control={<Switch checked={showHidden} onChange={(e) => setShowHidden(e.target.checked)} />}
          label="Show hidden"
        />
        <Button variant="outlined" disabled={selected.length === 0} onClick={handleHide}>
          Hide selected
        </Button>
        <Button variant="outlined" disabled={selected.length === 0} onClick={handleUnhide}>
          Restore selected
        </Button>
        <Button variant="outlined" color="error" disabled={selected.length === 0} onClick={() => setConfirmOpen(true)}>
          Delete selected permanently
        </Button>
      </Box>

      <Box sx={{ overflowX: "auto" }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox">
                <Checkbox
                  checked={allSelected}
                  indeterminate={selected.length > 0 && !allSelected}
                  onChange={toggleSelectAll}
                  disabled={selectableIds.length === 0}
                />
              </TableCell>
              <TableCell>Symbol</TableCell>
              <TableCell>Direction</TableCell>
              <TableCell>Confidence</TableCell>
              <TableCell>Source</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {signals.map((signal) => (
              <TableRow
                key={signal.id}
                sx={
                  signal.hidden_at
                    ? { opacity: 0.5, filter: "blur(0.3px)" }
                    : undefined
                }
              >
                <TableCell padding="checkbox">
                  <Tooltip title={signal.is_owner ? "" : "You can only manage signals you generated"}>
                    <span>
                      <Checkbox
                        checked={selected.includes(signal.id)}
                        disabled={!signal.is_owner}
                        onChange={() => toggleSelected(signal.id)}
                      />
                    </span>
                  </Tooltip>
                </TableCell>
                <TableCell>{signal.symbol}</TableCell>
                <TableCell>
                  <Chip
                    size="small"
                    label={signal.direction}
                    color={signal.direction === "long" ? "success" : signal.direction === "short" ? "error" : "default"}
                  />
                </TableCell>
                <TableCell>{(signal.confidence * 100).toFixed(0)}%</TableCell>
                <TableCell>{String(signal.reasoning?.source ?? "backtest")}</TableCell>
                <TableCell>{new Date(signal.created_at).toLocaleString()}</TableCell>
                <TableCell>{signal.hidden_at ? <Chip size="small" label="hidden" /> : null}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Box>
      {signals.length === 0 && <Typography color="text.secondary">No signals to show.</Typography>}

      <ConfirmDialog
        open={confirmOpen}
        title="Permanently delete signals?"
        description={`This will permanently delete ${selected.length} signal(s). This action cannot be undone — deleted signals are not recoverable, unlike hiding.`}
        confirmLabel="Delete permanently"
        destructive
        onConfirm={handleDeleteConfirmed}
        onCancel={() => setConfirmOpen(false)}
      />
    </Box>
  );
}