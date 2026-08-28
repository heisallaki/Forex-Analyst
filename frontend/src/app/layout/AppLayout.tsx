import { useState } from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Drawer,
  List,
  ListItemButton,
  ListItemText,
  IconButton,
  useMediaQuery,
  useTheme,
  Tooltip
} from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import LightModeIcon from "@mui/icons-material/LightMode";
import DarkModeIcon from "@mui/icons-material/DarkMode";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuthStore } from "@/features/auth/store/authStore";
import { logout as logoutRequest } from "@/features/auth/api/authApi";
import { useThemeStore } from "@/app/theme/themeStore";

const DRAWER_WIDTH = 240;

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
  const effectiveMode = useThemeStore((state) => state.effectiveMode());
  const toggleMode = useThemeStore((state) => state.toggleMode);
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isDesktop = useMediaQuery(theme.breakpoints.up("md"));
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = async () => {
    if (refreshToken) {
      await logoutRequest(refreshToken).catch(() => undefined);
    }
    clearSession();
    navigate("/login");
  };

  const handleNavigate = (path: string) => {
    navigate(path);
    if (!isDesktop) {
      setMobileOpen(false);
    }
  };

  const navList = (
    <List sx={{ px: 1 }}>
      {NAV_ITEMS.map((item) => (
        <ListItemButton
          key={item.path}
          selected={location.pathname === item.path}
          onClick={() => handleNavigate(item.path)}
        >
          <ListItemText primary={item.label} />
        </ListItemButton>
      ))}
    </List>
  );

  return (
    <Box sx={{ display: "flex" }}>
      {isDesktop ? (
        <Drawer
          variant="permanent"
          sx={{
            width: DRAWER_WIDTH,
            flexShrink: 0,
            "& .MuiDrawer-paper": { width: DRAWER_WIDTH, boxSizing: "border-box" }
          }}
        >
          <Toolbar>
            <Typography variant="h6" sx={{ fontWeight: 700 }}>
              Forex Analyst
            </Typography>
          </Toolbar>
          {navList}
        </Drawer>
      ) : (
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{ "& .MuiDrawer-paper": { width: DRAWER_WIDTH, boxSizing: "border-box" } }}
        >
          <Toolbar>
            <Typography variant="h6" sx={{ fontWeight: 700 }}>
              Forex Analyst
            </Typography>
          </Toolbar>
          {navList}
        </Drawer>
      )}
      <Box sx={{ flexGrow: 1, minWidth: 0 }}>
        <AppBar position="sticky">
          <Toolbar sx={{ gap: 1 }}>
            {!isDesktop && (
              <IconButton aria-label="Open navigation menu" onClick={() => setMobileOpen(true)} edge="start" color="inherit">
                <MenuIcon />
              </IconButton>
            )}
            <Box sx={{ flexGrow: 1 }} />
            <Tooltip title={effectiveMode === "dark" ? "Switch to light mode" : "Switch to dark mode"}>
              <IconButton aria-label="Toggle color mode" onClick={toggleMode} color="inherit">
                {effectiveMode === "dark" ? <LightModeIcon /> : <DarkModeIcon />}
              </IconButton>
            </Tooltip>
            {user && (
              <Typography variant="body2" sx={{ display: { xs: "none", sm: "block" } }}>
                {user.full_name}
              </Typography>
            )}
            {user && (
              <Button color="inherit" onClick={handleLogout}>
                Logout
              </Button>
            )}
          </Toolbar>
        </AppBar>
        <Box sx={{ maxWidth: "100vw", overflowX: "hidden" }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
}