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
  Divider,
  Stack,
  Tooltip,
  IconButton,
  Alert,
  LinearProgress,
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
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import type { AIRRRearrangement, IgBlastSearchResponse } from '../../../types/apiV2';

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

const SequenceDisplay = styled(Box)(({ theme }) => ({
  fontFamily: 'Monaco, Consolas, "Courier New", monospace',
  fontSize: '14px',
  lineHeight: 1.6,
  backgroundColor: '#FAFAFA',
  border: '1px solid #E0E0E0',
  borderRadius: theme.spacing(1),
  padding: theme.spacing(2),
  overflow: 'auto',
  maxHeight: '300px',
}));

const RegionChip = styled(Chip)<{ regionType: string }>(({ theme, regionType }) => {
  const colors = {
    FWR1: { bg: '#E3F2FD', border: '#1976D2', text: '#0D47A1' },
    CDR1: { bg: '#FFE0B2', border: '#F57C00', text: '#E65100' },
    FWR2: { bg: '#E8F5E8', border: '#388E3C', text: '#1B5E20' },
    CDR2: { bg: '#FCE4EC', border: '#C2185B', text: '#880E4F' },
    FWR3: { bg: '#F3E5F5', border: '#7B1FA2', text: '#4A148C' },
    CDR3: { bg: '#FFEBEE', border: '#D32F2F', text: '#B71C1C' },
    FWR4: { bg: '#E0F2F1', border: '#00796B', text: '#004D40' },
    V: { bg: '#E1F5FE', border: '#0277BD', text: '#01579B' },
    D: { bg: '#FFF3E0', border: '#FB8C00', text: '#E65100' },
    J: { bg: '#E8F5E8', border: '#43A047', text: '#2E7D32' },
    C: { bg: '#F1F8E9', border: '#689F38', text: '#33691E' },
  };
  
  const colorScheme = colors[regionType as keyof typeof colors] || colors.FWR1;
  
  return {
    backgroundColor: colorScheme.bg,
    color: colorScheme.text,
    border: `1px solid ${colorScheme.border}`,
    fontWeight: 500,
    margin: theme.spacing(0.25),
  };
});

interface AdvancedAIRRAnalysisProps {
  rearrangement: AIRRRearrangement;
  hitIndex: number;
}

