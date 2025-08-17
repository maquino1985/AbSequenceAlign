import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
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
  Grid,
  Card,
  CardContent,
  Divider,
} from '@mui/material';
import { ExpandMore, Biotech, Search } from '@mui/icons-material';

interface BlastResultsProps {
  results: any;
  searchType: 'standard' | 'antibody';
}

const BlastResults: React.FC<BlastResultsProps> = ({ results, searchType }) => {
  const [expanded, setExpanded] = useState<string | false>('panel1');

  const handleAccordionChange = (panel: string) => (
    event: React.SyntheticEvent,
    isExpanded: boolean
  ) => {
    setExpanded(isExpanded ? panel : false);
  };

  const formatEvalue = (evalue: number) => {
    if (evalue === 0) return '0.0';
    return evalue.toExponential(2);
  };

  const renderStandardResults = () => {
    const hits = results.results?.hits || [];
    
    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          <Search sx={{ mr: 1, verticalAlign: 'middle' }} />
          BLAST Search Results
        </Typography>
        
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Total Hits
                </Typography>
                <Typography variant="h4">
                  {hits.length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  BLAST Type
                </Typography>
                <Typography variant="h6">
                  {results.results?.blast_type || 'Unknown'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Query Info
                </Typography>
                <Typography variant="body2">
                  {results.results?.query_info?.query_id || 'Unknown'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {hits.length > 0 ? (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Subject ID</TableCell>
                  <TableCell>Identity (%)</TableCell>
                  <TableCell>Alignment Length</TableCell>
                  <TableCell>E-value</TableCell>
                  <TableCell>Bit Score</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {hits.map((hit: any, index: number) => (
                  <TableRow key={index}>
                    <TableCell>{hit.subject_id}</TableCell>
                    <TableCell>{hit.identity?.toFixed(1)}</TableCell>
                    <TableCell>{hit.alignment_length}</TableCell>
                    <TableCell>{formatEvalue(hit.evalue)}</TableCell>
                    <TableCell>{hit.bit_score?.toFixed(1)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        ) : (
          <Typography variant="body1" color="text.secondary">
            No significant hits found.
          </Typography>
        )}
      </Box>
    );
  };

  const renderAntibodyResults = () => {
    const hits = results.results?.hits || [];
    const summary = results.summary;
    const geneAssignments = results.gene_assignments;
    const cdr3Info = results.cdr3_info;
    
    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          <Biotech sx={{ mr: 1, verticalAlign: 'middle' }} />
          Antibody Analysis Results
        </Typography>

        {/* Summary Cards */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Total Hits
                </Typography>
                <Typography variant="h4">
                  {summary?.total_hits || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Best Identity
                </Typography>
                <Typography variant="h6">
                  {summary?.best_identity?.toFixed(1) || 0}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  V Gene
                </Typography>
                <Typography variant="body2">
                  {geneAssignments?.v_gene || 'Not found'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  CDR3 Sequence
                </Typography>
                <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                  {cdr3Info?.sequence || 'Not found'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Gene Assignments */}
        {geneAssignments && (
          <Accordion expanded={expanded === 'panel1'} onChange={handleAccordionChange('panel1')}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography variant="h6">Gene Assignments</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={6} md={3}>
                  <Typography variant="subtitle2" color="text.secondary">V Gene</Typography>
                  <Chip label={geneAssignments.v_gene || 'Not found'} variant="outlined" />
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="subtitle2" color="text.secondary">D Gene</Typography>
                  <Chip label={geneAssignments.d_gene || 'Not found'} variant="outlined" />
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="subtitle2" color="text.secondary">J Gene</Typography>
                  <Chip label={geneAssignments.j_gene || 'Not found'} variant="outlined" />
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="subtitle2" color="text.secondary">C Gene</Typography>
                  <Chip label={geneAssignments.c_gene || 'Not found'} variant="outlined" />
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        )}

        {/* CDR3 Information */}
        {cdr3Info && (
          <Accordion expanded={expanded === 'panel2'} onChange={handleAccordionChange('panel2')}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography variant="h6">CDR3 Information</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2" color="text.secondary">CDR3 Sequence</Typography>
                  <Typography variant="body1" sx={{ fontFamily: 'monospace', backgroundColor: '#f5f5f5', p: 1, borderRadius: 1 }}>
                    {cdr3Info.sequence}
                  </Typography>
                </Grid>
                <Grid item xs={6} md={4}>
                  <Typography variant="subtitle2" color="text.secondary">Start Position</Typography>
                  <Typography variant="body1">{cdr3Info.start}</Typography>
                </Grid>
                <Grid item xs={6} md={4}>
                  <Typography variant="subtitle2" color="text.secondary">End Position</Typography>
                  <Typography variant="body1">{cdr3Info.end}</Typography>
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        )}

        {/* Detailed Hits */}
        <Accordion expanded={expanded === 'panel3'} onChange={handleAccordionChange('panel3')}>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography variant="h6">Detailed Hits ({hits.length})</Typography>
          </AccordionSummary>
          <AccordionDetails>
            {hits.length > 0 ? (
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Subject ID</TableCell>
                      <TableCell>Identity (%)</TableCell>
                      <TableCell>V Gene</TableCell>
                      <TableCell>D Gene</TableCell>
                      <TableCell>J Gene</TableCell>
                      <TableCell>C Gene</TableCell>
                      <TableCell>E-value</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {hits.map((hit: any, index: number) => (
                      <TableRow key={index}>
                        <TableCell>{hit.subject_id}</TableCell>
                        <TableCell>{hit.identity?.toFixed(1)}</TableCell>
                        <TableCell>{hit.v_gene || 'N/A'}</TableCell>
                        <TableCell>{hit.d_gene || 'N/A'}</TableCell>
                        <TableCell>{hit.j_gene || 'N/A'}</TableCell>
                        <TableCell>{hit.c_gene || 'N/A'}</TableCell>
                        <TableCell>{formatEvalue(hit.evalue)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Typography variant="body1" color="text.secondary">
                No significant hits found.
              </Typography>
            )}
          </AccordionDetails>
        </Accordion>
      </Box>
    );
  };

  return (
    <Paper sx={{ p: 3, mt: 3 }}>
      {searchType === 'antibody' ? renderAntibodyResults() : renderStandardResults()}
    </Paper>
  );
};

export default BlastResults;
