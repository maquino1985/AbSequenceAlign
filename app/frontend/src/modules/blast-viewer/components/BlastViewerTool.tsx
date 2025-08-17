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
} from '@mui/material';
import { Search, Biotech } from '@mui/icons-material';
import api from '../../../services/api';
import BlastSearchForm from './BlastSearchForm';
import BlastResults from './BlastResults';
import AntibodyAnalysis from './AntibodyAnalysis';

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
  const [results, setResults] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Load databases and organisms in parallel
      const [dbResponse, orgResponse] = await Promise.all([
        api.getBlastDatabases(),
        api.getSupportedOrganisms()
      ]);
      
      setDatabases(dbResponse.data.databases);
      setOrganisms(orgResponse.data.organisms);
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
      let response;
      
      if (searchData.searchType === 'antibody') {
        response = await api.analyzeAntibodySequence(searchData);
      } else if (searchData.searchType === 'internal') {
        response = await api.searchInternalDatabase(searchData);
      } else {
        response = await api.searchPublicDatabases(searchData);
      }
      
      setResults(response.data);
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
        Search sequences against public databases, internal databases, or perform antibody-specific analysis using IgBLAST.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ width: '100%' }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          aria-label="BLAST search tabs"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
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

        <TabPanel value={tabValue} index={0}>
          <BlastSearchForm
            databases={databases}
            onSearch={handleSearch}
            loading={loading}
          />
          {results && (
            <BlastResults 
              results={results} 
              searchType="standard"
            />
          )}
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <AntibodyAnalysis
            organisms={organisms}
            onSearch={handleSearch}
            loading={loading}
          />
          {results && (
            <BlastResults 
              results={results} 
              searchType="antibody"
            />
          )}
        </TabPanel>
      </Paper>
    </Container>
  );
};
