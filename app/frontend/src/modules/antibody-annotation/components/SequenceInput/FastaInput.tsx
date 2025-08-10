import React, { useState, useCallback } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Stack,
  Paper,
  LinearProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  ContentPaste,
  Send,
  Clear,
  FileUpload,
  CloudUpload,
  Help
} from '@mui/icons-material';
import { NumberingScheme } from '../../../../types/api';

interface FastaInputProps {
  onSubmit: (fastaContent: string, numberingScheme: NumberingScheme) => void;
}

const EXAMPLE_SEQUENCES = {
  'Humira IgG (Heavy Chain)': `>Humira_Heavy
EVQLVESGGGLVQPGRSLRLSCAASGFTFDDYAMHWVRQAPGKGLEWVSAITWNSGHIDYADSVEGRFTISRDNAKNSLYLQMNSLRAEDTAVYYCAKVSYLSTASSLDYWGQGTLVTVSSASTKGPSVFPLAPSSKSTSGGTAALGCLVKDYFPEPVTVSWNSGALTSGVHTFPAVLQSSGLYSLSSVVTVPSSSLGTQTYICNVNHKPSNTKVDKKVEPKSCDKTHTCPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSRDELTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK`,
  
  'Humira IgG (Light Chain)': `>Humira_Light
DIQMTQSPSSLSASVGDRVTITCRASQGIRNYLAWYQQKPGKAPKLLIYAASSLQSGVPSRFSGSGSGTDFTLTISSLQPEDVATYYCQRYNRAPYTFGQGTKVEIKRTVAAPSVFIFPPSDEQLKSGTASVVCLLNNFYPREAKVQWKVNALQSGNSQESVTEQDSKDSTYSLSSTLTLSKADYEKHKVYACEVTHQGLSSPVTKSFNRGEC`,
  
  'scFv with Linker': `>scFv_Example
DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIKGGGGGSGGGGSGGGGSGGGGSQVQLKQSGAEVKKPGASVKVSCKASGYTFTDEYMNWVRQAPGKSLEWMGYINPNNGGADYNQKFQGRVTMTVDQSISTAYMELSRLRSDDSAVYFCARLGYSNPYFDFWGQGTLVKVSS`,
  
  'Multiple Sequences': `>Heavy_Chain_1
EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSSASTKGPSVFPLAPSSKSTSGGTAALGCLVKDYFPEPVTVSWNSGALTSGVHTFPAVLQSSGLYSLSSVVTVPSSSLGTQTYICNVNHKPSNTKVDKKAEPKSCDKTHTCPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRWSG

>Light_Chain_1
DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIKRTVAAPSVFIFPPSDEQLKSGTASVVCLLNNFYPREAKVQWKVNALQSGNSQESVTEQDSKDSTYSLSSTLTLSKADYEKHKVYACEVTHQGLSSPVTKSFNRGEC

>Heavy_Chain_2
ELQLQESGPGLVKPSETLSLTCAVSGVSFSDYHWAWIRDPPGKGLEWIGDINHRGHTNYNPSLKSRVTVSIDTSKNQFSLKLSSVTAADTAVYFCARDFPNFIFDFWGQGTLVTVSSASTKGPSVFPLAPSSKSTSGGTAALGCLVKDYFPEPVTVSWNSGALTSGVHTFPAVLQSSGLYSLSSVVTVPSSSLGTQTYICNVNHKPSNTKVDKKAEPKSCDKTHTCPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRWSG`
};

export const FastaInput: React.FC<FastaInputProps> = ({ onSubmit }) => {
  const [fastaContent, setFastaContent] = useState('');
  const [numberingScheme, setNumberingScheme] = useState<NumberingScheme>(NumberingScheme.IMGT);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  const handleSubmit = async () => {
    if (!fastaContent.trim()) return;
    
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
      reader.onload = (event) => {
        const content = event.target?.result as string;
        setFastaContent(content);
      };
      reader.readAsText(file);
    }
  };

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
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
  }, []);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setFastaContent(e.target.value);
  }, []);

  return (
    <Box>
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
            onChange={handleInputChange}
            disabled={isAnalyzing}
            inputProps={{
              'data-testid': 'sequence-input'
            }}
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

        {/* Numbering Scheme Selection */}
        <FormControl fullWidth>
          <InputLabel>Numbering Scheme</InputLabel>
          <Select
            value={numberingScheme}
            onChange={(e) => setNumberingScheme(e.target.value as NumberingScheme)}
            disabled={isAnalyzing}
            MenuProps={{
              PaperProps: {
                style: {
                  maxHeight: 300
                }
              }
            }}
          >
            <MenuItem value={NumberingScheme.IMGT}>IMGT</MenuItem>
            <MenuItem value={NumberingScheme.KABAT}>Kabat</MenuItem>
            <MenuItem value={NumberingScheme.CHOTHIA}>Chothia</MenuItem>
            <MenuItem value={NumberingScheme.MARTIN}>Martin</MenuItem>
            <MenuItem value={NumberingScheme.AHO}>AHO</MenuItem>
            <MenuItem value={NumberingScheme.CGG}>CGG</MenuItem>
          </Select>
        </FormControl>

        {/* Submit Button */}
        <Button
          variant="contained"
          size="large"
          startIcon={<Send />}
          onClick={handleSubmit}
          disabled={!fastaContent.trim() || isAnalyzing}
          fullWidth
          sx={{ borderRadius: 2 }}
          data-testid="submit-button"
        >
          {isAnalyzing ? 'Analyzing...' : 'Start Analysis'}
        </Button>

        {/* Example Sequences */}
        <Box>
          <Typography variant="subtitle2" sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
            <Help fontSize="small" />
            Example Sequences
          </Typography>
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            {Object.keys(EXAMPLE_SEQUENCES).map((key) => (
              <Button
                key={key}
                size="small"
                variant="outlined"
                onClick={() => handleExampleLoad(key as keyof typeof EXAMPLE_SEQUENCES)}
                disabled={isAnalyzing}
                sx={{ borderRadius: 1 }}
              >
                {key.replace(/_/g, ' ')}
              </Button>
            ))}
          </Stack>
        </Box>
      </Stack>
    </Box>
  );
};
