import { Box, Card, CardContent } from "@mui/material";
import { RegisterForm } from "@/features/auth/components/RegisterForm";

export function RegisterPage() {
  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        p: 2,
        bgcolor: "background.default",
        backgroundImage: (theme) =>
          theme.palette.mode === "dark"
            ? "radial-gradient(circle at 85% 20%, rgba(34,197,94,0.18), transparent 40%), radial-gradient(circle at 15% 80%, rgba(239,68,68,0.18), transparent 40%)"
            : "radial-gradient(circle at 85% 20%, rgba(34,197,94,0.12), transparent 40%), radial-gradient(circle at 15% 80%, rgba(239,68,68,0.12), transparent 40%)"
      }}
    >
      <Card sx={{ width: "100%", maxWidth: 420 }}>
        <CardContent sx={{ p: { xs: 3, sm: 5 }, display: "flex", justifyContent: "center" }}>
          <RegisterForm />
        </CardContent>
      </Card>
    </Box>
  );
}