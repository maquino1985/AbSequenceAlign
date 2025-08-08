import React, { useState } from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Tabs, 
  Tab
} from '@mui/material';
import type { SequenceData, ColorScheme } from '../../../../types/sequence';
import { DomainGraphics } from '../Visualization/DomainGraphics';
import { AminoAcidSequence } from '../Visualization/AminoAcidSequence';
import { FeatureTable } from '../FeatureTable/FeatureTable';

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
  const [selectedTab, setSelectedTab] = useState(0);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      {sequences.map((sequence) => (
        <Card key={sequence.id} variant="outlined">
          <CardContent>
            <Typography variant="h6" gutterBottom>
              {sequence.name}
            </Typography>
            
            {sequence.chains.map((chain) => (
              <Box key={chain.id}>
                <Typography variant="subtitle1" gutterBottom>
                  {chain.type} Chain
                </Typography>
                
                {/* Tabbed Interface */}
                <Box sx={{ width: '100%' }}>
                  <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                    <Tabs 
                      value={selectedTab} 
                      onChange={handleTabChange}
                      aria-label="sequence analysis tabs"
                    >
                      <Tab label="Sequence" />
                      <Tab label="Domain Structure" />
                      <Tab label="Features" />
                    </Tabs>
                  </Box>
                  
                  {/* Tab Content */}
                  <Box sx={{ mt: 2 }}>
                    {selectedTab === 0 && (
                      <Box>
                        <Typography variant="subtitle2" gutterBottom>
                          Interactive Amino Acid Sequence
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
                    )}
                    
                    {selectedTab === 1 && (
                      <Box>
                        <Typography variant="subtitle2" gutterBottom>
                          Domain Structure Visualization
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
                    )}
                    
                    {selectedTab === 2 && (
                      <Box>
                        <Typography variant="subtitle2" gutterBottom>
                          Feature Table
                        </Typography>
                        <FeatureTable
                          regions={chain.annotations}
                          selectedRegions={selectedRegions}
                          onRegionSelect={onRegionSelect}
                        />
                      </Box>
                    )}
                  </Box>
                </Box>
                
                {/* Region Summary Chips */}
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
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
                          {region.start}-{region.stop}
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
