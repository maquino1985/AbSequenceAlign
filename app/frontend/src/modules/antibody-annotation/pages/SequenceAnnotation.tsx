import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Tabs, 
  Tab,
  Alert,
  CircularProgress
} from '@mui/material';
import { FastaInput } from '../components/SequenceInput/FastaInput';
import { DomainGraphics } from '../components/Visualization/DomainGraphics';
import { AminoAcidSequence } from '../components/Visualization/AminoAcidSequence';
import { FeatureTable } from '../components/FeatureTable/FeatureTable';
import { DebugInfo } from '../components/FeatureTable/DebugInfo';
import { useSequenceData } from '../../../hooks/useSequenceData';
import type { NumberingScheme } from '../../../types/api';
import { api } from '../../../services/api';
import type { AnnotationRequestV2, AnnotationResultV2 } from '../../../types/apiV2';
import { addHistory, loadHistory, clearHistory as clearHistoryStore, type HistoryEntry } from '../../../utils/history';
import { parseFasta } from '../../../utils/fastaParser';

export const SequenceAnnotation: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedTab, setSelectedTab] = useState<number | false>(0);
  const [history, setHistory] = useState<HistoryEntry[]>(() => loadHistory());
  
  const { 
    sequences, 
    selectedRegions,
    selectedPositions,
    colorScheme,
    setColorScheme,
    selectRegion,
    selectPosition,
    setSequencesV2,
    clearSelection
  } = useSequenceData();

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
    // Reset selections when changing tabs
    clearSelection();
  };

  const handleSubmit = async (fastaContent: string, numberingScheme: NumberingScheme) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Parse FASTA content
      const parsedSequences = parseFasta(fastaContent);
      
      if (parsedSequences.length === 0) {
        throw new Error('No valid sequences found in FASTA content');
      }

      // Prepare request for API
      const request: AnnotationRequestV2 = {
        sequences: parsedSequences.map(seq => {
          // Determine sequence type based on FASTA header or sequence characteristics
          const header = seq.id.toLowerCase();
          let sequenceType = 'scfv'; // default
          
          // Check header first
          if (header.includes('heavy') || header.includes('h_chain') || header.includes('vh')) {
            sequenceType = 'heavy_chain';
          } else if (header.includes('light') || header.includes('l_chain') || header.includes('vl')) {
            sequenceType = 'light_chain';
          } else if (header.includes('kappa') || header.includes('k_chain')) {
            sequenceType = 'light_chain';
          } else if (header.includes('lambda') || header.includes('l_chain')) {
            sequenceType = 'light_chain';
          } else if (header.includes('scfv') || header.includes('single')) {
            sequenceType = 'scfv';
          } else {
            // If header doesn't give us a clue, analyze sequence content
            const sequence = seq.sequence.toUpperCase();
            
            // Check for linker patterns (GGGGS is common in scFv)
            if (sequence.includes('GGGGS') || sequence.includes('GGGGG')) {
              sequenceType = 'scfv';
            }
            // Check for typical heavy chain patterns (longer sequences, specific motifs)
            else if (sequence.length > 400) {
              sequenceType = 'heavy_chain';
            }
            // Check for typical light chain patterns (shorter sequences)
            else if (sequence.length < 250) {
              sequenceType = 'light_chain';
            }
          }
          
          // Create the appropriate chain object based on type
          const chainObject: { name: string; heavy_chain?: string; light_chain?: string; scfv?: string } = { 
            name: seq.id || `Sequence_${seq.sequence.substring(0, 10)}` 
          };
          
          if (sequenceType === 'heavy_chain') {
            chainObject.heavy_chain = seq.sequence;
          } else if (sequenceType === 'light_chain') {
            chainObject.light_chain = seq.sequence;
          } else {
            chainObject.scfv = seq.sequence;
          }
          
          return chainObject;
        }),
        numbering_scheme: numberingScheme
      };

      // Call API
      const resultV2: AnnotationResultV2 = await api.annotateSequencesV2(request);
      
      // Debug logging
      console.log('API Response:', resultV2);
      console.log('Response structure:', {
        success: resultV2.success,
        hasData: !!resultV2.data,
        hasResults: !!resultV2.data?.results,
        resultsLength: resultV2.data?.results?.length,
        hasFirstResult: !!resultV2.data?.results?.[0],
        hasSequence: !!resultV2.data?.results?.[0]?.data?.sequence,
        hasChains: !!resultV2.data?.results?.[0]?.data?.sequence?.chains,
        chainsLength: resultV2.data?.results?.[0]?.data?.sequence?.chains?.length
      });
      
      setSequencesV2(resultV2);
      
      // Extract summary from the v2 backend response structure
      const firstResult = resultV2.data?.results?.[0];
      const sequenceData = firstResult?.data?.sequence;
      const summary = {
        numChains: sequenceData?.chains?.length || 0,
        numDomains: (sequenceData?.chains || []).reduce((acc, c) => 
          acc + (c.domains?.length || 0), 0
        )
      };
      const entry: HistoryEntry = {
        id: `${Date.now()}`,
        name: parsedSequences[0].id || 'Sequence',
        fastaContent,
        numberingScheme,
        timestamp: Date.now(),
        summary,
        result: resultV2
      };
      addHistory(entry);
      setHistory(loadHistory());
    } catch (err) {
      console.error('Annotation error:', err);
      setError(err instanceof Error ? err.message : 'Failed to annotate sequences');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box data-testid="antibody-annotation-tool">
      <Typography variant="h4" component="h1" gutterBottom>
        Antibody Sequence Annotation
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Upload and analyze antibody sequences to identify regions and visualize annotations.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} data-testid="error-message">
          {error}
        </Alert>
      )}

      {isLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }} data-testid="loading-indicator">
          <CircularProgress />
        </Box>
      )}

      {/* Sequence Input Section */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Sequence Input
        </Typography>
        <FastaInput 
          onSubmit={handleSubmit}
        />
      </Paper>

      {/* History Section */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">History</Typography>
          <Box>
            <Typography
              variant="body2"
              sx={{ cursor: 'pointer', color: 'primary.main' }}
              onClick={() => { clearHistoryStore(); setHistory([]); }}
              data-testid="clear-history"
            >
              Clear history
            </Typography>
          </Box>
        </Box>
        {history.length === 0 ? (
          <Typography variant="body2" color="text.secondary">No history yet</Typography>
        ) : (
          <Box component="table" sx={{ width: '100%', borderCollapse: 'collapse' }}>
            <Box component="thead">
              <Box component="tr">
                <Box component="th" sx={{ textAlign: 'left', py: 1 }}>Name</Box>
                <Box component="th" sx={{ textAlign: 'left', py: 1 }}>Numbering</Box>
                <Box component="th" sx={{ textAlign: 'left', py: 1 }}>Chains</Box>
                <Box component="th" sx={{ textAlign: 'left', py: 1 }}>Domains</Box>
                <Box component="th" sx={{ textAlign: 'left', py: 1 }}>Actions</Box>
              </Box>
            </Box>
            <Box component="tbody">
              {history.map((h) => (
                <Box component="tr" key={h.id}>
                  <Box component="td" sx={{ py: 1 }}>{h.name}</Box>
                  <Box component="td" sx={{ py: 1 }}>{h.numberingScheme}</Box>
                  <Box component="td" sx={{ py: 1 }}>{h.summary?.numChains ?? '-'}</Box>
                  <Box component="td" sx={{ py: 1 }}>{h.summary?.numDomains ?? '-'}</Box>
                  <Box component="td" sx={{ py: 1, display: 'flex', gap: 1 }}>
                    <Typography
                      variant="body2"
                      sx={{ cursor: 'pointer', color: 'primary.main' }}
                      onClick={() => h.result && setSequencesV2(h.result)}
                      data-testid={`history-reload-${h.id}`}
                    >
                      Reload
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{ cursor: 'pointer', color: 'secondary.main' }}
                      onClick={() => handleSubmit(h.fastaContent, h.numberingScheme as NumberingScheme)}
                      data-testid={`history-reannotate-${h.id}`}
                    >
                      Re-annotate
                    </Typography>
                  </Box>
                </Box>
              ))}
            </Box>
          </Box>
        )}
      </Paper>

      {/* Results Section */}
      {sequences.length > 0 ? (
        <Box>
          {/* Tabbed Interface for Sequences */}
          <Box sx={{ width: '100%' }}>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs 
                value={selectedTab} 
                onChange={handleTabChange}
                aria-label="sequence tabs"
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
            
            {/* Tab Content */}
            {sequences.map((sequence, sequenceIndex) => (
              <Box
                key={sequence.id}
                role="tabpanel"
                hidden={selectedTab !== sequenceIndex}
                id={`sequence-tabpanel-${sequenceIndex}`}
                aria-labelledby={`sequence-tab-${sequenceIndex}`}
              >
                {selectedTab === sequenceIndex && (
                  <Box sx={{ mt: 3 }}>
                                         {sequence.chains.map((chain) => (
                      <Paper key={chain.id} sx={{ p: 3, mb: 3 }}>
                        <Typography variant="h6" gutterBottom>
                          {chain.type === 'scfv' ? 'scFv Chain' : 
                           chain.type === 'heavy_chain' ? 'Heavy Chain' :
                           chain.type === 'light_chain' ? 'Light Chain' :
                           chain.type === 'heavy_chain_1' ? 'Heavy Chain 1' :
                           chain.type === 'heavy_chain_2' ? 'Heavy Chain 2' :
                           chain.type === 'light_chain_1' ? 'Light Chain 1' :
                           chain.type === 'light_chain_2' ? 'Light Chain 2' :
                           `${chain.type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} Chain`}
                        </Typography>
                        
                        {/* Domain Structure Visualization */}
                        <Box sx={{ mb: 3 }}>
                          <Typography variant="subtitle1" gutterBottom>
                            Domain Structure
                          </Typography>
                          <DomainGraphics
                            regions={chain.annotations}
                            sequenceLength={chain.sequence.length}
                            width={800}
                            height={80}
                            onRegionClick={(region) => selectRegion(region.id)}
                            selectedRegions={selectedRegions}
                          />
                        </Box>
                        
                        {/* Interactive Amino Acid Sequence */}
                        <Box sx={{ mb: 3 }}>
                          <Typography variant="subtitle1" gutterBottom>
                            Amino Acid Sequence
                          </Typography>
                          <AminoAcidSequence
                            sequence={chain.sequence}
                            regions={chain.annotations}
                            colorScheme={colorScheme}
                            onAminoAcidClick={(position) => selectPosition(position)}
                            onColorSchemeChange={setColorScheme}
                            selectedPositions={selectedPositions}
                            selectedRegions={selectedRegions}
                          />
                        </Box>
                        
                        {/* Feature Table */}
                        <Box sx={{ mb: 3 }}>
                          <Typography variant="subtitle1" gutterBottom>
                            Feature Table
                          </Typography>
                          <FeatureTable
                            regions={chain.annotations}
                            selectedRegions={selectedRegions}
                            onRegionSelect={selectRegion}
                          />
                        </Box>
                        
                        {/* Region Summary Chips */}
                        <Box>
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
                                onClick={() => selectRegion(region.id)}
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
                      </Paper>
                    ))}
                  </Box>
                )}
              </Box>
            ))}
          </Box>
        </Box>
      ) : (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No sequences uploaded
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Upload FASTA sequences to begin analysis
          </Typography>
        </Paper>
      )}

      {/* Debug Information - Always show */}
      <DebugInfo />
    </Box>
  );
};
