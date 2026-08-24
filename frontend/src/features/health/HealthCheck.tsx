import { useEffect, useState } from "react";
import { Box, Typography, Chip } from "@mui/material";
import { httpGet } from "../../shared/api/httpClient";

interface HealthResponse {
  status: string;
}

export function HealthCheck() {
  const [status, setStatus] = useState<string>("checking");

  useEffect(() => {
    httpGet<HealthResponse>("/health")
      .then((data) => setStatus(data.status))
      .catch(() => setStatus("unreachable"));
  }, []);

  return (
    <Box sx={{ p: 4 }}>
      <Typography variant="h4" gutterBottom>
        Forex Trading Analyst
      </Typography>
      <Chip
        label={`Backend status: ${status}`}
        color={status === "ok" ? "success" : "warning"}
      />
    </Box>
  );
}