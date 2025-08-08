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
import { useModuleContext } from '../context/ModuleContext';

export const ModuleSelector: React.FC = () => {
  const { modules, currentModule, setCurrentModule, getCurrentModule } = useModuleContext();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  
  const currentModuleData = getCurrentModule();
  const open = Boolean(anchorEl);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleModuleSelect = (moduleId: string) => {
    setCurrentModule(moduleId);
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
          .filter(module => module.enabled)
          .sort((a, b) => a.order - b.order)
          .map((module) => (
            <MenuItem
              key={module.id}
              onClick={() => handleModuleSelect(module.id)}
              selected={module.id === currentModule}
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
              {module.id === currentModule && (
                <Chip label="Active" size="small" color="primary" />
              )}
            </MenuItem>
          ))}
      </Menu>
    </Box>
  );
};
