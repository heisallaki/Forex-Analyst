import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Box, Button, TextField, Typography, Alert, MenuItem } from "@mui/material";
import { register as registerUser } from "@/features/auth/api/authApi";
import { useAuthStore } from "@/features/auth/store/authStore";
import { useNavigate } from "react-router-dom";

const registerSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  full_name: z.string().min(1),
  role: z.enum(["admin", "analyst", "viewer"])
});

type RegisterFormValues = z.infer<typeof registerSchema>;

export function RegisterForm() {
  const {
    register: registerField,
    handleSubmit,
    formState: { errors }
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: { role: "viewer" }
  });
  const setSession = useAuthStore((state) => state.setSession);
  const navigate = useNavigate();
  const [serverError, setServerError] = useState<string | null>(null);

  const onSubmit = async (values: RegisterFormValues) => {
    setServerError(null);
    try {
      const response = await registerUser(values);
      setSession(response.user, response.access_token, response.refresh_token);
      navigate("/");
    } catch (error) {
      setServerError((error as Error).message);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ display: "flex", flexDirection: "column", gap: 2, maxWidth: 360 }}>
      <Typography variant="h5">Create account</Typography>
      {serverError && <Alert severity="error">{serverError}</Alert>}
      <TextField
        label="Full name"
        error={!!errors.full_name}
        helperText={errors.full_name?.message}
        {...registerField("full_name")}
      />
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
      <TextField label="Role" select defaultValue="viewer" {...registerField("role")}>
        <MenuItem value="viewer">Viewer</MenuItem>
        <MenuItem value="analyst">Analyst</MenuItem>
        <MenuItem value="admin">Admin</MenuItem>
      </TextField>
      <Button type="submit" variant="contained">
        Create account
      </Button>
    </Box>
  );
}