import { createTheme, ThemeProvider, CssBaseline } from "@mui/material";

const theme = createTheme();

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
    </ThemeProvider>
  );
}