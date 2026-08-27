import { AppBar, Toolbar, Typography, Button, Box, Drawer, List, ListItemButton, ListItemText } from "@mui/material";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuthStore } from "@/features/auth/store/authStore";
import { logout as logoutRequest } from "@/features/auth/api/authApi";

const DRAWER_WIDTH = 220;

const NAV_ITEMS = [
  { label: "Dashboard", path: "/" },
  { label: "Markets", path: "/markets" },
  { label: "Charts", path: "/charts" },
  { label: "AI Analysis", path: "/ai" },
  { label: "Signals", path: "/signals" },
  { label: "Strategies", path: "/strategies" },
  { label: "Backtesting", path: "/backtest" },
  { label: "Paper Trading", path: "/paper" },
  { label: "Analytics", path: "/analytics" },
  { label: "Settings", path: "/settings" }
];

export function AppLayout() {
  const { user, refreshToken, clearSession } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    if (refreshToken) {
      await logoutRequest(refreshToken).catch(() => undefined);
    }
    clearSession();
    navigate("/login");
  };

  return (
    <Box sx={{ display: "flex" }}>
      <Drawer
        variant="permanent"
        sx={{
          width: DRAWER_WIDTH,
          flexShrink: 0,
          "& .MuiDrawer-paper": { width: DRAWER_WIDTH, boxSizing: "border-box" }
        }}
      >
        <Toolbar>
          <Typography variant="h6">Forex Analyst</Typography>
        </Toolbar>
        <List>
          {NAV_ITEMS.map((item) => (
            <ListItemButton key={item.path} selected={location.pathname === item.path} onClick={() => navigate(item.path)}>
              <ListItemText primary={item.label} />
            </ListItemButton>
          ))}
        </List>
      </Drawer>
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar sx={{ justifyContent: "flex-end", gap: 2 }}>
            {user && <Typography variant="body2">{user.full_name}</Typography>}
            {user && (
              <Button color="inherit" onClick={handleLogout}>
                Logout
              </Button>
            )}
          </Toolbar>
        </AppBar>
        <Outlet />
      </Box>
    </Box>
  );
}