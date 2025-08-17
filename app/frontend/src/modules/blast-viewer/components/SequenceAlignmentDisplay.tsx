import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Divider,
  Stack,
  Chip,
  Card,
  CardContent,
  CardHeader,
} from '@mui/material';
import { styled } from '@mui/material/styles';

const AlignmentContainer = styled(Box)(({ theme }) => ({
  fontFamily: 'Monaco, Consolas, "Courier New", monospace',
  fontSize: '11px',
  lineHeight: 1.2,
  backgroundColor: '#FAFAFA',
  border: '1px solid #E0E0E0',
  borderRadius: theme.spacing(1),
  padding: theme.spacing(1),
  overflow: 'auto',
  maxHeight: '300px',
}));

const SequenceLine = styled(Box)({
  display: 'flex',
  alignItems: 'center',
  gap: '4px',
  marginBottom: '2px',
});

const SequenceLabel = styled(Typography)(({ theme }) => ({
  minWidth: '80px',
  fontWeight: 'bold',
  color: theme.palette.primary.main,
  fontSize: '10px',
}));

const SequenceContent = styled(Box)({
  flex: 1,
  display: 'flex',
  flexWrap: 'wrap',
  gap: '1px',
});

const PositionLabel = styled(Typography)(({ theme }) => ({
  minWidth: '80px',
  fontSize: '8px',
  color: theme.palette.text.secondary,
  textAlign: 'right',
  paddingRight: '4px',
}));

const PositionContent = styled(Box)({
  flex: 1,
  display: 'flex',
  flexWrap: 'wrap',
  gap: '1px',
  fontSize: '10px',
  color: '#666',
});

const AminoAcid = styled(Box)<{ 
  type: 'match' | 'mismatch' | 'gap' | 'normal';
  isQuery?: boolean;
}>(({ theme, type, isQuery }) => {
  const baseStyles = {
    width: '12px',
    height: '14px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '9px',
    fontWeight: 'bold',
    borderRadius: '1px',
    border: '1px solid transparent',
  };

  switch (type) {
    case 'match':
      return {
        ...baseStyles,
        backgroundColor: isQuery ? '#E8F5E8' : '#E8F5E8',
        color: '#2E7D32',
        borderColor: '#4CAF50',
      };
    case 'mismatch':
      return {
        ...baseStyles,
        backgroundColor: isQuery ? '#FFEBEE' : '#FFEBEE',
        color: '#C62828',
        borderColor: '#F44336',
      };
    case 'gap':
      return {
        ...baseStyles,
        backgroundColor: '#F5F5F5',
        color: '#757575',
        borderColor: '#BDBDBD',
      };
    default:
      return {
        ...baseStyles,
        backgroundColor: 'transparent',
        color: theme.palette.text.primary,
        borderColor: 'transparent',
      };
  }
});

const Nucleotide = styled(Box)<{ 
  type: 'match' | 'mismatch' | 'gap' | 'normal';
  isQuery?: boolean;
}>(({ theme, type, isQuery }) => {
  const baseStyles = {
    width: '10px',
    height: '12px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '8px',
    fontWeight: 'bold',
    borderRadius: '1px',
    border: '1px solid transparent',
  };

  switch (type) {
    case 'match':
      return {
        ...baseStyles,
        backgroundColor: isQuery ? '#E8F5E8' : '#E8F5E8',
        color: '#2E7D32',
        borderColor: '#4CAF50',
      };
    case 'mismatch':
      return {
        ...baseStyles,
        backgroundColor: isQuery ? '#FFEBEE' : '#FFEBEE',
        color: '#C62828',
        borderColor: '#F44336',
      };
    case 'gap':
      return {
        ...baseStyles,
        backgroundColor: '#F5F5F5',
        color: '#757575',
        borderColor: '#BDBDBD',
      };
    default:
      return {
        ...baseStyles,
        backgroundColor: 'transparent',
        color: theme.palette.text.primary,
        borderColor: 'transparent',
      };
  }
});

interface SequenceAlignmentDisplayProps {
  querySequence: string;
  subjectSequence: string;
  queryStart: number;
  subjectStart: number;
  isAminoAcid?: boolean;
  title?: string;
}

