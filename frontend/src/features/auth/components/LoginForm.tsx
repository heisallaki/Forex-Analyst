import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Box, Button, TextField, Typography, Alert } from "@mui/material";
import { login } from "@/features/auth/api/authApi";
import { useAuthStore } from "@/features/auth/store/authStore";
import { useNavigate } from "react-router-dom";

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(1)
});

type LoginFormValues = z.infer<typeof loginSchema>;

export function LoginForm() {
  const {
    register: registerField,
    handleSubmit,
    formState: { errors }
  } = useForm<LoginFormValues>({ resolver: zodResolver(loginSchema) });
  const setSession = useAuthStore((state) => state.setSession);
  const navigate = useNavigate();
  const [serverError, setServerError] = useState<string | null>(null);

  const onSubmit = async (values: LoginFormValues) => {
    setServerError(null);
    try {
      const response = await login(values);
      setSession(response.user, response.access_token, response.refresh_token);
      navigate("/");
    } catch (error) {
      setServerError((error as Error).message);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ display: "flex", flexDirection: "column", gap: 2, maxWidth: 360 }}>
      <Typography variant="h5">Sign in</Typography>
      {serverError && <Alert severity="error">{serverError}</Alert>}
      <TextField
        label="Email"
        type="email"
        error={!!errors.email}
        helperText={errors.email?.message}
        {...registerField("email")}
      />
      <TextField
        label="Password"
        type="password"
        error={!!errors.password}
        helperText={errors.password?.message}
        {...registerField("password")}
      />
      <Button type="submit" variant="contained">
        Sign in
      </Button>
    </Box>
  );
}