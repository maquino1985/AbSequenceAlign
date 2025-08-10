import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Chip,
  Tooltip
} from '@mui/material';

interface Region {
  id: string;
  name: string;
  start: number;
  stop: number;
  color: string;
  type: string;
}

interface RegionOverlayProps {
  regions: Region[];
  alignmentLength: number;
  onRegionClick?: (regionId: string) => void;
  selectedRegions?: string[];
}

export const RegionOverlay: React.FC<RegionOverlayProps> = ({
  regions,
  alignmentLength,
  onRegionClick,
  selectedRegions = []
}) => {
  const handleRegionClick = (regionId: string) => {
    onRegionClick?.(regionId);
  };

  const getRegionWidth = (region: Region) => {
    const width = ((region.stop - region.start + 1) / alignmentLength) * 100;
    return `${width}%`;
  };

  const getRegionLeft = (region: Region) => {
    const left = (region.start / alignmentLength) * 100;
    return `${left}%`;
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Region Overview
      </Typography>
      
      {regions.length === 0 ? (
        <Typography variant="body2" color="text.secondary">
          No regions annotated yet
        </Typography>
      ) : (
        <Box>
          {/* Region legend */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Region Types
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {Array.from(new Set(regions.map(r => r.type))).map(type => {
                const typeRegions = regions.filter(r => r.type === type);
                const color = typeRegions[0]?.color || '#ccc';
                
                return (
                  <Chip
                    key={type}
                    label={type.toUpperCase()}
                    size="small"
                    sx={{
                      backgroundColor: color + '20',
                      border: `1px solid ${color}`,
                      color: color,
                    }}
                  />
                );
              })}
            </Box>
          </Box>

          {/* Region timeline */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Region Positions
            </Typography>
            <Box sx={{ 
              position: 'relative', 
              height: 40, 
              border: '1px solid',
              borderColor: 'divider',
              borderRadius: 1,
              overflow: 'hidden'
            }}>
              {/* Position markers */}
              <Box sx={{ 
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                px: 1
              }}>
                {Array.from({ length: 11 }, (_, i) => {
                  const position = Math.floor((i / 10) * alignmentLength);
                  return (
                    <Box
                      key={i}
                      sx={{
                        position: 'absolute',
                        left: `${(i / 10) * 100}%`,
                        transform: 'translateX(-50%)',
                        fontSize: '10px',
                        color: 'text.secondary',
                        fontWeight: 'bold'
                      }}
                    >
                      {position}
                    </Box>
                  );
                })}
              </Box>

              {/* Region bars */}
              {regions.map((region) => (
                <Tooltip
                  key={region.id}
                  title={
                    <Box>
                      <Typography variant="caption">
                        <strong>{region.name}</strong>
                      </Typography>
                      <Typography variant="caption" display="block">
                        Positions: {region.start}-{region.stop}
                      </Typography>
                      <Typography variant="caption" display="block">
                        Type: {region.type}
                      </Typography>
                    </Box>
                  }
                  arrow
                >
                  <Box
                    onClick={() => handleRegionClick(region.id)}
                    sx={{
                      position: 'absolute',
                      left: getRegionLeft(region),
                      width: getRegionWidth(region),
                      height: '100%',
                      backgroundColor: region.color + '60',
                      border: `2px solid ${region.color}`,
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      opacity: selectedRegions.includes(region.id) ? 1 : 0.7,
                      '&:hover': {
                        opacity: 1,
                        transform: 'scaleY(1.1)',
                      },
                    }}
                  />
                </Tooltip>
              ))}
            </Box>
          </Box>

          {/* Region list */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Region Details
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {regions.map((region) => (
                <Chip
                  key={region.id}
                  label={`${region.name} (${region.start}-${region.stop})`}
                  size="small"
                  onClick={() => handleRegionClick(region.id)}
                  sx={{
                    backgroundColor: selectedRegions.includes(region.id) 
                      ? region.color 
                      : region.color + '20',
                    color: selectedRegions.includes(region.id) ? 'white' : region.color,
                    border: `1px solid ${region.color}`,
                    cursor: 'pointer',
                    '&:hover': {
                      backgroundColor: region.color,
                      color: 'white',
                    },
                  }}
                />
              ))}
            </Box>
          </Box>
        </Box>
      )}
    </Paper>
  );
};
