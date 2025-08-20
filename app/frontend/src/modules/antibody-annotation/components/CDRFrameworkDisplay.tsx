/**
 * CDR/Framework Display Component
 * 
 * Displays CDR and framework regions extracted from IgBLAST analysis results
 */

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Paper,
  Stack,
  Chip,
  Tooltip,
  IconButton,
  Collapse,
  Divider,
  Grid,
  Alert,
} from '@mui/material';
import {
  ExpandMore,
  ExpandLess,
  Info,
  Science,
  Biotech,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';

const StyledCard = styled(Card)(({ theme }) => ({
  marginBottom: theme.spacing(2),
  borderRadius: theme.spacing(2),
  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  '&:hover': {
    boxShadow: '0 8px 24px rgba(0, 0, 0, 0.15)',
    transform: 'translateY(-2px)',
  },
}));

const RegionChip = styled(Chip)<{ regionType: string }>(({ theme, regionType }) => {
  const colors = {
    FWR1: { bg: '#E3F2FD', border: '#1976D2', text: '#0D47A1' },
    CDR1: { bg: '#FFE0B2', border: '#F57C00', text: '#E65100' },
    FWR2: { bg: '#E8F5E8', border: '#388E3C', text: '#1B5E20' },
    CDR2: { bg: '#FCE4EC', border: '#C2185B', text: '#880E4F' },
    FWR3: { bg: '#F3E5F5', border: '#7B1FA2', text: '#4A148C' },
    CDR3: { bg: '#FFEBEE', border: '#D32F2F', text: '#B71C1C' },
    FWR4: { bg: '#E0F2F1', border: '#00796B', text: '#004D40' },
  };
  
  const colorScheme = colors[regionType as keyof typeof colors] || colors.FWR1;
  
  return {
    backgroundColor: colorScheme.bg,
    color: colorScheme.text,
    border: `1px solid ${colorScheme.border}`,
    fontWeight: 500,
    margin: theme.spacing(0.25),
  };
});

const SequenceDisplay = styled(Box)(({ theme }) => ({
  fontFamily: 'Monaco, Consolas, "Courier New", monospace',
  fontSize: '14px',
  lineHeight: 1.6,
  backgroundColor: '#FAFAFA',
  border: '1px solid #E0E0E0',
  borderRadius: theme.spacing(1),
  padding: theme.spacing(2),
  overflow: 'auto',
  maxHeight: '200px',
  position: 'relative',
}));

const RegionHighlight = styled(Box, {
  shouldForwardProp: (prop) => !['regionType', 'start', 'end', 'sequenceLength'].includes(prop as string),
})<{ 
  regionType: string; 
  start: number; 
  end: number; 
  sequenceLength: number;
}>(({ theme, regionType, start, end, sequenceLength }) => {
  const colors = {
    FWR1: '#E3F2FD',
    CDR1: '#FFE0B2',
    FWR2: '#E8F5E8',
    CDR2: '#FCE4EC',
    FWR3: '#F3E5F5',
    CDR3: '#FFEBEE',
    FWR4: '#E0F2F1',
  };
  
  const color = colors[regionType as keyof typeof colors] || '#E3F2FD';
  const width = ((end - start + 1) / sequenceLength) * 100;
  const left = (start / sequenceLength) * 100;
  
  return {
    position: 'absolute',
    top: '0',
    left: `${left}%`,
    width: `${width}%`,
    height: '100%',
    backgroundColor: color,
    opacity: 0.3,
    border: `1px solid ${color.replace('0.3', '0.8')}`,
    borderRadius: '2px',
    pointerEvents: 'none',
    zIndex: 1,
  };
});

interface CDRFrameworkData {
  fwr1_sequence?: string;
  cdr1_sequence?: string;
  fwr2_sequence?: string;
  cdr2_sequence?: string;
  fwr3_sequence?: string;
  cdr3_sequence?: string;
  fwr4_sequence?: string;
  cdr3_start?: number;
  cdr3_end?: number;
  cdr3_aa?: string;
}

interface CDRFrameworkDisplayProps {
  data: CDRFrameworkData;
  sequence?: string;
  sequenceType?: 'nucleotide' | 'protein';
}

export const CDRFrameworkDisplay: React.FC<CDRFrameworkDisplayProps> = ({
  data,
  sequence,
  sequenceType = 'protein',
}) => {
  const [expanded, setExpanded] = useState<string | false>('overview');
  const [hoveredRegion, setHoveredRegion] = useState<string | null>(null);

  const handleAccordionChange = (panel: string) => (
    event: React.SyntheticEvent,
    isExpanded: boolean
  ) => {
    setExpanded(isExpanded ? panel : false);
  };

  const regions = [
    { key: 'fwr1_sequence', name: 'FWR1', label: 'Framework Region 1', type: 'FWR1' },
    { key: 'cdr1_sequence', name: 'CDR1', label: 'Complementarity-Determining Region 1', type: 'CDR1' },
    { key: 'fwr2_sequence', name: 'FWR2', label: 'Framework Region 2', type: 'FWR2' },
    { key: 'cdr2_sequence', name: 'CDR2', label: 'Complementarity-Determining Region 2', type: 'CDR2' },
    { key: 'fwr3_sequence', name: 'FWR3', label: 'Framework Region 3', type: 'FWR3' },
    { key: 'cdr3_sequence', name: 'CDR3', label: 'Complementarity-Determining Region 3', type: 'CDR3' },
  ];

  const availableRegions = regions.filter(region => data[region.key as keyof CDRFrameworkData]);

  const renderRegionOverview = () => (
    <Box>
      <Typography variant="h6" gutterBottom color="primary">
        <Science sx={{ mr: 1, verticalAlign: 'middle' }} />
        CDR/Framework Regions Overview
      </Typography>
      
      {availableRegions.length > 0 ? (
        <Grid container spacing={2}>
          {availableRegions.map((region) => (
            <Grid item xs={12} sm={6} md={4} key={region.key}>
              <Paper 
                variant="outlined" 
                sx={{ 
                  p: 2, 
                  height: '100%',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
                    transform: 'translateY(-2px)',
                    borderColor: 'primary.main',
                  },
                }}
                onClick={() => setExpanded('detailed')}
                onMouseEnter={() => setHoveredRegion(region.name)}
                onMouseLeave={() => setHoveredRegion(null)}
              >
                <Stack direction="row" alignItems="center" spacing={1} mb={1}>
                  <RegionChip
                    label={region.name}
                    regionType={region.type}
                    size="small"
                  />
                  <Tooltip title={`Click to view detailed analysis of ${region.label}`}>
                    <IconButton size="small">
                      <Info fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Stack>
                
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {region.label}
                </Typography>
                
                {data[region.key as keyof CDRFrameworkData] && (
                  <Typography
                    variant="body2"
                    fontFamily="monospace"
                    sx={{
                      wordBreak: 'break-all',
                      backgroundColor: '#f5f5f5',
                      padding: 1,
                      borderRadius: 1,
                      fontSize: '12px',
                    }}
                  >
                    {data[region.key as keyof CDRFrameworkData]}
                  </Typography>
                )}
                
                {/* Special handling for CDR3 */}
                {region.key === 'cdr3_sequence' && data.cdr3_start && data.cdr3_end && (
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                    Position: {data.cdr3_start} - {data.cdr3_end}
                  </Typography>
                )}
                
                <Typography variant="caption" color="primary" sx={{ mt: 1, display: 'block', fontStyle: 'italic' }}>
                  Click for detailed analysis
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>
      ) : (
        <Alert severity="info">
          No CDR/framework region data available. This may be because:
          <ul>
            <li>The IgBLAST analysis didn't identify antibody regions</li>
            <li>The sequence is not an antibody sequence</li>
            <li>The analysis used protein IgBLAST (igblastp) which has limited region information</li>
          </ul>
        </Alert>
      )}
    </Box>
  );

  const renderDetailedView = () => (
    <Box>
      <Typography variant="h6" gutterBottom color="primary">
        <Biotech sx={{ mr: 1, verticalAlign: 'middle' }} />
        Detailed Region Analysis
      </Typography>
      
      {availableRegions.map((region, index) => (
        <Paper 
          key={region.key} 
          variant="outlined" 
          sx={{ 
            p: 2, 
            mb: 2,
            border: hoveredRegion === region.name ? '2px solid primary.main' : '1px solid',
            backgroundColor: hoveredRegion === region.name ? 'rgba(25, 118, 210, 0.04)' : 'transparent',
            transition: 'all 0.2s ease-in-out',
          }}
        >
          <Stack direction="row" alignItems="center" spacing={1} mb={2}>
            <RegionChip
              label={region.name}
              regionType={region.type}
            />
            <Typography variant="subtitle1" fontWeight="bold">
              {region.label}
            </Typography>
          </Stack>
          
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom>
                Sequence ({sequenceType})
              </Typography>
              <SequenceDisplay>
                {data[region.key as keyof CDRFrameworkData] || 'Not available'}
              </SequenceDisplay>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom>
                Region Information
              </Typography>
              <Stack spacing={1}>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Region Type:
                  </Typography>
                  <Typography variant="body2">
                    {region.name} ({region.label})
                  </Typography>
                </Box>
                
                {region.key === 'cdr3_sequence' && data.cdr3_start && data.cdr3_end && (
                  <>
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Position:
                      </Typography>
                      <Typography variant="body2">
                        {data.cdr3_start} - {data.cdr3_end} (length: {data.cdr3_end - data.cdr3_start + 1})
                      </Typography>
                    </Box>
                    
                    {data.cdr3_aa && (
                      <Box>
                        <Typography variant="caption" color="text.secondary">
                          Amino Acid Sequence:
                        </Typography>
                        <Typography
                          variant="body2"
                          fontFamily="monospace"
                          sx={{ backgroundColor: '#f5f5f5', padding: 1, borderRadius: 1 }}
                        >
                          {data.cdr3_aa}
                        </Typography>
                      </Box>
                    )}
                  </>
                )}
              </Stack>
            </Grid>
          </Grid>
        </Paper>
      ))}
    </Box>
  );

  const renderSequenceVisualization = () => {
    if (!sequence) {
      return (
        <Alert severity="info">
          No sequence data available for visualization.
        </Alert>
      );
    }

    // Helper function to check if a position is within a region
    const isPositionInRegion = (position: number, regionType: string) => {
      switch (regionType) {
        case 'FWR1':
          return data.fr1_start && data.fr1_end && position >= data.fr1_start - 1 && position <= data.fr1_end - 1;
        case 'CDR1':
          return data.cdr1_start && data.cdr1_end && position >= data.cdr1_start - 1 && position <= data.cdr1_end - 1;
        case 'FWR2':
          return data.fr2_start && data.fr2_end && position >= data.fr2_start - 1 && position <= data.fr2_end - 1;
        case 'CDR2':
          return data.cdr2_start && data.cdr2_end && position >= data.cdr2_start - 1 && position <= data.cdr2_end - 1;
        case 'FWR3':
          return data.fr3_start && data.fr3_end && position >= data.fr3_start - 1 && position <= data.fr3_end - 1;
        case 'CDR3':
          return data.cdr3_start && data.cdr3_end && position >= data.cdr3_start - 1 && position <= data.cdr3_end - 1;
        default:
          return false;
      }
    };

    // Helper function to get region info for tooltip
    const getRegionInfo = (position: number) => {
      if (isPositionInRegion(position, 'FWR1')) {
        return {
          name: 'Framework Region 1',
          sequence: data.fwr1_sequence,
          start: data.fr1_start,
          end: data.fr1_end,
        };
      } else if (isPositionInRegion(position, 'CDR1')) {
        return {
          name: 'Complementarity-Determining Region 1',
          sequence: data.cdr1_sequence,
          start: data.cdr1_start,
          end: data.cdr1_end,
        };
      } else if (isPositionInRegion(position, 'FWR2')) {
        return {
          name: 'Framework Region 2',
          sequence: data.fwr2_sequence,
          start: data.fr2_start,
          end: data.fr2_end,
        };
      } else if (isPositionInRegion(position, 'CDR2')) {
        return {
          name: 'Complementarity-Determining Region 2',
          sequence: data.cdr2_sequence,
          start: data.cdr2_start,
          end: data.cdr2_end,
        };
      } else if (isPositionInRegion(position, 'FWR3')) {
        return {
          name: 'Framework Region 3',
          sequence: data.fwr3_sequence,
          start: data.fr3_start,
          end: data.fr3_end,
        };
      } else if (isPositionInRegion(position, 'CDR3')) {
        return {
          name: 'Complementarity-Determining Region 3',
          sequence: data.cdr3_sequence,
          start: data.cdr3_start,
          end: data.cdr3_end,
        };
      }
      return null;
    };

    return (
      <Box>
        <Typography variant="h6" gutterBottom color="primary">
          Sequence with Region Highlights
        </Typography>
        
        <Paper variant="outlined" sx={{ p: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Full Sequence ({sequenceType})
          </Typography>
          
          <SequenceDisplay>
            {sequence.split('').map((char, index) => {
              const regionInfo = getRegionInfo(index);
              return (
                <Tooltip
                  key={index}
                  title={
                    regionInfo ? (
                      <Box>
                        <Typography variant="subtitle2" fontWeight="bold">
                          {regionInfo.name}
                        </Typography>
                        <Typography variant="body2">
                          Position: {regionInfo.start} - {regionInfo.end}
                        </Typography>
                        <Typography variant="body2" fontFamily="monospace">
                          Sequence: {regionInfo.sequence}
                        </Typography>
                      </Box>
                    ) : (
                      <Typography variant="body2">
                        Position: {index + 1}
                      </Typography>
                    )
                  }
                  arrow
                  placement="top"
                >
                  <span 
                    style={{ 
                      position: 'relative', 
                      zIndex: 2,
                      cursor: regionInfo ? 'pointer' : 'default',
                      backgroundColor: regionInfo ? 'rgba(255, 255, 0, 0.2)' : 'transparent',
                      borderRadius: '2px',
                      padding: '1px',
                    }}
                    onMouseEnter={() => regionInfo && setHoveredRegion(regionInfo.name)}
                    onMouseLeave={() => setHoveredRegion(null)}
                  >
                    {char}
                  </span>
                </Tooltip>
              );
            })}
            
            {/* Add region highlights for all available regions */}
            {/* Convert 1-based coordinates to 0-based for frontend positioning */}
            {data.fr1_start && data.fr1_end && (
              <RegionHighlight
                regionType="FWR1"
                start={data.fr1_start - 1}
                end={data.fr1_end - 1}
                sequenceLength={sequence.length}
              />
            )}
            
            {data.cdr1_start && data.cdr1_end && (
              <RegionHighlight
                regionType="CDR1"
                start={data.cdr1_start - 1}
                end={data.cdr1_end - 1}
                sequenceLength={sequence.length}
              />
            )}
            
            {data.fr2_start && data.fr2_end && (
              <RegionHighlight
                regionType="FWR2"
                start={data.fr2_start - 1}
                end={data.fr2_end - 1}
                sequenceLength={sequence.length}
              />
            )}
            
            {data.cdr2_start && data.cdr2_end && (
              <RegionHighlight
                regionType="CDR2"
                start={data.cdr2_start - 1}
                end={data.cdr2_end - 1}
                sequenceLength={sequence.length}
              />
            )}
            
            {data.fr3_start && data.fr3_end && (
              <RegionHighlight
                regionType="FWR3"
                start={data.fr3_start - 1}
                end={data.fr3_end - 1}
                sequenceLength={sequence.length}
              />
            )}
            
            {data.cdr3_start && data.cdr3_end && (
              <RegionHighlight
                regionType="CDR3"
                start={data.cdr3_start - 1}
                end={data.cdr3_end - 1}
                sequenceLength={sequence.length}
              />
            )}
          </SequenceDisplay>
          
          <Box sx={{ mt: 2 }}>
            <Typography variant="caption" color="text.secondary">
              Legend: Hover over highlighted regions to see detailed information. Click on regions for more details.
            </Typography>
          </Box>
        </Paper>
      </Box>
    );
  };

  return (
    <StyledCard>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          CDR/Framework Analysis
        </Typography>
        
        <Typography variant="body2" color="text.secondary" paragraph>
          Complementarity-Determining Regions (CDRs) and Framework Regions (FWRs) 
          extracted from IgBLAST analysis results.
        </Typography>

        {/* Overview Section */}
        <Box sx={{ mb: 3 }}>
          <Box
            display="flex"
            alignItems="center"
            justifyContent="space-between"
            sx={{ cursor: 'pointer' }}
            onClick={(e) => handleAccordionChange('overview')(e, expanded !== 'overview')}
          >
            <Typography variant="h6">Overview</Typography>
            {expanded === 'overview' ? <ExpandLess /> : <ExpandMore />}
          </Box>
          <Collapse in={expanded === 'overview'}>
            <Box sx={{ mt: 2 }}>
              {renderRegionOverview()}
            </Box>
          </Collapse>
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* Detailed Analysis Section */}
        <Box sx={{ mb: 3 }}>
          <Box
            display="flex"
            alignItems="center"
            justifyContent="space-between"
            sx={{ cursor: 'pointer' }}
            onClick={(e) => handleAccordionChange('detailed')(e, expanded !== 'detailed')}
          >
            <Typography variant="h6">Detailed Analysis</Typography>
            {expanded === 'detailed' ? <ExpandLess /> : <ExpandMore />}
          </Box>
          <Collapse in={expanded === 'detailed'}>
            <Box sx={{ mt: 2 }}>
              {renderDetailedView()}
            </Box>
          </Collapse>
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* Sequence Visualization Section */}
        <Box>
          <Box
            display="flex"
            alignItems="center"
            justifyContent="space-between"
            sx={{ cursor: 'pointer' }}
            onClick={(e) => handleAccordionChange('visualization')(e, expanded !== 'visualization')}
          >
            <Typography variant="h6">Sequence Visualization</Typography>
            {expanded === 'visualization' ? <ExpandLess /> : <ExpandMore />}
          </Box>
          <Collapse in={expanded === 'visualization'}>
            <Box sx={{ mt: 2 }}>
              {renderSequenceVisualization()}
            </Box>
          </Collapse>
        </Box>
      </CardContent>
    </StyledCard>
  );
};

export default CDRFrameworkDisplay;
