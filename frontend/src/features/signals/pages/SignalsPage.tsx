import { useEffect, useState } from "react";
import {
  Box,
  Typography,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Chip,
  CircularProgress,
  Alert
} from "@mui/material";
import { SignalListItem, listSignals } from "@/features/signals/api/signalsApi";

export function SignalsPage() {
  const [signals, setSignals] = useState<SignalListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listSignals(null, 50)
      .then(setSignals)
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
      <Typography variant="h4">Signals</Typography>
      {error && <Alert severity="error">{error}</Alert>}
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
      {signals.length === 0 && <Typography color="text.secondary">No signals yet.</Typography>}
    </Box>
  );
}