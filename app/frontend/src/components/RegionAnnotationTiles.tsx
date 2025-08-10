import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Chip,
  Tooltip,
  IconButton,
  Collapse,
  Divider
} from '@mui/material';
import { ExpandMore, ExpandLess, Visibility, VisibilityOff } from '@mui/icons-material';

interface Region {
  id: string;
  name: string;
  start: number;
  stop: number;
  sequence: string;
  type: 'CDR' | 'FR' | 'LIABILITY' | 'MUTATION';
  color: string;
  original_start?: number;
  original_stop?: number;
}

interface RegionAnnotationTilesProps {
  regions: Region[];
  selectedRegions: string[];
  onRegionSelect: (regionId: string) => void;
  onRegionDeselect: (regionId: string) => void;
  showRegions?: boolean;
  onToggleRegions?: (show: boolean) => void;
  maxWidth?: string;
}

export const RegionAnnotationTiles: React.FC<RegionAnnotationTilesProps> = ({
  regions,
  selectedRegions,
  onRegionSelect,
  onRegionDeselect,
  showRegions = true,
  onToggleRegions,
  maxWidth = '100%'
}) => {
  const [expanded, setExpanded] = useState(true);

  const handleRegionClick = (regionId: string) => {
    if (selectedRegions.includes(regionId)) {
      onRegionDeselect(regionId);
    } else {
      onRegionSelect(regionId);
    }
  };

  const handleToggleExpanded = () => {
    setExpanded(!expanded);
  };

  const handleToggleRegions = () => {
    if (onToggleRegions) {
      onToggleRegions(!showRegions);
    }
  };

  // Group regions by type
  const regionsByType = regions.reduce((acc, region) => {
    if (!acc[region.type]) {
      acc[region.type] = [];
    }
    acc[region.type].push(region);
    return acc;
  }, {} as Record<string, Region[]>);

  const getRegionTypeColor = (type: string) => {
    switch (type) {
      case 'CDR': return '#e91e63';
      case 'FR': return '#4caf50';
      case 'LIABILITY': return '#f44336';
      case 'MUTATION': return '#ff9800';
      default: return '#9e9e9e';
    }
  };

  const getRegionTypeLabel = (type: string) => {
    switch (type) {
      case 'CDR': return 'Complementarity-Determining Region';
      case 'FR': return 'Framework Region';
      case 'LIABILITY': return 'Liability Region';
      case 'MUTATION': return 'Mutation';
      default: return type;
    }
  };

  if (regions.length === 0) {
    return null;
  }

  return (
    <Paper sx={{ p: 2, maxWidth, overflow: 'hidden' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="h6" component="h3">
            Region Annotations
          </Typography>
          <Chip 
            label={`${regions.length} regions`} 
            size="small" 
            color="primary" 
            variant="outlined"
          />
          <Chip 
            label={`${selectedRegions.length} selected`} 
            size="small" 
            color="secondary" 
            variant="outlined"
          />
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {onToggleRegions && (
            <Tooltip title={showRegions ? "Hide region overlay" : "Show region overlay"}>
              <IconButton 
                size="small" 
                onClick={handleToggleRegions}
              >
                {showRegions ? <Visibility /> : <VisibilityOff />}
              </IconButton>
            </Tooltip>
          )}
          
          <Tooltip title={expanded ? "Collapse" : "Expand"}>
            <IconButton size="small" onClick={handleToggleExpanded}>
              {expanded ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Collapse in={expanded}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {Object.entries(regionsByType).map(([type, typeRegions]) => (
            <Box key={type}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Box
                  sx={{
                    width: 12,
                    height: 12,
                    borderRadius: '50%',
                    backgroundColor: getRegionTypeColor(type)
                  }}
                />
                <Typography variant="subtitle2" fontWeight={600}>
                  {getRegionTypeLabel(type)} ({typeRegions.length})
                </Typography>
              </Box>
              
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {typeRegions.map((region) => {
                  const isSelected = selectedRegions.includes(region.id);
                  
                  return (
                    <Tooltip
                      key={region.id}
                      title={
                        <Box>
                          <Typography variant="caption">
                            <strong>{region.name}</strong>
                          </Typography>
                          <Typography variant="caption" display="block">
                            Positions: {region.start + 1}-{region.stop + 1}
                          </Typography>
                          <Typography variant="caption" display="block">
                            Length: {region.sequence?.length || 0} AA
                          </Typography>
                          <Typography variant="caption" display="block">
                            Sequence: {region.sequence || 'N/A'}
                          </Typography>
                        </Box>
                      }
                    >
                      <Chip
                        label={`${region.name} (${region.start + 1}-${region.stop + 1})`}
                        size="small"
                        onClick={() => handleRegionClick(region.id)}
                        sx={{
                          backgroundColor: isSelected ? region.color : 'transparent',
                          color: isSelected ? 'white' : 'text.primary',
                          border: `2px solid ${region.color}`,
                          cursor: 'pointer',
                          '&:hover': {
                            backgroundColor: isSelected ? region.color : region.color + '20',
                            color: isSelected ? 'white' : 'text.primary'
                          }
                        }}
                      />
                    </Tooltip>
                  );
                })}
              </Box>
            </Box>
          ))}
        </Box>

        {selectedRegions.length > 0 && (
          <>
            <Divider sx={{ my: 2 }} />
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Selected Regions:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {selectedRegions.map((regionId) => {
                  const region = regions.find(r => r.id === regionId);
                  if (!region) return null;
                  
                  return (
                    <Chip
                      key={regionId}
                      label={region.name}
                      size="small"
                      onDelete={() => onRegionDeselect(regionId)}
                      sx={{
                        backgroundColor: region.color,
                        color: 'white',
                        '& .MuiChip-deleteIcon': {
                          color: 'white'
                        }
                      }}
                    />
                  );
                })}
              </Box>
            </Box>
          </>
        )}
      </Collapse>
    </Paper>
  );
};
