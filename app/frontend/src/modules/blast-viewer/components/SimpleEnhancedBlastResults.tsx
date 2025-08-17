import React, { useState, useMemo } from 'react';
import {
  Box,
  Paper,
  Typography,
  Chip,
  Card,
  CardContent,
  CardHeader,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tooltip,
  LinearProgress,
  Divider,
  IconButton,
  Alert,
  Badge,
  Stack,
  Avatar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Link,
} from '@mui/material';
import {
  ExpandMore,
  Biotech,
  Search,
  Timeline,
  Science,
  Visibility,
  Download,
  Info,
  CheckCircle,
  Warning,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import type { 
  BlastSearchResponse, 
  IgBlastSearchResponse, 
  IgBlastHit,
  BlastHit,
  AIRRRearrangement
} from '../../../types/apiV2';
import AdvancedBlastAnalysis from './AdvancedBlastAnalysis';
import AdvancedAIRRAnalysis from './AdvancedAIRRAnalysis';

// Styled components for enhanced visual design
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

const GradientHeader = styled(CardHeader)(({ theme }) => ({
  background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
  color: theme.palette.primary.contrastText,
  '& .MuiCardHeader-title': {
    fontWeight: 600,
  },
}));

const RegionChip = styled(Chip)<{ regionType: string }>(({ theme, regionType }) => {
  const colors = {
    FWR: { bg: theme.palette.grey[100], color: theme.palette.grey[700] },
    CDR: { bg: theme.palette.secondary.light, color: theme.palette.secondary.contrastText },
    V: { bg: theme.palette.primary.light, color: theme.palette.primary.contrastText },
    D: { bg: theme.palette.warning.light, color: theme.palette.warning.contrastText },
    J: { bg: theme.palette.success.light, color: theme.palette.success.contrastText },
    C: { bg: theme.palette.info.light, color: theme.palette.info.contrastText },
  };
  
  const colorScheme = colors[regionType as keyof typeof colors] || colors.FWR;
  
  return {
    backgroundColor: colorScheme.bg,
    color: colorScheme.color,
    fontWeight: 500,
    margin: theme.spacing(0.25),
    transition: 'all 0.2s ease',
    '&:hover': {
      transform: 'scale(1.05)',
      boxShadow: theme.shadows[2],
    },
  };
});

const MetricCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  textAlign: 'center',
  borderRadius: theme.spacing(1.5),
  background: `linear-gradient(145deg, ${theme.palette.background.paper} 0%, ${theme.palette.grey[50]} 100%)`,
  border: `1px solid ${theme.palette.divider}`,
  transition: 'all 0.2s ease',
  '&:hover': {
    borderColor: theme.palette.primary.main,
    transform: 'translateY(-1px)',
  },
}));

interface SimpleEnhancedBlastResultsProps {
  results: BlastSearchResponse['data'] | IgBlastSearchResponse['data'];
  searchType: 'standard' | 'antibody';
}

