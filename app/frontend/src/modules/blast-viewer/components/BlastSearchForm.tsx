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

    if (!selectedDatabase) {
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
    
    // Handle new database structure: { protein: {...}, nucleotide: {...} }
    if (databases.protein) {
      Object.entries(databases.protein as Record<string, any>).forEach(([key, dbInfo]) => {
        if (dbInfo && typeof dbInfo === 'object' && 'name' in dbInfo && 'description' in dbInfo) {
          options.push({ 
            value: dbInfo.path || key, 
            label: `${dbInfo.name} - ${dbInfo.description}` 
          });
        }
      });
    }
    
    if (databases.nucleotide) {
      Object.entries(databases.nucleotide as Record<string, any>).forEach(([key, dbInfo]) => {
        if (dbInfo && typeof dbInfo === 'object' && 'name' in dbInfo && 'description' in dbInfo) {
          options.push({ 
            value: dbInfo.path || key, 
            label: `${dbInfo.name} - ${dbInfo.description}` 
          });
        }
      });
    }

    // Filter databases based on BLAST type
    const sequenceType = getSequenceTypeFromBlastType(blastType);
    if (sequenceType === 'protein' && databases.protein) {
      // For protein BLAST types, only show protein databases
      return options.filter(option => {
        return Object.values(databases.protein as Record<string, any>).some(
          (dbInfo: any) => dbInfo.path === option.value
        );
      });
    } else if (sequenceType === 'nucleotide' && databases.nucleotide) {
      // For nucleotide BLAST types, only show nucleotide databases
      return options.filter(option => {
        return Object.values(databases.nucleotide as Record<string, any>).some(
          (dbInfo: any) => dbInfo.path === option.value
        );
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
        {/* BLAST Type */}
        <FormControl sx={{ minWidth: 200 }}>
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

        {/* Database Selection */}
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
