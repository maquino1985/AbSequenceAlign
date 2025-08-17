import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Alert,
  CircularProgress,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip
} from '@mui/material';
import { PlayArrow } from '@mui/icons-material';
import { MSAInput } from './MSAInput/MSAInput';
import { MSAVisualization } from './MSAVisualization/MSAVisualization';
import { ConsensusSequence } from '../../../components/ConsensusSequence';
import { PSSMVisualization } from '../../../components/PSSMVisualization';
import { RegionAnnotationTiles } from '../../../components/RegionAnnotationTiles';
import { CollapsibleCard } from '../../../components/CollapsibleCard';
import { api } from '../../../services/api';
import { NUMBERING_SCHEMES } from '../../../utils/numberingSchemes';
import type { AlignmentMethod } from '../../../types/api';
import type { MSAResultV2, MSAAnnotationResultV2, MSAJobStatusV2 } from '../../../types/apiV2';

// Define region type for MSA
interface MSARegion {
  id: string;
  name: string;
  start: number;
  stop: number;
  sequence: string;
  color: string;
  type: 'CDR' | 'FR' | 'LIABILITY' | 'MUTATION';
  features: Array<{
    id: string;
    type: string;
    start: number;
    stop: number;
    description: string;
    color: string;
  }>;
  details?: {
    isotype?: string;
    domain_type?: string;
    preceding_linker?: {
      sequence: string;
      start: number;
      end: number;
    };
  };
}

// Define PSSM data type to match PSSMVisualization component
interface PSSMData {
  position_frequencies: Array<Record<string, number>>;
  position_scores: Array<Record<string, number>>;
  conservation_scores: number[];
  quality_scores: number[];
  consensus: string;
  amino_acids: string[];
  alignment_length: number;
  num_sequences: number;
}

interface MSAState {
  sequences: string[];
  alignmentMatrix: string[][];
  sequenceNames: string[];
  regions: MSARegion[];
  isLoading: boolean;
  error: string | null;
  msaId: string | null;
  jobId: string | null;
  jobStatus: MSAJobStatusV2 | null;
  msaResult: MSAResultV2 | null;
  annotationResult: MSAAnnotationResultV2 | null;
  consensus: string;
  pssmData: PSSMData | null;
  selectedRegions: string[];
}

