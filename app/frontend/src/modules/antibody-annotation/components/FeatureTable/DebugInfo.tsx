import React from 'react';
import { Box, Typography, Paper, Accordion, AccordionSummary, AccordionDetails } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { useSequenceData } from '../../../../hooks/useSequenceData';

export const DebugInfo: React.FC = () => {
  const { sequences, selectedRegions, selectedPositions } = useSequenceData();

  return (
    <Paper sx={{ p: 2, mt: 2, backgroundColor: '#f5f5f5' }}>
      <Typography variant="h6" gutterBottom>
        🔍 Debug Information
      </Typography>
      
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography>Sequences State ({sequences.length} sequences)</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Box component="pre" sx={{ fontSize: '12px', overflow: 'auto', maxHeight: '300px' }}>
            {JSON.stringify(sequences, null, 2)}
          </Box>
        </AccordionDetails>
      </Accordion>

      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography>Selected Regions ({selectedRegions.length} selected)</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Box component="pre" sx={{ fontSize: '12px', overflow: 'auto', maxHeight: '200px' }}>
            {JSON.stringify(selectedRegions, null, 2)}
          </Box>
        </AccordionDetails>
      </Accordion>

      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography>Selected Positions ({selectedPositions.length} selected)</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Box component="pre" sx={{ fontSize: '12px', overflow: 'auto', maxHeight: '200px' }}>
            {JSON.stringify(selectedPositions, null, 2)}
          </Box>
        </AccordionDetails>
      </Accordion>

      <Box sx={{ mt: 2, p: 1, backgroundColor: '#e3f2fd', borderRadius: 1 }}>
        <Typography variant="body2" color="primary">
          💡 Debug Summary:
        </Typography>
        <Typography variant="body2">
          • Sequences loaded: {sequences.length}
        </Typography>
        <Typography variant="body2">
          • Total chains: {sequences.reduce((acc, seq) => acc + seq.chains.length, 0)}
        </Typography>
        <Typography variant="body2">
          • Total annotations: {sequences.reduce((acc, seq) => 
            acc + seq.chains.reduce((acc2, chain) => acc2 + chain.annotations.length, 0), 0
          )}
        </Typography>
        <Typography variant="body2">
          • Selected regions: {selectedRegions.length}
        </Typography>
        <Typography variant="body2">
          • Selected positions: {selectedPositions.length}
        </Typography>
      </Box>
    </Paper>
  );
};
