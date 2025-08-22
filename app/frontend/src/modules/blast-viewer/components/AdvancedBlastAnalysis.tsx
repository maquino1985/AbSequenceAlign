import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Card,
  CardContent,
  CardHeader,
  Stack,
  IconButton,
  Link,
  LinearProgress,
} from '@mui/material';
import {
  Science,
  Timeline,
  Biotech,
  Visibility,
  Info,
  Download,
  CheckCircle,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import type { BlastHit } from '../../../types/apiV2';
import SequenceAlignmentDisplay from './SequenceAlignmentDisplay';

const StyledCard = styled(Card)(({ theme }) => ({
  marginBottom: theme.spacing(2),
  borderRadius: theme.spacing(2),
  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  '&:hover': {
    boxShadow: '0 8px 24px rgba(0, 0, 0, 0.15)',
    transform: 'translateY(-2px)',
  },
}));

// SequenceDisplay component removed as it's not used

interface AdvancedBlastAnalysisProps {
  hit: BlastHit;
  hitIndex: number;
}

const AdvancedBlastAnalysis: React.FC<AdvancedBlastAnalysisProps> = ({
  hit,
  hitIndex,
}) => {
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const formatEvalue = (evalue: number) => {
    if (evalue === 0) return '0.0';
    return evalue.toExponential(2);
  };

  const getIdentityColor = (identity: number): 'success' | 'warning' | 'error' => {
    if (identity >= 90) return 'success';
    if (identity >= 70) return 'warning';
    return 'error';
  };

  const renderAlignmentDetails = () => {
    return (
      <Box>
        <Typography variant="h6" gutterBottom color="primary">
          Alignment Details
        </Typography>
        
        <Stack spacing={2}>
          <Card elevation={1}>
            <CardHeader title="Identity & Coverage" />
            <CardContent>
              <Stack spacing={2}>
                <Box>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                    <Typography variant="body2" color="textSecondary">
                      Identity: {hit.identity.toFixed(1)}%
                    </Typography>
                    <Chip 
                      label={`${hit.identity.toFixed(1)}%`}
                      color={getIdentityColor(hit.identity)}
                      size="small"
                    />
                  </Box>
                  {/* LinearProgress component removed as it's not imported */}
                </Box>
                
                <Box>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Alignment Length: {hit.alignment_length} bp
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={(hit.alignment_length / Math.max(hit.query_end - hit.query_start + 1, hit.subject_end - hit.subject_start + 1)) * 100} 
                    sx={{ height: 6, borderRadius: 3 }}
                  />
                </Box>
              </Stack>
            </CardContent>
          </Card>

          <Card elevation={1}>
            <CardHeader title="Statistical Significance" />
            <CardContent>
              <Stack spacing={1}>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">E-value:</Typography>
                  <Typography variant="body2" fontFamily="monospace" fontWeight="bold">
                    {formatEvalue(hit.evalue)}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">Bit Score:</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {hit.bit_score.toFixed(1)}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">Mismatches:</Typography>
                  <Typography variant="body2">
                    {hit.mismatches}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">Gap Opens:</Typography>
                  <Typography variant="body2">
                    {hit.gap_opens}
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Stack>
      </Box>
    );
  };

  const renderSequenceCoordinates = () => {
    return (
      <Box>
        <Typography variant="h6" gutterBottom color="primary">
          Sequence Coordinates
        </Typography>
        
        <TableContainer component={Paper} elevation={1}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Sequence</TableCell>
                <TableCell>Start</TableCell>
                <TableCell>End</TableCell>
                <TableCell>Length</TableCell>
                <TableCell>Strand</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <TableRow>
                <TableCell>
                  <Typography variant="body2" fontWeight="bold" color="primary">
                    Query ({hit.query_id})
                  </Typography>
                </TableCell>
                <TableCell>{hit.query_start}</TableCell>
                <TableCell>{hit.query_end}</TableCell>
                <TableCell>{hit.query_end - hit.query_start + 1}</TableCell>
                <TableCell>
                  <Chip label="+" size="small" color="primary" />
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>
                  <Typography variant="body2" fontWeight="bold" color="secondary">
                    Subject ({hit.subject_url ? (
                      <Link
                        href={hit.subject_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        sx={{ 
                          color: 'primary.main', 
                          textDecoration: 'underline',
                          fontWeight: 600,
                          cursor: 'pointer',
                          '&:hover': { 
                            color: 'primary.dark',
                            textDecoration: 'underline',
                            textDecorationThickness: '2px'
                          }
                        }}
                      >
                        {hit.subject_id}
                      </Link>
                    ) : (
                      hit.subject_id
                    )})
                  </Typography>
                </TableCell>
                <TableCell>{hit.subject_start}</TableCell>
                <TableCell>{hit.subject_end}</TableCell>
                <TableCell>{hit.subject_end - hit.subject_start + 1}</TableCell>
                <TableCell>
                  <Chip 
                    label={hit.subject_start < hit.subject_end ? "+" : "-"} 
                    size="small" 
                    color="secondary" 
                  />
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    );
  };

  const renderQualityMetrics = () => {
    const identityScore = hit.identity;
    const evalueScore = hit.evalue;
    const bitScore = hit.bit_score;
    
    // Calculate quality indicators
    const isHighIdentity = identityScore >= 90;
    const isHighBitScore = bitScore >= 100;
    const isLowEvalue = evalueScore <= 1e-10;
    
    const qualityScore = (
      (isHighIdentity ? 1 : 0) * 0.4 +
      (isHighBitScore ? 1 : 0) * 0.3 +
      (isLowEvalue ? 1 : 0) * 0.3
    ) * 100;

    return (
      <Box>
        <Typography variant="h6" gutterBottom color="primary">
          Quality Assessment
        </Typography>
        
        <Stack spacing={2}>
          <Card elevation={1}>
            <CardHeader title="Overall Quality Score" />
            <CardContent>
              <Box>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="body2" color="textSecondary">
                    Quality Score: {qualityScore.toFixed(0)}%
                  </Typography>
                  <Chip 
                    label={qualityScore >= 80 ? 'High' : qualityScore >= 60 ? 'Medium' : 'Low'}
                    color={qualityScore >= 80 ? 'success' : qualityScore >= 60 ? 'warning' : 'error'}
                    size="small"
                  />
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={qualityScore} 
                  color={qualityScore >= 80 ? 'success' : qualityScore >= 60 ? 'warning' : 'error'}
                  sx={{ height: 10, borderRadius: 5 }}
                />
              </Box>
            </CardContent>
          </Card>

          <Card elevation={1}>
            <CardHeader title="Quality Indicators" />
            <CardContent>
              <Stack spacing={1}>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="body2">High Identity (≥90%)</Typography>
                  <Chip 
                    icon={isHighIdentity ? <CheckCircle /> : <ErrorIcon />}
                    label={isHighIdentity ? 'Yes' : 'No'}
                    color={isHighIdentity ? 'success' : 'error'}
                    size="small"
                  />
                </Box>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="body2">High Bit Score (≥100)</Typography>
                  <Chip 
                    icon={isHighBitScore ? <CheckCircle /> : <ErrorIcon />}
                    label={isHighBitScore ? 'Yes' : 'No'}
                    color={isHighBitScore ? 'success' : 'error'}
                    size="small"
                  />
                </Box>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="body2">Low E-value (≤1e-10)</Typography>
                  <Chip 
                    icon={isLowEvalue ? <CheckCircle /> : <ErrorIcon />}
                    label={isLowEvalue ? 'Yes' : 'No'}
                    color={isLowEvalue ? 'success' : 'error'}
                    size="small"
                  />
                </Box>
              </Stack>
            </CardContent>
          </Card>

          <Card elevation={1}>
            <CardHeader title="Alignment Statistics" />
            <CardContent>
              <Stack spacing={1}>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">Coverage:</Typography>
                  <Typography variant="body2">
                    {((hit.alignment_length / Math.max(hit.query_end - hit.query_start + 1, hit.subject_end - hit.subject_start + 1)) * 100).toFixed(1)}%
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">Gap Percentage:</Typography>
                  <Typography variant="body2">
                    {hit.gap_opens > 0 ? 'Contains gaps' : 'No gaps'}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">Mismatch Rate:</Typography>
                  <Typography variant="body2">
                    {((hit.mismatches / hit.alignment_length) * 100).toFixed(1)}%
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Stack>
      </Box>
    );
  };

  const renderSequenceComparison = () => {
    // Check if we have actual alignment data
    const hasActualAlignment = hit.query_alignment && hit.subject_alignment;
    
    // Generate alignment data
    const getAlignmentData = () => {
      if (hasActualAlignment) {
        // Use actual alignment data from BLAST
        return {
          querySeq: hit.query_alignment!,
          subjectSeq: hit.subject_alignment!,
          isAminoAcid: hit.blast_type === 'blastp' || hit.blast_type === 'blastx',
          title: `BLAST Alignment (${hit.identity.toFixed(1)}% identity)`
        };
      } else {
        // Generate simulated alignment based on BLAST statistics
        const queryLength = hit.query_end - hit.query_start + 1;
        const subjectLength = hit.subject_end - hit.subject_start + 1;
        const alignmentLength = hit.alignment_length;
        const mismatches = hit.mismatches;
        const matches = alignmentLength - mismatches;
        
        // Create simulated sequences
        let querySeq = '';
        let subjectSeq = '';
        
        // Add aligned region
        for (let i = 0; i < alignmentLength; i++) {
          if (i < matches) {
            // Matching positions
            querySeq += 'A';
            subjectSeq += 'A';
          } else {
            // Mismatching positions
            querySeq += 'A';
            subjectSeq += 'T';
          }
        }
        
        // Add gaps if needed
        if (queryLength > alignmentLength) {
          querySeq += '-'.repeat(queryLength - alignmentLength);
        }
        if (subjectLength > alignmentLength) {
          subjectSeq += '-'.repeat(subjectLength - alignmentLength);
        }
        
        return {
          querySeq,
          subjectSeq,
          isAminoAcid: false,
          title: `Simulated Alignment (${hit.identity.toFixed(1)}% identity)`
        };
      }
    };

    const alignment = getAlignmentData();

    return (
      <Box>
        <Typography variant="h6" gutterBottom color="primary">
          Sequence Alignment Visualization
        </Typography>
        
        <Stack spacing={3}>
          {/* Alignment Display */}
          <SequenceAlignmentDisplay
            querySequence={alignment.querySeq}
            subjectSequence={alignment.subjectSeq}
            queryStart={hit.query_start}
            subjectStart={hit.subject_start}
            isAminoAcid={alignment.isAminoAcid}
            title={alignment.title}
          />

          <Card elevation={1}>
            <CardHeader title="Detailed Alignment Statistics" />
            <CardContent>
              <Stack spacing={2}>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">Query Sequence:</Typography>
                  <Typography variant="body2" fontFamily="monospace" fontWeight="bold">
                    {hit.query_id}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">Subject Sequence:</Typography>
                  <Typography variant="body2" fontFamily="monospace" fontWeight="bold">
                    {hit.subject_url ? (
                      <Link
                        href={hit.subject_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        sx={{ 
                          color: 'primary.main', 
                          textDecoration: 'underline',
                          fontWeight: 600,
                          cursor: 'pointer',
                          '&:hover': { 
                            color: 'primary.dark',
                            textDecoration: 'underline',
                            textDecorationThickness: '2px'
                          }
                        }}
                      >
                        {hit.subject_id}
                      </Link>
                    ) : (
                      hit.subject_id
                    )}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">Query Range:</Typography>
                  <Typography variant="body2" fontFamily="monospace">
                    {hit.query_start} - {hit.query_end} ({hit.query_end - hit.query_start + 1} bp)
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">Subject Range:</Typography>
                  <Typography variant="body2" fontFamily="monospace">
                    {hit.subject_start} - {hit.subject_end} ({hit.subject_end - hit.subject_start + 1} bp)
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">Alignment Length:</Typography>
                  <Typography variant="body2" fontFamily="monospace">
                    {hit.alignment_length} bp
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">Matching Positions:</Typography>
                  <Typography variant="body2" fontFamily="monospace">
                    {hit.alignment_length - hit.mismatches} bp
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">Mismatches:</Typography>
                  <Typography variant="body2" fontFamily="monospace">
                    {hit.mismatches} bp
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">Gap Opens:</Typography>
                  <Typography variant="body2" fontFamily="monospace">
                    {hit.gap_opens}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">Alignment Coverage:</Typography>
                  <Typography variant="body2" fontFamily="monospace">
                    {((hit.alignment_length / Math.max(hit.query_end - hit.query_start + 1, hit.subject_end - hit.subject_start + 1)) * 100).toFixed(1)}%
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>

          <Card elevation={1}>
            <CardHeader title="Alignment Quality Metrics" />
            <CardContent>
              <Stack spacing={2}>
                <Box>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Identity Score: {hit.identity.toFixed(1)}%
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={hit.identity} 
                    color={hit.identity > 90 ? 'success' : hit.identity > 70 ? 'warning' : 'error'}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                </Box>
                <Box>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Coverage: {((hit.alignment_length / Math.max(hit.query_end - hit.query_start + 1, hit.subject_end - hit.subject_start + 1)) * 100).toFixed(1)}%
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={(hit.alignment_length / Math.max(hit.query_end - hit.query_start + 1, hit.subject_end - hit.subject_start + 1)) * 100} 
                    sx={{ height: 6, borderRadius: 3 }}
                  />
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Stack>
      </Box>
    );
  };

  return (
    <StyledCard>
      <CardHeader
        title={
          <Box display="flex" alignItems="center" gap={1}>
            <Biotech />
            <Typography variant="h6">
              Advanced BLAST Analysis - Hit #{hitIndex + 1}
            </Typography>
          </Box>
        }
        action={
          <Box display="flex" gap={1}>
            <IconButton size="small">
              <Download />
            </IconButton>
          </Box>
        }
      />
      <CardContent>
        <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 2 }}>
          <Tab label="Alignment Details" icon={<Science />} iconPosition="start" />
          <Tab label="Coordinates" icon={<Timeline />} iconPosition="start" />
          <Tab label="Quality Metrics" icon={<Info />} iconPosition="start" />
          <Tab label="Sequence Comparison" icon={<Visibility />} iconPosition="start" />
        </Tabs>

        <Box sx={{ mt: 2 }}>
          {activeTab === 0 && renderAlignmentDetails()}
          {activeTab === 1 && renderSequenceCoordinates()}
          {activeTab === 2 && renderQualityMetrics()}
          {activeTab === 3 && renderSequenceComparison()}
        </Box>
      </CardContent>
    </StyledCard>
  );
};

export default AdvancedBlastAnalysis;
