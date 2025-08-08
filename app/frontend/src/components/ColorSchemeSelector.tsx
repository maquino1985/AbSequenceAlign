import React from 'react';
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Chip,
  Tooltip,
  IconButton
} from '@mui/material';
import { Palette, Info } from '@mui/icons-material';
import type { ColorScheme } from '../types/sequence';
import { COLOR_SCHEMES } from '../utils/colorUtils';
import { ColorSchemeType } from '../types/sequence';

interface ColorSchemeSelectorProps {
  selectedScheme: ColorScheme;
  onSchemeChange: (scheme: ColorScheme) => void;
  showLegend?: boolean;
  compact?: boolean;
  label?: string;
}

export const ColorSchemeSelector: React.FC<ColorSchemeSelectorProps> = ({
  selectedScheme,
  onSchemeChange,
  showLegend = true,
  compact = false,
  label = "Color Scheme"
}) => {
  const handleSchemeChange = (event: any) => {
    const newScheme = COLOR_SCHEMES[event.target.value as ColorSchemeType];
    onSchemeChange(newScheme);
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
      <FormControl size="small" sx={{ minWidth: compact ? 150 : 200 }}>
        <InputLabel>{label}</InputLabel>
        <Select
          value={selectedScheme.type}
          label={label}
          onChange={handleSchemeChange}
        >
          {Object.entries(COLOR_SCHEMES).map(([key, scheme]) => (
            <MenuItem key={key} value={key}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Palette fontSize="small" />
                {scheme.name}
              </Box>
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {showLegend && selectedScheme.type !== ColorSchemeType.CUSTOM && (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Tooltip title={selectedScheme.description}>
            <IconButton size="small">
              <Info fontSize="small" />
            </IconButton>
          </Tooltip>
          
          {!compact && (
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, maxWidth: 300 }}>
              {Object.entries(selectedScheme.colors).slice(0, 8).map(([aa, color]) => (
                <Tooltip key={aa} title={`${aa}: ${color}`}>
                  <Box
                    sx={{
                      width: 16,
                      height: 16,
                      backgroundColor: color,
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 0.5,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '8px',
                      color: 'white',
                      fontWeight: 'bold',
                      textShadow: '1px 1px 1px rgba(0,0,0,0.5)'
                    }}
                  >
                    {aa}
                  </Box>
                </Tooltip>
              ))}
              {Object.keys(selectedScheme.colors).length > 8 && (
                <Chip 
                  label={`+${Object.keys(selectedScheme.colors).length - 8}`} 
                  size="small" 
                  variant="outlined"
                />
              )}
            </Box>
          )}
        </Box>
      )}
    </Box>
  );
};
