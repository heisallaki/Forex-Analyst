import { ReactNode, useEffect, useState } from "react";
import {
  Box,
  Card,
  CardContent,
  Chip,
  Alert,
  List,
  ListItem,
  ListItemText,
  ToggleButtonGroup,
  ToggleButton,
  Typography,
  Tooltip,
  Grid2 as Grid
} from "@mui/material";
import LightModeIcon from "@mui/icons-material/LightMode";
import DarkModeIcon from "@mui/icons-material/DarkMode";
import SettingsBrightnessIcon from "@mui/icons-material/SettingsBrightness";
import CheckIcon from "@mui/icons-material/Check";
import { ExecutionStatus, UserProfile, getExecutionStatus, getProfile } from "@/features/settings/api/settingsApi";
import { PageHeader } from "@/shared/ui/PageHeader";
import { PageLoadingSkeleton } from "@/shared/ui/PageLoadingSkeleton";
import { ACCENT_COLOR_OPTIONS } from "@/app/theme";
import { ThemeModePreference, useThemeStore } from "@/app/theme/themeStore";

const MODE_OPTIONS: { value: ThemeModePreference; label: string; icon: ReactNode }[] = [
  { value: "light", label: "Light", icon: <LightModeIcon fontSize="small" /> },
  { value: "dark", label: "Dark", icon: <DarkModeIcon fontSize="small" /> },
  { value: "system", label: "System", icon: <SettingsBrightnessIcon fontSize="small" /> }
];

export function SettingsPage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [executionStatus, setExecutionStatus] = useState<ExecutionStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { modePreference, accentColor, setModePreference, setAccentColor } = useThemeStore();

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
    return <PageLoadingSkeleton />;
  }

  return (
    <Box sx={{ p: { xs: 2, sm: 4 }, display: "flex", flexDirection: "column", gap: 3 }}>
      <PageHeader title="Settings" subtitle="Your profile, appearance, and system configuration" />
      {error && <Alert severity="error">{error}</Alert>}

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Appearance
          </Typography>

          <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
            Theme mode
          </Typography>
          <ToggleButtonGroup
            value={modePreference}
            exclusive
            onChange={(_event, value: ThemeModePreference | null) => {
              if (value) {
                setModePreference(value);
              }
            }}
            sx={{
              flexWrap: "wrap",
              gap: 1,
              "& .MuiToggleButton-root": { borderRadius: 2, border: "1px solid", borderColor: "divider" }
            }}
          >
            {MODE_OPTIONS.map((option) => (
              <ToggleButton key={option.value} value={option.value} sx={{ px: 2, gap: 1 }}>
                {option.icon}
                {option.label}
              </ToggleButton>
            ))}
          </ToggleButtonGroup>

          <Typography variant="body2" color="text.secondary" sx={{ mt: 3, mb: 1.5 }}>
            Accent color
          </Typography>
          <Box sx={{ display: "flex", gap: 1.5, flexWrap: "wrap" }}>
            {ACCENT_COLOR_OPTIONS.map((option) => {
              const selected = option.key === accentColor;
              return (
                <Tooltip key={option.key} title={option.label}>
                  <Box
                    component="button"
                    type="button"
                    onClick={() => setAccentColor(option.key)}
                    aria-label={`Use ${option.label} accent color`}
                    aria-pressed={selected}
                    sx={{
                      width: 40,
                      height: 40,
                      p: 0,
                      borderRadius: "50%",
                      border: "2px solid",
                      borderColor: selected ? "text.primary" : "transparent",
                      backgroundColor: option.main,
                      cursor: "pointer",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      transition: "transform 140ms ease, box-shadow 140ms ease",
                      boxShadow: selected ? `0 0 0 3px ${option.main}55` : "none",
                      "&:hover": { transform: "translateY(-2px) scale(1.05)" },
                      "&:focus-visible": { outline: "2px solid", outlineColor: "text.primary", outlineOffset: 2 }
                    }}
                  >
                    {selected && <CheckIcon sx={{ color: "#fff", fontSize: 18 }} />}
                  </Box>
                </Tooltip>
              );
            })}
          </Box>
          <Typography variant="caption" color="text.secondary" sx={{ display: "block", mt: 1.5 }}>
            The accent color updates buttons, navigation, and highlights across the app. Bullish (green) and bearish
            (red) trading indicators always keep their fixed meaning regardless of accent.
          </Typography>
        </CardContent>
      </Card>

      {profile && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Profile
            </Typography>
            <Typography>{profile.full_name}</Typography>
            <Typography color="text.secondary">{profile.email}</Typography>
            <Chip sx={{ mt: 1 }} label={profile.role} color="primary" variant="outlined" />
            <Typography variant="subtitle2" sx={{ mt: 2 }}>
              Permissions
            </Typography>
            <List dense>
              {Object.entries(profile.permissions).map(([key, value]) => (
                <ListItem key={key} disableGutters>
                  <ListItemText primary={key} secondary={value ? "granted" : "not granted"} />
                  <Chip size="small" label={value ? "✅" : "❌"} variant="outlined" />
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
            <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
              <Chip
                label={executionStatus.execution_enabled ? "ENABLED" : "DISABLED"}
                color={executionStatus.execution_enabled ? "error" : "success"}
              />
              <Chip
                label={executionStatus.broker_configured ? "Broker configured" : "No broker configured"}
                variant="outlined"
              />
            </Box>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid size={{ xs: 6, sm: 4 }}>
                <Typography variant="body2" color="text.secondary">
                  Max position size
                </Typography>
                <Typography variant="h6">{executionStatus.max_position_size}</Typography>
              </Grid>
              <Grid size={{ xs: 6, sm: 4 }}>
                <Typography variant="body2" color="text.secondary">
                  Max open positions
                </Typography>
                <Typography variant="h6">{executionStatus.max_open_positions}</Typography>
              </Grid>
              <Grid size={{ xs: 6, sm: 4 }}>
                <Typography variant="body2" color="text.secondary">
                  Max daily loss
                </Typography>
                <Typography variant="h6">{executionStatus.max_daily_loss_pct}%</Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}