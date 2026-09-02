import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Box, Button, TextField, Typography, MenuItem, CircularProgress } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { register as registerUser } from "@/features/auth/api/authApi";
import { useAuthStore } from "@/features/auth/store/authStore";
import { PasswordField } from "@/shared/ui/PasswordField";
import { useToast } from "@/shared/ui/useToast";

const registerSchema = z.object({
  email: z.string().email("Enter a valid email address"),
  password: z.string().min(8, "At least 8 characters"),
  full_name: z.string().min(1, "Full name is required"),
  role: z.enum(["admin", "analyst", "viewer"])
});

type RegisterFormValues = z.infer<typeof registerSchema>;

export function RegisterForm() {
  const {
    register: registerField,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting }
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: { email: "", password: "", full_name: "", role: "viewer" }
  });
  const setSession = useAuthStore((state) => state.setSession);
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [success, setSuccess] = useState(false);
  const passwordValue = watch("password");

  const onSubmit = async (values: RegisterFormValues) => {
    try {
      const response = await registerUser(values);
      setSession(response.user, response.access_token, response.refresh_token);
      setSuccess(true);
      showToast("Account created successfully", "success");
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
          Create your account
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
          Start analyzing forex and gold with explainable AI
        </Typography>
      </Box>
      <TextField
        label="Full name"
        autoComplete="name"
        error={!!errors.full_name}
        helperText={errors.full_name?.message}
        {...registerField("full_name")}
      />
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
        autoComplete="new-password"
        showStrength
        error={!!errors.password}
        helperText={errors.password?.message}
        value={passwordValue || ""}
        {...registerField("password")}
      />
      <TextField label="Role" select defaultValue="viewer" {...registerField("role")}>
        <MenuItem value="viewer">Viewer</MenuItem>
        <MenuItem value="analyst">Analyst</MenuItem>
        <MenuItem value="admin">Admin</MenuItem>
      </TextField>
      <Button type="submit" variant="contained" color="primary" size="large" disabled={isSubmitting || success} sx={{ py: 1.3 }}>
        {isSubmitting ? <CircularProgress size={22} color="inherit" /> : success ? "Account created ✅" : "Create account"}
      </Button>
      <Typography variant="body2" color="text.secondary" sx={{ textAlign: "center" }}>
        Already have an account?{" "}
        <Box component="span" onClick={() => navigate("/login")} sx={{ color: "primary.main", cursor: "pointer", fontWeight: 600 }}>
          Sign in
        </Box>
      </Typography>
    </Box>
  );
}