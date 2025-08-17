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
  Chip,
  OutlinedInput,
  SelectChangeEvent,
  FormHelperText,
  Grid,
  Alert,
  CircularProgress,
} from '@mui/material';
import { Search, Upload } from '@mui/icons-material';
import api from '../../../services/api';

interface BlastSearchFormProps {
  databases: any;
  onSearch: (searchData: any) => void;
  loading: boolean;
}

const BlastSearchForm: React.FC<BlastSearchFormProps> = ({
  databases,
  onSearch,
  loading,
}) => {
  const [sequence, setSequence] = useState('');
  const [selectedDatabases, setSelectedDatabases] = useState<string[]>([]);
  const [blastType, setBlastType] = useState('blastp');
  const [evalue, setEvalue] = useState('1e-10');
  const [maxTargetSeqs, setMaxTargetSeqs] = useState('10');
  const [searchType, setSearchType] = useState('public');
  const [error, setError] = useState<string | null>(null);

  const blastTypes = [
    { value: 'blastp', label: 'BLASTP (Protein vs Protein)' },
    { value: 'blastn', label: 'BLASTN (Nucleotide vs Nucleotide)' },
    { value: 'blastx', label: 'BLASTX (Nucleotide vs Protein)' },
    { value: 'tblastn', label: 'TBLASTN (Protein vs Nucleotide)' },
  ];

  const handleDatabaseChange = (event: SelectChangeEvent<string[]>) => {
    const value = event.target.value;
    setSelectedDatabases(typeof value === 'string' ? value.split(',') : value);
  };

  const handleSearch = async () => {
    if (!sequence.trim()) {
      setError('Please enter a sequence');
      return;
    }

    if (searchType === 'public' && selectedDatabases.length === 0) {
      setError('Please select at least one database');
      return;
    }

    setError(null);

    const searchData = {
      query_sequence: sequence.trim(),
      databases: selectedDatabases,
      blast_type: blastType,
      evalue: parseFloat(evalue),
      max_target_seqs: parseInt(maxTargetSeqs),
      searchType: searchType,
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
    } catch (err: any) {
      setError(`Upload failed: ${err.message}`);
    }
  };

  const renderDatabaseOptions = () => {
    if (!databases) return [];

    const options: { value: string; label: string }[] = [];
    
    if (databases.public) {
      Object.entries(databases.public).forEach(([key, value]) => {
        options.push({ value: key, label: `${key} - ${value}` });
      });
    }
    
    if (databases.custom) {
      Object.entries(databases.custom).forEach(([key, value]) => {
        options.push({ value: key, label: `Custom: ${key} - ${value}` });
      });
    }

    return options;
  };

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        BLAST Search Configuration
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Search Type */}
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Search Type</InputLabel>
            <Select
              value={searchType}
              label="Search Type"
              onChange={(e) => setSearchType(e.target.value)}
            >
              <MenuItem value="public">Public Databases</MenuItem>
              <MenuItem value="internal">Internal Database</MenuItem>
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

        {/* Database Selection (only for public searches) */}
        {searchType === 'public' && (
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Databases</InputLabel>
              <Select
                multiple
                value={selectedDatabases}
                onChange={handleDatabaseChange}
                input={<OutlinedInput label="Databases" />}
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((value) => (
                      <Chip key={value} label={value} />
                    ))}
                  </Box>
                )}
              >
                {renderDatabaseOptions().map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
              <FormHelperText>
                Select one or more databases to search against
              </FormHelperText>
            </FormControl>
          </Grid>
        )}

        {/* Parameters */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="E-value"
            value={evalue}
            onChange={(e) => setEvalue(e.target.value)}
            helperText="E-value threshold (e.g., 1e-10)"
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Max Target Sequences"
            value={maxTargetSeqs}
            onChange={(e) => setMaxTargetSeqs(e.target.value)}
            helperText="Maximum number of hits to return"
          />
        </Grid>

        {/* Sequence Input */}
        <Grid item xs={12}>
          <Typography variant="subtitle1" gutterBottom>
            Query Sequence
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
              Or paste your sequence below
            </Typography>
          </Box>

          <TextField
            fullWidth
            multiline
            rows={6}
            value={sequence}
            onChange={(e) => setSequence(e.target.value)}
            placeholder="Enter your sequence here (FASTA format or raw sequence)..."
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
            startIcon={loading ? <CircularProgress size={20} /> : <Search />}
            sx={{ minWidth: 200 }}
          >
            {loading ? 'Searching...' : 'Run BLAST Search'}
          </Button>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default BlastSearchForm;
