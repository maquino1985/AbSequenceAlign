import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Chip,
  Tooltip,
  IconButton,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import { ZoomIn, ZoomOut, FilterList } from '@mui/icons-material';

interface PSSMData {
  position_frequencies: Array<Record<string, number>>;
  position_scores: Array<Record<string, number>>;
  conservation_scores: number[];
  consensus: string;
  amino_acids: string[];
  alignment_length: number;
  num_sequences: number;
}

interface PSSMVisualizationProps {
  pssmData: PSSMData;
  maxWidth?: string;
  maxHeight?: string;
}

export const PSSMVisualization: React.FC<PSSMVisualizationProps> = ({
  pssmData,
  maxWidth = '100%',
  maxHeight = '400px'
}) => {
  const [displayMode, setDisplayMode] = useState<'frequencies' | 'scores'>('scores');
  const [zoomLevel, setZoomLevel] = useState(1);
  const [startPosition, setStartPosition] = useState(0);
  const [visiblePositions, setVisiblePositions] = useState(50);

  const getScoreColor = (score: number, mode: 'frequencies' | 'scores') => {
    if (mode === 'frequencies') {
      // Frequency mode: 0-1 scale
      if (score >= 0.8) return '#d32f2f'; // Very high - dark red
      if (score >= 0.6) return '#f44336'; // High - red
      if (score >= 0.4) return '#ff9800'; // Medium - orange
      if (score >= 0.2) return '#ffeb3b'; // Low - yellow
      return '#f5f5f5'; // Very low - light grey
    } else {
      // Score mode: log-odds scale
      if (score >= 2) return '#d32f2f'; // Very high - dark red
      if (score >= 1) return '#f44336'; // High - red
      if (score >= 0) return '#ff9800'; // Medium - orange
      if (score >= -1) return '#ffeb3b'; // Low - yellow
      return '#f5f5f5'; // Very low - light grey
    }
  };

  const getTextColor = (score: number, mode: 'frequencies' | 'scores') => {
    if (mode === 'frequencies') {
      return score >= 0.4 ? 'white' : 'black';
    } else {
      return score >= 0 ? 'white' : 'black';
    }
  };

  const handleZoomChange = (event: Event, newValue: number | number[]) => {
    setZoomLevel(newValue as number);
  };

  const handlePositionChange = (event: Event, newValue: number | number[]) => {
    setStartPosition(newValue as number);
  };

  const handleVisiblePositionsChange = (event: Event, newValue: number | number[]) => {
    setVisiblePositions(newValue as number);
  };

  const visibleData = pssmData.position_scores.slice(startPosition, startPosition + visiblePositions);
  const visibleConsensus = pssmData.consensus.slice(startPosition, startPosition + visiblePositions);
  const visibleConservation = pssmData.conservation_scores.slice(startPosition, startPosition + visiblePositions);

  return (
    <Paper sx={{ p: 2, maxWidth, maxHeight, overflow: 'hidden' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6" component="h3">
          Position-Specific Scoring Matrix
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Chip 
            label={`${pssmData.alignment_length} positions`} 
            size="small" 
            color="primary" 
            variant="outlined"
          />
          <Chip 
            label={`${pssmData.num_sequences} sequences`} 
            size="small" 
            color="secondary" 
            variant="outlined"
          />
        </Box>
      </Box>

      {/* Controls */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2, flexWrap: 'wrap' }}>
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Display Mode</InputLabel>
          <Select
            value={displayMode}
            label="Display Mode"
            onChange={(e) => setDisplayMode(e.target.value as 'frequencies' | 'scores')}
          >
            <MenuItem value="scores">Log-Odds Scores</MenuItem>
            <MenuItem value="frequencies">Frequencies</MenuItem>
          </Select>
        </FormControl>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <ZoomOut fontSize="small" />
          <Slider
            value={zoomLevel}
            onChange={handleZoomChange}
            min={0.5}
            max={3}
            step={0.1}
            sx={{ width: 100 }}
          />
          <ZoomIn fontSize="small" />
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="caption">Positions:</Typography>
          <Slider
            value={visiblePositions}
            onChange={handleVisiblePositionsChange}
            min={10}
            max={Math.min(100, pssmData.alignment_length)}
            step={5}
            sx={{ width: 100 }}
          />
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="caption">Start:</Typography>
          <Slider
            value={startPosition}
            onChange={handlePositionChange}
            min={0}
            max={Math.max(0, pssmData.alignment_length - visiblePositions)}
            step={1}
            sx={{ width: 100 }}
          />
        </Box>
      </Box>

      {/* PSSM Heatmap */}
      <Box sx={{ overflow: 'auto', maxHeight: '300px' }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          {/* Amino Acid Labels */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box sx={{ width: 80, height: 20 }} /> {/* Spacer for position labels */}
            {pssmData.amino_acids.map((aa) => (
              <Tooltip key={aa} title={aa}>
                <Box
                  sx={{
                    width: 20 * zoomLevel,
                    height: 20,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: `${12 * zoomLevel}px`,
                    fontWeight: 'bold',
                    backgroundColor: 'background.default',
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 0.5
                  }}
                >
                  {aa}
                </Box>
              </Tooltip>
            ))}
          </Box>

          {/* Position Rows */}
          {visibleData.map((positionData, posIndex) => {
            const globalPos = startPosition + posIndex;
            const consensusAA = visibleConsensus[posIndex];
            const conservation = visibleConservation[posIndex];
            
            return (
              <Box key={globalPos} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {/* Position Label */}
                <Tooltip title={`Position ${globalPos + 1}`}>
                  <Box
                    sx={{
                      width: 80,
                      height: 20 * zoomLevel,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: `${10 * zoomLevel}px`,
                      backgroundColor: 'background.default',
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 0.5,
                      fontWeight: 'bold'
                    }}
                  >
                    {globalPos + 1}
                  </Box>
                </Tooltip>

                {/* Amino Acid Scores */}
                {pssmData.amino_acids.map((aa) => {
                  const value = displayMode === 'frequencies' 
                    ? pssmData.position_frequencies[globalPos]?.[aa] || 0
                    : positionData[aa] || -10;
                  
                  return (
                    <Tooltip
                      key={aa}
                      title={
                        <Box>
                          <Typography variant="caption">
                            Position {globalPos + 1}, {aa}: {value.toFixed(3)}
                          </Typography>
                          <Typography variant="caption" display="block">
                            Conservation: {(conservation * 100).toFixed(1)}%
                          </Typography>
                          <Typography variant="caption" display="block">
                            Consensus: {consensusAA}
                          </Typography>
                        </Box>
                      }
                    >
                      <Box
                        sx={{
                          width: 20 * zoomLevel,
                          height: 20 * zoomLevel,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: `${10 * zoomLevel}px`,
                          fontWeight: 'bold',
                          backgroundColor: getScoreColor(value, displayMode),
                          color: getTextColor(value, displayMode),
                          border: '1px solid',
                          borderColor: 'divider',
                          borderRadius: 0.5,
                          cursor: 'pointer',
                          '&:hover': {
                            opacity: 0.8
                          }
                        }}
                      >
                        {aa === consensusAA ? '●' : ''}
                      </Box>
                    </Tooltip>
                  );
                })}
              </Box>
            );
          })}
        </Box>
      </Box>

      {/* Legend */}
      <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
        <Typography variant="caption" color="text.secondary">
          Legend:
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box sx={{ width: 16, height: 16, backgroundColor: '#d32f2f' }} />
          <Typography variant="caption">High</Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box sx={{ width: 16, height: 16, backgroundColor: '#ff9800' }} />
          <Typography variant="caption">Medium</Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box sx={{ width: 16, height: 16, backgroundColor: '#f5f5f5' }} />
          <Typography variant="caption">Low</Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="caption">● = Consensus</Typography>
        </Box>
      </Box>
    </Paper>
  );
};

