import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
  useTheme,
  useMediaQuery,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Translate as TranslateIcon,
  Settings as SettingsIcon,
  History as HistoryIcon,
  Info as InfoIcon,
  Menu as MenuIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const Header: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);

  const navItems = [
    { label: 'Translator', path: '/', icon: <TranslateIcon /> },
    { label: 'Real-time', path: '/realtime', icon: <TranslateIcon /> },
    { label: 'History', path: '/history', icon: <HistoryIcon /> },
    { label: 'Settings', path: '/settings', icon: <SettingsIcon /> },
    { label: 'About', path: '/about', icon: <InfoIcon /> },
  ];

  const handleNavigation = (path: string) => {
    console.log('Navigating to:', path);
    navigate(path);
  };

  return (
    <>
      <AppBar position="static" elevation={2} sx={{ zIndex: 1000 }}>
        <Toolbar>
          {/* Logo and Title */}
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              cursor: 'pointer',
              mr: 3,
            }}
            onClick={() => navigate('/')}
          >
            <TranslateIcon sx={{ mr: 1, fontSize: 32, color: '#ffffff' }} />
            <Typography
              variant="h5"
              component="div"
              sx={{
                fontWeight: 700,
                color: '#ffffff',
                textShadow: '2px 2px 4px rgba(0, 0, 0, 0.3)',
              }}
            >
              Body Language Translator
            </Typography>
          </Box>

          {/* Navigation Menu */}
          <Box sx={{ flexGrow: 1, display: 'flex', justifyContent: 'center' }}>
            {!isMobile && (
              <Box sx={{ display: 'flex', gap: 1 }}>
                                {navItems.map((item) => (
                  <Button
                    key={item.path}
                    color="inherit"
                    startIcon={item.icon}
                    onClick={() => handleNavigation(item.path)}
                    sx={{
                      mx: 0.5,
                      px: 2,
                      py: 1,
                      borderRadius: 2,
                      minHeight: 48,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      backgroundColor:
                        location.pathname === item.path
                          ? 'rgba(255, 255, 255, 0.1)'
                          : 'transparent',
                      '&:hover': {
                        backgroundColor: 'rgba(255, 255, 255, 0.1)',
                      },
                      position: 'relative',
                      zIndex: 1,
                      cursor: 'pointer',
                      '& .MuiButton-startIcon': {
                        marginRight: 1,
                      },
                    }}
                  >
                    {item.label}
                  </Button>
                ))}
              </Box>
            )}
          </Box>

          {/* Mobile Menu Button */}
          {isMobile && (
            <IconButton
              color="inherit"
              aria-label="menu"
              sx={{ ml: 'auto' }}
              onClick={() => setMobileOpen(true)}
            >
              <MenuIcon />
            </IconButton>
          )}

          {/* Status Indicator */}
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              ml: 2,
            }}
          >
            <Box
              sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                backgroundColor: '#4caf50',
                mr: 1,
              }}
            />
            <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
              Connected
            </Typography>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Mobile Drawer */}
      <Drawer
        anchor="left"
        open={mobileOpen}
        onClose={() => setMobileOpen(false)}
      >
        <Box sx={{ width: 250, pt: 2 }}>
          <List>
            {navItems.map((item) => (
              <ListItem
                key={item.path}
                onClick={() => {
                  handleNavigation(item.path);
                  setMobileOpen(false);
                }}
                sx={{
                  backgroundColor: location.pathname === item.path ? 'rgba(25, 118, 210, 0.1)' : 'transparent',
                  cursor: 'pointer',
                }}
              >
                <ListItemIcon sx={{ color: location.pathname === item.path ? 'primary.main' : 'inherit' }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText 
                  primary={item.label}
                  sx={{ 
                    color: location.pathname === item.path ? 'primary.main' : 'inherit',
                    fontWeight: location.pathname === item.path ? 600 : 400,
                  }}
                />
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>
    </>
  );
};

export default Header;
