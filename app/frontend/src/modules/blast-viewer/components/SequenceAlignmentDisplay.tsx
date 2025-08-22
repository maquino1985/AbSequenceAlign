import React from 'react';
import {
  Box,
  Typography,
  Divider,
  Stack,
  Card,
  CardContent,
  CardHeader,
  Tooltip,
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
  position: 'relative',
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
  position: 'relative',
});

const PositionLabel = styled(Typography)(({ theme }) => ({
  minWidth: '80px',
  fontSize: '8px',
  color: theme.palette.text.secondary,
  textAlign: 'right',
  paddingRight: '4px',
}));

// PositionContent component removed as it's not used

// New styled component for region boundary indicators
const RegionBoundaryIndicator = styled(Box, {
  shouldForwardProp: (prop) => !['regionType', 'start', 'end', 'sequenceLength', 'isStart'].includes(prop as string),
})<{ 
  regionType: string; 
  start: number; 
  end: number; 
  sequenceLength: number;
  isStart: boolean;
}>(({ regionType, start, end, sequenceLength, isStart }) => {
  const colors = {
    FWR1: '#E3F2FD',
    CDR1: '#FFE0B2',
    FWR2: '#E8F5E8',
    CDR2: '#FCE4EC',
    FWR3: '#F3E5F5',
    CDR3: '#FFEBEE',
    FWR4: '#E0F2F1',
  };
  
  const color = colors[regionType as keyof typeof colors] || '#E3F2FD';
  const position = isStart ? start : end;
  const left = (position / sequenceLength) * 100;
  
  return {
    position: 'absolute',
    top: isStart ? '-8px' : 'auto',
    bottom: isStart ? 'auto' : '-8px',
    left: `${left}%`,
    width: '2px',
    height: '16px',
    backgroundColor: color,
    border: `1px solid ${color.replace('0.3', '0.8')}`,
    borderRadius: '1px',
    zIndex: 2,
    transform: 'translateX(-50%)',
    '&::after': {
      content: `"${regionType}"`,
      position: 'absolute',
      left: '50%',
      top: isStart ? '-20px' : '16px',
      transform: 'translateX(-50%)',
      fontSize: '8px',
      fontWeight: 'bold',
      color: color.replace('0.3', '0.8'),
      whiteSpace: 'nowrap',
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      padding: '1px 2px',
      borderRadius: '2px',
      border: `1px solid ${color}`,
    },
  };
});

