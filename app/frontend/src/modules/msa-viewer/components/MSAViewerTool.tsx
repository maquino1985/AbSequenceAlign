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
import type { AlignmentMethod, MSAResult, MSAAnnotationResult, MSAJobStatus } from '../../../types/api';

interface MSAState {
  sequences: string[];
  alignmentMatrix: string[][];
  sequenceNames: string[];
  regions: any[];
  isLoading: boolean;
  error: string | null;
  msaId: string | null;
  jobId: string | null;
  jobStatus: MSAJobStatus | null;
  msaResult: MSAResult | null;
  annotationResult: MSAAnnotationResult | null;
  consensus: string;
  pssmData: any;
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

    const pollJobStatus = async () => {
      try {
        const response = await api.getJobStatus(msaState.jobId!);
        if (response.success && response.data) {
          const jobStatus = response.data as MSAJobStatus;
          setMsaState(prev => ({ ...prev, jobStatus }));

          if (jobStatus.status === 'completed' && jobStatus.result) {
            // Job completed, update with results
            const msaResult = (jobStatus.result as any).msa_result || null;
            const annotationResult = (jobStatus.result as any).annotation_result || null;
            
            setMsaState(prev => ({
              ...prev,
              msaResult,
              annotationResult,
              alignmentMatrix: msaResult?.alignment_matrix || [],
              sequenceNames: msaResult?.sequences?.map((s: any) => s.name) || [],
              consensus: msaResult?.consensus || '',
              pssmData: msaResult?.metadata?.pssm_data || null,
              regions: annotationResult?.annotated_sequences?.flatMap((seq: any) => seq.annotations || []) || [],
              isLoading: false
            }));
          } else if (jobStatus.status === 'failed') {
            setMsaState(prev => ({
              ...prev,
              error: jobStatus.message,
              isLoading: false
            }));
          }
        }
      } catch (error) {
        console.error('Error polling job status:', error);
      }
    };

    const interval = setInterval(pollJobStatus, 2000); // Poll every 2 seconds
    return () => clearInterval(interval);
  }, [msaState.jobId]);

  const handleSequencesUpload = async (sequences: string[]) => {
    setMsaState(prev => ({ ...prev, sequences, isLoading: true, error: null }));
    
    try {
      // Create FormData for upload
      const formData = new FormData();
      const fastaContent = sequences.map((seq, i) => `>Sequence_${i + 1}\n${seq}`).join('\n');
      formData.append('sequences', fastaContent);
      
      const response = await api.uploadMSASequences(formData);
      
      if (response.success && response.data) {
        setMsaState(prev => ({ 
          ...prev, 
          isLoading: false,
          msaId: 'uploaded-sequences'
        }));
      } else {
        throw new Error(response.message || 'Upload failed');
      }
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
      // Prepare sequences for MSA creation
      const sequenceInputs = msaState.sequences.map((seq, i) => ({
        name: `Sequence_${i + 1}`,
        heavy_chain: seq
      }));
      
      const request = {
        sequences: sequenceInputs,
        alignment_method: selectedAlgorithm as AlignmentMethod,
        numbering_scheme: selectedNumberingScheme as any
      };
      
      const response = await api.createMSA(request);
      
      if (response.success && response.data) {
        const data = response.data;
          if (data.use_background) {
          // Background job created
          setMsaState(prev => ({ 
            ...prev, 
            jobId: data.job_id || null,
            isLoading: false
          }));
        } else {
          // Immediate result
          setMsaState(prev => ({ 
            ...prev, 
            isLoading: false,
            msaResult: data.msa_result || null,
            annotationResult: data.annotation_result || null,
            alignmentMatrix: (data as any).msa_result?.alignment_matrix || [],
            sequenceNames: (data as any).msa_result?.sequences?.map((s: any) => s.name) || [],
            consensus: (data as any).consensus || '',
            pssmData: (data as any).pssm_data || null,
            regions: data.annotation_result?.annotated_sequences?.flatMap((seq: any) => seq.annotations || []) || []
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
      <Alert severity="error" sx={{ mb: 2 }}>
        Error: {msaState.error}
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Multiple Sequence Alignment
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Upload multiple sequences to create and visualize alignments with region annotations.
      </Typography>

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
                  >
                    {NUMBERING_SCHEMES.map((scheme) => (
                      <MenuItem key={scheme.id} value={scheme.id}>
                        {scheme.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Button
                    variant="contained"
                    startIcon={<PlayArrow />}
                    onClick={handleCreateMSA}
                    disabled={msaState.isLoading || !msaState.msaId}
                    size="small"
                  >
                    Create MSA
                  </Button>
                  

                </Box>
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
            <CollapsibleCard title="Alignment Results" defaultExpanded={true}>
              <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
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
                <Box sx={{ mt: 2 }}>
              <ConsensusSequence
                consensus={msaState.consensus}
                conservationScores={msaState.pssmData?.conservation_scores || []}
                qualityScores={msaState.pssmData?.quality_scores || []}
              />
                </Box>
              )}

              {/* PSSM Visualization */}
              {msaState.pssmData && (
                <Box sx={{ mt: 2 }}>
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
