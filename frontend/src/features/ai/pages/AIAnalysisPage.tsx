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
  Alert,
  CircularProgress,
  Divider,
  List,
  ListItem,
  ListItemText
} from "@mui/material";
import {
  PredictMarketResponse,
  RecommendationResponse,
  getPredictions,
  getRecommendation
} from "@/features/ai/api/aiApi";

const INTERVALS = ["1min", "5min", "15min", "1h", "1day"];

export function AIAnalysisPage() {
  const [symbol, setSymbol] = useState("EUR/USD");
  const [interval, setInterval] = useState("1min");
  const [predictions, setPredictions] = useState<PredictMarketResponse | null>(null);
  const [recommendation, setRecommendation] = useState<RecommendationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
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
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 4, display: "flex", flexDirection: "column", gap: 3 }}>
      <Typography variant="h4">AI Analysis</Typography>
      <Box sx={{ display: "flex", gap: 2, alignItems: "center" }}>
        <TextField label="Symbol" value={symbol} onChange={(e) => setSymbol(e.target.value)} sx={{ minWidth: 160 }} />
        <TextField select label="Interval" value={interval} onChange={(e) => setInterval(e.target.value)} sx={{ minWidth: 140 }}>
          {INTERVALS.map((value) => (
            <MenuItem key={value} value={value}>
              {value}
            </MenuItem>
          ))}
        </TextField>
        <Button variant="contained" onClick={handleAnalyze} disabled={loading}>
          Analyze
        </Button>
      </Box>
      {loading && <CircularProgress />}
      {error && <Alert severity="error">{error}</Alert>}

      {recommendation && (
        <Card>
          <CardContent sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
            <Box sx={{ display: "flex", gap: 2, alignItems: "center", flexWrap: "wrap" }}>
              <Typography variant="h5">Recommendation</Typography>
              <Chip
                label={recommendation.action.toUpperCase()}
                color={
                  recommendation.action === "long" ? "success" : recommendation.action === "short" ? "error" : "default"
                }
              />
              <Chip label={`${(recommendation.confidence * 100).toFixed(0)}% confidence`} variant="outlined" />
              <Chip label={`risk: ${recommendation.risk_level}`} variant="outlined" />
              <Chip label={`regime: ${recommendation.market_regime}`} variant="outlined" />
            </Box>
            <Typography variant="body1">{recommendation.reasoning}</Typography>
            <Divider sx={{ my: 1 }} />
            <Typography variant="subtitle2">Supporting indicators</Typography>
            <List dense>
              {recommendation.supporting_indicators.map((item) => (
                <ListItem key={item}>
                  <ListItemText primary={item} />
                </ListItem>
              ))}
            </List>
            <Typography variant="subtitle2">Alternative scenarios</Typography>
            <List dense>
              {recommendation.alternative_scenarios.map((item) => (
                <ListItem key={item}>
                  <ListItemText primary={item} />
                </ListItem>
              ))}
            </List>
            <Typography variant="subtitle2">Invalidation conditions</Typography>
            <List dense>
              {recommendation.invalidation_conditions.map((item) => (
                <ListItem key={item}>
                  <ListItemText primary={item} />
                </ListItem>
              ))}
            </List>
            <Alert severity="info">{recommendation.disclaimer}</Alert>
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
                <Typography variant="body2" component="pre" sx={{ whiteSpace: "pre-wrap" }}>
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