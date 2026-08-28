import { useEffect, useState } from "react";
import { Box, Table, TableHead, TableRow, TableCell, TableBody, Chip, Typography } from "@mui/material";
import { SignalListItem, listSignals } from "@/features/signals/api/signalsApi";
import { PageHeader } from "@/shared/ui/PageHeader";
import { PageLoadingSkeleton } from "@/shared/ui/PageLoadingSkeleton";
import { useToast } from "@/shared/ui/ToastProvider";

export function SignalsPage() {
  const [signals, setSignals] = useState<SignalListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const { showToast } = useToast();

  useEffect(() => {
    listSignals(null, 50)
      .then(setSignals)
      .catch((err) => showToast((err as Error).message, "error"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <PageLoadingSkeleton variant="table" />;
  }

  return (
    <Box sx={{ p: { xs: 2, sm: 4 }, display: "flex", flexDirection: "column", gap: 2 }}>
      <PageHeader title="Signals" subtitle="Every recommendation and backtest signal generated so far" />
      <Box sx={{ overflowX: "auto" }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Symbol</TableCell>
              <TableCell>Direction</TableCell>
              <TableCell>Confidence</TableCell>
              <TableCell>Source</TableCell>
              <TableCell>Created</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {signals.map((signal) => (
              <TableRow key={signal.id}>
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
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Box>
      {signals.length === 0 && <Typography color="text.secondary">No signals yet.</Typography>}
    </Box>
  );
}