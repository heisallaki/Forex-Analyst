import { ThemeProvider, CssBaseline } from "@mui/material";
import { theme } from "@/app/theme";
import { AppRouter } from "@/app/AppRouter";

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppRouter />
    </ThemeProvider>
  );
}