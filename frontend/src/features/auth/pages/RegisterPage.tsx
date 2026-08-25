import { Box } from "@mui/material";
import { RegisterForm } from "@/features/auth/components/RegisterForm";

export function RegisterPage() {
  return (
    <Box sx={{ display: "flex", justifyContent: "center", pt: 8 }}>
      <RegisterForm />
    </Box>
  );
}