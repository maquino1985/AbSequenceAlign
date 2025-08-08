import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Alert,
  Snackbar,
  CircularProgress,
  Backdrop,
  Tabs,
  Tab
} from '@mui/material';
import { FastaInput } from './SequenceInput/FastaInput';
import { SequenceCards } from './SequenceCards/SequenceCards';
import { FeatureTable } from './FeatureTable/FeatureTable';
import { useApi } from '../hooks/useApi';
import { useSequenceData } from '../hooks/useSequenceData';
import type { SequenceInput, NumberingScheme } from '../types/api';
import { parseFasta, validateSequence } from '../utils/fastaParser';

export const SequenceAnnotationTool: React.FC = () => {
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'warning' | 'info';
  }>({
    open: false,
    message: '',
    severity: 'info'
  });

  const [selectedTab, setSelectedTab] = useState(0);

  const { annotation, annotateSequences } = useApi();
  const {
    sequences,
    selectedRegions,
    selectedPositions,
    colorScheme,
    setSequences,
    selectRegion,
    selectPosition,
    setColorScheme
  } = useSequenceData();

  const handleSequenceSubmit = async (
    fastaContent: string,
    numberingScheme: NumberingScheme
  ) => {
    try {
      // Parse FASTA content
      const parsedSequences = parseFasta(fastaContent);
      
      if (parsedSequences.length === 0) {
        setSnackbar({
          open: true,
          message: 'No valid sequences found in FASTA content',
          severity: 'error'
        });
        return;
      }

      // Validate sequences
      const validationErrors: string[] = [];
      parsedSequences.forEach((seq, index) => {
        const { isValid, errors } = validateSequence(seq.sequence);
        if (!isValid) {
          validationErrors.push(`Sequence ${index + 1} (${seq.id}): ${errors.join(', ')}`);
        }
      });

      if (validationErrors.length > 0) {
        setSnackbar({
          open: true,
          message: `Validation errors: ${validationErrors.join('; ')}`,
          severity: 'error'
        });
        return;
      }

      // Convert to API format - use custom_chains to preserve original names
      const sequenceInputs: SequenceInput[] = parsedSequences.map(seq => ({
        name: seq.id,
        custom_chains: {
          [seq.id]: seq.sequence // Use the original FASTA header as the chain name
        }
      }));

      // Submit for annotation
      const result = await annotateSequences({
        sequences: sequenceInputs,
        numbering_scheme: numberingScheme
      });

      // Update sequence data
      setSequences(result);

      setSnackbar({
        open: true,
        message: `Successfully annotated ${result.total_sequences} sequences`,
        severity: 'success'
      });

      // Reset tab to first sequence
      setSelectedTab(0);

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      setSnackbar({
        open: true,
        message: `Annotation failed: ${errorMessage}`,
        severity: 'error'
      });
    }
  };

  const handleSnackbarClose = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  return (
    <Box>
      {/* Loading Backdrop */}
      <Backdrop
        sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1 }}
        open={annotation.loading}
      >
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
          <CircularProgress color="inherit" />
          <Typography variant="h6">
            Annotating sequences...
          </Typography>
        </Box>
      </Backdrop>

      {/* Input Section */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          Sequence Input
        </Typography>
        <FastaInput onSubmit={handleSequenceSubmit} />
      </Paper>

      {/* Results Section */}
      {sequences.length > 0 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h5" gutterBottom>
            Sequence Analysis Results
          </Typography>
          
          {/* Tabs for multiple sequences */}
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
            <Tabs 
              value={selectedTab} 
              onChange={(_, newValue) => setSelectedTab(newValue)}
              variant="scrollable"
              scrollButtons="auto"
            >
              {sequences.map((sequence, index) => (
                <Tab 
                  key={sequence.id} 
                  label={sequence.name}
                  id={`sequence-tab-${index}`}
                  aria-controls={`sequence-tabpanel-${index}`}
                />
              ))}
            </Tabs>
          </Box>

          {/* Tab Panels */}
          {sequences.map((sequence, index) => (
            <Box
              key={sequence.id}
              role="tabpanel"
              hidden={selectedTab !== index}
              id={`sequence-tabpanel-${index}`}
              aria-labelledby={`sequence-tab-${index}`}
            >
              {selectedTab === index && (
                <Box>
                  {/* Display each chain separately */}
                  {sequence.chains.map((chain, chainIndex) => (
                    <Box key={chain.id} sx={{ mb: 4 }}>
                      {/* Chain Header */}
                      <Typography variant="h5" gutterBottom sx={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        gap: 1,
                        pb: 1,
                        borderBottom: '2px solid',
                        borderColor: 'primary.main'
                      }}>
                        {chain.type} Chain
                        <Typography variant="body1" color="text.secondary">
                          ({chain.sequence.length} amino acids, {chain.annotations.length} regions)
                        </Typography>
                      </Typography>

                      {/* Chain Visualization */}
                      <Box sx={{ mb: 3 }}>
                        <Typography variant="h6" gutterBottom>
                          Visualization
                        </Typography>
                        <SequenceCards
                          sequences={[{
                            ...sequence,
                            chains: [chain] // Show only this chain
                          }]}
                          selectedRegions={selectedRegions}
                          selectedPositions={selectedPositions}
                          colorScheme={colorScheme}
                          onRegionSelect={selectRegion}
                          onPositionSelect={selectPosition}
                          onColorSchemeChange={setColorScheme}
                        />
                      </Box>

                      {/* Feature Table for this chain only */}
                      <Box sx={{ mb: 4 }}>
                        <Typography variant="h6" gutterBottom>
                          Feature Table - {chain.type} Chain
                        </Typography>
                        <FeatureTable
                          regions={chain.annotations}
                          selectedRegions={selectedRegions}
                          onRegionSelect={selectRegion}
                        />
                      </Box>

                      {/* Divider between chains (if multiple) */}
                      {chainIndex < sequence.chains.length - 1 && (
                        <Box sx={{ my: 4 }}>
                          <hr style={{ border: '1px solid #e0e0e0' }} />
                        </Box>
                      )}
                    </Box>
                  ))}
                </Box>
              )}
            </Box>
          ))}
        </Paper>
      )}

      {/* Error Display */}
      {annotation.error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {annotation.error}
        </Alert>
      )}

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleSnackbarClose} 
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};
