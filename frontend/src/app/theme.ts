import { createTheme, Theme } from "@mui/material/styles";

export type AppThemeMode = "light" | "dark";
export type AccentColorKey = "blue" | "purple" | "green" | "orange" | "yellow" | "red" | "pink" | "cyan";

interface AccentDefinition {
  key: AccentColorKey;
  label: string;
  main: string;
  light: string;
  dark: string;
}

export const ACCENT_COLOR_OPTIONS: AccentDefinition[] = [
  { key: "blue", label: "Blue", main: "#3b82f6", light: "#60a5fa", dark: "#2563eb" },
  { key: "purple", label: "Purple", main: "#8b5cf6", light: "#a78bfa", dark: "#7c3aed" },
  { key: "green", label: "Green", main: "#10b981", light: "#34d399", dark: "#059669" },
  { key: "orange", label: "Orange", main: "#f97316", light: "#fb923c", dark: "#ea580c" },
  { key: "yellow", label: "Yellow", main: "#eab308", light: "#facc15", dark: "#ca8a04" },
  { key: "red", label: "Red", main: "#ef4444", light: "#f87171", dark: "#dc2626" },
  { key: "pink", label: "Pink", main: "#ec4899", light: "#f472b6", dark: "#db2777" },
  { key: "cyan", label: "Cyan", main: "#06b6d4", light: "#22d3ee", dark: "#0891b2" }
];

function getAccent(key: AccentColorKey): AccentDefinition {
  return ACCENT_COLOR_OPTIONS.find((option) => option.key === key) ?? ACCENT_COLOR_OPTIONS[0];
}

const bullishGradient = "linear-gradient(135deg, #16a34a 0%, #22c55e 100%)";
const bearishGradient = "linear-gradient(135deg, #dc2626 0%, #ef4444 100%)";