const SequenceAlignmentDisplay: React.FC<SequenceAlignmentDisplayProps> = ({
  querySequence,
  subjectSequence,
  queryStart,
  subjectStart,
  isAminoAcid = false,
  title = 'Sequence Alignment',
}) => {
  const LINE_LENGTH = 60; // Characters per line
  const charWidth = isAminoAcid ? 12 : 10;
  const positionWidth = isAminoAcid ? 12 : 10;

  const compareSequences = (seq1: string, seq2: string) => {
    const result = [];
    const maxLength = Math.max(seq1.length, seq2.length);
    
    for (let i = 0; i < maxLength; i++) {
      const char1 = seq1[i] || '-';
      const char2 = seq2[i] || '-';
      
      if (char1 === '-' || char2 === '-') {
        result.push({ type: 'gap' as const, query: char1, subject: char2 });
      } else if (char1 === char2) {
        result.push({ type: 'match' as const, query: char1, subject: char2 });
      } else {
        result.push({ type: 'mismatch' as const, query: char1, subject: char2 });
      }
    }
    
    return result;
  };

  const splitIntoLines = (sequence: string, startPos: number) => {
    const lines = [];
    for (let i = 0; i < sequence.length; i += LINE_LENGTH) {
      const line = sequence.slice(i, i + LINE_LENGTH);
      const lineStart = startPos + i;
      const lineEnd = Math.min(startPos + i + LINE_LENGTH - 1, startPos + sequence.length - 1);
      lines.push({
        sequence: line,
        start: lineStart,
        end: lineEnd,
        position: lineStart
      });
    }
    return lines;
  };

  const alignment = compareSequences(querySequence, subjectSequence);
  const queryLines = splitIntoLines(querySequence, queryStart);
  const subjectLines = splitIntoLines(subjectSequence, subjectStart);

  const AminoAcidComponent = isAminoAcid ? AminoAcid : Nucleotide;

  return (
    <Card elevation={1}>
      <CardHeader 
        title={title}
        titleTypographyProps={{ variant: 'h6', color: 'primary' }}
      />
      <CardContent>
        <AlignmentContainer>
          {queryLines.map((queryLine, lineIndex) => {
            const subjectLine = subjectLines[lineIndex];
            if (!subjectLine) return null;

            const queryAlignment = compareSequences(queryLine.sequence, subjectLine.sequence);
            
            return (
              <Box key={lineIndex} sx={{ mb: 1 }}>
                {/* Position indicator */}
                <Box display="flex" alignItems="center" mb={0.5}>
                  <PositionLabel>Pos:</PositionLabel>
                  <Typography variant="caption" sx={{ fontSize: '8px', color: 'text.secondary' }}>
                    {queryLine.start}-{queryLine.end}
                  </Typography>
                </Box>
                
                {/* Query sequence line */}
                <SequenceLine>
                  <SequenceLabel>Query:</SequenceLabel>
                  <SequenceContent>
                    {queryAlignment.map((item, index) => (
                      <AminoAcidComponent
                        key={index}
                        type={item.type}
                        isQuery={true}
                      >
                        {item.query}
                      </AminoAcidComponent>
                    ))}
                  </SequenceContent>
                </SequenceLine>
                
                {/* Subject sequence line */}
                <SequenceLine>
                  <SequenceLabel>Subj:</SequenceLabel>
                  <SequenceContent>
                    {queryAlignment.map((item, index) => (
                      <AminoAcidComponent
                        key={index}
                        type={item.type}
                        isQuery={false}
                      >
                        {item.subject}
                      </AminoAcidComponent>
                    ))}
                  </SequenceContent>
                </SequenceLine>
                
                {/* Position indicator for subject */}
                <Box display="flex" alignItems="center" mt={0.5}>
                  <PositionLabel>Pos:</PositionLabel>
                  <Typography variant="caption" sx={{ fontSize: '8px', color: 'text.secondary' }}>
                    {subjectLine.start}-{subjectLine.end}
                  </Typography>
                </Box>
                
                {lineIndex < queryLines.length - 1 && <Divider sx={{ my: 1 }} />}
              </Box>
            );
          })}
        </AlignmentContainer>
        
        {/* Compact Legend */}
        <Box sx={{ mt: 1 }}>
          <Stack direction="row" spacing={1} flexWrap="wrap" alignItems="center">
            <Typography variant="caption" sx={{ fontWeight: 'bold' }}>Legend:</Typography>
            <Box display="flex" alignItems="center" gap={0.5}>
              <AminoAcidComponent type="match" />
              <Typography variant="caption">Match</Typography>
            </Box>
            <Box display="flex" alignItems="center" gap={0.5}>
              <AminoAcidComponent type="mismatch" />
              <Typography variant="caption">Mismatch</Typography>
            </Box>
            <Box display="flex" alignItems="center" gap={0.5}>
              <AminoAcidComponent type="gap" />
              <Typography variant="caption">Gap</Typography>
            </Box>
          </Stack>
        </Box>
      </CardContent>
    </Card>
  );
};

export default SequenceAlignmentDisplay;
