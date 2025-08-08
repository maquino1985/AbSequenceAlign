import React from 'react';
import { Box, Card, CardContent, Typography } from '@mui/material';
import type { SequenceData, ColorScheme } from '../../types/sequence';
import { DomainGraphics } from '../Visualization/DomainGraphics';
import { AminoAcidSequence } from '../Visualization/AminoAcidSequence';

interface SequenceCardsProps {
  sequences: SequenceData[];
  selectedRegions: string[];
  colorScheme: ColorScheme;
  onRegionSelect: (regionId: string) => void;
  onColorSchemeChange: (colorScheme: ColorScheme) => void;
  onPositionSelect?: (position: number) => void;
  selectedPositions?: number[];
}

export const SequenceCards: React.FC<SequenceCardsProps> = ({
  sequences,
  selectedRegions,
  colorScheme,
  onRegionSelect,
  onColorSchemeChange,
  onPositionSelect,
  selectedPositions = []
}) => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      {sequences.map((sequence) => (
        <Card key={sequence.id} variant="outlined">
          <CardContent>
            {sequence.chains.map((chain) => (
              <Box key={chain.id}>
                
                {/* Domain Graphics Visualization */}
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Domain Structure
                  </Typography>
                  <DomainGraphics
                    regions={chain.annotations}
                    sequenceLength={chain.sequence.length}
                    width={800}
                    height={80}
                    onRegionClick={(region) => onRegionSelect(region.id)}
                    selectedRegions={selectedRegions}
                  />
                </Box>
                
                {/* Interactive Amino Acid Sequence */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Amino Acid Sequence
                  </Typography>
                  <AminoAcidSequence
                    sequence={chain.sequence}
                    regions={chain.annotations}
                    colorScheme={colorScheme}
                    onAminoAcidClick={(position) => {
                      if (onPositionSelect) {
                        onPositionSelect(position);
                      }
                    }}
                    onColorSchemeChange={onColorSchemeChange}
                    selectedPositions={selectedPositions}
                    selectedRegions={selectedRegions}
                  />
                </Box>
                
                {/* Region Summary Chips */}
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Regions ({chain.annotations.length})
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {chain.annotations.map((region) => (
                      <Box
                        key={region.id}
                        sx={{
                          px: 1.5,
                          py: 0.5,
                          bgcolor: region.color,
                          color: 'white',
                          borderRadius: 1,
                          fontSize: '0.875rem',
                          cursor: 'pointer',
                          opacity: selectedRegions.includes(region.id) ? 1 : 0.8,
                          border: selectedRegions.includes(region.id) ? '2px solid #000' : '1px solid transparent',
                          transition: 'all 0.2s ease',
                          '&:hover': {
                            opacity: 1,
                            transform: 'translateY(-1px)',
                            boxShadow: 2
                          }
                        }}
                        onClick={() => onRegionSelect(region.id)}
                      >
                        <Typography variant="caption" component="span" sx={{ fontWeight: 'bold' }}>
                          {region.name}
                        </Typography>
                        <Typography variant="caption" component="span" sx={{ ml: 1, opacity: 0.9 }}>
                          {region.start}-{region.stop} ({region.sequence.length} AA)
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                </Box>
              </Box>
            ))}
          </CardContent>
        </Card>
      ))}
    </Box>
  );
};

export default SequenceCards;
