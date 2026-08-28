import { useState } from "react";
import {
  Box,
  Typography,
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
  Alert
} from "@mui/material";
import { PredictMarketResponse, RecommendationResponse, getPredictions, getRecommendation } from "@/features/ai/api/aiApi";
import { useToast } from "@/shared/ui/ToastProvider";

const INTERVALS = ["1min", "5min", "15min", "1h", "1day"];

export function AIAnalysisPage() {
  const [symbol, setSymbol] = useState("EUR/USD");
  const [interval, setInterval] = useState("1min");
  const [predictions, setPredictions] = useState<PredictMarketResponse | null>(null);
  const [recommendation, setRecommendation] = useState<RecommendationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const { showToast } = useToast();

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
      <Typography variant="h4">AI Analysis</Typography>
      <Box sx={{ display: "flex", gap: 2, alignItems: "center", flexWrap: "wrap" }}>
        <TextField label="Symbol" value={symbol} onChange={(e) => setSymbol(e.target.value)} sx={{ minWidth: 160 }} />
        <TextField select label="Interval" value={interval} onChange={(e) => setInterval(e.target.value)} sx={{ minWidth: 140 }}>
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