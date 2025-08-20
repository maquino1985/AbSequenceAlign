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

// Example sequences for BLAST
const EXAMPLE_SEQUENCES = {
  'Nucleotide Heavy Chain': `gaagtgcagctggtggaaagcggcggcggcctggtgcagccgggccgcagcctgcgcctgagctgcgcggcgagcggctttacctttgatgattatgcgatgcattgggtgcgccaggcgccgggcaaaggcctggaatgggtgagcgcgattacctggaacagcggccatattgattatgcggatagcgtggaaggccgctttaccattagccgcgataacgcgaaaaacagcctgtatctgcagatgaacagcctgcgcgcggaagataccgcggtgtattattgcgcgaaagtgagctatctgagcaccgcgagcagcctggattattggggccagggcaccctggtgaccgtgagcagcgcgagcaccaaaggcccgagcgtgtttccgctggcgccgagcagcaaaagcaccagcggcggcaccgcggcgctgggctgcctggtgaaagattattttccggaaccggtgaccgtgagctggaacagcggcgcgctgaccagcggcgtgcatacctttccggcggtgctgcagagcagcggcctgtatagcctgagcagcgtggtgaccgtgccgagcagcagcctgggcacccagacctatatttgcaacgtgaaccataaaccgagcaacaccaaagtggataaaaaagtggaaccgaaaagctgcgataaaacccatacctgcccgccgtgcccggcgccggaactgctgggcggcccgagcgtgtttctgtttccgccgaaaccgaaagataccctgatgattagccgcaccccggaagtgacctgcgtggtggtggatgtgagccatgaagatccggaagtgaaatttaactggtatgtggatggcgtggaagtgcataacgcgaaaaccaaaccgcgcgaagaacagtat`,
  
  'Nucleotide Light Chain': `gatattcagatgacccagagcccgagcagcctgagcgcgagcgtgggcgatcgcgtgaccattacctgccgcgcgagccagggcattcgcaactatctggcgtggtatcagcagaaaccgggcaaagcgccgaaactgctgatttatgcggcgagcagcctgcagagcggcgtgccgagccgctttagcggcagcggcagcggcaccgattttaccctgaccattagcagcctgcagccggaagatgtggcgacctattattgccagcgctataaccgcgcgccgtatacctttggccagggcaccaaagtggaaattaaacgcaccgtggcggcgccgagcgtgtttatttttccgccgagcgatgaacagctgaaaagcggcaccgcgagcgtggtgtgcctgctgaacaacttttatccgcgcgaagcgaaagtgcagtggaaagtgaacgcgctgcagagcggcaacagccaggaaagcgtgaccgaacaggatagcaaagatagcacctatagcctgagcagcaccctgaccctgagcaaagcggattatgaaaaacataaagtgtatgcgtgcgaagtgacccatcagggcctgagcagcccggtgaccaaaagctttaaccgcggcgaatgc`,
  
  'Protein Heavy Chain': `EVQLVESGGGLVQPGRSLRLSCAASGFTFDDYAMHWVRQAPGKGLEWVSAITWNSGHIDYADSVEGRFTISRDNAKNSLYLQMNSLRAEDTAVYYCAKVSYLSTASSLDYWGQGTLVTVSSASTKGPSVFPLAPSSKSTSGGTAALGCLVKDYFPEPVTVSWNSGALTSGVHTFPAVLQSSGLYSLSSVVTVPSSSLGTQTYICNVNHKPSNTKVDKKVEPKSCDKTHTCPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSRDELTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK`,
  
  'Protein Light Chain': `DIQMTQSPSSLSASVGDRVTITCRASQGIRNYLAWYQQKPGKAPKLLIYAASSLQSGVPSRFSGSGSGTDFTLTISSLQPEDVATYYCQRYNRAPYTFGQGTKVEIKRTVAAPSVFIFPPSDEQLKSGTASVVCLLNNFYPREAKVQWKVNALQSGNSQESVTEQDSKDSTYSLSSTLTLSKADYEKHKVYACEVTHQGLSSPVTKSFNRGEC`
};

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
  // BLASTN-specific parameters
  const [wordSize, setWordSize] = useState('11');
  const [percIdentity, setPercIdentity] = useState('70');
  const [softMasking, setSoftMasking] = useState(true);
  const [dust, setDust] = useState(true);
  // Removed searchType state - no longer needed

  const [error, setError] = useState<string | null>(null);

  const blastTypes = [
    { value: 'blastp', label: 'BLASTP (Protein vs Protein)' },
    { value: 'blastn', label: 'BLASTN (Nucleotide vs Nucleotide)' },
    { value: 'blastx', label: 'BLASTX (Nucleotide vs Protein)' },
    { value: 'tblastn', label: 'TBLASTN (Protein vs Nucleotide)' },
  ];

  // Removed searchTypes - no longer needed as we're simplifying to single database selection

  const handleDatabaseChange = (event: any) => {
    const value = event.target.value as string;
    setSelectedDatabase(value);
  };

  const handleSearch = async () => {
    // Validate sequence
    if (!sequence.trim()) {
      setError('Please enter a sequence');
      return;
    }

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
      // Add BLASTN-specific parameters only for BLASTN
      ...(blastType === 'blastn' && {
        word_size: parseInt(wordSize),
        perc_identity: parseFloat(percIdentity),
        soft_masking: softMasking,
        dust: dust,
      }),
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

  const handleLoadExample = (exampleKey: keyof typeof EXAMPLE_SEQUENCES) => {
    setSequence(EXAMPLE_SEQUENCES[exampleKey]);
    setError(null);
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

    // Handle legacy database structure: { public: {...}, custom: {...}, internal: {...} }
    // Now showing all databases without distinction
    if (databases.public) {
      Object.entries(databases.public as Record<string, any>).forEach(([key, value]) => {
        if (typeof value === 'string') {
          options.push({ 
            value: key, 
            label: `${key} - ${value}` 
          });
        }
      });
    }

    if (databases.custom) {
      Object.entries(databases.custom as Record<string, any>).forEach(([key, value]) => {
        if (typeof value === 'string') {
          options.push({ 
            value: key, 
            label: `${key} - ${value}` 
          });
        }
      });
    }

    if (databases.internal) {
      Object.entries(databases.internal as Record<string, any>).forEach(([key, value]) => {
        if (typeof value === 'string') {
          options.push({ 
            value: key, 
            label: `${key} - ${value}` 
          });
        }
      });
    }

    // Filter databases based on BLAST type for legacy structure
    const sequenceType = getSequenceTypeFromBlastType(blastType);
    
    if (sequenceType === 'protein') {
      // For protein BLAST types, only show protein databases
      return options.filter(option => {
        const proteinDbs = ['swissprot', 'pdbaa', 'pdb'];
        return proteinDbs.includes(option.value);
      });
    } else if (sequenceType === 'nucleotide') {
      // For nucleotide BLAST types, only show nucleotide databases
      return options.filter(option => {
        const nucleotideDbs = ['refseq_select_rna', 'GCF_000001635.27_top_level', 'GCF_000001405.39_top_level', '16S_ribosomal_RNA', 'euk_cdna'];
        return nucleotideDbs.includes(option.value);
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
        {/* Search Type selector removed - simplified to single database selection */}

        {/* BLAST Type */}
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel id="blast-type-label">BLAST Type</InputLabel>
          <Select
            labelId="blast-type-label"
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
            <InputLabel id="database-label">Database</InputLabel>
            {databases ? (
              <Select
                labelId="database-label"
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
                labelId="database-label"
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

        {/* BLASTN-specific Parameters */}
        {blastType === 'blastn' && (
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <TextField
              sx={{ flex: 1, minWidth: 150 }}
              label="Word Size"
              value={wordSize}
              onChange={(e) => setWordSize(e.target.value)}
              helperText="Word size for initial matches"
              type="number"
            />

            <TextField
              sx={{ flex: 1, minWidth: 150 }}
              label="Percent Identity"
              value={percIdentity}
              onChange={(e) => setPercIdentity(e.target.value)}
              helperText="Minimum percent identity threshold"
              type="number"
            />

            <FormControl sx={{ flex: 1, minWidth: 150 }}>
              <InputLabel id="soft-masking-label">Soft Masking</InputLabel>
              <Select
                labelId="soft-masking-label"
                value={softMasking ? 'true' : 'false'}
                label="Soft Masking"
                onChange={(e) => setSoftMasking(e.target.value === 'true')}
              >
                <MenuItem value="true">Enabled</MenuItem>
                <MenuItem value="false">Disabled</MenuItem>
              </Select>
            </FormControl>

            <FormControl sx={{ flex: 1, minWidth: 150 }}>
              <InputLabel id="dust-label">Dust Filter</InputLabel>
              <Select
                labelId="dust-label"
                value={dust ? 'true' : 'false'}
                label="Dust Filter"
                onChange={(e) => setDust(e.target.value === 'true')}
              >
                <MenuItem value="true">Enabled</MenuItem>
                <MenuItem value="false">Disabled</MenuItem>
              </Select>
            </FormControl>
          </Box>
        )}

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

          {/* Example Sequences */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Example Sequences:
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {blastType === 'blastn' || blastType === 'blastx' ? (
                <>
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={() => handleLoadExample('Nucleotide Heavy Chain')}
                    disabled={loading}
                  >
                    Nucleotide Heavy
                  </Button>
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={() => handleLoadExample('Nucleotide Light Chain')}
                    disabled={loading}
                  >
                    Nucleotide Light
                  </Button>
                </>
              ) : (
                <>
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={() => handleLoadExample('Protein Heavy Chain')}
                    disabled={loading}
                  >
                    Protein Heavy
                  </Button>
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={() => handleLoadExample('Protein Light Chain')}
                    disabled={loading}
                  >
                    Protein Light
                  </Button>
                </>
              )}
            </Box>
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
