import { Suspense, useState } from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  Drawer,
  List,
  ListItemButton,
  ListItemText,
  IconButton,
  useMediaQuery,
  useTheme,
  Tooltip,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  ListItemIcon
} from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import LightModeIcon from "@mui/icons-material/LightMode";
import DarkModeIcon from "@mui/icons-material/DarkMode";
import SettingsIcon from "@mui/icons-material/Settings";
import LogoutIcon from "@mui/icons-material/Logout";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuthStore } from "@/features/auth/store/authStore";
import { logout as logoutRequest } from "@/features/auth/api/authApi";
import { useThemeStore } from "@/app/theme/themeStore";
import { PageLoadingSkeleton } from "@/shared/ui/PageLoadingSkeleton";

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
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleLogout = async () => {
    setAnchorEl(null);
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

  const initials = user?.full_name
    ? user.full_name
        .split(" ")
        .map((part) => part[0])
        .slice(0, 2)
        .join("")
        .toUpperCase()
    : "?";

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
              <>
                <Tooltip title={user.full_name}>
                  <IconButton onClick={(e) => setAnchorEl(e.currentTarget)} aria-label="Account menu" sx={{ p: 0.5 }}>
                    <Avatar
                      sx={{
                        width: 36,
                        height: 36,
                        fontSize: 14,
                        fontWeight: 700,
                        backgroundImage: `linear-gradient(135deg, ${theme.palette.primary.dark} 0%, ${theme.palette.primary.light} 100%)`,
                        border: "2px solid",
                        borderColor: "background.paper",
                        boxShadow: `0 0 0 1px ${theme.palette.primary.main}66`,
                        transition: "transform 160ms ease, box-shadow 160ms ease",
                        "&:hover": { transform: "scale(1.06)", boxShadow: `0 0 0 3px ${theme.palette.primary.main}55` }
                      }}
                    >
                      {initials}
                    </Avatar>
                  </IconButton>
                </Tooltip>
                <Menu anchorEl={anchorEl} open={!!anchorEl} onClose={() => setAnchorEl(null)}>
                  <Box sx={{ px: 2, py: 1, minWidth: 200 }}>
                    <Typography variant="subtitle2">{user.full_name}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {user.email}
                    </Typography>
                  </Box>
                  <Divider />
                  <MenuItem
                    onClick={() => {
                      setAnchorEl(null);
                      navigate("/settings");
                    }}
                  >
                    <ListItemIcon>
                      <SettingsIcon fontSize="small" />
                    </ListItemIcon>
                    Settings
                  </MenuItem>
                  <MenuItem onClick={handleLogout}>
                    <ListItemIcon>
                      <LogoutIcon fontSize="small" />
                    </ListItemIcon>
                    Logout
                  </MenuItem>
                </Menu>
              </>
            )}
          </Toolbar>
        </AppBar>
        <Box sx={{ maxWidth: "100vw", overflowX: "hidden" }}>
          <Suspense fallback={<PageLoadingSkeleton />}>
            <Outlet />
          </Suspense>
        </Box>
      </Box>
    </Box>
  );
}