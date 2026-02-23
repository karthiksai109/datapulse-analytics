import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  Box, Drawer, AppBar, Toolbar, Typography, List, ListItem,
  ListItemButton, ListItemIcon, ListItemText, IconButton, Avatar,
  Menu, MenuItem, Divider, Chip,
} from '@mui/material';
import {
  Dashboard as DashboardIcon, Storage, Event, NotificationsActive,
  Assessment, AutoAwesome, Settings, Menu as MenuIcon, Logout,
  Person, ChevronLeft,
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';

const DRAWER_WIDTH = 260;

const navItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
  { text: 'Data Sources', icon: <Storage />, path: '/sources' },
  { text: 'Events', icon: <Event />, path: '/events' },
  { text: 'Alerts', icon: <NotificationsActive />, path: '/alerts' },
  { text: 'Reports', icon: <Assessment />, path: '/reports' },
  { text: 'AI Insights', icon: <AutoAwesome />, path: '/ai-insights' },
  { text: 'Settings', icon: <Settings />, path: '/settings' },
];

const Layout = () => {
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [anchorEl, setAnchorEl] = useState(null);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    setAnchorEl(null);
    logout();
    navigate('/login');
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppBar
        position="fixed"
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
          background: '#111827',
          borderBottom: '1px solid rgba(255,255,255,0.06)',
          boxShadow: 'none',
        }}
      >
        <Toolbar>
          <IconButton color="inherit" onClick={() => setDrawerOpen(!drawerOpen)} edge="start" sx={{ mr: 2 }}>
            {drawerOpen ? <ChevronLeft /> : <MenuIcon />}
          </IconButton>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexGrow: 1 }}>
            <Typography variant="h6" sx={{ fontWeight: 800, color: '#e8913a', letterSpacing: '-0.02em' }}>
              DataPulse
            </Typography>
            <Chip label="v1.0" size="small" sx={{ bgcolor: 'rgba(232,145,58,0.12)', color: '#e8913a', fontSize: '0.7rem', height: 20 }} />
          </Box>
          <IconButton onClick={(e) => setAnchorEl(e.currentTarget)} sx={{ p: 0 }}>
            <Avatar sx={{ bgcolor: '#e8913a', width: 36, height: 36, fontSize: 15, fontWeight: 700 }}>
              {user?.username?.[0]?.toUpperCase() || 'U'}
            </Avatar>
          </IconButton>
          <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={() => setAnchorEl(null)}>
            <MenuItem disabled>
              <Person sx={{ mr: 1 }} /> {user?.username}
            </MenuItem>
            <Divider />
            <MenuItem onClick={() => { setAnchorEl(null); navigate('/settings'); }}>
              <Settings sx={{ mr: 1 }} /> Settings
            </MenuItem>
            <MenuItem onClick={handleLogout}>
              <Logout sx={{ mr: 1 }} /> Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      <Drawer
        variant="persistent"
        open={drawerOpen}
        sx={{
          width: drawerOpen ? DRAWER_WIDTH : 0,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
            background: '#0d1117',
            borderRight: '1px solid rgba(255,255,255,0.06)',
          },
        }}
      >
        <Toolbar />
        <List sx={{ mt: 1 }}>
          {navItems.map((item) => (
            <ListItem key={item.text} disablePadding sx={{ px: 1, mb: 0.5 }}>
              <ListItemButton
                onClick={() => navigate(item.path)}
                selected={location.pathname === item.path}
                sx={{
                  borderRadius: 2,
                  '&.Mui-selected': {
                    bgcolor: 'rgba(232,145,58,0.1)',
                    borderLeft: '3px solid #e8913a',
                    '&:hover': { bgcolor: 'rgba(232,145,58,0.15)' },
                  },
                }}
              >
                <ListItemIcon sx={{ color: location.pathname === item.path ? '#e8913a' : '#8892a4', minWidth: 40 }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText primary={item.text} primaryTypographyProps={{ fontSize: '0.875rem', color: location.pathname === item.path ? '#d1d5db' : '#8892a4' }} />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, p: 3, mt: 8, transition: 'margin 0.3s', ml: drawerOpen ? 0 : `-${DRAWER_WIDTH}px` }}>
        <Outlet />
      </Box>
    </Box>
  );
};

export default Layout;