export function createAppTheme(mode: AppThemeMode, accentColor: AccentColorKey): Theme {
  const isDark = mode === "dark";
  const accent = getAccent(accentColor);
  const primaryGradient = `linear-gradient(135deg, ${accent.dark} 0%, ${accent.light} 100%)`;

  return createTheme({
    palette: {
      mode,
      primary: { main: accent.main, light: accent.light, dark: accent.dark },
      success: { main: "#22c55e", dark: "#16a34a", light: "#4ade80" },
      error: { main: "#ef4444", dark: "#dc2626", light: "#f87171" },
      warning: { main: "#f59e0b" },
      background: {
        default: isDark ? "#0b0f17" : "#f4f6fb",
        paper: isDark ? "rgba(22, 27, 38, 0.72)" : "rgba(255, 255, 255, 0.78)"
      },
      text: {
        primary: isDark ? "#e6e9f0" : "#1a1f2b",
        secondary: isDark ? "#9aa4b8" : "#5b6479"
      }
    },
    shape: { borderRadius: 14 },
    typography: {
      fontFamily: "Inter, -apple-system, BlinkMacSystemFont, Roboto, Arial, sans-serif",
      h4: { fontWeight: 700 },
      h5: { fontWeight: 700 },
      h6: { fontWeight: 600 }
    },
    components: {
      MuiCssBaseline: {
        styleOverrides: `
          @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
              animation-duration: 0.001ms !important;
              animation-iteration-count: 1 !important;
              transition-duration: 0.001ms !important;
              scroll-behavior: auto !important;
            }
          }
          :focus-visible {
            outline: 2px solid ${accent.main};
            outline-offset: 2px;
          }
          html { scroll-behavior: smooth; }
          body { overflow-x: hidden; }
        `
      },
      MuiPaper: {
        styleOverrides: {
          root: { backgroundImage: "none" }
        }
      },
      MuiCard: {
        styleOverrides: {
          root: {
            backgroundColor: isDark ? "rgba(22, 27, 38, 0.6)" : "rgba(255, 255, 255, 0.7)",
            backdropFilter: "blur(16px)",
            WebkitBackdropFilter: "blur(16px)",
            border: isDark ? "1px solid rgba(255,255,255,0.08)" : "1px solid rgba(15,23,42,0.06)",
            borderRadius: 16,
            boxShadow: isDark ? "0 8px 32px rgba(0,0,0,0.35)" : "0 8px 32px rgba(15,23,42,0.08)",
            transition: "transform 180ms ease, box-shadow 180ms ease",
            "&:hover": {
              boxShadow: isDark ? "0 12px 40px rgba(0,0,0,0.45)" : "0 12px 40px rgba(15,23,42,0.12)"
            }
          }
        }
      },
      MuiAppBar: {
        styleOverrides: {
          root: {
            backgroundColor: isDark ? "rgba(11, 15, 23, 0.72)" : "rgba(244, 246, 251, 0.78)",
            backdropFilter: "blur(20px)",
            WebkitBackdropFilter: "blur(20px)",
            boxShadow: "none",
            borderBottom: isDark ? "1px solid rgba(255,255,255,0.06)" : "1px solid rgba(15,23,42,0.06)",
            color: isDark ? "#e6e9f0" : "#1a1f2b"
          }
        }
      },
      MuiDrawer: {
        styleOverrides: {
          paper: {
            backgroundColor: isDark ? "rgba(11, 15, 23, 0.85)" : "rgba(255, 255, 255, 0.85)",
            backdropFilter: "blur(20px)",
            WebkitBackdropFilter: "blur(20px)",
            borderRight: isDark ? "1px solid rgba(255,255,255,0.06)" : "1px solid rgba(15,23,42,0.06)"
          }
        }
      },
      MuiButton: {
        styleOverrides: {
          root: {
            textTransform: "none",
            fontWeight: 600,
            borderRadius: 12,
            transition: "transform 140ms ease, box-shadow 140ms ease, filter 140ms ease",
            "&:hover": { transform: "translateY(-1px)" },
            "&:active": { transform: "translateY(0) scale(0.98)" }
          },
          containedSuccess: {
            backgroundImage: bullishGradient,
            boxShadow: "0 4px 16px rgba(34,197,94,0.35)",
            "&:hover": {
              backgroundImage: bullishGradient,
              filter: "brightness(1.08)",
              boxShadow: "0 6px 20px rgba(34,197,94,0.45)"
            }
          },
          containedError: {
            backgroundImage: bearishGradient,
            boxShadow: "0 4px 16px rgba(239,68,68,0.35)",
            "&:hover": {
              backgroundImage: bearishGradient,
              filter: "brightness(1.08)",
              boxShadow: "0 6px 20px rgba(239,68,68,0.45)"
            }
          },
          containedPrimary: {
            backgroundImage: primaryGradient,
            boxShadow: `0 4px 16px ${accent.main}59`,
            "&:hover": {
              backgroundImage: primaryGradient,
              filter: "brightness(1.08)",
              boxShadow: `0 6px 20px ${accent.main}73`
            }
          }
        }
      },
      MuiChip: {
        styleOverrides: {
          root: { borderRadius: 999, fontWeight: 600 },
          colorSuccess: { backgroundImage: bullishGradient, color: "#ffffff" },
          colorError: { backgroundImage: bearishGradient, color: "#ffffff" }
        }
      },
      MuiOutlinedInput: {
        styleOverrides: {
          root: {
            borderRadius: 12,
            transition: "box-shadow 140ms ease",
            "&.Mui-focused": { boxShadow: `0 0 0 3px ${accent.main}40` }
          }
        }
      },
      MuiIconButton: {
        styleOverrides: {
          root: {
            transition: "transform 140ms ease, background-color 140ms ease",
            "&:hover": { transform: "translateY(-1px)" }
          }
        }
      },
      MuiListItemButton: {
        styleOverrides: {
          root: {
            borderRadius: 10,
            marginLeft: 8,
            marginRight: 8,
            marginBottom: 2,
            "&.Mui-selected": {
              backgroundImage: primaryGradient,
              color: "#ffffff",
              "& .MuiListItemText-primary": { fontWeight: 700 },
              "&:hover": { backgroundImage: primaryGradient, filter: "brightness(1.08)" }
            }
          }
        }
      },
      MuiToggleButton: {
        styleOverrides: {
          root: {
            textTransform: "none",
            "&.Mui-selected": {
              backgroundImage: primaryGradient,
              color: "#ffffff",
              "&:hover": { backgroundImage: primaryGradient, filter: "brightness(1.08)" }
            }
          }
        }
      }
    }
  });
}

export const bullishGradientCss = bullishGradient;
export const bearishGradientCss = bearishGradient;