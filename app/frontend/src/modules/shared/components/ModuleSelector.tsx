import React from 'react';
import {
  Box,
  Typography,
  Menu,
  MenuItem,
  Tooltip,
  Chip
} from '@mui/material';
import { KeyboardArrowDown } from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useModuleContext } from '../context';

export const ModuleSelector: React.FC = () => {
  const { modules, getCurrentModule } = useModuleContext();
  const navigate = useNavigate();
  const location = useLocation();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  
  // Find current module based on current route
  const currentModuleData = modules.find(module => module.route === location.pathname) || modules[0];
  const open = Boolean(anchorEl);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleModuleSelect = (moduleId: string) => {
    const selectedModule = modules.find(module => module.id === moduleId);
    if (selectedModule) {
      navigate(selectedModule.route);
    }
    handleClose();
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      <Tooltip title="Select Analysis Module">
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            cursor: 'pointer',
            padding: '8px 12px',
            borderRadius: 1,
            border: '1px solid',
            borderColor: 'divider',
            backgroundColor: 'background.paper',
            '&:hover': {
              backgroundColor: 'action.hover',
            },
          }}
          onClick={handleClick}
        >
          {currentModuleData && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <currentModuleData.icon fontSize="small" />
              <Typography variant="body2" fontWeight={600}>
                {currentModuleData.name}
              </Typography>
              <KeyboardArrowDown fontSize="small" />
            </Box>
          )}
        </Box>
      </Tooltip>

      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        PaperProps={{
          sx: {
            minWidth: 250,
            mt: 1,
          },
        }}
      >
        {modules
          .filter((module) => module.enabled)
          .sort((a, b) => (a.order || 0) - (b.order || 0))
          .map((module) => (
            <MenuItem
              key={module.id}
              onClick={() => handleModuleSelect(module.id)}
              selected={module.route === location.pathname}
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 2,
                py: 1.5,
              }}
            >
              <module.icon fontSize="small" />
              <Box sx={{ flexGrow: 1 }}>
                <Typography variant="body2" fontWeight={600}>
                  {module.name}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {module.description}
                </Typography>
              </Box>
              {module.route === location.pathname && (
                <Chip label="Active" size="small" color="primary" />
              )}
            </MenuItem>
          ))}
      </Menu>
    </Box>
  );
};
