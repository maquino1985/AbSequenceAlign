/**
 * IgBLAST Results Display Component
 * 
 * Comprehensive display of IgBLAST analysis results with enhanced visualization
 */

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
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
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider,
  Stack,
  Tooltip,
  IconButton,
  Alert,
  LinearProgress,
  Grid,
  Paper,
} from '@mui/material';
import {
  Science,
  Timeline,
  Biotech,
  Visibility,
  Download,
  Info,
  CheckCircle,
  Warning,
  Error as ErrorIcon,
  ExpandMore,
  Link as LinkIcon,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import type { IgBlastResponse } from '../../../types/database';
import AdvancedAIRRAnalysis from '../../blast-viewer/components/AdvancedAIRRAnalysis';
import type { AIRRRearrangement } from '../../../types/apiV2';
import { Link } from '@mui/material';
import CDRFrameworkDisplay from './CDRFrameworkDisplay';

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

const RegionChip = styled(Chip, {
  shouldForwardProp: (prop) => prop !== 'regionType',
})<{ regionType: string }>(({ theme, regionType }) => {
  const colors = {
    V: { bg: '#E1F5FE', border: '#0277BD', text: '#01579B' },
    D: { bg: '#FFF3E0', border: '#FB8C00', text: '#E65100' },
    J: { bg: '#E8F5E8', border: '#43A047', text: '#2E7D32' },
    C: { bg: '#F1F8E9', border: '#689F38', text: '#33691E' },
    heavy: { bg: '#E3F2FD', border: '#1976D2', text: '#0D47A1' },
    light: { bg: '#FFF8E1', border: '#F57F17', text: '#E65100' },
  };
  
  const colorScheme = colors[regionType as keyof typeof colors] || colors.V;
  
  return {
    backgroundColor: colorScheme.bg,
    color: colorScheme.text,
    border: `1px solid ${colorScheme.border}`,
    fontWeight: 500,
    margin: theme.spacing(0.25),
  };
});

interface IgBlastResultsDisplayProps {
  results: IgBlastResponse;
}

export const IgBlastResultsDisplay: React.FC<IgBlastResultsDisplayProps> = ({ results }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [expanded, setExpanded] = useState<string | false>('panel1');

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleAccordionChange = (panel: string) => (
    event: React.SyntheticEvent,
    isExpanded: boolean
  ) => {
    setExpanded(isExpanded ? panel : false);
  };

  const formatEvalue = (evalue: number | string) => {
    if (evalue === 0) return '0.0';
    const numValue = typeof evalue === 'string' ? parseFloat(evalue) : evalue;
    return numValue.toExponential(2);
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  const convertAirrDataToRearrangement = (airrData: any): AIRRRearrangement => {
    return {
      sequence_id: airrData.sequence_id || 'query',
      sequence: airrData.sequence || '',
      sequence_aa: airrData.sequence_aa,
      locus: airrData.locus,
      productive: airrData.productive,
      stop_codon: airrData.stop_codon === 'T',
      vj_in_frame: airrData.vj_in_frame === 'T',
      v_frameshift: airrData.v_frameshift,
      rev_comp: airrData.rev_comp === 'T',
      complete_vdj: airrData.complete_vdj === 'T',
      d_frame: airrData.d_frame ? parseInt(airrData.d_frame) : undefined,
      
      // Gene assignments
      v_call: airrData.v_call,
      d_call: airrData.d_call,
      j_call: airrData.j_call,
      c_call: airrData.c_call,
      
      // Sequence coordinates
      v_sequence_start: airrData.v_sequence_start ? parseInt(airrData.v_sequence_start) : undefined,
      v_sequence_end: airrData.v_sequence_end ? parseInt(airrData.v_sequence_end) : undefined,
      v_germline_start: airrData.v_germline_start ? parseInt(airrData.v_germline_start) : undefined,
      v_germline_end: airrData.v_germline_end ? parseInt(airrData.v_germline_end) : undefined,
      d_sequence_start: airrData.d_sequence_start ? parseInt(airrData.d_sequence_start) : undefined,
      d_sequence_end: airrData.d_sequence_end ? parseInt(airrData.d_sequence_end) : undefined,
      d_germline_start: airrData.d_germline_start ? parseInt(airrData.d_germline_start) : undefined,
      d_germline_end: airrData.d_germline_end ? parseInt(airrData.d_germline_end) : undefined,
      j_sequence_start: airrData.j_sequence_start ? parseInt(airrData.j_sequence_start) : undefined,
      j_sequence_end: airrData.j_sequence_end ? parseInt(airrData.j_sequence_end) : undefined,
      j_germline_start: airrData.j_germline_start ? parseInt(airrData.j_germline_start) : undefined,
      j_germline_end: airrData.j_germline_end ? parseInt(airrData.j_germline_end) : undefined,
      
      // Alignment details
      v_alignment: airrData.v_identity ? {
        identity: parseFloat(airrData.v_identity),
        score: airrData.v_score ? parseFloat(airrData.v_score) : undefined
      } : undefined,
      d_alignment: airrData.d_identity ? {
        identity: parseFloat(airrData.d_identity),
        score: airrData.d_score ? parseFloat(airrData.d_score) : undefined
      } : undefined,
      j_alignment: airrData.j_identity ? {
        identity: parseFloat(airrData.j_identity),
        score: airrData.j_score ? parseFloat(airrData.j_score) : undefined
      } : undefined,
      
      // Framework and CDR regions
      fwr1: airrData.fwr1 ? {
        sequence: airrData.fwr1,
        sequence_aa: airrData.fwr1_aa,
        start: airrData.fwr1_start ? parseInt(airrData.fwr1_start) : undefined,
        end: airrData.fwr1_end ? parseInt(airrData.fwr1_end) : undefined
      } : undefined,
      cdr1: airrData.cdr1 ? {
        sequence: airrData.cdr1,
        sequence_aa: airrData.cdr1_aa,
        start: airrData.cdr1_start ? parseInt(airrData.cdr1_start) : undefined,
        end: airrData.cdr1_end ? parseInt(airrData.cdr1_end) : undefined
      } : undefined,
      fwr2: airrData.fwr2 ? {
        sequence: airrData.fwr2,
        sequence_aa: airrData.fwr2_aa,
        start: airrData.fwr2_start ? parseInt(airrData.fwr2_start) : undefined,
        end: airrData.fwr2_end ? parseInt(airrData.fwr2_end) : undefined
      } : undefined,
      cdr2: airrData.cdr2 ? {
        sequence: airrData.cdr2,
        sequence_aa: airrData.cdr2_aa,
        start: airrData.cdr2_start ? parseInt(airrData.cdr2_start) : undefined,
        end: airrData.cdr2_end ? parseInt(airrData.cdr2_end) : undefined
      } : undefined,
      fwr3: airrData.fwr3 ? {
        sequence: airrData.fwr3,
        sequence_aa: airrData.fwr3_aa,
        start: airrData.fwr3_start ? parseInt(airrData.fwr3_start) : undefined,
        end: airrData.fwr3_end ? parseInt(airrData.fwr3_end) : undefined
      } : undefined,
      fwr4: airrData.fwr4 ? {
        sequence: airrData.fwr4,
        sequence_aa: airrData.fwr4_aa,
        start: airrData.fwr4_start ? parseInt(airrData.fwr4_start) : undefined,
        end: airrData.fwr4_end ? parseInt(airrData.fwr4_end) : undefined
      } : undefined,
      
      // Junction/CDR3 region
      junction_region: airrData.cdr3 ? {
        junction: airrData.junction,
        junction_aa: airrData.junction_aa,
        junction_length: airrData.junction_length ? parseInt(airrData.junction_length) : undefined,
        junction_aa_length: airrData.junction_aa_length ? parseInt(airrData.junction_aa_length) : undefined,
        cdr3: airrData.cdr3,
        cdr3_aa: airrData.cdr3_aa,
        cdr3_start: airrData.cdr3_start ? parseInt(airrData.cdr3_start) : undefined,
        cdr3_end: airrData.cdr3_end ? parseInt(airrData.cdr3_end) : undefined,
        np1: airrData.np1,
        np1_length: airrData.np1_length ? parseInt(airrData.np1_length) : undefined,
        np2: airrData.np2,
        np2_length: airrData.np2_length ? parseInt(airrData.np2_length) : undefined
      } : undefined,
      
      // Full sequence alignments
      sequence_alignment: airrData.sequence_alignment,
      germline_alignment: airrData.germline_alignment,
      sequence_alignment_aa: airrData.sequence_alignment_aa,
      germline_alignment_aa: airrData.germline_alignment_aa
    };
  };

  const renderSummary = () => (
    <StyledCard>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          <Science sx={{ mr: 1, verticalAlign: 'middle' }} />
          Analysis Summary
        </Typography>
        
        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid>
            <Card variant="outlined">
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Total Hits
                </Typography>
                <Typography variant="h4" color="primary">
                  {results.total_hits}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid>
            <Card variant="outlined">
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  BLAST Type
                </Typography>
                <Typography variant="h6">
                  {results.result.blast_type}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid>
            <Card variant="outlined">
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Chain Type
                </Typography>
                <Typography variant="h6">
                  {results.result.analysis_summary?.chain_type || 'Unknown'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid>
            <Card variant="outlined">
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Productive
                </Typography>
                <Typography variant="h6">
                  {results.result.analysis_summary?.productive ? 'Yes' : 'No'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Gene Assignments */}
        {results.result.analysis_summary && (
          <Box>
            <Typography variant="subtitle1" gutterBottom>
              Gene Assignments
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              {results.result.analysis_summary.v_gene && (
                <RegionChip
                  label={`V: ${results.result.analysis_summary.v_gene}`}
                  regionType="V"
                  size="medium"
                />
              )}
              {results.result.analysis_summary.d_gene && (
                <RegionChip
                  label={`D: ${results.result.analysis_summary.d_gene}`}
                  regionType="D"
                  size="medium"
                />
              )}
              {results.result.analysis_summary.j_gene && (
                <RegionChip
                  label={`J: ${results.result.analysis_summary.j_gene}`}
                  regionType="J"
                  size="medium"
                />
              )}
            </Stack>
          </Box>
        )}

        {/* CDR3 Information */}
        {results.result.analysis_summary?.cdr3_sequence && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              CDR3 Sequence
            </Typography>
            <Paper variant="outlined" sx={{ p: 2, bgcolor: 'grey.50' }}>
              <Typography
                variant="body1"
                fontFamily="monospace"
                sx={{ wordBreak: 'break-all' }}
              >
                {results.result.analysis_summary.cdr3_sequence}
              </Typography>
              {results.result.analysis_summary.cdr3_start && results.result.analysis_summary.cdr3_end && (
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  Position: {results.result.analysis_summary.cdr3_start} - {results.result.analysis_summary.cdr3_end}
                </Typography>
              )}
            </Paper>
          </Box>
        )}
      </CardContent>
    </StyledCard>
  );

  const renderHitsTable = () => (
    <StyledCard>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          <Biotech sx={{ mr: 1, verticalAlign: 'middle' }} />
          Detailed Hits
        </Typography>
        
        {results.result.hits && results.result.hits.length > 0 ? (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Type</TableCell>
                  <TableCell>Subject ID</TableCell>
                  <TableCell>Identity (%)</TableCell>
                  <TableCell>Alignment Length</TableCell>
                  <TableCell>E-value</TableCell>
                  <TableCell>Bit Score</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {results.result.hits.map((hit: any, index: number) => (
                  <TableRow key={index}>
                    <TableCell>
                      <RegionChip
                        label={hit.hit_type || 'Unknown'}
                        regionType={hit.hit_type || 'V'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {hit.subject_url ? (
                        <Link
                          href={hit.subject_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          sx={{ 
                            color: 'primary.main', 
                            textDecoration: 'none',
                            '&:hover': { textDecoration: 'underline' }
                          }}
                        >
                          <Typography variant="body2" fontFamily="monospace">
                            {hit.subject_id || hit.v_call || hit.d_call || hit.j_call || 'N/A'}
                          </Typography>
                        </Link>
                      ) : (
                        <Typography variant="body2" fontFamily="monospace">
                          {hit.subject_id || hit.v_call || hit.d_call || hit.j_call || 'N/A'}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      {hit.percent_identity ? formatPercentage(hit.percent_identity) : 
                       hit.v_identity ? formatPercentage(hit.v_identity) : 'N/A'}
                    </TableCell>
                    <TableCell>{hit.alignment_length || 'N/A'}</TableCell>
                    <TableCell>
                      {hit.evalue ? formatEvalue(hit.evalue) : 'N/A'}
                    </TableCell>
                    <TableCell>{hit.bit_score || 'N/A'}</TableCell>
                    <TableCell>
                      {hit.subject_url && (
                        <Tooltip title="View in IMGT">
                          <IconButton
                            size="small"
                            onClick={() => window.open(hit.subject_url, '_blank')}
                          >
                            <LinkIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        ) : (
          <Alert severity="info">
            No hits found in the analysis results.
          </Alert>
        )}
      </CardContent>
    </StyledCard>
  );

  const renderAIRRData = () => (
    <StyledCard>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          <Timeline sx={{ mr: 1, verticalAlign: 'middle' }} />
          AIRR Format Data
        </Typography>
        
        {results.result.airr_data && Object.keys(results.result.airr_data).length > 0 ? (
          <Box>
            {/* Use the existing AdvancedAIRRAnalysis component for rich visualization */}
            {results.result.airr_data && (
              <Box mb={3}>
                <Typography variant="subtitle1" gutterBottom>
                  Advanced AIRR Analysis
                </Typography>
                {/* Convert airr_data to AIRRRearrangement format */}
                <AdvancedAIRRAnalysis 
                  rearrangement={convertAirrDataToRearrangement(results.result.airr_data)}
                  hitIndex={0}
                />
              </Box>
            )}
            
            {/* Raw AIRR data in expandable section */}
            <Accordion
              expanded={expanded === 'airr-panel'}
              onChange={handleAccordionChange('airr-panel')}
            >
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography>Raw AIRR Data</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
                  <pre style={{ fontSize: '12px', fontFamily: 'monospace' }}>
                    {JSON.stringify(results.result.airr_data, null, 2)}
                  </pre>
                </Box>
              </AccordionDetails>
            </Accordion>
          </Box>
        ) : (
          <Alert severity="info">
            No AIRR format data available. Try enabling AIRR format output.
          </Alert>
        )}
      </CardContent>
    </StyledCard>
  );

  const renderCDRFramework = () => {
    // Extract CDR and framework data from the results
    const cdrFrameworkData = {
      fwr1_sequence: results.result.analysis_summary?.fr1_sequence,
      fwr1_aa: results.result.analysis_summary?.fr1_aa,
      cdr1_sequence: results.result.analysis_summary?.cdr1_sequence,
      cdr1_aa: results.result.analysis_summary?.cdr1_aa,
      fwr2_sequence: results.result.analysis_summary?.fr2_sequence,
      fwr2_aa: results.result.analysis_summary?.fr2_aa,
      cdr2_sequence: results.result.analysis_summary?.cdr2_sequence,
      cdr2_aa: results.result.analysis_summary?.cdr2_aa,
      fwr3_sequence: results.result.analysis_summary?.fr3_sequence,
      fwr3_aa: results.result.analysis_summary?.fr3_aa,
      cdr3_sequence: results.result.analysis_summary?.cdr3_sequence,
      cdr3_aa: results.result.analysis_summary?.cdr3_aa,
      fwr4_sequence: results.result.analysis_summary?.fr4_sequence,
      fwr4_aa: results.result.analysis_summary?.fr4_aa,
      cdr3_start: results.result.analysis_summary?.cdr3_start,
      cdr3_end: results.result.analysis_summary?.cdr3_end,
      // Add additional data for enhanced display
      fwr1_start: results.result.analysis_summary?.fr1_start,
      fwr1_end: results.result.analysis_summary?.fr1_end,
      cdr1_start: results.result.analysis_summary?.cdr1_start,
      cdr1_end: results.result.analysis_summary?.cdr1_end,
      fwr2_start: results.result.analysis_summary?.fr2_start,
      fwr2_end: results.result.analysis_summary?.fr2_end,
      cdr2_start: results.result.analysis_summary?.cdr2_start,
      cdr2_end: results.result.analysis_summary?.cdr2_end,
      fwr3_start: results.result.analysis_summary?.fr3_start,
      fwr3_end: results.result.analysis_summary?.fr3_end,
      fwr4_start: results.result.analysis_summary?.fr4_start,
      fwr4_end: results.result.analysis_summary?.fr4_end,
    };

    // Determine sequence type based on BLAST type
    const sequenceType = results.result.blast_type === 'igblastp' ? 'protein' : 'nucleotide';
    
    // Get the query sequence if available
    const sequence = results.result.query_sequence || results.result.airr_data?.sequence;

    return (
      <Box>
        <CDRFrameworkDisplay
          data={cdrFrameworkData}
          sequence={sequence}
          sequenceType={sequenceType}
        />
        
        {/* Note about sequence alignment availability */}
        {results.result.blast_type === 'igblastp' && (
          <Alert severity="info" sx={{ mt: 2 }}>
            <Typography variant="body2">
              <strong>Note:</strong> Detailed sequence alignment visualization is only available for nucleotide IgBLAST (igblastn) with AIRR format output. 
              For protein IgBLAST (igblastp), the CDR/framework analysis shows the extracted regions from the protein sequence.
            </Typography>
          </Alert>
        )}
      </Box>
    );
  };

  const renderDatabases = () => (
    <StyledCard>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          <Info sx={{ mr: 1, verticalAlign: 'middle' }} />
          Databases Used
        </Typography>
        
        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
          {Object.entries(results.databases_used).map(([gene, dbPath]) => (
            dbPath && (
              <Chip
                key={gene}
                label={`${gene}: ${dbPath.split('/').pop()}`}
                variant="outlined"
                size="small"
              />
            )
          ))}
        </Stack>
      </CardContent>
    </StyledCard>
  );

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        IgBLAST Analysis Results
      </Typography>
      
      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 2 }}>
        <Tab label="Summary" />
        <Tab label="Hits" />
        <Tab label="AIRR Data" />
        <Tab label="CDR/Framework" />
        <Tab label="Databases" />
      </Tabs>

      {activeTab === 0 && renderSummary()}
      {activeTab === 1 && renderHitsTable()}
      {activeTab === 2 && renderAIRRData()}
      {activeTab === 3 && renderCDRFramework()}
      {activeTab === 4 && renderDatabases()}
    </Box>
  );
};
