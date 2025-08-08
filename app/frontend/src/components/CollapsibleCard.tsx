import React, { useState } from 'react';
import {
  Paper,
  Typography,
  IconButton,
  Box,
  Collapse,
  Tooltip,
} from '@mui/material';
import {
  ExpandMore,
  ExpandLess,
  UnfoldLess,
  UnfoldMore,
} from '@mui/icons-material';

interface CollapsibleCardProps {
  title: string;
  children: React.ReactNode;
  defaultExpanded?: boolean;
  minHeight?: string;
  maxHeight?: string;
  sx?: any;
}

export const CollapsibleCard: React.FC<CollapsibleCardProps> = ({
  title,
  children,
  defaultExpanded = true,
  minHeight,
  maxHeight,
  sx = {},
}) => {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const [minimized, setMinimized] = useState(false);

  const handleToggleExpanded = () => {
    setExpanded(!expanded);
  };

  const handleToggleMinimized = () => {
    setMinimized(!minimized);
  };

  return (
    <Paper
      sx={{
        p: 2,
        minHeight: minimized ? 'auto' : minHeight,
        maxHeight: minimized ? 'auto' : maxHeight,
        overflow: 'hidden',
        transition: 'all 0.3s ease-in-out',
        ...sx,
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
        <Typography variant="h6" component="h3" sx={{ fontWeight: 600 }}>
          {title}
        </Typography>
        <Box sx={{ display: 'flex', gap: 0.5 }}>
          <Tooltip title={minimized ? 'Maximize' : 'Minimize'}>
            <IconButton
              size="small"
              onClick={handleToggleMinimized}
              sx={{ color: 'text.secondary' }}
            >
              {minimized ? <UnfoldMore /> : <UnfoldLess />}
            </IconButton>
          </Tooltip>
          <Tooltip title={expanded ? 'Collapse' : 'Expand'}>
            <IconButton
              size="small"
              onClick={handleToggleExpanded}
              sx={{ color: 'text.secondary' }}
            >
              {expanded ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
          </Tooltip>
        </Box>
      </Box>
      
      <Collapse in={expanded && !minimized}>
        <Box sx={{ pt: 1 }}>
          {children}
        </Box>
      </Collapse>
    </Paper>
  );
};
