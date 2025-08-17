import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Alert,
  CircularProgress,
} from '@mui/material';
import { Biotech, Upload } from '@mui/icons-material';
import api from '../../../services/api';

interface AntibodyAnalysisProps {
  organisms: string[];
  onSearch: (searchData: Record<string, unknown>) => void;
  loading: boolean;
}

const AntibodyAnalysis: React.FC<AntibodyAnalysisProps> = ({
  organisms,
  onSearch,
  loading,
}) => {
  const [sequence, setSequence] = useState('');
  const [organism, setOrganism] = useState('human');
  const [blastType, setBlastType] = useState('igblastn');
  const [evalue, setEvalue] = useState('1e-10');
  const [error, setError] = useState<string | null>(null);

  const blastTypes = [
    { value: 'igblastn', label: 'IgBLASTN (Nucleotide antibody sequences)' },
    { value: 'igblastp', label: 'IgBLASTP (Protein antibody sequences)' },
  ];

  const handleSearch = async () => {
    if (!sequence.trim()) {
      setError('Please enter a sequence');
      return;
    }

    if (!organism) {
      setError('Please select an organism');
      return;
    }

    setError(null);

    const searchData = {
      query_sequence: sequence.trim(),
      organism: organism,
      blast_type: blastType,
      evalue: parseFloat(evalue),
      searchType: 'antibody',
    };

    onSearch(searchData);
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.fasta') && !file.name.endsWith('.fa') && !file.name.endsWith('.txt')) {
      setError('Please upload a FASTA file (.fasta, .fa, or .txt)');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.uploadSequencesForBlast(formData);
      setSequence(response.data.sequence);
      setError(null);
    } catch (err: unknown) {
      setError(`Upload failed: ${err.message}`);
    }
  };

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        <Biotech sx={{ mr: 1, verticalAlign: 'middle' }} />
        Antibody Sequence Analysis (IgBLAST)
      </Typography>
      
      <Typography variant="body2" color="text.secondary" paragraph>
        Analyze antibody sequences to identify V, D, J, and C genes, and extract CDR3 regions.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Organism Selection */}
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Organism</InputLabel>
            <Select
              value={organism}
              label="Organism"
              onChange={(e) => setOrganism(e.target.value)}
            >
              {organisms.map((org) => (
                <MenuItem key={org} value={org}>
                  {org.charAt(0).toUpperCase() + org.slice(1)}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        {/* BLAST Type */}
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>BLAST Type</InputLabel>
            <Select
              value={blastType}
              label="BLAST Type"
              onChange={(e) => setBlastType(e.target.value)}
            >
              {blastTypes.map((type) => (
                <MenuItem key={type.value} value={type.value}>
                  {type.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        {/* E-value */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="E-value"
            value={evalue}
            onChange={(e) => setEvalue(e.target.value)}
            helperText="E-value threshold (e.g., 1e-10)"
          />
        </Grid>

        {/* Sequence Input */}
        <Grid item xs={12}>
          <Typography variant="subtitle1" gutterBottom>
            Antibody Sequence
          </Typography>
          
          <Box sx={{ mb: 2 }}>
            <Button
              variant="outlined"
              component="label"
              startIcon={<Upload />}
              sx={{ mr: 2 }}
            >
              Upload FASTA File
              <input
                type="file"
                hidden
                accept=".fasta,.fa,.txt"
                onChange={handleFileUpload}
              />
            </Button>
            <Typography variant="caption" color="text.secondary">
              Or paste your antibody sequence below (DNA for IgBLASTN, protein for IgBLASTP)
            </Typography>
          </Box>

          <TextField
            fullWidth
            multiline
            rows={6}
            value={sequence}
            onChange={(e) => setSequence(e.target.value)}
            placeholder="Enter your antibody sequence here (FASTA format or raw sequence)..."
            variant="outlined"
          />
        </Grid>

        {/* Search Button */}
        <Grid item xs={12}>
          <Button
            variant="contained"
            size="large"
            onClick={handleSearch}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : <Biotech />}
            sx={{ minWidth: 200 }}
          >
            {loading ? 'Analyzing...' : 'Run Antibody Analysis'}
          </Button>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default AntibodyAnalysis;
