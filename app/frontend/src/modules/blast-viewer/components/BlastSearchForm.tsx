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
  FormHelperText,
  Alert,
  CircularProgress,
} from '@mui/material';
import { Search, Upload } from '@mui/icons-material';
import api from '../../../services/api';
import { validateSequence, getSequenceTypeFromBlastType } from '../../../utils/fastaParser';

interface BlastSearchFormProps {
  databases: Record<string, unknown> | null;
  onSearch: (searchData: Record<string, unknown>) => void;
  loading: boolean;
}

const BlastSearchForm: React.FC<BlastSearchFormProps> = ({
  databases,
  onSearch,
  loading,
}) => {
  const [sequence, setSequence] = useState('');
  const [selectedDatabase, setSelectedDatabase] = useState<string>('');
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

  const handleDatabaseChange = (event: any) => {
    const value = event.target.value as string;
    setSelectedDatabase(value);
  };

  const handleSearch = async () => {
    // Validate sequence
    const sequenceType = getSequenceTypeFromBlastType(blastType);
    const validation = validateSequence(sequence, sequenceType);
    
    if (!validation.isValid) {
      setError(`Sequence validation failed: ${validation.errors.join(', ')}`);
      return;
    }

    if (searchType === 'public' && !selectedDatabase) {
      setError('Please select a database');
      return;
    }

    setError(null);

    const searchData = {
      query_sequence: validation.cleanSequence,
      databases: [selectedDatabase],
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
      if (response.data?.sequence) {
        setSequence(response.data.sequence as string);
      }
      setError(null);
    } catch (err: unknown) {
      setError(`Upload failed: ${(err as Error).message}`);
    }
  };

  const renderDatabaseOptions = () => {
    if (!databases) return [];

    const options: { value: string; label: string }[] = [];
    
    if (databases.public) {
      Object.entries(databases.public as Record<string, unknown>).forEach(([key, value]) => {
        options.push({ value: key, label: `${key} - ${value}` });
      });
    }
    
    if (databases.custom) {
      Object.entries(databases.custom as Record<string, unknown>).forEach(([key, value]) => {
        options.push({ value: key, label: `Custom: ${key} - ${value}` });
      });
    }

    if (databases.internal) {
      Object.entries(databases.internal as Record<string, unknown>).forEach(([key, value]) => {
        options.push({ value: key, label: `Internal: ${key} - ${value}` });
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

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {/* Search Type and BLAST Type */}
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <FormControl sx={{ minWidth: 200, flex: 1 }}>
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

          <FormControl sx={{ minWidth: 200, flex: 1 }}>
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
        </Box>

        {/* Database Selection (only for public searches) */}
        {searchType === 'public' && (
          <FormControl fullWidth>
            <InputLabel>Database</InputLabel>
            {databases ? (
              <Select
                value={selectedDatabase}
                onChange={handleDatabaseChange}
                input={<OutlinedInput label="Database" />}
              >
                {renderDatabaseOptions().map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            ) : (
              <Select
                value=""
                input={<OutlinedInput label="Database" />}
                disabled
              >
                <MenuItem value="">Loading databases...</MenuItem>
              </Select>
            )}
            <FormHelperText>
              {databases 
                ? renderDatabaseOptions().length > 0
                  ? `Select a database to search against (${renderDatabaseOptions().length} available)`
                  : 'No databases available'
                : 'Loading available databases...'
              }
            </FormHelperText>
          </FormControl>
        )}

        {/* Parameters */}
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <TextField
            sx={{ flex: 1, minWidth: 200 }}
            label="E-value"
            value={evalue}
            onChange={(e) => setEvalue(e.target.value)}
            helperText="E-value threshold (e.g., 1e-10)"
          />

          <TextField
            sx={{ flex: 1, minWidth: 200 }}
            label="Max Target Sequences"
            value={maxTargetSeqs}
            onChange={(e) => setMaxTargetSeqs(e.target.value)}
            helperText="Maximum number of hits to return"
          />
        </Box>

        {/* Sequence Input */}
        <Box>
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
        </Box>

        {/* Search Button */}
        <Box>
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
        </Box>
      </Box>
    </Paper>
  );
};

export default BlastSearchForm;
