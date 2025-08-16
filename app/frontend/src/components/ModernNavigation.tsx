import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  useTheme,
  useMediaQuery,
  Switch,
  FormControlLabel,
  Divider,
  ListItemButton,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Close as CloseIcon,
  Brightness4,
  Brightness7,
} from '@mui/icons-material';
import { Link, useLocation } from 'react-router-dom';
import { useModuleContext } from '../modules/shared/context';
import { ModuleSelector } from '../modules/shared/components/ModuleSelector';
import { IgGMolecule } from './IgGMolecule';

interface ModernNavigationProps {
  darkMode: boolean;
  onThemeToggle: () => void;
}

export const ModernNavigation: React.FC<ModernNavigationProps> = ({
  darkMode,
  onThemeToggle,
}) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { modules } = useModuleContext();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const currentModuleRoute = location.pathname;

  const handleModuleSelect = (moduleId: string) => {
    // This function is no longer needed as navigation is handled by Link
    // Keeping it for now in case it's called elsewhere or for future use.
  };


  return (
    <>
      <AppBar
        position="static"
        elevation={0}
        sx={{
          background: darkMode
            ? 'linear-gradient(135deg, #000000 0%, #1C1C1E 100%)'
            : 'linear-gradient(135deg, #F2F2F7 0%, #FFFFFF 100%)',
          backdropFilter: 'blur(20px)',
          borderBottom: darkMode
            ? '1px solid rgba(255, 255, 255, 0.1)'
            : '1px solid rgba(0, 0, 0, 0.1)',
          transition: 'all 0.3s ease-in-out',
        }}
      >
        <Toolbar sx={{ minHeight: '72px !important' }}>
          {/* Logo and Title */}
          <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mr: 3 }}>
              <IgGMolecule size={32} />
              <Typography
                variant="h5"
                component="div"
                sx={{
                  ml: 1,
                  fontWeight: 700,
                  background: darkMode
                    ? 'linear-gradient(135deg, #FFFFFF 0%, #E5E5E7 100%)'
                    : 'linear-gradient(135deg, #000000 0%, #1C1C1E 100%)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  letterSpacing: '-0.02em',
                }}
              >
                AbSequenceAlign
              </Typography>
            </Box>

            {/* Subtitle */}
            <Typography
              variant="body2"
              sx={{
                color: darkMode ? '#E5E5E7' : '#3A3A3C',
                fontWeight: 500,
                opacity: 0.8,
                display: { xs: 'none', sm: 'block' },
              }}
            >
              Antibody Sequence Analysis Platform
            </Typography>
          </Box>

          {/* Desktop Navigation */}
          <Box sx={{ display: { xs: 'none', md: 'flex' }, alignItems: 'center', gap: 2 }}>
            {/* Module Selector */}
            <ModuleSelector />

            {/* Theme Toggle */}
            <FormControlLabel
              control={
                <Switch
                  checked={darkMode}
                  onChange={onThemeToggle}
                  sx={{
                    '& .MuiSwitch-switchBase': {
                      color: darkMode ? '#90caf9' : '#1976d2',
                    },
                    '& .MuiSwitch-track': {
                      backgroundColor: darkMode ? '#90caf9' : '#1976d2',
                    },
                  }}
                />
              }
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  {darkMode ? <Brightness7 fontSize="small" /> : <Brightness4 fontSize="small" />}
                  <Typography
                    variant="body2"
                    sx={{
                      color: darkMode ? '#FFFFFF' : '#000000',
                      fontWeight: 500,
                    }}
                  >
                    {darkMode ? 'Light' : 'Dark'}
                  </Typography>
                </Box>
              }
              labelPlacement="start"
            />
          </Box>

          {/* Mobile Menu Button */}
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* Mobile Drawer */}
      <Drawer
        variant="temporary"
        anchor="right"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true,
        }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: 280,
            background: darkMode
              ? 'linear-gradient(135deg, #000000 0%, #1C1C1E 100%)'
              : 'linear-gradient(135deg, #F2F2F7 0%, #FFFFFF 100%)',
            backdropFilter: 'blur(20px)',
            borderLeft: darkMode
              ? '1px solid rgba(255, 255, 255, 0.1)'
              : '1px solid rgba(0, 0, 0, 0.1)',
          },
        }}
      >
        <Box sx={{ p: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <IgGMolecule size={24} />
              <Typography
                variant="h6"
                sx={{
                  ml: 1,
                  fontWeight: 700,
                  color: darkMode ? '#FFFFFF' : '#000000',
                }}
              >
                AbSequenceAlign
              </Typography>
            </Box>
            <IconButton onClick={handleDrawerToggle}>
              <CloseIcon />
            </IconButton>
          </Box>

          <Typography
            variant="body2"
            sx={{
              color: darkMode ? '#A1A1A6' : '#6C6C70',
              mb: 3,
              fontWeight: 500,
            }}
          >
            Select Analysis Module
          </Typography>

          <Divider sx={{ mb: 2 }} />

          <List>
            {modules.map((module) => (
              <ListItem key={module.id} disablePadding>
                <ListItemButton
                  component={Link}
                  to={module.route}
                  selected={module.route === currentModuleRoute}
                  onClick={() => {
                    if (isMobile) {
                      setMobileOpen(false);
                    }
                  }}
                  sx={{
                    borderRadius: 2,
                    mb: 1,
                    background: module.route === currentModuleRoute
                      ? darkMode
                        ? 'rgba(255, 255, 255, 0.1)'
                        : 'rgba(0, 0, 0, 0.05)'
                      : 'transparent',
                    '&:hover': {
                      background: darkMode
                        ? 'rgba(255, 255, 255, 0.05)'
                        : 'rgba(0, 0, 0, 0.02)',
                    },
                  }}
                >
                  <ListItemIcon>
                    {module.icon && <module.icon />}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Typography
                        variant="body2"
                        sx={{
                          fontWeight: 600,
                          color: darkMode ? '#FFFFFF' : '#000000',
                        }}
                      >
                        {module.name}
                      </Typography>
                    }
                    secondary={
                      <Typography
                        variant="caption"
                        sx={{
                          color: '#6C6C70',
                        }}
                      >
                        {module.description}
                      </Typography>
                    }
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>

          <Divider sx={{ my: 2 }} />

          {/* Mobile Theme Toggle */}
          <FormControlLabel
            control={
              <Switch
                checked={darkMode}
                onChange={onThemeToggle}
                sx={{
                  '& .MuiSwitch-switchBase': {
                    color: darkMode ? '#90caf9' : '#1976d2',
                  },
                  '& .MuiSwitch-track': {
                    backgroundColor: darkMode ? '#90caf9' : '#1976d2',
                  },
                }}
              />
            }
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                {darkMode ? <Brightness7 fontSize="small" /> : <Brightness4 fontSize="small" />}
                <Typography
                  variant="body2"
                  sx={{
                    color: darkMode ? '#FFFFFF' : '#000000',
                    fontWeight: 500,
                  }}
                >
                  {darkMode ? 'Light Mode' : 'Dark Mode'}
                </Typography>
              </Box>
            }
            labelPlacement="start"
          />
        </Box>
      </Drawer>
    </>
  );
};
