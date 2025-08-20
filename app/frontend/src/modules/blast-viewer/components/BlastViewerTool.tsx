import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Tabs,
  Tab,
  Alert,
  CircularProgress,
  Switch,
  FormControlLabel,
} from '@mui/material';
import { Search, Biotech } from '@mui/icons-material';
import api from '../../../services/api';
import BlastSearchForm from './BlastSearchForm';
import BlastResults from './BlastResults';
import AntibodyAnalysis from './AntibodyAnalysis';
import SimpleEnhancedBlastResults from './SimpleEnhancedBlastResults';
import type { BlastSearchResponse, IgBlastSearchResponse } from '../../../types/apiV2';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`blast-tabpanel-${index}`}
      aria-labelledby={`blast-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

export const BlastViewerTool: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [databases, setDatabases] = useState<Record<string, unknown> | null>(null);
  const [organisms, setOrganisms] = useState<string[]>([]);
  const [results, setResults] = useState<BlastSearchResponse['data'] | IgBlastSearchResponse['data'] | null>(null);
  const [useEnhancedView, setUseEnhancedView] = useState(true);


  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Load databases (organisms endpoint doesn't exist yet)
      const dbResponse = await api.getBlastDatabases();
      
      console.log('BLAST Database Response:', dbResponse);
      
      setDatabases(dbResponse.data?.databases || {});
      setOrganisms([]); // TODO: Add organisms endpoint
    } catch (err: unknown) {
      setError(`Failed to load initial data: ${(err as Error).message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    setResults(null);
    setError(null);
  };

  const handleSearch = async (searchData: Record<string, unknown>) => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await api.searchPublicDatabases(searchData);
      
      if (response.data) {
        setResults(response.data as BlastSearchResponse['data'] | IgBlastSearchResponse['data']);
      }
    } catch (err: unknown) {
      setError(`Search failed: ${(err as Error).message}`);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !databases) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, textAlign: 'center' }}>
        <CircularProgress />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Loading BLAST tools...
        </Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        <Search sx={{ mr: 1, verticalAlign: 'middle' }} />
        BLAST Sequence Search
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Search sequences against protein and nucleotide databases, or perform antibody-specific analysis using IgBLAST.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ width: '100%' }}>
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            aria-label="BLAST search tabs"
          >
            <Tab 
              label="Standard BLAST" 
              icon={<Search />} 
              iconPosition="start"
            />
            <Tab 
              label="Antibody Analysis" 
              icon={<Biotech />} 
              iconPosition="start"
            />
          </Tabs>
          
          <FormControlLabel
            control={
              <Switch
                checked={useEnhancedView}
                onChange={(e) => setUseEnhancedView(e.target.checked)}
                color="primary"
              />
            }
            label="Enhanced View"
          />
        </Box>

        <TabPanel value={tabValue} index={0}>
          <BlastSearchForm
            databases={databases || null}
            onSearch={handleSearch}
            loading={loading}
          />
          {results && (
            <>
              {useEnhancedView ? (
                <SimpleEnhancedBlastResults 
                  results={results} 
                  searchType="blast"
                />
              ) : (
                <BlastResults 
                  results={results} 
                  searchType="blast"
                />
              )}
            </>
          )}
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <AntibodyAnalysis
            organisms={organisms}
            onSearch={handleSearch}
            loading={loading}
          />
          {results && (
            <>
              {useEnhancedView ? (
                <SimpleEnhancedBlastResults 
                  results={results} 
                  searchType="antibody"
                />
              ) : (
                <BlastResults 
                  results={results} 
                  searchType="antibody"
                />
              )}
            </>
          )}
        </TabPanel>
      </Paper>
    </Container>
  );
};