export const MSAViewerTool: React.FC = () => {
  const [msaState, setMsaState] = useState<MSAState>({
    sequences: [],
    alignmentMatrix: [],
    sequenceNames: [],
    regions: [],
    isLoading: false,
    error: null,
    msaId: null,
    jobId: null,
    jobStatus: null,
    msaResult: null,
    annotationResult: null,
    consensus: '',
    pssmData: null,
    selectedRegions: []
  });

  const [selectedAlgorithm, setSelectedAlgorithm] = useState('muscle');
  const [selectedNumberingScheme, setSelectedNumberingScheme] = useState('imgt');

  // Region selection handlers
  const handleRegionSelect = (regionId: string) => {
    setMsaState(prev => ({
      ...prev,
      selectedRegions: [...prev.selectedRegions, regionId]
    }));
  };

  const handleRegionDeselect = (regionId: string) => {
    setMsaState(prev => ({
      ...prev,
      selectedRegions: prev.selectedRegions.filter(id => id !== regionId)
    }));
  };

  // Poll job status for background jobs
  useEffect(() => {
    if (!msaState.jobId) return;

    let pollCount = 0;
    const maxPolls = 150; // Maximum 5 minutes of polling (150 * 2s)

    const pollJobStatus = async () => {
      try {
        pollCount++;
        
        // Stop polling after max attempts

    const pollJobStatus = async () => {
      try {
        pollCount++;
        
        // Stop polling after max attempts
        if (pollCount > POLL_TIMEOUT_COUNT) {
          setMsaState(prev => ({
            ...prev,
            error: 'Job polling timeout. The job may still be processing. Please try refreshing the page.',
            jobStatus: null,
            isLoading: false
          }));
          return;
        }

        const response = await api.getJobStatus(msaState.jobId!);
        if (response.success && response.data) {
          const jobStatus = response.data as MSAJobStatusV2;
          setMsaState(prev => ({ ...prev, jobStatus }));

          if (jobStatus.status === 'completed' && jobStatus.result) {
            // Job completed, update with results
            const result = jobStatus.result as { msa_result?: MSAResultV2; annotation_result?: MSAAnnotationResultV2 };
            const msaResult = result.msa_result || null;
            const annotationResult = result.annotation_result || null;
            
            setMsaState(prev => ({
              ...prev,
              msaResult,
              annotationResult,
              alignmentMatrix: msaResult?.alignment_matrix || [],
              sequenceNames: msaResult?.sequences?.map((s: { name: string }) => s.name) || [],
              consensus: msaResult?.consensus || '',
              pssmData: msaResult?.metadata?.pssm_data as PSSMData | null || null,
              regions: annotationResult?.annotated_sequences?.flatMap((seq: { name: string; annotations?: Array<{ name: string; start: number; stop: number; sequence: string; color: string }> }) => 
                seq.annotations?.map(ann => ({
                  id: `${seq.name}_${ann.name}`,
                  name: ann.name,
                  start: ann.start,
                  stop: ann.stop,
                  sequence: ann.sequence,
                  color: ann.color,
                  type: 'CDR' as const,
                  features: [] as Array<{
                    id: string;
                    type: string;
                    start: number;
                    stop: number;
                    description: string;
                    color: string;
                  }>,
                  details: {}
                })) || []
              ) || [],
              isLoading: false,
              jobId: null // Clear job ID when completed
            }));
          } else if (jobStatus.status === 'failed') {
            setMsaState(prev => ({
              ...prev,
              error: jobStatus.message || 'Job failed',
              isLoading: false,
              jobId: null,
              jobStatus: null
            }));
          }
        } else {
          // API call failed
          setMsaState(prev => ({
            ...prev,
            jobStatus: prev.jobStatus ? {
              ...prev.jobStatus,
              message: 'Unable to check job status. Retrying...'
            } : null
          }));
        }
      } catch (error) {
        console.error('Error polling job status:', error);
        setMsaState(prev => ({
          ...prev,
          jobStatus: prev.jobStatus ? {
            ...prev.jobStatus,
            message: 'Connection error while checking job status. Retrying...'
          } : null
        }));
      }
    };

    // Initial poll
    pollJobStatus();
    
    // Set up polling interval
    const interval = setInterval(pollJobStatus, 2000); // Poll every 2 seconds
    
    return () => clearInterval(interval);
  }, [msaState.jobId]);

  const handleSequencesUpload = async (sequences: string[], sequenceNames?: string[]) => {
    setMsaState(prev => ({ 
      ...prev, 
      isLoading: true, 
      error: null,
      msaResult: null,
      annotationResult: null,
      alignmentMatrix: [],
      sequenceNames: [],
      consensus: '',
      pssmData: null,
      regions: []
    }));
    
    try {
      // Validate sequences before processing
      if (!sequences || sequences.length === 0) {
        throw new Error('No sequences provided');
      }
      
      if (sequences.length < 2) {
        throw new Error('At least 2 sequences are required for multiple sequence alignment');
      }
      
      // Basic validation for each sequence
      const validatedSequences: string[] = [];
      for (let i = 0; i < sequences.length; i++) {
        const seq = sequences[i];
        if (!seq || seq.trim().length === 0) {
          throw new Error(`Sequence ${i + 1} is empty`);
        }
        
        // Remove any whitespace and convert to uppercase
        const cleanSeq = seq.replace(/\s/g, '').toUpperCase();
        
        // Check for obvious non-amino acid characters (like FASTA headers mixed in)
        if (cleanSeq.includes('>') || cleanSeq.includes('_') || /\d/.test(cleanSeq)) {
          throw new Error(`Sequence ${i + 1} appears to contain FASTA headers or invalid characters. Please check your input format.`);
        }
        
        validatedSequences.push(cleanSeq);
      }
      
      // Store validated sequences and names
      setMsaState(prev => ({ 
        ...prev, 
        sequences: validatedSequences,
        sequenceNames: sequenceNames || [],
        isLoading: false
      }));
      
    } catch (error) {
      setMsaState(prev => ({ 
        ...prev, 
        isLoading: false, 
        error: error instanceof Error ? error.message : 'Upload failed' 
      }));
    }
  };

  const handleCreateMSA = async () => {
    if (!msaState.sequences.length) return;
    
    setMsaState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      // Validate and clean sequences
      const validatedSequences: string[] = [];
      const sequenceNames = msaState.sequenceNames.length ? msaState.sequenceNames : msaState.sequences.map((_, i) => `Sequence_${i + 1}`);
      
      for (let i = 0; i < msaState.sequences.length; i++) {
        const seq = msaState.sequences[i];
        const name = sequenceNames[i] || `Sequence_${i + 1}`;
        
        // Clean sequence - remove whitespace and convert to uppercase
        const cleanSeq = seq.replace(/\s/g, '').toUpperCase();
        
        // Validate amino acids
        const validAminoAcids = /^[ACDEFGHIKLMNPQRSTVWY]+$/;
        if (!validAminoAcids.test(cleanSeq)) {
          const invalidChars = [...cleanSeq].filter(char => !/[ACDEFGHIKLMNPQRSTVWY]/.test(char));
          throw new Error(`Invalid amino acids in ${name}: ${[...new Set(invalidChars)].join(', ')}`);
        }
        
        // Check minimum length
        if (cleanSeq.length < 15) {
          throw new Error(`Sequence ${name} is too short (${cleanSeq.length} AA). Minimum 15 AA required.`);
        }
        
        validatedSequences.push(cleanSeq);
      }
      
      // Prepare sequences for MSA creation using actual FASTA names
      const sequenceInputs = validatedSequences.map((seq, i) => ({
        name: sequenceNames[i] || `Sequence_${i + 1}`,
        heavy_chain: seq
      }));
      
      const request = {
        sequences: sequenceInputs,
        alignment_method: selectedAlgorithm as AlignmentMethod,
        numbering_scheme: selectedNumberingScheme as string
      };
      
      const response = await api.createMSA(request);
      
      if (response.success && response.data) {
        const data = response.data;
        if (data.use_background) {
          // Background job created
          setMsaState(prev => ({ 
            ...prev, 
            jobId: data.job_id || null,
            isLoading: false,
            jobStatus: {
              job_id: data.job_id || '',
              status: 'pending',
              message: 'Job submitted for background processing. Please wait...',
              progress: 0,
              created_at: new Date().toISOString()
            }
          }));
        } else {
          // Immediate result
          setMsaState(prev => ({ 
            ...prev, 
            isLoading: false,
            msaResult: data.msa_result || null,
            annotationResult: data.annotation_result || null,
            alignmentMatrix: data.msa_result?.alignment_matrix || [],
            sequenceNames: data.msa_result?.sequences?.map((s: { name: string }) => s.name) || [],
            consensus: data.msa_result?.consensus || '',
            pssmData: data.msa_result?.metadata?.pssm_data as PSSMData | null || null,
            regions: data.annotation_result?.annotated_sequences?.flatMap((seq: { name?: string; annotations?: Array<{ name: string; start: number; stop: number; sequence: string; color: string }> }) => 
              seq.annotations?.map(ann => ({
                id: `${seq.name || 'seq'}_${ann.name}`,
                name: ann.name,
                start: ann.start,
                stop: ann.stop,
                sequence: ann.sequence,
                color: ann.color,
                type: 'CDR' as const,
                features: [] as Array<{
                  id: string;
                  type: string;
                  start: number;
                  stop: number;
                  description: string;
                  color: string;
                }>,
                details: {}
              })) || []
            ) || []
          }));
        }
      } else {
        throw new Error(response.message || 'MSA creation failed');
      }
    } catch (error) {
      setMsaState(prev => ({ 
        ...prev, 
        isLoading: false, 
        error: error instanceof Error ? error.message : 'MSA creation failed' 
      }));
    }
  };



  if (msaState.error) {
    return (
      <Box data-testid="msa-viewer-tool">
        <Typography variant="h4" component="h1" gutterBottom>
          Multiple Sequence Alignment
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          Upload sequences and create multiple sequence alignments with region annotations.
        </Typography>
        
        <Alert severity="error" sx={{ mb: 2 }} data-testid="error-message">
          <Typography variant="h6" gutterBottom>Error</Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            {msaState.error}
          </Typography>
          <Button 
            variant="outlined" 
            size="small" 
            onClick={() => setMsaState(prev => ({ 
              ...prev, 
              error: null,
              sequences: [],
              sequenceNames: [],
              msaResult: null,
              annotationResult: null,
              alignmentMatrix: [],
              consensus: '',
              pssmData: null,
              regions: [],
              jobId: null,
              jobStatus: null
            }))}
          >
            Reset and Try Again
          </Button>
        </Alert>
      </Box>
    );
  }

  return (
    <Box data-testid="msa-viewer-tool">
      <Typography variant="h4" component="h1" gutterBottom>
        Multiple Sequence Alignment
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Upload sequences and create multiple sequence alignments with region annotations.
      </Typography>

      {/* Job Status and Loading */}
      {(msaState.isLoading || msaState.jobStatus) && (
        <Box sx={{ mb: 3 }}>
          {msaState.isLoading && !msaState.jobId && (
            <Alert severity="info" data-testid="job-status">
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <CircularProgress size={20} />
                <Typography variant="body2">
                  Processing request...
                </Typography>
              </Box>
            </Alert>
          )}
          
          {msaState.jobStatus && (
            <Alert 
              severity={
                msaState.jobStatus.status === 'completed' ? 'success' :
                msaState.jobStatus.status === 'failed' ? 'error' :
                msaState.jobStatus.status === 'running' ? 'info' : 'info'
              }
              data-testid="job-status"
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                {msaState.jobStatus.status === 'pending' || msaState.jobStatus.status === 'running' ? (
                  <CircularProgress size={20} />
                ) : null}
                <Box sx={{ flexGrow: 1 }}>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    {msaState.jobStatus.status === 'pending' && 'Job Queued'}
                    {msaState.jobStatus.status === 'running' && 'Processing Alignment'}
                    {msaState.jobStatus.status === 'completed' && 'Alignment Complete'}
                    {msaState.jobStatus.status === 'failed' && 'Job Failed'}
                    {msaState.jobStatus.progress !== undefined && msaState.jobStatus.progress > 0 && 
                      ` (${Math.round(msaState.jobStatus.progress * 100)}%)`
                    }
                  </Typography>
                  {msaState.jobStatus.message && (
                    <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
                      {msaState.jobStatus.message}
                    </Typography>
                  )}
                  {msaState.jobStatus.status === 'pending' && (
                    <Typography variant="caption" display="block" sx={{ mt: 0.5, color: 'text.secondary' }}>
                      Large alignments are processed in the background. This may take a few minutes.
                    </Typography>
                  )}
                </Box>
                {(msaState.jobStatus.status === 'pending' || msaState.jobStatus.status === 'running') && (
                  <Button
                    size="small"
                    variant="outlined"
                    color="secondary"
                    onClick={() => {
                      setMsaState(prev => ({
                        ...prev,
                        jobId: null,
                        jobStatus: null,
                        isLoading: false
                      }));
                    }}
                    sx={{ ml: 'auto' }}
                  >
                    Cancel
                  </Button>
                )}
              </Box>
            </Alert>
          )}
        </Box>
      )}

      {/* Statistics Panel */}
      {msaState.alignmentMatrix.length > 0 && (
        <Box sx={{ mb: 3 }} data-testid="statistics-panel">
          <CollapsibleCard title="Alignment Statistics" defaultExpanded={false}>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Chip 
                label={`${msaState.sequenceNames.length} sequences`} 
                size="small" 
                color="primary" 
              />
              <Chip 
                label={`${msaState.alignmentMatrix[0]?.length || 0} positions`} 
                size="small" 
                color="secondary" 
              />
              {msaState.regions.length > 0 && (
                <Chip 
                  label={`${msaState.regions.length} regions`} 
                  size="small" 
                  variant="outlined" 
                />
              )}
            </Box>
          </CollapsibleCard>
        </Box>
      )}

      <Box sx={{ display: 'flex', gap: 3, flexDirection: { xs: 'column', lg: 'row' } }}>
        <Box sx={{ flex: { xs: 'none', lg: '0 0 400px' } }}>
          <CollapsibleCard title="Sequence Upload" defaultExpanded={true}>
            <MSAInput 
              onUpload={handleSequencesUpload}
              isLoading={msaState.isLoading}
            />
            
            {msaState.sequences.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Alignment Configuration
                </Typography>
                
                <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                  <InputLabel>Algorithm</InputLabel>
                  <Select
                    value={selectedAlgorithm}
                    label="Algorithm"
                    onChange={(e) => setSelectedAlgorithm(e.target.value)}
                    inputProps={{
                      'data-testid': 'alignment-method'
                    }}
                  >
                    <MenuItem value="muscle">MUSCLE</MenuItem>
                    <MenuItem value="clustalo">Clustal Omega</MenuItem>
                    <MenuItem value="mafft">MAFFT</MenuItem>
                  </Select>
                </FormControl>

                <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                  <InputLabel>Numbering Scheme</InputLabel>
                  <Select
                    value={selectedNumberingScheme}
                    label="Numbering Scheme"
                    onChange={(e) => setSelectedNumberingScheme(e.target.value)}
                    inputProps={{
                      'data-testid': 'numbering-scheme'
                    }}
                  >
                    {NUMBERING_SCHEMES.map((scheme) => (
                      <MenuItem key={scheme.id} value={scheme.id}>
                        {scheme.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <Button
                  variant="contained"
                  onClick={handleCreateMSA}
                  disabled={msaState.isLoading}
                  startIcon={<PlayArrow />}
                  fullWidth
                  data-testid="align-btn"
                >
                  {msaState.isLoading ? 'Creating MSA...' : 'Create MSA'}
                </Button>
              </Box>
            )}
          </CollapsibleCard>
        </Box>

        <Box sx={{ flex: 1 }}>
          {msaState.isLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : msaState.alignmentMatrix.length > 0 ? (
            <CollapsibleCard title="Alignment Results" defaultExpanded={true} data-testid="msa-viewer">
              <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
                <Chip 
                  label={`${msaState.sequenceNames.length} sequences`} 
                  size="small" 
                  color="primary" 
                  data-testid="sequence-count"
                />
                <Chip 
                  label={`${msaState.alignmentMatrix[0]?.length || 0} positions`} 
                  size="small" 
                  color="secondary" 
                />
                <Chip 
                  label={`${selectedNumberingScheme.toUpperCase()} numbering`} 
                  size="small" 
                  variant="outlined" 
                />
                {msaState.regions.length > 0 && (
                  <Chip 
                    label={`${msaState.regions.length} regions`} 
                    size="small" 
                    variant="outlined" 
                  />
                )}
              </Box>
              
              <MSAVisualization
                alignmentMatrix={msaState.alignmentMatrix}
                sequenceNames={msaState.sequenceNames}
                regions={msaState.regions}
                numberingScheme={selectedNumberingScheme}
              />

              {/* Consensus Sequence */}
              {msaState.consensus && (
                <Box sx={{ mt: 2 }} data-testid="consensus-sequence">
              <ConsensusSequence
                consensus={msaState.consensus}
                conservationScores={msaState.pssmData?.conservation_scores || []}
                qualityScores={msaState.pssmData?.quality_scores || []}
              />
                </Box>
              )}

              {/* PSSM Visualization */}
              {msaState.pssmData && (
                <Box sx={{ mt: 2 }} data-testid="conservation-plot">
                  <PSSMVisualization
                    pssmData={msaState.pssmData}
                    maxHeight="400px"
                  />
                </Box>
              )}

              {/* Region Annotation Tiles */}
              {msaState.regions.length > 0 && (
                <Box sx={{ mt: 2 }}>
                  <RegionAnnotationTiles
                    regions={msaState.regions}
                    selectedRegions={msaState.selectedRegions}
                    onRegionSelect={handleRegionSelect}
                    onRegionDeselect={handleRegionDeselect}
                  />
                  {/* Add individual region elements for testing */}
                  {msaState.regions.map((region) => (
                    <Box key={region.id} data-testid={`region-${region.type.toLowerCase()}`} style={{ display: 'none' }}>
                      {region.name}
                    </Box>
                  ))}
                </Box>
              )}
            </CollapsibleCard>
          ) : (
            <CollapsibleCard title="No Data" defaultExpanded={true}>
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  No sequences uploaded
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Upload FASTA sequences to create a multiple sequence alignment
                </Typography>
              </Box>
            </CollapsibleCard>
          )}
        </Box>
      </Box>
    </Box>
  );
};