// New styled component for region span indicators
const RegionSpanIndicator = styled(Box, {
  shouldForwardProp: (prop) => !['regionType', 'start', 'end', 'sequenceLength'].includes(prop as string),
})<{ 
  regionType: string; 
  start: number; 
  end: number; 
  sequenceLength: number;
}>(({ regionType, start, end, sequenceLength }) => {
  const colors = {
    FWR1: '#E3F2FD',
    CDR1: '#FFE0B2',
    FWR2: '#E8F5E8',
    CDR2: '#FCE4EC',
    FWR3: '#F3E5F5',
    CDR3: '#FFEBEE',
    FWR4: '#E0F2F1',
  };
  
  const color = colors[regionType as keyof typeof colors] || '#E3F2FD';
  const width = ((end - start + 1) / sequenceLength) * 100;
  const left = (start / sequenceLength) * 100;
  
  return {
    position: 'absolute',
    top: '-4px',
    left: `${left}%`,
    width: `${width}%`,
    height: '8px',
    backgroundColor: color,
    opacity: 0.6,
    border: `1px solid ${color.replace('0.3', '0.8')}`,
    borderRadius: '2px',
    zIndex: 1,
  };
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

// Interface for region boundary data
interface RegionBoundary {
  type: string;
  start: number;
  end: number;
  label: string;
}

interface SequenceAlignmentDisplayProps {
  querySequence: string;
  subjectSequence: string;
  queryStart: number;
  subjectStart: number;
  isAminoAcid?: boolean;
  title?: string;
  regionBoundaries?: RegionBoundary[];
}

const SequenceAlignmentDisplay: React.FC<SequenceAlignmentDisplayProps> = ({
  querySequence,
  subjectSequence,
  queryStart,
  subjectStart,
  isAminoAcid = false,
  title = 'Sequence Alignment',
  regionBoundaries = [],
}) => {
  const LINE_LENGTH = 60; // Characters per line

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

  // const alignment = compareSequences(querySequence, subjectSequence);
  const queryLines = splitIntoLines(querySequence, queryStart);
  const subjectLines = splitIntoLines(subjectSequence, subjectStart);

  const AminoAcidComponent = isAminoAcid ? AminoAcid : Nucleotide;

  // Helper function to render region boundary indicators for a line
  const renderRegionBoundaries = (lineStart: number, lineEnd: number, sequenceLength: number) => {
    const relevantBoundaries = regionBoundaries.filter(boundary => 
      (boundary.start >= lineStart && boundary.start <= lineEnd) ||
      (boundary.end >= lineStart && boundary.end <= lineEnd) ||
      (boundary.start <= lineStart && boundary.end >= lineEnd)
    );

    return relevantBoundaries.map((boundary, index) => {
      const adjustedStart = Math.max(boundary.start, lineStart);
      const adjustedEnd = Math.min(boundary.end, lineEnd);
      
      return (
        <React.Fragment key={`${boundary.type}-${index}`}>
          {/* Start boundary indicator */}
          {boundary.start >= lineStart && boundary.start <= lineEnd && (
            <Tooltip title={`${boundary.label} Start (Position ${boundary.start})`}>
              <RegionBoundaryIndicator
                regionType={boundary.type}
                start={boundary.start - lineStart + 1}
                end={boundary.end - lineStart + 1}
                sequenceLength={sequenceLength}
                isStart={true}
              />
            </Tooltip>
          )}
          
          {/* End boundary indicator */}
          {boundary.end >= lineStart && boundary.end <= lineEnd && (
            <Tooltip title={`${boundary.label} End (Position ${boundary.end})`}>
              <RegionBoundaryIndicator
                regionType={boundary.type}
                start={boundary.start - lineStart + 1}
                end={boundary.end - lineStart + 1}
                sequenceLength={sequenceLength}
                isStart={false}
              />
            </Tooltip>
          )}
          
          {/* Region span indicator */}
          {adjustedStart <= adjustedEnd && (
            <Tooltip title={`${boundary.label} (Positions ${boundary.start}-${boundary.end})`}>
              <RegionSpanIndicator
                regionType={boundary.type}
                start={adjustedStart - lineStart + 1}
                end={adjustedEnd - lineStart + 1}
                sequenceLength={sequenceLength}
              />
            </Tooltip>
          )}
        </React.Fragment>
      );
    });
  };

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
            const sequenceLength = queryLine.sequence.length;
            
            return (
              <Box key={lineIndex} sx={{ mb: 1, position: 'relative' }}>
                {/* Position indicator */}
                <Box display="flex" alignItems="center" mb={0.5}>
                  <PositionLabel>Pos:</PositionLabel>
                  <Typography variant="caption" sx={{ fontSize: '8px', color: 'text.secondary' }}>
                    {queryLine.start}-{queryLine.end}
                  </Typography>
                </Box>
                
                {/* Query sequence line with region boundaries */}
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
                    {/* Region boundary indicators */}
                    {renderRegionBoundaries(queryLine.start, queryLine.end, sequenceLength)}
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
        
        {/* Enhanced Legend with Region Boundaries */}
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
            
            {/* Region boundary legend */}
            {regionBoundaries.length > 0 && (
              <>
                <Divider orientation="vertical" flexItem />
                <Typography variant="caption" sx={{ fontWeight: 'bold' }}>Regions:</Typography>
                {Array.from(new Set(regionBoundaries.map(b => b.type))).map(regionType => {
                  const colors = {
                    FWR1: '#E3F2FD',
                    CDR1: '#FFE0B2',
                    FWR2: '#E8F5E8',
                    CDR2: '#FCE4EC',
                    FWR3: '#F3E5F5',
                    CDR3: '#FFEBEE',
                    FWR4: '#E0F2F1',
                  };
                  const color = colors[regionType as keyof typeof colors] || '#E3F2FD';
                  
                  return (
                    <Box key={regionType} display="flex" alignItems="center" gap={0.5}>
                      <Box
                        sx={{
                          width: '12px',
                          height: '8px',
                          backgroundColor: color,
                          border: `1px solid ${color.replace('0.3', '0.8')}`,
                          borderRadius: '1px',
                        }}
                      />
                      <Typography variant="caption">{regionType}</Typography>
                    </Box>
                  );
                })}
              </>
            )}
          </Stack>
        </Box>
      </CardContent>
    </Card>
  );
};

export default SequenceAlignmentDisplay;
