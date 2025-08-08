import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem,
  Chip,
  IconButton,
  Tooltip
} from '@mui/material';
import { ZoomIn, ZoomOut, Palette } from '@mui/icons-material';
import type { Region, ColorScheme } from '../../types/sequence';
import { COLOR_SCHEMES, getAminoAcidColor } from '../../utils/colorUtils';
import { ColorSchemeType } from '../../types/sequence';

interface AminoAcidSequenceProps {
  sequence: string;
  regions: Region[];
  colorScheme: ColorScheme;
  onAminoAcidClick: (position: number, aminoAcid: string) => void;
  onColorSchemeChange: (colorScheme: ColorScheme) => void;
  selectedPositions: number[];
  selectedRegions: string[];
}

export const AminoAcidSequence: React.FC<AminoAcidSequenceProps> = ({
  sequence,
  regions,
  colorScheme,
  onAminoAcidClick,
  onColorSchemeChange,
  selectedPositions,
  selectedRegions
}) => {
  const [fontSize, setFontSize] = useState(14);
  const [showPositions, setShowPositions] = useState(true);

  // Create a map of positions to regions for quick lookup
  const positionToRegion = new Map<number, Region>();
  regions.forEach(region => {
    for (let pos = region.start; pos <= region.stop; pos++) {
      positionToRegion.set(pos, region);
    }
  });

  const handleFontSizeChange = (delta: number) => {
    setFontSize(prev => Math.max(8, Math.min(24, prev + delta)));
  };

  const renderSequenceLines = () => {
    const aminoAcids = sequence.split('');
    const lines: React.ReactElement[] = [];
    const charsPerLine = Math.floor(800 / (fontSize * 0.6)); // Approximate chars per line
    
    for (let i = 0; i < aminoAcids.length; i += charsPerLine) {
      const lineAAs = aminoAcids.slice(i, i + charsPerLine);
      const startPos = i + 1; // 1-based positioning
      
      lines.push(
        <Box key={i} sx={{ mb: 1 }}>
          {/* Position numbers */}
          {showPositions && (
            <Box sx={{ 
              fontFamily: 'monospace', 
              fontSize: '10px', 
              color: 'text.secondary',
              mb: 0.5,
              pl: 1
            }}>
              {Array.from({ length: Math.ceil(lineAAs.length / 10) }, (_, idx) => {
                const pos = startPos + (idx * 10);
                return pos <= sequence.length ? (
                  <span key={idx} style={{ 
                    display: 'inline-block', 
                    width: `${fontSize * 6}px`,
                    textAlign: 'left'
                  }}>
                    {pos}
                  </span>
                ) : null;
              })}
            </Box>
          )}
          
          {/* Amino acid sequence */}
          <Box sx={{ 
            fontFamily: 'monospace', 
            fontSize: `${fontSize}px`,
            lineHeight: 1.2,
            letterSpacing: '1px'
          }}>
            {lineAAs.map((aa, idx) => {
              const position = startPos + idx;
              const region = positionToRegion.get(position);
              const isSelected = selectedPositions.includes(position);
              
              // Determine background color
              let backgroundColor = 'transparent';
              let borderColor = 'transparent';
              let textColor = 'black';
              
              // Check if this position's region is selected
              const isRegionSelected = region && selectedRegions.includes(region.id);
              
              if (isRegionSelected) {
                // If region is selected, use region color as background
                backgroundColor = region.color;
                textColor = 'white';
                borderColor = region.color;
              } else if (region && colorScheme.type === ColorSchemeType.CUSTOM) {
                // If using custom color scheme, show region colors lightly
                backgroundColor = region.color + '40'; // Add transparency
                borderColor = region.color;
              }
              
              if (isSelected) {
                borderColor = '#000';
              }

              // Get amino acid color based on color scheme
              let aaColor = backgroundColor;
              
              if (isRegionSelected) {
                // If region is selected, use the region color
                aaColor = region.color;
              } else if (colorScheme.type !== ColorSchemeType.CUSTOM) {
                // Otherwise use the color scheme
                aaColor = getAminoAcidColor(aa, colorScheme);
              } else if (region) {
                // For custom color scheme, show region colors lightly
                aaColor = region.color + '40'; // Add transparency
              }

              return (
                <Tooltip 
                  key={idx}
                  title={
                    <Box>
                      <Typography variant="caption">
                        <strong>{aa}{position}</strong>
                      </Typography>
                      {region && (
                        <Typography variant="caption" display="block">
                          Region: {region.name} ({region.type})
                        </Typography>
                      )}
                    </Box>
                  }
                  arrow
                >
                  <span
                    style={{
                      backgroundColor: aaColor,
                      color: textColor,
                      border: `2px solid ${borderColor}`,
                      padding: '2px 1px',
                      margin: '0 1px',
                      cursor: 'pointer',
                      borderRadius: '2px',
                      display: 'inline-block',
                      minWidth: `${fontSize}px`,
                      textAlign: 'center',
                      transition: 'all 0.2s ease',
                      opacity: isSelected ? 1 : 0.9,
                      fontWeight: isRegionSelected ? 'bold' : 'normal'
                    }}
                    onClick={() => onAminoAcidClick(position, aa)}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'scale(1.1)';
                      e.currentTarget.style.zIndex = '10';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'scale(1)';
                      e.currentTarget.style.zIndex = '1';
                    }}
                  >
                    {aa}
                  </span>
                </Tooltip>
              );
            })}
          </Box>
        </Box>
      );
    }
    
    return lines;
  };

  return (
    <Box>
      {/* Controls */}
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: 2, 
        mb: 2,
        flexWrap: 'wrap'
      }}>
        <FormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel>Color Scheme</InputLabel>
          <Select
            value={colorScheme.type}
            label="Color Scheme"
            onChange={(e) => {
              const newScheme = COLOR_SCHEMES[e.target.value as ColorSchemeType];
              onColorSchemeChange(newScheme);
            }}
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

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="body2">Font Size:</Typography>
          <IconButton size="small" onClick={() => handleFontSizeChange(-2)}>
            <ZoomOut />
          </IconButton>
          <Chip label={`${fontSize}px`} size="small" />
          <IconButton size="small" onClick={() => handleFontSizeChange(2)}>
            <ZoomIn />
          </IconButton>
        </Box>

        <Chip 
          label={showPositions ? "Hide Positions" : "Show Positions"}
          onClick={() => setShowPositions(!showPositions)}
          variant="outlined"
          size="small"
        />
      </Box>

      {/* Sequence Display */}
      <Box sx={{ 
        border: '1px solid',
        borderColor: 'divider',
        borderRadius: 1,
        p: 2,
        bgcolor: 'background.paper',
        maxHeight: 400,
        overflow: 'auto'
      }}>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          Sequence Length: {sequence.length} amino acids
          {selectedPositions.length > 0 && ` | Selected: ${selectedPositions.length} positions`}
        </Typography>
        
        {renderSequenceLines()}
      </Box>

      {/* Color Scheme Legend */}
      {colorScheme.type !== ColorSchemeType.CUSTOM && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="caption" color="text.secondary" gutterBottom display="block">
            {colorScheme.description}
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {Object.entries(colorScheme.colors).slice(0, 10).map(([aa, color]) => (
              <Box
                key={aa}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 0.5,
                  fontSize: '12px'
                }}
              >
                <Box
                  sx={{
                    width: 16,
                    height: 16,
                    backgroundColor: color,
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 0.5
                  }}
                />
                {aa}
              </Box>
            ))}
            {Object.keys(colorScheme.colors).length > 10 && (
              <Typography variant="caption" color="text.secondary">
                +{Object.keys(colorScheme.colors).length - 10} more...
              </Typography>
            )}
          </Box>
        </Box>
      )}
    </Box>
  );
};
