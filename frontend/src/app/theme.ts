import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    mode: "dark",
    primary: { main: "#2196f3" },
    background: { default: "#0d1117", paper: "#161b22" }
  },
  typography: {
    fontFamily: "Inter, Roboto, Arial, sans-serif"
  }
});