const AdvancedAIRRAnalysis: React.FC<AdvancedAIRRAnalysisProps> = ({
  rearrangement,
  hitIndex,
}) => {
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

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

  const renderSequenceAlignment = () => {
    if (!rearrangement.sequence_alignment || !rearrangement.germline_alignment) {
      return (
        <Alert severity="info">
          <Typography variant="body2">
            Sequence alignment data not available for this hit.
          </Typography>
        </Alert>
      );
    }

    return (
      <Box>
        <Typography variant="h6" gutterBottom color="primary">
          Query vs Germline Alignment
        </Typography>
        <SequenceDisplay>
          <Box mb={2}>
            <Typography variant="subtitle2" color="primary" gutterBottom>
              Query Sequence:
            </Typography>
            <Typography variant="body2" fontFamily="monospace">
              {rearrangement.sequence_alignment}
            </Typography>
          </Box>
          <Divider sx={{ my: 2 }} />
          <Box>
            <Typography variant="subtitle2" color="primary" gutterBottom>
              Germline Sequence:
            </Typography>
            <Typography variant="body2" fontFamily="monospace">
              {rearrangement.germline_alignment}
            </Typography>
          </Box>
        </SequenceDisplay>
      </Box>
    );
  };

  const renderGeneDetails = () => {
    const genes = [
      { type: 'V', call: rearrangement.v_call, start: rearrangement.v_sequence_start, end: rearrangement.v_sequence_end },
      { type: 'D', call: rearrangement.d_call, start: rearrangement.d_sequence_start, end: rearrangement.d_sequence_end },
      { type: 'J', call: rearrangement.j_call, start: rearrangement.j_sequence_start, end: rearrangement.j_sequence_end },
      { type: 'C', call: rearrangement.c_call, start: undefined, end: undefined },
    ].filter(gene => gene.call);

    return (
      <Box>
        <Typography variant="h6" gutterBottom color="primary">
          Gene Assignment Details
        </Typography>
        <TableContainer component={Paper} elevation={1}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Gene Type</TableCell>
                <TableCell>Gene Call</TableCell>
                <TableCell>Sequence Position</TableCell>
                <TableCell>Germline Position</TableCell>
                <TableCell>Identity</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {genes.map((gene) => (
                <TableRow key={gene.type}>
                  <TableCell>
                    <RegionChip regionType={gene.type} label={gene.type} size="small" />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontFamily="monospace">
                      {gene.call}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {gene.start && gene.end ? `${gene.start}-${gene.end}` : 'N/A'}
                  </TableCell>
                  <TableCell>
                    {gene.type === 'V' && rearrangement.v_germline_start && rearrangement.v_germline_end 
                      ? `${rearrangement.v_germline_start}-${rearrangement.v_germline_end}`
                      : gene.type === 'D' && rearrangement.d_germline_start && rearrangement.d_germline_end
                      ? `${rearrangement.d_germline_start}-${rearrangement.d_germline_end}`
                      : gene.type === 'J' && rearrangement.j_germline_start && rearrangement.j_germline_end
                      ? `${rearrangement.j_germline_start}-${rearrangement.j_germline_end}`
                      : 'N/A'
                    }
                  </TableCell>
                  <TableCell>
                    {gene.type === 'V' && rearrangement.v_alignment?.identity 
                      ? `${rearrangement.v_alignment.identity.toFixed(1)}%`
                      : gene.type === 'D' && rearrangement.d_alignment?.identity
                      ? `${rearrangement.d_alignment.identity.toFixed(1)}%`
                      : gene.type === 'J' && rearrangement.j_alignment?.identity
                      ? `${rearrangement.j_alignment.identity.toFixed(1)}%`
                      : 'N/A'
                    }
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    );
  };

  const renderCDR3Analysis = () => {
    const junction = rearrangement.junction_region;
    if (!junction) {
      return (
        <Alert severity="info">
          <Typography variant="body2">
            CDR3/Junction analysis data not available for this hit.
          </Typography>
        </Alert>
      );
    }

    return (
      <Box>
        <Typography variant="h6" gutterBottom color="primary">
          CDR3/Junction Analysis
        </Typography>
        
        <Stack spacing={2}>
          <Card elevation={1}>
            <CardHeader
              title="CDR3 Sequence"
              action={
                <IconButton size="small">
                  <Download />
                </IconButton>
              }
            />
            <CardContent>
              <Box sx={{ 
                p: 2, 
                bgcolor: 'grey.50', 
                borderRadius: 1,
                fontFamily: 'monospace'
              }}>
                <Typography variant="body1" gutterBottom>
                  {junction.cdr3_aa || junction.cdr3 || 'N/A'}
                </Typography>
                {junction.cdr3_start && junction.cdr3_end && (
                  <Typography variant="body2" color="textSecondary">
                    Position: {junction.cdr3_start} - {junction.cdr3_end}
                  </Typography>
                )}
              </Box>
            </CardContent>
          </Card>

          <Card elevation={1}>
            <CardHeader title="Junction Details" />
            <CardContent>
              <Stack spacing={1}>
                {junction.junction && (
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2" color="textSecondary">Junction (NT):</Typography>
                    <Typography variant="body2" fontFamily="monospace">{junction.junction}</Typography>
                  </Box>
                )}
                {junction.junction_aa && (
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2" color="textSecondary">Junction (AA):</Typography>
                    <Typography variant="body2" fontFamily="monospace">{junction.junction_aa}</Typography>
                  </Box>
                )}
                {junction.junction_length && (
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2" color="textSecondary">Length:</Typography>
                    <Typography variant="body2">{junction.junction_length} bp</Typography>
                  </Box>
                )}
                {junction.np1 && (
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2" color="textSecondary">N1 Region:</Typography>
                    <Typography variant="body2" fontFamily="monospace">{junction.np1}</Typography>
                  </Box>
                )}
                {junction.np2 && (
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2" color="textSecondary">N2 Region:</Typography>
                    <Typography variant="body2" fontFamily="monospace">{junction.np2}</Typography>
                  </Box>
                )}
              </Stack>
            </CardContent>
          </Card>
        </Stack>
      </Box>
    );
  };

  const renderFrameworkCDRRegions = () => {
    const regions = [
      { name: 'FWR1', data: rearrangement.fwr1 },
      { name: 'CDR1', data: rearrangement.cdr1 },
      { name: 'FWR2', data: rearrangement.fwr2 },
      { name: 'CDR2', data: rearrangement.cdr2 },
      { name: 'FWR3', data: rearrangement.fwr3 },
      { name: 'FWR4', data: rearrangement.fwr4 },
    ];

    return (
      <Box>
        <Typography variant="h6" gutterBottom color="primary">
          Framework & CDR Regions
        </Typography>
        
        <Stack spacing={2}>
          {regions.map((region) => {
            if (!region.data) return null;
            
            return (
              <Card key={region.name} elevation={1}>
                <CardHeader
                  title={
                    <Box display="flex" alignItems="center" gap={1}>
                      <RegionChip regionType={region.name} label={region.name} size="small" />
                      <Typography variant="subtitle1">{region.name}</Typography>
                    </Box>
                  }
                />
                <CardContent>
                  <Stack spacing={1}>
                    {region.data.sequence && (
                      <Box>
                        <Typography variant="body2" color="textSecondary" gutterBottom>
                          Sequence:
                        </Typography>
                        <Typography 
                          variant="body1" 
                          fontFamily="monospace"
                          sx={{ 
                            bgcolor: 'grey.50', 
                            p: 1, 
                            borderRadius: 1,
                            wordBreak: 'break-all'
                          }}
                        >
                          {region.data.sequence}
                        </Typography>
                      </Box>
                    )}
                    {region.data.sequence_aa && (
                      <Box>
                        <Typography variant="body2" color="textSecondary" gutterBottom>
                          Amino Acid Sequence:
                        </Typography>
                        <Typography 
                          variant="body1" 
                          fontFamily="monospace"
                          sx={{ 
                            bgcolor: 'grey.50', 
                            p: 1, 
                            borderRadius: 1,
                            wordBreak: 'break-all'
                          }}
                        >
                          {region.data.sequence_aa}
                        </Typography>
                      </Box>
                    )}
                    {region.data.start && region.data.end && (
                      <Box display="flex" justifyContent="space-between">
                        <Typography variant="body2" color="textSecondary">Position:</Typography>
                        <Typography variant="body2">{region.data.start} - {region.data.end}</Typography>
                      </Box>
                    )}
                  </Stack>
                </CardContent>
              </Card>
            );
          })}
        </Stack>
      </Box>
    );
  };

  const renderQualityMetrics = () => {
    const productivityStatus = getProductivityStatus(rearrangement.productive);
    
    return (
      <Box>
        <Typography variant="h6" gutterBottom color="primary">
          Quality & Productivity Metrics
        </Typography>
        
        <Stack spacing={2}>
          <Card elevation={1}>
            <CardHeader title="Productivity Analysis" />
            <CardContent>
              <Stack spacing={2}>
                <Box display="flex" alignItems="center" gap={1}>
                  {productivityStatus.icon}
                  <Typography variant="body1">
                    Status: {productivityStatus.label}
                  </Typography>
                  <Chip 
                    label={productivityStatus.label} 
                    color={productivityStatus.color} 
                    size="small" 
                  />
                </Box>
                
                <Stack spacing={1}>
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2" color="textSecondary">Complete VDJ:</Typography>
                    <Typography variant="body2">
                      {rearrangement.complete_vdj ? 'Yes' : 'No'}
                    </Typography>
                  </Box>
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2" color="textSecondary">Stop Codon:</Typography>
                    <Typography variant="body2">
                      {rearrangement.stop_codon ? 'Yes' : 'No'}
                    </Typography>
                  </Box>
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2" color="textSecondary">VJ In Frame:</Typography>
                    <Typography variant="body2">
                      {rearrangement.vj_in_frame ? 'Yes' : 'No'}
                    </Typography>
                  </Box>
                  {rearrangement.v_frameshift && (
                    <Box display="flex" justifyContent="space-between">
                      <Typography variant="body2" color="textSecondary">V Frameshift:</Typography>
                      <Typography variant="body2">{rearrangement.v_frameshift}</Typography>
                    </Box>
                  )}
                  {rearrangement.d_frame !== undefined && (
                    <Box display="flex" justifyContent="space-between">
                      <Typography variant="body2" color="textSecondary">D Frame:</Typography>
                      <Typography variant="body2">{rearrangement.d_frame}</Typography>
                    </Box>
                  )}
                </Stack>
              </Stack>
            </CardContent>
          </Card>

          <Card elevation={1}>
            <CardHeader title="Alignment Quality" />
            <CardContent>
              <Stack spacing={2}>
                {rearrangement.v_alignment && (
                  <Box>
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      V Gene Alignment Score: {rearrangement.v_alignment.score || 'N/A'}
                    </Typography>
                    <LinearProgress 
                      variant="determinate" 
                      value={rearrangement.v_alignment.identity || 0} 
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                  </Box>
                )}
                {rearrangement.j_alignment && (
                  <Box>
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      J Gene Alignment Score: {rearrangement.j_alignment.score || 'N/A'}
                    </Typography>
                    <LinearProgress 
                      variant="determinate" 
                      value={rearrangement.j_alignment.identity || 0} 
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                  </Box>
                )}
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
            <Science />
            <Typography variant="h6">
              Advanced AIRR Analysis - Hit #{hitIndex + 1}
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
          <Tab label="Sequence Alignment" icon={<Biotech />} iconPosition="start" />
          <Tab label="Gene Details" icon={<Timeline />} iconPosition="start" />
          <Tab label="CDR3 Analysis" icon={<Science />} iconPosition="start" />
          <Tab label="Framework/CDR" icon={<Visibility />} iconPosition="start" />
          <Tab label="Quality Metrics" icon={<Info />} iconPosition="start" />
        </Tabs>

        <Box sx={{ mt: 2 }}>
          {activeTab === 0 && renderSequenceAlignment()}
          {activeTab === 1 && renderGeneDetails()}
          {activeTab === 2 && renderCDR3Analysis()}
          {activeTab === 3 && renderFrameworkCDRRegions()}
          {activeTab === 4 && renderQualityMetrics()}
        </Box>
      </CardContent>
    </StyledCard>
  );
};

export default AdvancedAIRRAnalysis;
