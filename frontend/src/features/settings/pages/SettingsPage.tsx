import { useEffect, useState } from "react";
import { Box, Typography, Card, CardContent, Chip, Alert, CircularProgress, List, ListItem, ListItemText } from "@mui/material";
import { ExecutionStatus, UserProfile, getExecutionStatus, getProfile } from "@/features/settings/api/settingsApi";

export function SettingsPage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [executionStatus, setExecutionStatus] = useState<ExecutionStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getProfile()
      .then(async (result) => {
        setProfile(result);
        if (result.role === "admin") {
          const status = await getExecutionStatus();
          setExecutionStatus(status);
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
      <Typography variant="h4">Settings</Typography>
      {error && <Alert severity="error">{error}</Alert>}

      {profile && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Profile
            </Typography>
            <Typography>{profile.full_name}</Typography>
            <Typography color="text.secondary">{profile.email}</Typography>
            <Chip sx={{ mt: 1 }} label={profile.role} />
            <Typography variant="subtitle2" sx={{ mt: 2 }}>
              Permissions
            </Typography>
            <List dense>
              {Object.entries(profile.permissions).map(([key, value]) => (
                <ListItem key={key}>
                  <ListItemText primary={key} secondary={value ? "granted" : "not granted"} />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      {executionStatus && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Execution engine status
            </Typography>
            <Chip
              label={executionStatus.execution_enabled ? "ENABLED" : "DISABLED"}
              color={executionStatus.execution_enabled ? "error" : "success"}
            />
            <Chip sx={{ ml: 1 }} label={executionStatus.broker_configured ? "Broker configured" : "No broker configured"} />
            <Typography variant="body2" sx={{ mt: 2 }} color="text.secondary">
              Max position size: {executionStatus.max_position_size} · Max open positions:{" "}
              {executionStatus.max_open_positions} · Max daily loss: {executionStatus.max_daily_loss_pct}%
            </Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}