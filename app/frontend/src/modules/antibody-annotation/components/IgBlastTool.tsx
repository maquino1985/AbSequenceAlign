/**
 * IgBLAST Tool Component
 * 
 * Provides a complete interface for IgBLAST analysis with database selection
 */

import React, { useState, useCallback, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  FormControlLabel,
  Switch,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Divider,
  Chip,
  Grid
} from '@mui/material';
import { PlayArrow as PlayIcon, Refresh as RefreshIcon } from '@mui/icons-material';
import { DatabaseSelector } from '../../../components/DatabaseSelector';
import { IgBlastResultsDisplay } from './IgBlastResultsDisplay';
import { api } from '../../../services/api';
import type { DatabaseSelection, IgBlastRequest, IgBlastResponse } from '../../../types/database';

interface IgBlastToolProps {
  onResults?: (results: IgBlastResponse) => void;
}

export const IgBlastTool: React.FC<IgBlastToolProps> = ({ onResults }) => {
  const [sequence, setSequence] = useState('');
  const [blastType, setBlastType] = useState<'igblastn' | 'igblastp'>('igblastn');
  const [useAirrFormat, setUseAirrFormat] = useState(false);
  const [domainSystem, setDomainSystem] = useState<'imgt' | 'kabat'>('imgt');
  const [databaseSelection, setDatabaseSelection] = useState<DatabaseSelection>({
    v_db: '',
    d_db: '',
    j_db: '',
    c_db: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<IgBlastResponse | null>(null);

  const handleSequenceChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setSequence(value);
  }, []);

  const handleDatabaseSelectionChange = useCallback((selection: DatabaseSelection) => {
    setDatabaseSelection(selection);
  }, []);

  const validateInput = useCallback((): string | null => {
    if (!sequence.trim()) {
      return 'Please enter a sequence';
    }
    
    if (!databaseSelection.v_db) {
      return 'Please select a V gene database';
    }
    
    // For nucleotide IgBLAST, J database is required
    if (blastType === 'igblastn' && !databaseSelection.j_db) {
      return 'Please select a J gene database';
    }

    // Clean sequence by removing spaces, newlines, and converting to uppercase
    const cleanSequence = sequence.replace(/[\s\n\r]/g, '').toUpperCase();
    
    // Validate sequence format based on blast type
    if (blastType === 'igblastn') {
      // Check for nucleotide sequence (A, C, G, T, N)
      if (!/^[ACGTN]+$/.test(cleanSequence)) {
        return 'Invalid nucleotide sequence. Please use only A, C, G, T, and N characters.';
      }
    } else if (blastType === 'igblastp') {
      // Check for protein sequence (standard amino acids)
      if (!/^[ACDEFGHIKLMNPQRSTVWY]+$/.test(cleanSequence)) {
        return 'Invalid protein sequence. Please use only standard amino acid characters.';
      }
    }

    return null;
  }, [sequence, databaseSelection.v_db, databaseSelection.j_db, blastType]);

  const handleExecute = useCallback(async () => {
    const validationError = validateInput();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Clean sequence by removing spaces, newlines, and converting to uppercase
      const cleanSequence = sequence.replace(/[\s\n\r]/g, '').toUpperCase();
      
      const request: IgBlastRequest = {
        query_sequence: cleanSequence,
        v_db: databaseSelection.v_db,
        d_db: blastType === 'igblastn' ? (databaseSelection.d_db || undefined) : undefined,
        j_db: blastType === 'igblastn' ? databaseSelection.j_db : undefined,
        c_db: blastType === 'igblastn' ? (databaseSelection.c_db || undefined) : undefined,
        blast_type: blastType,
        use_airr_format: useAirrFormat,
        domain_system: blastType === 'igblastp' ? domainSystem : undefined
      };

      const response = await api.executeIgBlast(request);
      setResults(response);
      
      if (onResults) {
        onResults(response);
      }
    } catch (err) {
      console.error('IgBLAST execution failed:', err);
      setError(err instanceof Error ? err.message : 'IgBLAST execution failed');
    } finally {
      setLoading(false);
    }
  }, [validateInput, sequence, databaseSelection, blastType, useAirrFormat, onResults]);

  const handleClear = useCallback(() => {
    setSequence('');
    setResults(null);
    setError(null);
  }, []);

  const canExecute = useMemo(() => 
    sequence.trim() && databaseSelection.v_db && 
    (blastType === 'igblastn' ? databaseSelection.j_db : true) && !loading,
    [sequence, databaseSelection.v_db, databaseSelection.j_db, blastType, loading]
  );

  return (
    <Box>
      <Typography variant="h5" component="h2" gutterBottom>
        IgBLAST Analysis
      </Typography>
      
      <Typography variant="body2" color="text.secondary" paragraph>
        Perform immunoglobulin gene analysis using IgBLAST with user-selected databases.
      </Typography>

      <Grid container spacing={3}>
        {/* Left Column - Input */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Input Parameters
              </Typography>

              {/* Sequence Input */}
              <TextField
                fullWidth
                multiline
                rows={6}
                label="Query Sequence"
                value={sequence}
                onChange={handleSequenceChange}
                placeholder="Enter nucleotide or protein sequence..."
                margin="normal"
                disabled={loading}
                error={!!error && error.includes('sequence')}
                helperText={
                  blastType === 'igblastn' 
                    ? 'Enter nucleotide sequence (A, C, G, T, N)'
                    : 'Enter protein sequence (amino acids)'
                }
              />

              {/* BLAST Type Selection */}
              <FormControl fullWidth margin="normal" disabled={loading}>
                <InputLabel>BLAST Type</InputLabel>
                <Select
                  value={blastType}
                  onChange={(e) => {
                    const newBlastType = e.target.value as 'igblastn' | 'igblastp';
                    setBlastType(newBlastType);
                    // Disable AIRR format for protein IgBLAST
                    if (newBlastType === 'igblastp' && useAirrFormat) {
                      setUseAirrFormat(false);
                    }
                  }}
                  label="BLAST Type"
                >
                  <MenuItem value="igblastn">IgBLAST Nucleotide (igblastn)</MenuItem>
                  <MenuItem value="igblastp">IgBLAST Protein (igblastp)</MenuItem>
                </Select>
              </FormControl>

              {/* Numbering System Selection - Only for Protein IgBLAST */}
              {blastType === 'igblastp' && (
                <FormControl fullWidth margin="normal" disabled={loading}>
                  <InputLabel>Numbering System</InputLabel>
                  <Select
                    value={domainSystem}
                    onChange={(e) => setDomainSystem(e.target.value as 'imgt' | 'kabat')}
                    label="Numbering System"
                  >
                    <MenuItem value="imgt">IMGT Numbering</MenuItem>
                    <MenuItem value="kabat">Kabat Numbering</MenuItem>
                  </Select>
                </FormControl>
              )}

              {/* AIRR Format Toggle - Only available for nucleotide IgBLAST */}
              <FormControlLabel
                control={
                  <Switch
                    checked={useAirrFormat}
                    onChange={(e) => setUseAirrFormat(e.target.checked)}
                    disabled={loading || blastType === 'igblastp'}
                  />
                }
                label={`Use AIRR Format Output${blastType === 'igblastp' ? ' (Nucleotide only)' : ''}`}
                sx={{ mt: 1 }}
              />

              {/* Action Buttons */}
              <Box mt={2} display="flex" gap={1}>
                <Button
                  variant="contained"
                  startIcon={loading ? <CircularProgress size={20} /> : <PlayIcon />}
                  onClick={handleExecute}
                  disabled={!canExecute}
                  fullWidth
                >
                  {loading ? 'Executing...' : 'Execute IgBLAST'}
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  onClick={handleClear}
                  disabled={loading}
                >
                  Clear
                </Button>
              </Box>

              {/* Error Display */}
              {error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {error}
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Right Column - Database Selection */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <DatabaseSelector
                value={databaseSelection}
                onChange={handleDatabaseSelectionChange}
                disabled={loading}
                showDescriptions={true}
                blastType={blastType}
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Results Display */}
      {results && (
        <Box sx={{ mt: 3 }}>
          <IgBlastResultsDisplay results={results} />
        </Box>
      )}
    </Box>
  );
};
