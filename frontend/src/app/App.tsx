import { ThemeProvider, CssBaseline } from "@mui/material";
import { createAppTheme } from "@/app/theme";
import { useThemeStore } from "@/app/theme/themeStore";
import { AppRouter } from "@/app/AppRouter";
import { ToastProvider } from "@/shared/ui/ToastProvider";

export default function App() {
  const mode = useThemeStore((state) => state.mode);
  const theme = createAppTheme(mode);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <ToastProvider>
        <AppRouter />
      </ToastProvider>
    </ThemeProvider>
  );
}