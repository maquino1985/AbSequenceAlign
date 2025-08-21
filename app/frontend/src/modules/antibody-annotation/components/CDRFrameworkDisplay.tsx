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
  CardHeader,
  Typography,
  Paper,
  Alert,
  Stack,
  Tooltip,
  Chip,
  Grid,
} from '@mui/material';
import {
  Biotech,
  Visibility,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';

// StyledCard component removed as it's not used

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
  fontSize: '12px',
  lineHeight: 1.4,
  backgroundColor: '#FAFAFA',
  border: '1px solid #E0E0E0',
  borderRadius: theme.spacing(0.5),
  padding: theme.spacing(1),
  overflow: 'auto',
  maxHeight: '120px',
  position: 'relative',
}));

const RegionHighlight = styled(Box, {
  shouldForwardProp: (prop) => !['regionType', 'start', 'end', 'sequenceLength'].includes(prop as string),
})<{ 
  regionType: string; 
  start: number; 
  end: number; 
  sequenceLength: number;
}>(({ regionType, start, end, sequenceLength }) => {
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
  fwr1_aa?: string;
  fwr1_start?: number;
  fwr1_end?: number;
  cdr1_sequence?: string;
  cdr1_aa?: string;
  cdr1_start?: number;
  cdr1_end?: number;
  fwr2_sequence?: string;
  fwr2_aa?: string;
  fwr2_start?: number;
  fwr2_end?: number;
  cdr2_sequence?: string;
  cdr2_aa?: string;
  cdr2_start?: number;
  cdr2_end?: number;
  fwr3_sequence?: string;
  fwr3_aa?: string;
  fwr3_start?: number;
  fwr3_end?: number;
  cdr3_sequence?: string;
  cdr3_aa?: string;
  cdr3_start?: number;
  cdr3_end?: number;
  fwr4_sequence?: string;
  fwr4_aa?: string;
  fwr4_start?: number;
  fwr4_end?: number;
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
  const [expanded, setExpanded] = useState<string | false>(false);
  const [hoveredRegion, setHoveredRegion] = useState<string | null>(null);

  // handleAccordionChange function removed as it's not used

  const regions = [
    { key: 'fwr1_sequence', aaKey: 'fwr1_aa', name: 'FWR1', label: 'Framework Region 1', type: 'FWR1' },
    { key: 'cdr1_sequence', aaKey: 'cdr1_aa', name: 'CDR1', label: 'Complementarity-Determining Region 1', type: 'CDR1' },
    { key: 'fwr2_sequence', aaKey: 'fwr2_aa', name: 'FWR2', label: 'Framework Region 2', type: 'FWR2' },
    { key: 'cdr2_sequence', aaKey: 'cdr2_aa', name: 'CDR2', label: 'Complementarity-Determining Region 2', type: 'CDR2' },
    { key: 'fwr3_sequence', aaKey: 'fwr3_aa', name: 'FWR3', label: 'Framework Region 3', type: 'FWR3' },
    { key: 'cdr3_sequence', aaKey: 'cdr3_aa', name: 'CDR3', label: 'Complementarity-Determining Region 3', type: 'CDR3' },
  ];

  const availableRegions = regions.filter(region => data[region.key as keyof CDRFrameworkData]);

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
          return data.fwr1_start && data.fwr1_end && position >= data.fwr1_start - 1 && position <= data.fwr1_end - 1;
        case 'CDR1':
          return data.cdr1_start && data.cdr1_end && position >= data.cdr1_start - 1 && position <= data.cdr1_end - 1;
        case 'FWR2':
          return data.fwr2_start && data.fwr2_end && position >= data.fwr2_start - 1 && position <= data.fwr2_end - 1;
        case 'CDR2':
          return data.cdr2_start && data.cdr2_end && position >= data.cdr2_start - 1 && position <= data.cdr2_end - 1;
        case 'FWR3':
          return data.fwr3_start && data.fwr3_end && position >= data.fwr3_start - 1 && position <= data.fwr3_end - 1;
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
          start: data.fwr1_start,
          end: data.fwr1_end,
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
          start: data.fwr2_start,
          end: data.fwr2_end,
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
          start: data.fwr3_start,
          end: data.fwr3_end,
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
          {data.fwr1_start && data.fwr1_end && (
            <RegionHighlight
              regionType="FWR1"
              start={data.fwr1_start - 1}
              end={data.fwr1_end - 1}
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
          
          {data.fwr2_start && data.fwr2_end && (
            <RegionHighlight
              regionType="FWR2"
              start={data.fwr2_start - 1}
              end={data.fwr2_end - 1}
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
          
          {data.fwr3_start && data.fwr3_end && (
            <RegionHighlight
              regionType="FWR3"
              start={data.fwr3_start - 1}
              end={data.fwr3_end - 1}
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
      </Box>
    );
  };

  return (
    <Card>
      <CardHeader
        title="CDR/Framework Analysis"
        subheader="Complementarity-Determining Regions (CDRs) and Framework Regions (FWRs) extracted from IgBLAST analysis results"
        avatar={<Biotech color="primary" />}
      />
      <CardContent>
        {/* Single Comprehensive View */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom color="primary">
            <Biotech sx={{ mr: 1, verticalAlign: 'middle' }} />
            CDR/Framework Regions Analysis
          </Typography>
          
          {availableRegions.length > 0 ? (
            <Grid container spacing={2}>
              {availableRegions.map((region) => (
                <Grid key={region.key}>
                  <Paper 
                    variant="outlined" 
                    sx={{ 
                      p: 2,
                      height: '100%',
                      border: hoveredRegion === region.name ? '2px solid primary.main' : '1px solid',
                      backgroundColor: hoveredRegion === region.name ? 'rgba(25, 118, 210, 0.04)' : 'transparent',
                      transition: 'all 0.2s ease-in-out',
                      cursor: 'pointer',
                    }}
                    onClick={() => setExpanded(expanded === region.key ? false : region.key)}
                    onMouseEnter={() => setHoveredRegion(region.name)}
                    onMouseLeave={() => setHoveredRegion(null)}
                  >
                    <Stack direction="row" alignItems="center" spacing={1} mb={1}>
                      <RegionChip
                        label={region.name}
                        regionType={region.type}
                        size="small"
                      />
                      <Typography variant="subtitle2" fontWeight="bold">
                        {region.label}
                      </Typography>
                    </Stack>
                    
                    {data[region.key as keyof CDRFrameworkData] && (
                      <Box>
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                          Nucleotide Sequence:
                        </Typography>
                        <Typography
                          variant="body2"
                          fontFamily="monospace"
                          sx={{
                            wordBreak: 'break-all',
                            backgroundColor: '#f5f5f5',
                            padding: 0.5,
                            borderRadius: 0.5,
                            fontSize: '10px',
                            mb: 1,
                          }}
                        >
                          {data[region.key as keyof CDRFrameworkData]}
                        </Typography>
                        
                        {data[region.aaKey as keyof CDRFrameworkData] && (
                          <>
                            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                              Amino Acid Sequence:
                            </Typography>
                            <Typography
                              variant="body2"
                              fontFamily="monospace"
                              sx={{
                                wordBreak: 'break-all',
                                backgroundColor: '#E8F5E8',
                                padding: 0.5,
                                borderRadius: 0.5,
                                fontSize: '10px',
                                color: '#2E7D32',
                                fontWeight: 500,
                              }}
                            >
                              {data[region.aaKey as keyof CDRFrameworkData]}
                            </Typography>
                          </>
                        )}
                      </Box>
                    )}
                    
                    {/* Special handling for CDR3 */}
                    {region.key === 'cdr3_sequence' && data.cdr3_start && data.cdr3_end && (
                      <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                        Position: {data.cdr3_start} - {data.cdr3_end}
                      </Typography>
                    )}
                    
                    {/* Expandable detailed view */}
                    {expanded === region.key && (
                      <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid #e0e0e0' }}>
                        <Typography variant="caption" color="text.secondary" gutterBottom>
                          Region Information:
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Type: {region.name} ({region.label})
                        </Typography>
                        {region.key === 'cdr3_sequence' && data.cdr3_start && data.cdr3_end && (
                          <Typography variant="body2" color="text.secondary">
                            Length: {data.cdr3_end - data.cdr3_start + 1} nucleotides
                          </Typography>
                        )}
                      </Box>
                    )}
                    
                    <Typography variant="caption" color="primary" sx={{ mt: 1, display: 'block', fontStyle: 'italic' }}>
                      {expanded === region.key ? 'Click to collapse' : 'Click to expand'}
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

        {/* Sequence Visualization Section */}
        <Box>
          <Typography variant="h6" gutterBottom color="primary">
            <Visibility sx={{ mr: 1, verticalAlign: 'middle' }} />
            Sequence Visualization
          </Typography>
          {renderSequenceVisualization()}
        </Box>
      </CardContent>
    </Card>
  );
};

export default CDRFrameworkDisplay;
