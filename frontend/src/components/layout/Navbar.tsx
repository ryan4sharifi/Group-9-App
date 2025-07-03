import React, { useState, useEffect } from 'react';
import {
  AppBar, Toolbar, Typography, Button, Box, Container,
  useTheme, useMediaQuery, IconButton, Drawer, List, ListItemButton,
  ListItemText, Divider, ListItemIcon, Chip, alpha, Avatar
} from '@mui/material';
import { Link as RouterLink, useNavigate, useLocation } from 'react-router-dom';
import {
  Menu as MenuIcon, PersonOutline as PersonIcon, EventNote as EventIcon,
  NotificationsNone as NotificationsIcon, Assessment as AssessmentIcon,
  Login as LoginIcon, HowToReg as RegisterIcon, Logout as LogoutIcon,
  Home as HomeIcon, KeyboardArrowRight as ArrowIcon, History as HistoryIcon,
} from '@mui/icons-material';
import { useUser } from '../../context/UserContext';
import NotificationBell from './NotificationBell'; //NTran

interface NavItem {
  label: string;
  path: string;
  icon: React.ReactElement;
  badge?: number;
}

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery('(max-width:1080px)'); // Changed from theme.breakpoints.down('md')
  const isSmall = useMediaQuery(theme.breakpoints.down('sm'));
  const { userId, setUserId } = useUser();
  const isLoggedIn = !!userId;
  const role = sessionStorage.getItem('role');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);

  // Track scrolling for navbar styling
  useEffect(() => {
    const onScroll = () => setIsScrolled(window.scrollY > 20);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const handleLogout = () => {
    sessionStorage.clear();
    setUserId(null);
    navigate('/login');
    setDrawerOpen(false);
  };

  // Navigation items based on user role
  const getNavItems = (): NavItem[] => {
    if (!isLoggedIn) {
      return [
    { label: 'Login', path: '/login', icon: <LoginIcon /> },
    { label: 'Register', path: '/register', icon: <RegisterIcon /> },
  ];
    }

    return role === 'admin' ? [
      // { label: 'Create Event', path: '/event-form', icon: <EventIcon /> },
      // { label: 'Reports', path: '/reports', icon: <AssessmentIcon /> },
      // { label: 'Notifications', path: '/notifications', icon: <NotificationsIcon /> },
      // { label: 'History', path: '/history', icon: <HistoryIcon /> },
      { label: 'Profile', path: '/profile', icon: <PersonIcon /> },
    ] : [
      { label: 'Home', path: '/', icon: <HomeIcon /> },
      { label: 'Profile', path: '/profile', icon: <PersonIcon /> },
      // { label: 'Events', path: '/match', icon: <EventIcon /> },
      // { label: 'Notifications', path: '/notifications', icon: <NotificationsIcon /> },
      // { label: 'History', path: '/history', icon: <HistoryIcon /> },
    ];
  };

  const navItems = getNavItems();
  const isActive = (path: string) => location.pathname === path;

  // Drawer component for mobile view
  const MobileDrawer = () => (
    <Drawer
      anchor="right"
      open={drawerOpen}
      onClose={() => setDrawerOpen(false)}
      PaperProps={{
        sx: {
          width: 280,
          borderRadius: '12px 0 0 12px',
          boxShadow: theme.shadows[6]
        }
            }}
          >
      <Box sx={{ p: 2.5, bgcolor: 'background.paper' }}>
        <Typography variant="h6" sx={{ fontWeight: 500, color: 'primary.main' }}>
          Group 9 Volunteer Portal
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {isLoggedIn ? `Signed in as ${role}` : 'Please sign in to continue'}
            </Typography>
          </Box>
      <Divider />
      <List sx={{ p: 1.5 }}>
              {navItems.map(({ label, path, icon, badge }) => (
          <ListItemButton
                  key={label}
                  component={RouterLink}
                  to={path}
            selected={isActive(path)}
            onClick={() => setDrawerOpen(false)}
                  sx={{
              my: 0.5,
              borderRadius: 1.5,
              '&.Mui-selected': {
                bgcolor: alpha(theme.palette.primary.main, 0.08),
                '&:hover': { bgcolor: alpha(theme.palette.primary.main, 0.12) }
              }
                  }}
                >
            <ListItemIcon sx={{ color: isActive(path) ? 'primary.main' : 'text.secondary', minWidth: 40 }}>
              {icon}
            </ListItemIcon>
            <ListItemText primary={label} primaryTypographyProps={{ fontWeight: isActive(path) ? 500 : 400 }} />
            {badge && <Chip size="small" label={badge} color="primary" sx={{ height: 20, fontSize: 11 }} />}
            {isActive(path) && <ArrowIcon fontSize="small" color="primary" />}
          </ListItemButton>
        ))}
      </List>
      {/* NTran: Added NotificationBell component for mobile drawer */}
      {isLoggedIn && (
        <Box sx={{ px: 2, py: 1, display: 'flex', justifyContent: 'center' }}>
          <NotificationBell />
        </Box>
      )}
              {isLoggedIn && (
        <Box sx={{ p: 2, mt: 'auto' }}>
                <Button
                  onClick={handleLogout}
            fullWidth
            variant="outlined"
                  startIcon={<LogoutIcon />}
            sx={{ borderRadius: 2, textTransform: 'none', py: 1 }}
                >
                  Sign Out
                </Button>
            </Box>
          )}
    </Drawer>
  );

  return (
    <AppBar
      position="sticky"
      elevation={0}
      sx={{
        bgcolor: isScrolled ? alpha(theme.palette.background.default, 0.95) : 'transparent',
        backdropFilter: isScrolled ? 'blur(10px)' : 'none',
        boxShadow: isScrolled ? '0 2px 16px rgba(0,0,0,0.05)' : 'none',
        color: 'text.primary',
        transition: 'all 0.3s ease',
        borderBottom: isScrolled ? 'none' : `1px solid ${alpha(theme.palette.divider, 0.08)}`
      }}
    >
      <Container maxWidth="xl">
        <Toolbar sx={{ py: 0.75 }}>
          {/* Logo */}
          <Box
            component={RouterLink}
            to="/"
            sx={{ textDecoration: 'none', color: 'inherit', display: 'flex', alignItems: 'center' }}
          >
            <Typography
              variant={isSmall ? "h6" : "h5"}
              sx={{ fontWeight: 500, color: 'primary.main', lineHeight: 1.2 }}
            >
              Group 9 
            </Typography>
            {!isSmall && (
              <Typography variant={isSmall ? "subtitle1" : "h5"} sx={{ fontWeight: 300, ml: 0.5 }}>
                Volunteer Portal
              </Typography>
            )}
          </Box>

          <Box sx={{ flexGrow: 1 }} />

          {/* Mobile menu button */}
          {isMobile ? (
            <>
              {/* NTran: Added NotificationBell for mobile view before menu button */}
              {isLoggedIn && <NotificationBell />}
              <IconButton
                onClick={() => setDrawerOpen(true)}
                sx={{ borderRadius: 1.5, p: 1 }}
              >
                <MenuIcon />
              </IconButton>
              <MobileDrawer />
            </>
          ) : (
            /* Desktop navigation */
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              {navItems.map(({ label, path, icon, badge }) => (
                <Button
                  key={label}
                  component={RouterLink}
                  to={path}
                  startIcon={icon}
                  sx={{
                    color: isActive(path) ? 'primary.main' : 'text.secondary',
                    fontWeight: isActive(path) ? 500 : 400,
                    borderBottom: isActive(path) ? `2px solid ${theme.palette.primary.main}` : '2px solid transparent',
                    borderRadius: 0,
                    mx: 1,
                    px: 1,
                    py: 1.5,
                    textTransform: 'none',
                    '&:hover': {
                      backgroundColor: 'transparent',
                      color: 'primary.main',
                      borderBottom: `2px solid ${alpha(theme.palette.primary.main, 0.5)}`
                    }
                  }}
                >
                  {label}
                  {badge && <Chip size="small" label={badge} color="primary" sx={{ ml: 0.5, height: 20 }} />}
                </Button>
              ))}
              {/* NTran: Added NotificationBell component for desktop navigation */}
              {isLoggedIn && <NotificationBell />}
              {isLoggedIn && (
                <Button
                  onClick={handleLogout}
                  startIcon={<LogoutIcon />}
                  sx={{
                    ml: 1.5,
                    textTransform: 'none',
                    borderRadius: 2,
                    px: 1.5,
                    border: `1px solid ${alpha(theme.palette.text.secondary, 0.2)}`,
                    '&:hover': { borderColor: 'primary.main', color: 'primary.main' }
                  }}
                >
                  Sign Out
                </Button>
              )}
            </Box>
          )}
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Navbar;