import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  IconButton,
  Tooltip,
  Chip,
  Slider
} from '@mui/material';
import { ZoomIn, ZoomOut, Visibility, VisibilityOff } from '@mui/icons-material';
import { getAminoAcidColor } from '../../../../utils/colorUtils';
import { COLOR_SCHEMES } from '../../../../utils/colorUtils';
import { ColorSchemeType } from '../../../../types/sequence';
import { ColorSchemeSelector } from '../../../../components/ColorSchemeSelector';

interface MSAVisualizationProps {
  alignmentMatrix: string[][];
  sequenceNames: string[];
  regions: any[];
  numberingScheme: string;
}

export const MSAVisualization: React.FC<MSAVisualizationProps> = ({
  alignmentMatrix,
  sequenceNames,
  regions,
  numberingScheme
}) => {
  const [zoomLevel, setZoomLevel] = useState(1);
  const [showNumbering, setShowNumbering] = useState(true);
  const [showRegions, setShowRegions] = useState(true);
  const [colorScheme, setColorScheme] = useState(COLOR_SCHEMES[ColorSchemeType.HYDROPHOBICITY]);
  const [startPosition, setStartPosition] = useState(0);
  const [visibleColumns] = useState(80);
  const [showRegionOverlay, setShowRegionOverlay] = useState(true);
  const [showColorScheme, setShowColorScheme] = useState(true);
  
  const handlePositionChange = (_event: Event, newValue: number | number[]) => {
    setStartPosition(newValue as number);
  };

  const getRegionForPosition = (position: number) => {
    return regions.find(region => 
      position >= region.start && position <= region.stop
    );
  };

  const renderAlignmentRow = (sequenceIndex: number, sequenceName: string) => {
    const sequence = alignmentMatrix[sequenceIndex];
    const visibleSequence = sequence.slice(startPosition, startPosition + visibleColumns);

    return (
      <Box key={sequenceIndex} sx={{ mb: 1 }}>
        {/* Sequence name */}
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          mb: 0.5,
          minWidth: 150,
          pr: 2
        }}>
          <Typography variant="caption" fontWeight="bold" noWrap>
            {sequenceName}
          </Typography>
        </Box>

        {/* Alignment row */}
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center',
          fontFamily: 'monospace',
          fontSize: `${12 * zoomLevel}px`,
          lineHeight: 1.2
        }}>
          {visibleSequence.map((aminoAcid, position) => {
            const globalPosition = startPosition + position;
            const region = getRegionForPosition(globalPosition);
            const isGap = aminoAcid === '-';
            
            let backgroundColor = 'transparent';
            let textColor = 'text.primary';
            let borderColor = 'transparent';

            if (isGap) {
              backgroundColor = 'grey.100';
              textColor = 'text.disabled';
            } else if (region && showRegionOverlay) {
              backgroundColor = region.color + '40';
              borderColor = region.color;
            } else if (showColorScheme) {
              backgroundColor = getAminoAcidColor(aminoAcid, colorScheme);
              textColor = 'white';
            } else {
              backgroundColor = 'transparent';
              textColor = 'text.primary';
            }

            return (
              <Tooltip
                key={position}
                title={
                  <Box>
                    <Typography variant="caption">
                      <strong>{aminoAcid}{globalPosition + 1}</strong>
                    </Typography>
                    {region && (
                      <Typography variant="caption" display="block">
                        Region: {region.name}
                      </Typography>
                    )}
                  </Box>
                }
                arrow
              >
                <Box
                  sx={{
                    backgroundColor,
                    color: textColor,
                    border: `1px solid ${borderColor}`,
                    padding: `${2 * zoomLevel}px ${1 * zoomLevel}px`,
                    margin: '0 1px',
                    borderRadius: '2px',
                    minWidth: `${8 * zoomLevel}px`,
                    textAlign: 'center',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      transform: 'scale(1.1)',
                      zIndex: 10,
                    },
                  }}
                >
                  {aminoAcid}
                </Box>
              </Tooltip>
            );
          })}
        </Box>
      </Box>
    );
  };

  const renderNumberingRow = () => {
    if (!showNumbering) return null;

    const visiblePositions = Array.from(
      { length: visibleColumns }, 
      (_, i) => startPosition + i
    );

    return (
      <Box sx={{ mb: 1 }}>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center',
          minWidth: 150,
          pr: 2
        }}>
          <Typography variant="caption" fontWeight="bold">
            Position
          </Typography>
        </Box>

        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center',
          fontFamily: 'monospace',
          fontSize: `${10 * zoomLevel}px`,
          color: 'text.secondary'
        }}>
          {visiblePositions.map((position, index) => {
            const isFirstOrLast = index === 0 || index === visibleColumns - 1;
            const isEveryTen = position % 10 === 0;
            const shouldShowNumber = isFirstOrLast || isEveryTen;

            return (
              <Box
                key={index}
                sx={{
                  minWidth: `${8 * zoomLevel}px`,
                  margin: '0 1px',
                  padding: `${2 * zoomLevel}px ${1 * zoomLevel}px`,
                  textAlign: 'center',
                  fontSize: `${8 * zoomLevel}px`,
                  color: shouldShowNumber ? 'text.secondary' : 'transparent',
                  fontWeight: shouldShowNumber ? 'bold' : 'normal',
                }}
              >
                {shouldShowNumber ? position + 1 : ''}
              </Box>
            );
          })}
        </Box>
      </Box>
    );
  };

  const renderRegionRow = () => {
    if (!showRegions || regions.length === 0) return null;

    const visiblePositions = Array.from(
      { length: visibleColumns }, 
      (_, i) => startPosition + i
    );

    return (
      <Box sx={{ mb: 1 }}>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center',
          minWidth: 150,
          pr: 2
        }}>
          <Typography variant="caption" fontWeight="bold">
            Regions
          </Typography>
        </Box>

        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center',
          height: `${16 * zoomLevel}px`
        }}>
          {visiblePositions.map((position, index) => {
            const region = getRegionForPosition(position);
            
            return (
              <Box
                key={index}
                sx={{
                  minWidth: `${8 * zoomLevel}px`,
                  margin: '0 1px',
                  height: `${12 * zoomLevel}px`,
                  backgroundColor: region ? region.color + '60' : 'transparent',
                  borderRadius: '1px',
                  border: region ? `1px solid ${region.color}` : 'none',
                }}
              />
            );
          })}
        </Box>
      </Box>
    );
  };

  return (
    <Paper sx={{ p: 3 }}>
      {/* Controls */}
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
        <ColorSchemeSelector
          selectedScheme={colorScheme}
          onSchemeChange={setColorScheme}
          compact={true}
        />

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="body2">Zoom:</Typography>
          <IconButton size="small" onClick={() => setZoomLevel(Math.max(0.5, zoomLevel - 0.2))}>
            <ZoomOut />
          </IconButton>
          <Chip label={`${Math.round(zoomLevel * 100)}%`} size="small" />
          <IconButton size="small" onClick={() => setZoomLevel(Math.min(3, zoomLevel + 0.2))}>
            <ZoomIn />
          </IconButton>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Tooltip title={showNumbering ? "Hide numbering" : "Show numbering"}>
            <IconButton 
              size="small" 
              onClick={() => setShowNumbering(!showNumbering)}
            >
              {showNumbering ? <Visibility /> : <VisibilityOff />}
            </IconButton>
          </Tooltip>
          <Typography variant="body2">Numbering</Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Tooltip title={showRegionOverlay ? "Hide region overlay" : "Show region overlay"}>
            <IconButton 
              size="small" 
              onClick={() => setShowRegionOverlay(!showRegionOverlay)}
            >
              {showRegionOverlay ? <Visibility /> : <VisibilityOff />}
            </IconButton>
          </Tooltip>
          <Typography variant="body2">Region Overlay</Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Tooltip title={showColorScheme ? "Hide color scheme" : "Show color scheme"}>
            <IconButton 
              size="small" 
              onClick={() => setShowColorScheme(!showColorScheme)}
            >
              {showColorScheme ? <Visibility /> : <VisibilityOff />}
            </IconButton>
          </Tooltip>
          <Typography variant="body2">Color Scheme</Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, minWidth: 200 }}>
          <Typography variant="body2">Position:</Typography>
          <Slider
            value={startPosition}
            onChange={handlePositionChange}
            min={0}
            max={Math.max(0, alignmentMatrix[0]?.length - visibleColumns)}
            size="small"
            sx={{ mx: 1 }}
          />
        </Box>
      </Box>

      {/* Alignment Display */}
      <Box sx={{ 
        overflow: 'auto', 
        maxHeight: 600,
        border: '1px solid',
        borderColor: 'divider',
        borderRadius: 1,
        p: 2
      }}>
        {/* Numbering row */}
        {renderNumberingRow()}

        {/* Region row */}
        {renderRegionRow()}

        {/* Sequence rows */}
        {sequenceNames.map((name, index) => 
          renderAlignmentRow(index, name)
        )}
      </Box>

      {/* Statistics */}
      <Box sx={{ mt: 2, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <Chip 
          label={`${sequenceNames.length} sequences`} 
          size="small" 
          color="primary" 
        />
        <Chip 
          label={`${alignmentMatrix[0]?.length || 0} positions`} 
          size="small" 
          color="secondary" 
        />
        <Chip 
          label={`${numberingScheme.toUpperCase()} numbering`} 
          size="small" 
          variant="outlined" 
        />
        {regions.length > 0 && (
          <Chip 
            label={`${regions.length} regions`} 
            size="small" 
            variant="outlined" 
          />
        )}
      </Box>
    </Paper>
  );
};
