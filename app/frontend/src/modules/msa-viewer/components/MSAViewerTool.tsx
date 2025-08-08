import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Alert,
  CircularProgress,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip
} from '@mui/material';
import { PlayArrow, Download } from '@mui/icons-material';
import { MSAInput } from './MSAInput/MSAInput';
import { MSAVisualization } from './MSAVisualization/MSAVisualization';
import { api } from '../../../services/api';
import type { AlignmentMethod, NumberingScheme, MSAResult, MSAAnnotationResult, MSAJobStatus } from '../../../types/api';

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
    annotationResult: null
  });

  const [selectedAlgorithm, setSelectedAlgorithm] = useState('muscle');
  const [selectedNumberingScheme, setSelectedNumberingScheme] = useState('imgt');

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
            setMsaState(prev => ({
              ...prev,
              msaResult: jobStatus.result.msa_result || null,
              annotationResult: jobStatus.result.annotation_result || null,
              alignmentMatrix: jobStatus.result.msa_result?.alignment_matrix || [],
              sequenceNames: jobStatus.result.msa_result?.sequences?.map((s: any) => s.name) || [],
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
        numbering_scheme: selectedNumberingScheme as NumberingScheme
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
            alignmentMatrix: data.msa_result?.alignment_matrix || [],
            sequenceNames: data.msa_result?.sequences?.map((s: any) => s.name) || []
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

  const handleAnnotateMSA = async () => {
    if (!msaState.msaId) return;
    
    setMsaState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      // TODO: Implement MSA annotation API call
      console.log('Annotating MSA with scheme:', selectedNumberingScheme);
      
      // Mock response for now
      setTimeout(() => {
        setMsaState(prev => ({ 
          ...prev, 
          isLoading: false,
          regions: [
            { id: 'fr1', name: 'FR1', start: 1, stop: 26, color: '#ff6b6b' },
            { id: 'cdr1', name: 'CDR1', start: 27, stop: 38, color: '#4ecdc4' },
            { id: 'fr2', name: 'FR2', start: 39, stop: 55, color: '#45b7d1' },
            { id: 'cdr2', name: 'CDR2', start: 56, stop: 65, color: '#96ceb4' },
            { id: 'fr3', name: 'FR3', start: 66, stop: 104, color: '#feca57' },
            { id: 'cdr3', name: 'CDR3', start: 105, stop: 117, color: '#ff9ff3' },
            { id: 'fr4', name: 'FR4', start: 118, stop: 128, color: '#54a0ff' }
          ]
        }));
      }, 2000);
    } catch (error) {
      setMsaState(prev => ({ 
        ...prev, 
        isLoading: false, 
        error: error instanceof Error ? error.message : 'MSA annotation failed' 
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

      <Box sx={{ display: 'flex', gap: 3, flexDirection: { xs: 'column', md: 'row' } }}>
        <Box sx={{ flex: { xs: 'none', md: '0 0 33%' } }}>
          <Paper sx={{ p: 3, height: 'fit-content' }}>
            <Typography variant="h6" gutterBottom>
              Sequence Upload
            </Typography>
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
                    <MenuItem value="imgt">IMGT</MenuItem>
                    <MenuItem value="kabat">Kabat</MenuItem>
                    <MenuItem value="chothia">Chothia</MenuItem>
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
                  
                  {msaState.alignmentMatrix.length > 0 && (
                    <Button
                      variant="outlined"
                      startIcon={<Download />}
                      onClick={handleAnnotateMSA}
                      disabled={msaState.isLoading}
                      size="small"
                    >
                      Annotate
                    </Button>
                  )}
                </Box>
              </Box>
            )}
          </Paper>
        </Box>

        <Box sx={{ flex: { xs: 'none', md: '1' } }}>
          {msaState.isLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : msaState.alignmentMatrix.length > 0 ? (
            <Box>
              <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
                <Typography variant="h6">
                  Alignment Results
                </Typography>
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
              </Box>
              
              <MSAVisualization
                alignmentMatrix={msaState.alignmentMatrix}
                sequenceNames={msaState.sequenceNames}
                regions={msaState.regions}
                numberingScheme={selectedNumberingScheme}
              />
            </Box>
          ) : (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No sequences uploaded
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Upload FASTA sequences to create a multiple sequence alignment
              </Typography>
            </Paper>
          )}
        </Box>
      </Box>
    </Box>
  );
};
