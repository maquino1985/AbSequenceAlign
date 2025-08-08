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

  // Format selected positions and regions for display
  const formatSelections = () => {
    const selections: string[] = [];
    
    // Add selected regions
    const selectedRegionObjects = regions.filter(r => selectedRegions.includes(r.id));
    selectedRegionObjects.forEach(region => {
      selections.push(`${region.name}:${region.start}-${region.stop}`);
    });
    
    // Add selected individual positions
    const individualSelections = selectedPositions.filter(pos => 
      !selectedRegionObjects.some(region => pos >= region.start && pos <= region.stop)
    );
    
    if (individualSelections.length > 0) {
      // Group consecutive positions
      const groups: number[][] = [];
      let currentGroup: number[] = [];
      
      individualSelections.sort((a, b) => a - b).forEach(pos => {
        if (currentGroup.length === 0 || pos === currentGroup[currentGroup.length - 1] + 1) {
          currentGroup.push(pos);
        } else {
          if (currentGroup.length > 0) {
            groups.push([...currentGroup]);
          }
          currentGroup = [pos];
        }
      });
      
      if (currentGroup.length > 0) {
        groups.push(currentGroup);
      }
      
      groups.forEach(group => {
        if (group.length === 1) {
          selections.push(`${sequence[group[0] - 1]}${group[0]}`);
        } else {
          selections.push(`${sequence[group[0] - 1]}${group[0]}-${sequence[group[group.length - 1] - 1]}${group[group.length - 1]}`);
        }
      });
    }
    
    return selections;
  };

  const renderSequenceLines = () => {
    const aminoAcids = sequence.split('');
    const lines: React.ReactElement[] = [];
    const maxAAsPerLine = 50; // Reduced to 50 amino acids per line for better readability
    
    for (let i = 0; i < aminoAcids.length; i += maxAAsPerLine) {
      const lineAAs = aminoAcids.slice(i, i + maxAAsPerLine);
      const startPos = i + 1; // 1-based positioning
      const endPos = Math.min(i + maxAAsPerLine, aminoAcids.length);
      
      lines.push(
        <Box key={i} sx={{ mb: 1 }}>
          {/* Position numbers */}
          {showPositions && (
            <Box sx={{ 
              fontFamily: 'monospace', 
              fontSize: '10px', 
              color: 'text.secondary',
              mb: 0.5,
              pl: 1,
              display: 'flex',
              alignItems: 'center',
              flexWrap: 'nowrap'
            }}>
              {/* Position numbers aligned with amino acids */}
              {Array.from({ length: lineAAs.length }, (_, idx) => {
                const position = startPos + idx;
                const isFirstOrLast = position === startPos || position === endPos;
                const isEveryTen = position % 10 === 0;
                const shouldShowNumber = isFirstOrLast || isEveryTen;
                
                // Use the exact same width as amino acid blocks
                const blockWidth = fontSize + 2; // Same as minWidth in amino acid blocks
                
                if (!shouldShowNumber) {
                  // Return exact-width spacer to maintain alignment
                  return (
                    <span
                      key={idx}
                      style={{
                        display: 'inline-block',
                        minWidth: `${blockWidth}px`,
                        margin: '0 1px',
                        padding: '2px 1px',
                        height: '12px' // Match the height of the number text
                      }}
                    />
                  );
                }
                
                return (
                  <span
                    key={idx}
                    style={{
                      display: 'inline-block',
                      minWidth: `${blockWidth}px`,
                      margin: '0 1px',
                      padding: '2px 1px',
                      textAlign: 'center',
                      fontSize: '8px',
                      color: 'text.primary',
                      fontWeight: 'bold'
                    }}
                  >
                    {position}
                  </span>
                );
              })}
            </Box>
          )}
          
          {/* Amino acid sequence */}
          <Box sx={{ 
            fontFamily: 'monospace', 
            fontSize: `${fontSize}px`,
            lineHeight: 1.2,
            letterSpacing: '1px',
            display: 'flex',
            flexWrap: 'nowrap'
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
                      fontWeight: isRegionSelected ? 'bold' : 'normal',
                      flexShrink: 0
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

  const selections = formatSelections();
  const hasSelections = selections.length > 0;

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
        </Typography>
        
        {/* Selection Summary */}
        {hasSelections && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Selected: {selectedPositions.length} positions, {selectedRegions.length} regions
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, alignItems: 'center' }}>
              {selections.slice(0, 5).map((selection, index) => (
                <Chip
                  key={index}
                  label={selection}
                  size="small"
                  variant="outlined"
                  color="primary"
                />
              ))}
              {selections.length > 5 && (
                <Tooltip
                  title={
                    <Box>
                      <Typography variant="caption">
                        {selections.slice(5).join(', ')}
                      </Typography>
                    </Box>
                  }
                  arrow
                >
                  <Chip
                    label={`+${selections.length - 5} more`}
                    size="small"
                    variant="outlined"
                    color="secondary"
                  />
                </Tooltip>
              )}
            </Box>
          </Box>
        )}
        
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