const SimpleEnhancedBlastResults: React.FC<SimpleEnhancedBlastResultsProps> = ({ 
  results, 
  searchType 
}) => {
  const [expanded, setExpanded] = useState<string | false>('summary');
  const [selectedHit, setSelectedHit] = useState<number | null>(null);
  const [advancedAnalysisOpen, setAdvancedAnalysisOpen] = useState(false);
  const [selectedHitForAnalysis, setSelectedHitForAnalysis] = useState<number | null>(null);

  const handleAccordionChange = (panel: string) => (
    event: React.SyntheticEvent,
    isExpanded: boolean
  ) => {
    setExpanded(isExpanded ? panel : false);
  };

  // Enhanced data processing for IgBLAST results
  const processedData = useMemo(() => {
    if (searchType === 'antibody') {
      const igBlastData = results as IgBlastSearchResponse['data'];
      const hits = igBlastData.results?.hits || [];
      const summary = igBlastData.analysis_summary;
      const airrResult = igBlastData.airr_result;
      
      return {
        hits,
        summary,
        airrResult,
        hasAirrData: !!airrResult && airrResult.rearrangements.length > 0,
        productivityRate: airrResult ? 
          (airrResult.productive_sequences / airrResult.total_sequences * 100) : 0,
      };
    } else {
      const blastData = results as BlastSearchResponse['data'];
      return {
        hits: blastData.results?.hits || [],
        summary: null,
        airrResult: null,
        hasAirrData: false,
        productivityRate: 0,
      };
    }
  }, [results, searchType]);

  const getProductivityStatus = (productive?: string) => {
    if (!productive) return { label: 'Unknown', color: 'default' as const, icon: <Info /> };
    if (productive === 'T') return { 
      label: 'Productive', 
      color: 'success' as const, 
      icon: <CheckCircle /> 
    };
    if (productive === 'F') return { 
      label: 'Unproductive', 
      color: 'error' as const, 
      icon: <ErrorIcon /> 
    };
    return { label: 'Unknown', color: 'default' as const, icon: <Info /> };
  };

  const formatEvalue = (evalue: number | string) => {
    if (evalue === 0) return '0.0';
    const numValue = typeof evalue === 'string' ? parseFloat(evalue) : evalue;
    return numValue.toExponential(2);
  };

  const renderSummaryPanel = () => {
    const { hits, summary, hasAirrData, productivityRate, airrResult } = processedData;
    
    return (
      <StyledCard>
        <GradientHeader
          title={
            <Box display="flex" alignItems="center" gap={1}>
              <Science />
              <Typography variant="h6">
                {searchType === 'antibody' ? 'IgBLAST Analysis Summary' : 'BLAST Search Summary'}
              </Typography>
            </Box>
          }
          action={
            <Badge badgeContent={hits.length} color="secondary">
              <Biotech />
            </Badge>
          }
        />
        <CardContent>
          <Box display="flex" flexWrap="wrap" gap={2} mb={3}>
            {/* Key Metrics */}
            <MetricCard elevation={0} sx={{ minWidth: 120 }}>
              <Typography variant="h4" color="primary" fontWeight="bold">
                {hits.length}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Total Hits
              </Typography>
            </MetricCard>
            
            {hasAirrData && (
              <>
                <MetricCard elevation={0} sx={{ minWidth: 120 }}>
                  <Typography variant="h4" color="success.main" fontWeight="bold">
                    {productivityRate.toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Productive Rate
                  </Typography>
                </MetricCard>
                <MetricCard elevation={0} sx={{ minWidth: 120 }}>
                  <Box display="flex" alignItems="center" gap={1}>
                    {getProductivityStatus(airrResult?.rearrangements?.[0]?.productive).icon}
                    <Typography variant="h6" fontWeight="bold">
                      {getProductivityStatus(airrResult?.rearrangements?.[0]?.productive).label}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="textSecondary">
                    Status
                  </Typography>
                </MetricCard>
              </>
            )}
          </Box>

          {/* Gene Assignments (for IgBLAST) */}
          {searchType === 'antibody' && summary && (
            <Box mb={3}>
              <Typography variant="h6" gutterBottom color="primary">
                Best Gene Assignments
              </Typography>
              <Stack direction="row" flexWrap="wrap" spacing={1}>
                {summary.best_v_gene && (
                  <RegionChip regionType="V" label={`V: ${summary.best_v_gene}`} size="small" />
                )}
                {summary.best_d_gene && (
                  <RegionChip regionType="D" label={`D: ${summary.best_d_gene}`} size="small" />
                )}
                {summary.best_j_gene && (
                  <RegionChip regionType="J" label={`J: ${summary.best_j_gene}`} size="small" />
                )}
                {summary.best_c_gene && (
                  <RegionChip regionType="C" label={`C: ${summary.best_c_gene}`} size="small" />
                )}
              </Stack>
            </Box>
          )}

          {/* CDR3 Information */}
          {searchType === 'antibody' && summary?.cdr3_sequence && (
            <Box>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom color="primary">
                CDR3 Analysis
              </Typography>
              <Box sx={{ 
                p: 2, 
                bgcolor: 'grey.50', 
                borderRadius: 2,
                border: '1px solid',
                borderColor: 'grey.200'
              }}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  CDR3 Sequence:
                </Typography>
                <Typography 
                  variant="h6" 
                  fontFamily="monospace"
                  sx={{ 
                    bgcolor: 'background.paper',
                    p: 1,
                    borderRadius: 1,
                    border: '1px solid',
                    borderColor: 'divider',
                    wordBreak: 'break-all',
                    mb: 2
                  }}
                >
                  {summary.cdr3_sequence}
                </Typography>
                
                <Stack direction="row" spacing={2} flexWrap="wrap">
                  {summary.junction_length && (
                    <Chip label={`Length: ${summary.junction_length} bp`} size="small" />
                  )}
                  {summary.locus && (
                    <Chip label={`Locus: ${summary.locus}`} size="small" color="primary" />
                  )}
                </Stack>
              </Box>
            </Box>
          )}
        </CardContent>
      </StyledCard>
    );
  };

  const renderHitDetails = (hit: IgBlastHit, index: number) => {
    const productivityStatus = getProductivityStatus(hit.productive);
    
    return (
      <StyledCard key={index}>
        <CardHeader
          avatar={
            <Avatar sx={{ bgcolor: 'primary.main' }}>
              {index + 1}
            </Avatar>
          }
          title={
            <Box display="flex" alignItems="center" gap={1}>
              <Typography variant="h6">
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
                    {hit.subject_id || hit.query_id}
                  </Link>
                ) : (
                  hit.subject_id || hit.query_id
                )}
              </Typography>
              {hit.productive && (
                <Chip
                  icon={productivityStatus.icon}
                  label={productivityStatus.label}
                  color={productivityStatus.color}
                  size="small"
                />
              )}
            </Box>
          }
          action={
            <Box display="flex" gap={1}>
              <Tooltip title="Identity Score">
                <Chip 
                  label={`${hit.identity.toFixed(1)}%`} 
                  color={hit.identity > 90 ? 'success' : hit.identity > 70 ? 'warning' : 'default'}
                  size="small"
                />
              </Tooltip>
              <IconButton 
                size="small" 
                onClick={() => {
                  setSelectedHitForAnalysis(index);
                  setAdvancedAnalysisOpen(true);
                }}
              >
                <Visibility />
              </IconButton>
            </Box>
          }
        />
        <CardContent>
          <Box display="flex" flexWrap="wrap" gap={2} mb={2}>
            {/* Basic Alignment Info */}
            <Box flex="1" minWidth={200}>
              <Typography variant="subtitle2" gutterBottom color="primary">
                Alignment Details
              </Typography>
              <Stack spacing={1}>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">Identity:</Typography>
                  <Box display="flex" alignItems="center" gap={1}>
                    <LinearProgress 
                      variant="determinate" 
                      value={hit.identity} 
                      sx={{ width: 60, height: 6, borderRadius: 3 }}
                      color={hit.identity > 90 ? 'success' : hit.identity > 70 ? 'warning' : 'error'}
                    />
                    <Typography variant="body2" fontWeight="bold">
                      {hit.identity.toFixed(1)}%
                    </Typography>
                  </Box>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">E-value:</Typography>
                  <Typography variant="body2" fontFamily="monospace">
                    {formatEvalue(hit.evalue)}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">Bit Score:</Typography>
                  <Typography variant="body2">{hit.bit_score.toFixed(1)}</Typography>
                </Box>
              </Stack>
            </Box>

            {/* Gene Assignments (for IgBLAST) */}
            {searchType === 'antibody' && (
              <Box flex="1" minWidth={200}>
                <Typography variant="subtitle2" gutterBottom color="primary">
                  Gene Assignments
                </Typography>
                <Stack direction="row" flexWrap="wrap" spacing={0.5}>
                  {hit.v_gene && <RegionChip regionType="V" label={hit.v_gene} size="small" />}
                  {hit.d_gene && <RegionChip regionType="D" label={hit.d_gene} size="small" />}
                  {hit.j_gene && <RegionChip regionType="J" label={hit.j_gene} size="small" />}
                  {hit.c_gene && <RegionChip regionType="C" label={hit.c_gene} size="small" />}
                </Stack>
              </Box>
            )}
          </Box>

          {/* CDR3 Details */}
          {searchType === 'antibody' && hit.cdr3_sequence && (
            <Box>
              <Divider sx={{ my: 1 }} />
              <Typography variant="subtitle2" gutterBottom color="primary">
                CDR3 Details
              </Typography>
              <Box sx={{ 
                p: 2, 
                bgcolor: 'grey.50', 
                borderRadius: 1,
                fontFamily: 'monospace'
              }}>
                <Typography variant="body2" gutterBottom>
                  Sequence: {hit.cdr3_sequence}
                </Typography>
                {hit.cdr3_start && hit.cdr3_end && (
                  <Typography variant="body2" color="textSecondary">
                    Position: {hit.cdr3_start} - {hit.cdr3_end}
                  </Typography>
                )}
              </Box>
            </Box>
          )}


        </CardContent>
      </StyledCard>
    );
  };

  const { hits } = processedData;

  if (!hits || hits.length === 0) {
    return (
      <Alert severity="info" sx={{ mt: 2 }}>
        <Typography variant="h6" gutterBottom>
          No results found
        </Typography>
        <Typography variant="body2">
          No significant alignments were found for your query sequence.
        </Typography>
      </Alert>
    );
  }

  return (
    <Box>
      {/* Summary Panel */}
      <Accordion 
        expanded={expanded === 'summary'} 
        onChange={handleAccordionChange('summary')}
        sx={{ mb: 2, borderRadius: 2 }}
      >
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Timeline />
            Analysis Summary
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          {renderSummaryPanel()}
        </AccordionDetails>
      </Accordion>

      {/* Results Panel */}
      <Accordion 
        expanded={expanded === 'results'} 
        onChange={handleAccordionChange('results')}
        defaultExpanded
      >
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Search />
            Detailed Results ({hits.length} hits)
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Box>
            {hits.map((hit, index) => renderHitDetails(hit as IgBlastHit, index))}
          </Box>
        </AccordionDetails>
      </Accordion>

      {/* Advanced Analysis Dialog */}
      <Dialog 
        open={advancedAnalysisOpen} 
        onClose={() => setAdvancedAnalysisOpen(false)}
        maxWidth="lg"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 2 }
        }}
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <Science />
            <Typography variant="h6">
              Advanced Analysis
            </Typography>
          </Box>
        </DialogTitle>
        <DialogContent sx={{ p: 3 }}>
          {selectedHitForAnalysis !== null && (
            <>
              {searchType === 'antibody' ? (
                // For IgBLAST results, show AIRR analysis if available
                (() => {
                  // results is already the 'data' part of the API response
                  const igBlastData = results as IgBlastSearchResponse['data'];
                  const airrResult = igBlastData.airr_result;
                  
                  if (airrResult && airrResult.rearrangements && airrResult.rearrangements.length > 0) {
                    // For IgBLAST, there's typically one rearrangement per query sequence
                    // Use the first rearrangement (index 0) since we're analyzing one sequence at a time
                    const rearrangement = airrResult.rearrangements[0];
                    
                    console.log('AIRR Data Available:', {
                      airrResult,
                      rearrangements: airrResult.rearrangements,
                      selectedRearrangement: rearrangement,
                      hitIndex: selectedHitForAnalysis
                    });
                    
                    return (
                      <AdvancedAIRRAnalysis 
                        rearrangement={rearrangement}
                        hitIndex={selectedHitForAnalysis}
                      />
                    );
                  } else {
                    // Fallback to basic hit data
                    const hit = hits[selectedHitForAnalysis] as IgBlastHit;
                    

                    
                    return (
                      <Box>
                        <Alert severity="info" sx={{ mb: 2 }}>
                          <Typography variant="body2">
                            Advanced AIRR analysis data not available for this hit. 
                            Showing basic hit information.
                          </Typography>
                        </Alert>
                        <Card>
                          <CardContent>
                            <Typography variant="h6" gutterBottom>
                              Hit #{selectedHitForAnalysis + 1}: {hit.subject_url ? (
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
                            <Typography variant="body2">
                              Identity: {hit.identity.toFixed(1)}% | 
                              E-value: {formatEvalue(hit.evalue)} | 
                              Bit Score: {hit.bit_score.toFixed(1)}
                            </Typography>
                          </CardContent>
                        </Card>
                      </Box>
                    );
                  }
                })()
              ) : (
                // For standard BLAST results
                <AdvancedBlastAnalysis 
                  hit={hits[selectedHitForAnalysis] as BlastHit}
                  hitIndex={selectedHitForAnalysis}
                />
              )}
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAdvancedAnalysisOpen(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SimpleEnhancedBlastResults;
