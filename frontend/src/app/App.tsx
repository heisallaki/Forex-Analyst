import { ThemeProvider, CssBaseline } from "@mui/material";
import { createAppTheme } from "@/app/theme";
import { useThemeStore } from "@/app/theme/themeStore";
import { AppRouter } from "@/app/AppRouter";
import { ToastProvider } from "@/shared/ui/ToastProvider";
import { ErrorBoundary } from "@/app/ErrorBoundary";

export default function App() {
  const effectiveMode = useThemeStore((state) => state.effectiveMode());
  const accentColor = useThemeStore((state) => state.accentColor);
  const theme = createAppTheme(effectiveMode, accentColor);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <ErrorBoundary>
        <ToastProvider>
          <AppRouter />
        </ToastProvider>
      </ErrorBoundary>
    </ThemeProvider>
  );
}