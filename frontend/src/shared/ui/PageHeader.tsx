import { ReactNode } from "react";
import { Box, Typography, alpha, useTheme } from "@mui/material";

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  action?: ReactNode;
}

export function PageHeader({ title, subtitle, action }: PageHeaderProps) {
  const theme = useTheme();
  const isDark = theme.palette.mode === "dark";
  const primaryMain = theme.palette.primary.main;
  const primaryLight = theme.palette.primary.light;

  return (
    <Box
      sx={{
        position: "relative",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: 2,
        flexWrap: "wrap",
        px: { xs: 2.5, sm: 3.5 },
        py: { xs: 2, sm: 2.5 },
        mb: { xs: 2, sm: 3 },
        borderRadius: 4,
        overflow: "hidden",
        backgroundColor: isDark ? alpha(primaryMain, 0.1) : alpha(primaryMain, 0.06),
        backdropFilter: "blur(20px)",
        WebkitBackdropFilter: "blur(20px)",
        border: `1px solid ${alpha(primaryMain, isDark ? 0.28 : 0.18)}`,
        boxShadow: `0 8px 32px ${alpha(primaryMain, isDark ? 0.22 : 0.12)}`,
        transition: "box-shadow 220ms ease, transform 220ms ease, border-color 220ms ease",
        "&:hover": {
          boxShadow: `0 12px 40px ${alpha(primaryMain, isDark ? 0.32 : 0.18)}`,
          borderColor: alpha(primaryMain, isDark ? 0.4 : 0.28),
          transform: "translateY(-1px)"
        },
        "&::before": {
          content: '""',
          position: "absolute",
          inset: 0,
          background: `linear-gradient(120deg, ${alpha(primaryMain, isDark ? 0.16 : 0.08)} 0%, transparent 60%)`,
          pointerEvents: "none"
        }
      }}
    >
      <Box sx={{ position: "relative", minWidth: 0 }}>
        <Typography
          variant="h4"
          sx={{
            fontWeight: 700,
            letterSpacing: "-0.01em",
            backgroundImage: `linear-gradient(135deg, ${primaryMain} 0%, ${primaryLight} 100%)`,
            backgroundClip: "text",
            WebkitBackgroundClip: "text",
            color: "transparent",
            fontSize: { xs: "1.5rem", sm: "1.85rem" }
          }}
        >
          {title}
        </Typography>
        {subtitle && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            {subtitle}
          </Typography>
        )}
      </Box>
      {action && (
        <Box sx={{ position: "relative", flexShrink: 0 }}>
          {action}
        </Box>
      )}
    </Box>
  );
}