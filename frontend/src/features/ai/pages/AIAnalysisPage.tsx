import { useEffect, useState } from "react";
import {
  Box,
  TextField,
  MenuItem,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  List,
  ListItem,
  ListItemText,
  Alert,
  Typography,
  Tooltip
} from "@mui/material";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import CancelIcon from "@mui/icons-material/Cancel";
import { getMarketStatus } from "@/features/market/api/marketApi";
import {
  ModelStatusResponse,
  PredictMarketResponse,
  RecommendationResponse,
  getModelStatus,
  getPredictions,
  getRecommendation,
  trainModels
} from "@/features/ai/api/aiApi";
import { useToast } from "@/shared/ui/ToastProvider";
import { PageHeader } from "@/shared/ui/PageHeader";
import { getPreference, setPreference } from "@/shared/utils/userPreferences";

const INTERVALS = ["1min", "5min", "15min", "30min", "45min", "1h", "1day"];

export function AIAnalysisPage() {
  const [instruments, setInstruments] = useState<string[]>([]);
  const [symbol, setSymbol] = useState(() => getPreference("ai_symbol", "EUR/USD"));
  const [interval, setInterval] = useState(() => getPreference("ai_interval", "1min"));
  const [modelStatus, setModelStatus] = useState<ModelStatusResponse | null>(null);
  const [predictions, setPredictions] = useState<PredictMarketResponse | null>(null);
  const [recommendation, setRecommendation] = useState<RecommendationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [training, setTraining] = useState(false);
  const { showToast } = useToast();

  useEffect(() => {
    getMarketStatus()
      .then((status) => setInstruments(status.instruments))
      .catch(() => undefined);
  }, []);

  const loadModelStatus = () => {
    getModelStatus(symbol, interval)
      .then(setModelStatus)
      .catch(() => setModelStatus(null));
  };

  useEffect(() => {
    if (symbol) {
      loadModelStatus();
    }
  }, [symbol, interval]);

  const handleSymbolChange = (value: string) => {
    setSymbol(value);
    setPreference("ai_symbol", value);
  };

  const handleIntervalChange = (value: string) => {
    setInterval(value);
    setPreference("ai_interval", value);
  };

  const handleTrain = async () => {
    setTraining(true);
    try {
      const response = await trainModels(symbol, interval);
      showToast(`Trained 6 models on ${response.dataset_size} samples`, "success");
      loadModelStatus();
    } catch (err) {
      const message = (err as Error).message;
      if (message.toLowerCase().includes("admin")) {
        showToast("Admin permission required to train models. Ask an administrator.", "warning");
      } else if (message.toLowerCase().includes("verif")) {
        showToast("Verify your email in Settings before training models.", "warning");
      } else {
        showToast(message, "error");
      }
    } finally {
      setTraining(false);
    }
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setPredictions(null);
    setRecommendation(null);
    try {
      const [predictionResult, recommendationResult] = await Promise.all([
        getPredictions(symbol, interval),
        getRecommendation(symbol, interval)
      ]);
      setPredictions(predictionResult);
      setRecommendation(recommendationResult);
    } catch (err) {
      showToast((err as Error).message, "error");
    } finally {
      setLoading(false);
    }
  };

  const actionColor =
    recommendation?.action === "long" ? "success" : recommendation?.action === "short" ? "error" : "default";

  return (
    <Box sx={{ p: { xs: 2, sm: 4 }, display: "flex", flexDirection: "column", gap: 3 }}>
      <PageHeader title="AI Analysis" subtitle="Explainable predictions and recommendations, never a bare buy/sell" />
      <Box sx={{ display: "flex", gap: 2, alignItems: "center", flexWrap: "wrap" }}>
        <TextField
          select
          label="Symbol"
          value={instruments.includes(symbol) ? symbol : ""}
          onChange={(e) => handleSymbolChange(e.target.value)}
          sx={{ minWidth: 160 }}
        >
          {instruments.map((instrument) => (
            <MenuItem key={instrument} value={instrument}>
              {instrument}
            </MenuItem>
          ))}
        </TextField>
        <TextField select label="Interval" value={interval} onChange={(e) => handleIntervalChange(e.target.value)} sx={{ minWidth: 140 }}>
          {INTERVALS.map((value) => (
            <MenuItem key={value} value={value}>
              {value}
            </MenuItem>
          ))}
        </TextField>
        <Button variant="contained" onClick={handleAnalyze} disabled={loading}>
          {loading ? <CircularProgress size={22} color="inherit" /> : "Analyze"}
        </Button>
      </Box>

      <Card>
        <CardContent>
          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 1 }}>
            <Typography variant="subtitle2">
              Model status for {symbol} · {interval}
            </Typography>
            <Button size="small" variant="outlined" onClick={handleTrain} disabled={training}>
              {training ? <CircularProgress size={18} color="inherit" /> : "Train models"}
            </Button>
          </Box>
          <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap", mt: 1 }}>
            {modelStatus?.models.map((model) => (
              <Tooltip
                key={model.model_name}
                title={model.trained ? `Trained at ${model.trained_at}` : "Not trained yet for this symbol/interval"}
              >
                <Chip
                  size="small"
                  icon={model.trained ? <CheckCircleIcon /> : <CancelIcon />}
                  label={model.model_name.replace(/_/g, " ")}
                  color={model.trained ? "success" : "default"}
                  variant={model.trained ? "filled" : "outlined"}
                />
              </Tooltip>
            ))}
          </Box>
          {modelStatus && !modelStatus.all_trained && (
            <Typography variant="caption" color="text.secondary" sx={{ display: "block", mt: 1 }}>
              Not all models are trained yet for this symbol and interval. Training requires an admin account and a
              verified email.
            </Typography>
          )}
        </CardContent>
      </Card>

      {recommendation && (
        <Card sx={{ borderLeft: "4px solid", borderLeftColor: actionColor === "default" ? "divider" : `${actionColor}.main` }}>
          <CardContent sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
            <Box sx={{ display: "flex", gap: 2, alignItems: "center", flexWrap: "wrap" }}>
              <Typography variant="h5">Recommendation</Typography>
              <Chip label={recommendation.action.toUpperCase()} color={actionColor} />
              <Chip label={`${(recommendation.confidence * 100).toFixed(0)}% confidence`} variant="outlined" />
              <Chip label={`risk: ${recommendation.risk_level}`} variant="outlined" />
              <Chip label={`regime: ${recommendation.market_regime}`} variant="outlined" />
            </Box>
            <Typography variant="body1">{recommendation.reasoning}</Typography>
            <Divider sx={{ my: 1 }} />
            <Typography variant="subtitle2">Supporting indicators</Typography>
            <List dense>
              {recommendation.supporting_indicators.map((item) => (
                <ListItem key={item} disableGutters>
                  <ListItemText primary={item} />
                </ListItem>
              ))}
            </List>
            <Typography variant="subtitle2">Alternative scenarios</Typography>
            <List dense>
              {recommendation.alternative_scenarios.map((item) => (
                <ListItem key={item} disableGutters>
                  <ListItemText primary={item} />
                </ListItem>
              ))}
            </List>
            <Typography variant="subtitle2">Invalidation conditions</Typography>
            <List dense>
              {recommendation.invalidation_conditions.map((item) => (
                <ListItem key={item} disableGutters>
                  <ListItemText primary={item} />
                </ListItem>
              ))}
            </List>
            <Alert severity="info" sx={{ borderRadius: 2 }}>
              {recommendation.disclaimer}
            </Alert>
          </CardContent>
        </Card>
      )}

      {predictions && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Raw model predictions
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {predictions.note}
            </Typography>
            {predictions.predictions.map((prediction) => (
              <Box key={prediction.model_name} sx={{ mb: 1 }}>
                <Typography variant="subtitle2">{prediction.model_name}</Typography>
                <Typography variant="body2" component="pre" sx={{ whiteSpace: "pre-wrap", fontFamily: "monospace", fontSize: 12 }}>
                  {JSON.stringify(prediction.output, null, 2)}
                </Typography>
              </Box>
            ))}
          </CardContent>
        </Card>
      )}
    </Box>
  );
}