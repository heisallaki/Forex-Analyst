import { Box, Typography, Button, useTheme, alpha } from "@mui/material";
import HomeIcon from "@mui/icons-material/Home";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/features/auth/store/authStore";

export function NotFoundPage() {
  const navigate = useNavigate();
  const theme = useTheme();
  const isDark = theme.palette.mode === "dark";
  const isAuthenticated = !!useAuthStore((state) => state.accessToken);
  const primaryMain = theme.palette.primary.main;
  const primaryLight = theme.palette.primary.light;

  return (
    <Box
      sx={{
        minHeight: "100vh",
        width: "100%",
        position: "relative",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        overflow: "hidden",
        bgcolor: "background.default",
        p: 2
      }}
    >
      <Box
        aria-hidden
        sx={{
          position: "absolute",
          inset: 0,
          opacity: isDark ? 0.35 : 0.22,
          filter: "blur(6px)",
          backgroundImage:
            "repeating-linear-gradient(90deg, transparent 0 46px, rgba(34,197,94,0.55) 46px 52px, transparent 52px 98px, rgba(239,68,68,0.5) 98px 104px, transparent 104px 150px)",
          backgroundSize: "150px 100%",
          maskImage: "linear-gradient(to bottom, transparent, black 30%, black 70%, transparent)",
          WebkitMaskImage: "linear-gradient(to bottom, transparent, black 30%, black 70%, transparent)"
        }}
      />
      <Box
        aria-hidden
        sx={{
          position: "absolute",
          inset: 0,
          background:
            `radial-gradient(circle at 20% 30%, ${alpha(primaryMain, isDark ? 0.18 : 0.1)}, transparent 45%), ` +
            `radial-gradient(circle at 80% 70%, ${alpha("#22c55e", isDark ? 0.14 : 0.08)}, transparent 45%)`
        }}
      />

      <Box
        sx={{
          position: "relative",
          textAlign: "center",
          maxWidth: 460,
          px: { xs: 3, sm: 5 },
          py: { xs: 4, sm: 6 },
          borderRadius: 4,
          backgroundColor: isDark ? "rgba(22, 27, 38, 0.6)" : "rgba(255, 255, 255, 0.75)",
          backdropFilter: "blur(20px)",
          WebkitBackdropFilter: "blur(20px)",
          border: `1px solid ${alpha(primaryMain, isDark ? 0.25 : 0.15)}`,
          boxShadow: `0 12px 48px ${alpha(primaryMain, isDark ? 0.25 : 0.12)}`
        }}
      >
        <Typography
          sx={{
            fontSize: { xs: "4.5rem", sm: "6rem" },
            fontWeight: 800,
            lineHeight: 1,
            letterSpacing: "-0.02em",
            backgroundImage: `linear-gradient(135deg, ${primaryMain} 0%, ${primaryLight} 100%)`,
            backgroundClip: "text",
            WebkitBackgroundClip: "text",
            color: "transparent"
          }}
        >
          404
        </Typography>
        <Typography variant="h5" sx={{ fontWeight: 700, mt: 2 }}>
          Page not found
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1, mb: 4 }}>
          The page you're looking for doesn't exist or may have moved.
        </Typography>
        <Button
          variant="contained"
          size="large"
          startIcon={<HomeIcon />}
          onClick={() => navigate(isAuthenticated ? "/" : "/login")}
          sx={{ px: 4, py: 1.3 }}
        >
          {isAuthenticated ? "Back to Dashboard" : "Back to Login"}
        </Button>
      </Box>
    </Box>
  );
}