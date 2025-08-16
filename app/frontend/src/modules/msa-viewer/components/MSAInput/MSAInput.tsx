import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Alert,
  Chip,
  Paper
} from '@mui/material';
import { CloudUpload } from '@mui/icons-material';
import { parseFasta } from '../../../../utils/fastaParser';

const EXAMPLE_MSA_SEQUENCES = {
  'Antibody Heavy Chains': `>Heavy_Chain_1
EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK

>Heavy_Chain_2
EVQLVESGGGLVQPGGSLRLSCAASGFTFSDYHWAWIRDPPGKGLEWIGDINHRGHTNYNPSLKSRVTVSIDTSKNQFSLKLSSVTAADTAVYFCAR

>Heavy_Chain_3
EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK`,

  'Antibody Light Chains': `>Light_Chain_1
DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK

>Light_Chain_2
DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK

>Light_Chain_3
DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK`,

  'Mixed Antibody Sequences': `>Heavy_Chain_1
EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK

>Light_Chain_1
DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK

>Heavy_Chain_2
EVQLVESGGGLVQPGGSLRLSCAASGFTFSDYHWAWIRDPPGKGLEWIGDINHRGHTNYNPSLKSRVTVSIDTSKNQFSLKLSSVTAADTAVYFCAR

>Light_Chain_2
DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK`
};

interface MSAInputProps {
  onUpload: (sequences: string[], sequenceNames?: string[]) => void;
  isLoading: boolean;
}

export const MSAInput: React.FC<MSAInputProps> = ({ onUpload, isLoading }) => {
  const [inputText, setInputText] = useState('');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sequences, setSequences] = useState<string[]>([]);
  const [sequenceNames, setSequenceNames] = useState<string[]>([]);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.fasta') && 
        !file.name.toLowerCase().endsWith('.fa') && 
        !file.name.toLowerCase().endsWith('.txt')) {
      setError('Please upload a FASTA file (.fasta, .fa, or .txt)');
      return;
    }

    setUploadedFile(file);
    setError(null);

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      try {
        const parsedSequences = parseFasta(content);
        setSequences(parsedSequences.map(seq => seq.sequence));
        setSequenceNames(parsedSequences.map(seq => seq.id));
        setError(null);
      } catch {
        setError('Invalid FASTA format');
        setSequences([]);
        setSequenceNames([]);
      }
    };
    reader.readAsText(file);
  };

  const handleTextInput = (event: React.ChangeEvent<HTMLInputElement>) => {
    const text = event.target.value;
    setInputText(text);
    setError(null);

    if (text.trim()) {
      try {
        const parsedSequences = parseFasta(text);
        setSequences(parsedSequences.map(seq => seq.sequence));
        setSequenceNames(parsedSequences.map(seq => seq.id));
      } catch {
        setError('Invalid FASTA format');
        setSequences([]);
        setSequenceNames([]);
      }
    } else {
      setSequences([]);
      setSequenceNames([]);
    }
  };

  const handleUpload = () => {
    if (sequences.length === 0) {
      setError('Please provide valid FASTA sequences');
      return;
    }

    if (sequences.length < 2) {
      setError('At least 2 sequences are required for MSA');
      return;
    }

    setError(null);
    onUpload(sequences, sequenceNames);
  };

  const handleClear = () => {
    setInputText('');
    setUploadedFile(null);
    setSequences([]);
    setSequenceNames([]);
    setError(null);
  };

  const handleExampleLoad = (exampleKey: keyof typeof EXAMPLE_MSA_SEQUENCES) => {
    const exampleContent = EXAMPLE_MSA_SEQUENCES[exampleKey];
    setInputText(exampleContent);
    try {
      const parsedSequences = parseFasta(exampleContent);
      setSequences(parsedSequences.map(seq => seq.sequence));
      setSequenceNames(parsedSequences.map(seq => seq.id));
      setError(null);
    } catch {
      setError('Invalid FASTA format');
      setSequences([]);
      setSequenceNames([]);
    }
  };

  return (
    <Box>
      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          Upload FASTA File
        </Typography>
        <Button
          variant="outlined"
          component="label"
          startIcon={<CloudUpload />}
          disabled={isLoading}
          fullWidth
          data-testid="file-input"
        >
          Choose FASTA File
          <input
            type="file"
            hidden
            accept=".fasta,.fa,.txt"
            onChange={handleFileUpload}
          />
        </Button>
        {uploadedFile && (
          <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip 
              label={uploadedFile.name} 
              size="small" 
              color="primary" 
            />
            <Typography variant="caption" color="text.secondary">
              {sequences.length} sequences
            </Typography>
          </Box>
        )}
      </Box>

      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          Or Paste FASTA Text
        </Typography>
        <TextField
          multiline
          rows={6}
          fullWidth
          placeholder=">Sequence_1&#10;EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK&#10;&#10;>Sequence_2&#10;EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK"
          value={inputText}
          onChange={handleTextInput}
          disabled={isLoading}
          error={!!error}
          helperText={error}
          data-testid="sequence-input"
        />
      </Box>

      {sequences.length > 0 && (
        <Paper sx={{ p: 2, mb: 2, bgcolor: 'background.default' }} data-testid="sequence-list">
          <Typography variant="subtitle2" gutterBottom>
            Sequences Ready ({sequences.length})
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {sequences.slice(0, 3).map((seq, index) => (
              <Chip
                key={index}
                label={sequenceNames[index] ? `${sequenceNames[index]} (${seq.length})` : `Seq_${index + 1} (${seq.length})`}
                size="small"
                variant="outlined"
              />
            ))}
            {sequences.length > 3 && (
              <Chip
                label={`+${sequences.length - 3} more`}
                size="small"
                variant="outlined"
              />
            )}
          </Box>
        </Paper>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Example Sequences */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          Example Sequences
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {Object.keys(EXAMPLE_MSA_SEQUENCES).map((exampleKey) => (
            <Chip
              key={exampleKey}
              label={exampleKey}
              variant="outlined"
              clickable
              disabled={isLoading}
              onClick={() => handleExampleLoad(exampleKey as keyof typeof EXAMPLE_MSA_SEQUENCES)}
              sx={{ 
                '&:hover': {
                  backgroundColor: 'action.hover',
                }
              }}
            />
          ))}
        </Box>
      </Box>

      <Box sx={{ display: 'flex', gap: 1 }}>
        <Button
          variant="contained"
          onClick={handleUpload}
          disabled={isLoading || sequences.length === 0}
          fullWidth
          data-testid="upload-btn"
        >
          {isLoading ? 'Uploading...' : 'Upload Sequences'}
        </Button>
        <Button
          variant="outlined"
          onClick={handleClear}
          disabled={isLoading}
        >
          Clear
        </Button>
      </Box>
    </Box>
  );
};
