import { useState } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  CircularProgress,
  Alert
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import { forgotPassword, resetPassword } from "@/features/auth/api/authApi";
import { PasswordField } from "@/shared/ui/PasswordField";
import { useToast } from "@/shared/ui/useToast";
import TextField from "@mui/material/TextField";

export function ForgotPasswordPage() {
  const [step, setStep] = useState<"request" | "reset">("request");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { showToast } = useToast();

  const handleRequest = async () => {
    setLoading(true);
    try {
      const response = await forgotPassword(email);
      showToast(response.message, "info");
      setStep("reset");
    } catch (err) {
      showToast((err as Error).message, "error");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    setLoading(true);
    try {
      await resetPassword(email, code, newPassword);
      showToast("Password reset. Please log in.", "success");
      navigate("/login");
    } catch (err) {
      showToast((err as Error).message, "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        p: 2,
        bgcolor: "background.default"
      }}
    >
      <Card sx={{ width: "100%", maxWidth: 420 }}>
        <CardContent sx={{ p: { xs: 3, sm: 5 } }}>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2.5 }}>
            <Box>
              <Typography variant="h4" sx={{ fontWeight: 700 }}>
                Reset your password
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                {step === "request"
                  ? "Enter your account email to receive a reset code"
                  : "Enter the code we sent and choose a new password"}
              </Typography>
            </Box>

            {step === "request" ? (
              <>
                <TextField
                  label="Email"
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
                <Button variant="contained" size="large" onClick={handleRequest} disabled={loading || !email} sx={{ py: 1.3 }}>
                  {loading ? <CircularProgress size={22} color="inherit" /> : "Send reset code"}
                </Button>
              </>
            ) : (
              <>
                <Alert severity="info">Codes expire after 10 minutes.</Alert>
                <TextField
                  label="Reset code"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  inputProps={{ maxLength: 6 }}
                />
                <PasswordField
                  label="New password"
                  autoComplete="new-password"
                  showStrength
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                />
                <Button
                  variant="contained"
                  size="large"
                  onClick={handleReset}
                  disabled={loading || code.length !== 6 || newPassword.length < 8}
                  sx={{ py: 1.3 }}
                >
                  {loading ? <CircularProgress size={22} color="inherit" /> : "Reset password"}
                </Button>
                <Button variant="text" onClick={() => setStep("request")}>
                  Didn't get a code? Try again
                </Button>
              </>
            )}

            <Typography variant="body2" color="text.secondary" sx={{ textAlign: "center" }}>
              Remembered it?{" "}
              <Box component="span" onClick={() => navigate("/login")} sx={{ color: "primary.main", cursor: "pointer", fontWeight: 600 }}>
                Back to sign in
              </Box>
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}