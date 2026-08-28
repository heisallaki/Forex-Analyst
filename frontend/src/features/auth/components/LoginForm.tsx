import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Box, Button, TextField, Typography, CircularProgress } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { login } from "@/features/auth/api/authApi";
import { useAuthStore } from "@/features/auth/store/authStore";
import { PasswordField } from "@/shared/ui/PasswordField";
import { useToast } from "@/shared/ui/ToastProvider";

const loginSchema = z.object({
  email: z.string().email("Enter a valid email address"),
  password: z.string().min(1, "Password is required")
});

type LoginFormValues = z.infer<typeof loginSchema>;

export function LoginForm() {
  const {
    register: registerField,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting }
  } = useForm<LoginFormValues>({ resolver: zodResolver(loginSchema), defaultValues: { email: "", password: "" } });
  const setSession = useAuthStore((state) => state.setSession);
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [success, setSuccess] = useState(false);
  const passwordValue = watch("password");

  const onSubmit = async (values: LoginFormValues) => {
    try {
      const response = await login(values);
      setSession(response.user, response.access_token, response.refresh_token);
      setSuccess(true);
      showToast(`Welcome back, ${response.user.full_name.split(" ")[0]}`, "success");
      navigate("/");
    } catch (error) {
      showToast((error as Error).message, "error");
    }
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit(onSubmit)}
      noValidate
      sx={{ display: "flex", flexDirection: "column", gap: 2.5, width: "100%", maxWidth: 380 }}
    >
      <Box>
        <Typography variant="h4" sx={{ fontWeight: 700 }}>
          Welcome back
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
          Sign in to continue to your trading analyst
        </Typography>
      </Box>
      <TextField
        label="Email"
        type="email"
        autoComplete="email"
        error={!!errors.email}
        helperText={errors.email?.message}
        {...registerField("email")}
      />
      <PasswordField
        label="Password"
        autoComplete="current-password"
        error={!!errors.password}
        helperText={errors.password?.message}
        value={passwordValue || ""}
        {...registerField("password")}
      />
      <Button type="submit" variant="contained" color="primary" size="large" disabled={isSubmitting || success} sx={{ py: 1.3 }}>
        {isSubmitting ? <CircularProgress size={22} color="inherit" /> : success ? "Signed in ✅" : "Sign in"}
      </Button>
      <Typography variant="body2" color="text.secondary" sx={{ textAlign: "center" }}>
        Don't have an account?{" "}
        <Box component="span" onClick={() => navigate("/register")} sx={{ color: "primary.main", cursor: "pointer", fontWeight: 600 }}>
          Create one
        </Box>
      </Typography>
    </Box>
  );
}