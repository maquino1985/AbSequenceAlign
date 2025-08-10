import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Chip,
  Tooltip,
} from '@mui/material';
import { Info } from '@mui/icons-material';

interface ConsensusSequenceProps {
  consensus: string;
  conservationScores?: number[];
  qualityScores?: number[];
  showQuality?: boolean;
  showConservation?: boolean;
  maxWidth?: string;
}

export const ConsensusSequence: React.FC<ConsensusSequenceProps> = ({
  consensus,
  conservationScores = [],
  qualityScores = [],
  showQuality = true,
  showConservation = true,
  maxWidth = '100%'
}) => {
  const getConservationColor = (score: number) => {
    if (score >= 0.8) return '#4caf50'; // High conservation - green
    if (score >= 0.6) return '#ff9800'; // Medium conservation - orange
    if (score >= 0.4) return '#f44336'; // Low conservation - red
    return '#9e9e9e'; // Very low conservation - grey
  };

  const getQualityColor = (score: number) => {
    if (score >= 0.8) return '#4caf50'; // High quality - green
    if (score >= 0.6) return '#ff9800'; // Medium quality - orange
    if (score >= 0.4) return '#f44336'; // Low quality - red
    return '#9e9e9e'; // Very low quality - grey
  };

  return (
    <Paper sx={{ p: 2, maxWidth, overflow: 'hidden' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <Typography variant="h6" component="h3">
          Consensus Sequence
        </Typography>
        <Chip 
          label={`${consensus.length} positions`} 
          size="small" 
          color="primary" 
          variant="outlined"
        />
        {conservationScores.length > 0 && (
          <Chip 
            label={`${(conservationScores.reduce((a, b) => a + b, 0) / conservationScores.length * 100).toFixed(1)}% avg conservation`} 
            size="small" 
            color="secondary" 
            variant="outlined"
          />
        )}
      </Box>

      {/* Consensus Sequence Display */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Consensus:
        </Typography>
        <Box
          sx={{
            fontFamily: 'monospace',
            fontSize: '14px',
            lineHeight: 1.5,
            backgroundColor: 'background.default',
            p: 1,
            borderRadius: 1,
            border: '1px solid',
            borderColor: 'divider',
            overflowX: 'auto',
            whiteSpace: 'nowrap'
          }}
        >
          {consensus.split('').map((aa, index) => (
            <Tooltip
              key={index}
              title={
                <Box>
                  <Typography variant="caption">
                    Position {index + 1}: {aa}
                  </Typography>
                  {conservationScores[index] !== undefined && (
                    <Typography variant="caption" display="block">
                      Conservation: {(conservationScores[index] * 100).toFixed(1)}%
                    </Typography>
                  )}
                  {qualityScores[index] !== undefined && (
                    <Typography variant="caption" display="block">
                      Quality: {(qualityScores[index] * 100).toFixed(1)}%
                    </Typography>
                  )}
                </Box>
              }
            >
              <span
                style={{
                  display: 'inline-block',
                  padding: '2px 1px',
                  margin: '0 1px',
                  borderRadius: '2px',
                  backgroundColor: conservationScores[index] !== undefined 
                    ? getConservationColor(conservationScores[index]) + '20'
                    : 'transparent',
                  border: conservationScores[index] !== undefined 
                    ? `1px solid ${getConservationColor(conservationScores[index])}`
                    : '1px solid transparent',
                  fontWeight: conservationScores[index] !== undefined && conservationScores[index] > 0.8 
                    ? 'bold' 
                    : 'normal'
                }}
              >
                {aa}
              </span>
            </Tooltip>
          ))}
        </Box>
      </Box>

      {/* Conservation/Quality Bars */}
      {(showConservation && conservationScores.length > 0) || (showQuality && qualityScores.length > 0) ? (
        <Box sx={{ mt: 2 }}>
          {showConservation && conservationScores.length > 0 && (
            <Box sx={{ mb: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                <Typography variant="caption" color="text.secondary">
                  Conservation
                </Typography>
                <Tooltip title="Shows how conserved each position is across all sequences">
                  <Info fontSize="small" sx={{ color: 'text.secondary' }} />
                </Tooltip>
              </Box>
              <Box sx={{ display: 'flex', gap: 0.5, height: 8 }}>
                {conservationScores.map((score, index) => (
                  <Tooltip key={index} title={`Position ${index + 1}: ${(score * 100).toFixed(1)}%`}>
                    <Box
                      sx={{
                        flex: 1,
                        backgroundColor: getConservationColor(score),
                        borderRadius: 0.5,
                        opacity: 0.8
                      }}
                    />
                  </Tooltip>
                ))}
              </Box>
            </Box>
          )}

          {showQuality && qualityScores.length > 0 && (
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                <Typography variant="caption" color="text.secondary">
                  Quality
                </Typography>
                <Tooltip title="Shows the confidence in the consensus call at each position">
                  <Info fontSize="small" sx={{ color: 'text.secondary' }} />
                </Tooltip>
              </Box>
              <Box sx={{ display: 'flex', gap: 0.5, height: 8 }}>
                {qualityScores.map((score, index) => (
                  <Tooltip key={index} title={`Position ${index + 1}: ${(score * 100).toFixed(1)}%`}>
                    <Box
                      sx={{
                        flex: 1,
                        backgroundColor: getQualityColor(score),
                        borderRadius: 0.5,
                        opacity: 0.8
                      }}
                    />
                  </Tooltip>
                ))}
              </Box>
            </Box>
          )}
        </Box>
      ) : null}
    </Paper>
  );
};

