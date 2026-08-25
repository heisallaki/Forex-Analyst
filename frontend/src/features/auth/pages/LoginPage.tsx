import { Box } from "@mui/material";
import { LoginForm } from "@/features/auth/components/LoginForm";

export function LoginPage() {
  return (
    <Box sx={{ display: "flex", justifyContent: "center", pt: 8 }}>
      <LoginForm />
    </Box>
  );
}