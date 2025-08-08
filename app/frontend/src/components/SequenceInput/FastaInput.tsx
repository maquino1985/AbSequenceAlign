import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Alert,
  Card,
  CardContent,
  Chip,
  Paper,
  Stack,
  LinearProgress
} from '@mui/material';
import { 
  PlayArrow, 
  Clear, 
  Help, 
  CloudUpload,
  Science,
  AutoAwesome,
  FileUpload,
  ContentPaste
} from '@mui/icons-material';
import { NumberingScheme } from '../../types/api';

interface FastaInputProps {
  onSubmit: (fastaContent: string, numberingScheme: NumberingScheme) => void;
}

const EXAMPLE_SEQUENCES = {
  'Heavy Chain IgG': `>IGHG1_Example
EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS`,
  
  'Light Chain Kappa': `>IGKV_Example
DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK`,
  
  'Multiple Sequences': `>Heavy_Chain_1
EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS

>Light_Chain_1
DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK

>Heavy_Chain_2
ELQLQESGPGLVKPSETLSLTCAVSGVSFSDYHWAWIRDPPGKGLEWIGDINHRGHTNYNPSLKSRVTVSIDTSKNQFSLKLSSVTAADTAVYFCARDFPNFIFDFWGQGTLVTVSS`
};

export const FastaInput: React.FC<FastaInputProps> = ({ onSubmit }) => {
  const [fastaContent, setFastaContent] = useState('');
  const [numberingScheme, setNumberingScheme] = useState<NumberingScheme>(NumberingScheme.IMGT);
  const [dragActive, setDragActive] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleSubmit = async () => {
    if (!fastaContent.trim()) {
      return;
    }
    setIsAnalyzing(true);
    try {
      await onSubmit(fastaContent, numberingScheme);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleClear = () => {
    setFastaContent('');
  };

  const handleExampleLoad = (exampleKey: keyof typeof EXAMPLE_SEQUENCES) => {
    setFastaContent(EXAMPLE_SEQUENCES[exampleKey]);
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        setFastaContent(content);
      };
      reader.readAsText(file);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      const reader = new FileReader();
      reader.onload = (event) => {
        const content = event.target?.result as string;
        setFastaContent(content);
      };
      reader.readAsText(file);
    }
  };

  return (
    <Box>
      {/* Hero Section */}
      <Paper 
        elevation={0}
        sx={{ 
          p: 4, 
          mb: 4, 
          background: (theme) => 
            theme.palette.mode === 'dark' 
              ? 'linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%)'
              : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          borderRadius: 3,
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        <Box sx={{ position: 'relative', zIndex: 1 }}>
          <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
            <Science sx={{ fontSize: 40 }} />
            <Box>
              <Typography variant="h4" sx={{ fontWeight: 800, mb: 0.5 }}>
                Sequence Analysis
              </Typography>
              <Typography variant="h6" sx={{ opacity: 0.9, fontWeight: 400 }}>
                Analyze antibody sequences with advanced annotation
              </Typography>
            </Box>
          </Stack>
        </Box>
        
        {/* Background decoration */}
        <Box
          sx={{
            position: 'absolute',
            top: -50,
            right: -50,
            width: 200,
            height: 200,
            borderRadius: '50%',
            background: 'rgba(255,255,255,0.1)',
            zIndex: 0,
          }}
        />
      </Paper>

      {/* Main Content */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '2fr 1fr' }, gap: 4 }}>
        
        {/* Input Section */}
        <Card elevation={0} sx={{ p: 0 }}>
          <CardContent sx={{ p: 4 }}>
            <Stack spacing={3}>
              
              {/* Section Header */}
              <Box>
                <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <ContentPaste color="primary" />
                  Input Sequences
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Paste your FASTA sequences or upload a file to get started
                </Typography>
              </Box>

              {/* Drag & Drop Area */}
              <Paper
                sx={{
                  border: dragActive 
                    ? '3px dashed' 
                    : '2px dashed',
                  borderColor: dragActive 
                    ? 'primary.main' 
                    : 'divider',
                  backgroundColor: dragActive 
                    ? 'action.hover' 
                    : 'background.paper',
                  borderRadius: 3,
                  p: 0,
                  transition: 'all 0.3s ease',
                  position: 'relative',
                  overflow: 'hidden'
                }}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                {isAnalyzing && (
                  <LinearProgress 
                    sx={{ 
                      position: 'absolute', 
                      top: 0, 
                      left: 0, 
                      right: 0,
                      zIndex: 1
                    }} 
                  />
                )}
                
                <TextField
                  fullWidth
                  multiline
                  rows={14}
                  variant="outlined"
                  placeholder={dragActive 
                    ? "Drop your FASTA file here..." 
                    : "Paste your FASTA sequences here...\n\nExample:\n>Heavy_Chain_1\nEVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEW..."
                  }
                  value={fastaContent}
                  onChange={(e) => setFastaContent(e.target.value)}
                  disabled={isAnalyzing}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      fontFamily: 'JetBrains Mono, Consolas, Monaco, monospace',
                      fontSize: '0.875rem',
                      lineHeight: 1.6,
                      '& fieldset': {
                        border: 'none',
                      },
                      '&:hover fieldset': {
                        border: 'none',
                      },
                      '&.Mui-focused fieldset': {
                        border: 'none',
                      },
                    },
                    '& .MuiInputBase-input': {
                      '&::placeholder': {
                        opacity: 0.7,
                        fontSize: '0.875rem',
                      }
                    }
                  }}
                />
                
                {dragActive && (
                  <Box
                    sx={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      bottom: 0,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      backgroundColor: 'rgba(25, 118, 210, 0.1)',
                      zIndex: 2,
                      pointerEvents: 'none',
                    }}
                  >
                    <Box sx={{ textAlign: 'center' }}>
                      <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
                      <Typography variant="h6" color="primary">
                        Drop FASTA file here
                      </Typography>
                    </Box>
                  </Box>
                )}
              </Paper>

              {/* Action Buttons */}
              <Stack direction="row" spacing={2}>
                <Button
                  variant="outlined"
                  component="label"
                  startIcon={<FileUpload />}
                  disabled={isAnalyzing}
                  sx={{ borderRadius: 2 }}
                >
                  Upload File
                  <input
                    type="file"
                    hidden
                    accept=".fasta,.fa,.txt"
                    onChange={handleFileUpload}
                  />
                </Button>
                
                <Button
                  variant="outlined"
                  color="secondary"
                  startIcon={<Clear />}
                  onClick={handleClear}
                  disabled={!fastaContent || isAnalyzing}
                  sx={{ borderRadius: 2 }}
                >
                  Clear
                </Button>
              </Stack>
            </Stack>
          </CardContent>
        </Card>

        {/* Controls & Examples Section */}
        <Stack spacing={3}>
          
          {/* Analysis Settings */}
          <Card elevation={0}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                <AutoAwesome color="primary" />
                Analysis Settings
              </Typography>
              
              <Stack spacing={3}>
                <FormControl fullWidth>
                  <InputLabel>Numbering Scheme</InputLabel>
                  <Select
                    value={numberingScheme}
                    label="Numbering Scheme"
                    onChange={(e) => setNumberingScheme(e.target.value as NumberingScheme)}
                    disabled={isAnalyzing}
                  >
                    <MenuItem value={NumberingScheme.IMGT}>IMGT</MenuItem>
                    <MenuItem value={NumberingScheme.KABAT}>Kabat</MenuItem>
                    <MenuItem value={NumberingScheme.CHOTHIA}>Chothia</MenuItem>
                    <MenuItem value={NumberingScheme.MARTIN}>Martin</MenuItem>
                    <MenuItem value={NumberingScheme.AHO}>AHo</MenuItem>
                    <MenuItem value={NumberingScheme.CGG}>CGG</MenuItem>
                  </Select>
                </FormControl>

                <Button
                  variant="contained"
                  size="large"
                  startIcon={isAnalyzing ? <Science /> : <PlayArrow />}
                  onClick={handleSubmit}
                  disabled={!fastaContent.trim() || isAnalyzing}
                  sx={{ 
                    py: 1.5,
                    fontSize: '1.1rem',
                    borderRadius: 2,
                    background: (theme) => 
                      theme.palette.mode === 'dark'
                        ? 'linear-gradient(45deg, #90caf9 30%, #42a5f5 90%)'
                        : 'linear-gradient(45deg, #1976d2 30%, #1565c0 90%)',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: '0 8px 25px rgba(25, 118, 210, 0.3)',
                    }
                  }}
                >
                  {isAnalyzing ? 'Analyzing...' : 'Analyze Sequences'}
                </Button>
              </Stack>
            </CardContent>
          </Card>

          {/* Examples */}
          <Card elevation={0}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <Help color="primary" />
                Example Sequences
              </Typography>
              <Stack spacing={1.5}>
                {Object.keys(EXAMPLE_SEQUENCES).map((exampleKey) => (
                  <Chip
                    key={exampleKey}
                    label={exampleKey}
                    variant="outlined"
                    clickable
                    disabled={isAnalyzing}
                    onClick={() => handleExampleLoad(exampleKey as keyof typeof EXAMPLE_SEQUENCES)}
                    sx={{ 
                      justifyContent: 'flex-start',
                      py: 1,
                      '&:hover': {
                        backgroundColor: 'action.hover',
                        transform: 'translateX(4px)',
                      },
                      transition: 'all 0.2s ease'
                    }}
                  />
                ))}
              </Stack>
            </CardContent>
          </Card>

          {/* Help Info */}
          <Alert 
            severity="info" 
            sx={{ 
              borderRadius: 2,
              '& .MuiAlert-message': { width: '100%' }
            }}
          >
            <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
              Supported Formats
            </Typography>
            <Typography variant="body2" component="div">
              • Standard FASTA format with headers<br />
              • Raw sequences (without headers)<br />
              • Multiple sequences in one input<br />
              • Minimum 15 amino acids per sequence
            </Typography>
          </Alert>
        </Stack>
      </Box>
    </Box>
  );
};
