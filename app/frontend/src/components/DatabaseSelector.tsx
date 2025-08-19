/**
 * Database Selector Component
 * 
 * Allows users to select IgBLAST databases for V, D, J, and C genes
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  Chip,
  Alert,
  CircularProgress,
  Button
} from '@mui/material';
import { Refresh as RefreshIcon } from '@mui/icons-material';
import { useDatabaseDiscovery } from '../hooks/useDatabaseDiscovery';
import type { DatabaseOption, DatabaseSelection } from '../types/database';

interface DatabaseSelectorProps {
  value: DatabaseSelection;
  onChange: (selection: DatabaseSelection) => void;
  disabled?: boolean;
  showDescriptions?: boolean;
  blastType?: 'igblastn' | 'igblastp';
}

export const DatabaseSelector: React.FC<DatabaseSelectorProps> = React.memo(({
  value,
  onChange,
  disabled = false,
  showDescriptions = true,
  blastType = 'igblastn'
}) => {
  const {
    databases,
    organisms,
    geneTypes,
    loading,
    error,
    refreshDatabases,
    getSuggestion
  } = useDatabaseDiscovery();

  const [selectedOrganism, setSelectedOrganism] = useState<string>('human');

  // Auto-select databases when organism changes
  useEffect(() => {
    if (databases && selectedOrganism && databases[selectedOrganism]) {
      const organismDbs = databases[selectedOrganism];
      const newSelection: DatabaseSelection = {
        v_db: organismDbs.V?.path || '',
        d_db: organismDbs.D?.path || '',
        j_db: organismDbs.J?.path || '',
        c_db: organismDbs.C?.path || ''
      };
      onChange(newSelection);
    }
  }, [selectedOrganism, databases]); // Removed onChange from dependencies

  const handleOrganismChange = useCallback((organism: string) => {
    setSelectedOrganism(organism);
  }, []);

  const handleDatabaseChange = useCallback((geneType: keyof DatabaseSelection, dbPath: string) => {
    onChange({
      ...value,
      [geneType]: dbPath
    });
  }, [value, onChange]);

  const handleAutoSelect = useCallback(async () => {
    if (!selectedOrganism) return;

    const newSelection: DatabaseSelection = { v_db: '' };
    
    // Auto-select V database (required)
    const vSuggestion = await getSuggestion(selectedOrganism, 'V');
    if (vSuggestion) {
      newSelection.v_db = vSuggestion.path;
    }

    // Auto-select D database (optional, only for heavy chains)
    const dSuggestion = await getSuggestion(selectedOrganism, 'D');
    if (dSuggestion) {
      newSelection.d_db = dSuggestion.path;
    }

    // Auto-select J database (required)
    const jSuggestion = await getSuggestion(selectedOrganism, 'J');
    if (jSuggestion) {
      newSelection.j_db = jSuggestion.path;
    }

    // Auto-select C database (optional)
    const cSuggestion = await getSuggestion(selectedOrganism, 'C');
    if (cSuggestion) {
      newSelection.c_db = cSuggestion.path;
    }

    onChange(newSelection);
  }, [selectedOrganism, getSuggestion, onChange]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" p={2}>
        <CircularProgress size={24} />
        <Typography variant="body2" ml={1}>
          Loading databases...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" action={
        <Button color="inherit" size="small" onClick={refreshDatabases}>
          Retry
        </Button>
      }>
        Failed to load databases: {error}
      </Alert>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6" component="h3">
          Database Selection
        </Typography>
        <Button
          startIcon={<RefreshIcon />}
          onClick={refreshDatabases}
          size="small"
          disabled={disabled}
        >
          Refresh
        </Button>
      </Box>

      {/* Organism Selection */}
      <FormControl fullWidth margin="normal" disabled={disabled}>
        <InputLabel>Organism</InputLabel>
        <Select
          value={selectedOrganism}
          onChange={(e) => handleOrganismChange(e.target.value)}
          label="Organism"
        >
          {organisms.map((organism) => (
            <MenuItem key={organism} value={organism}>
              {organism.charAt(0).toUpperCase() + organism.slice(1)}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {/* Database Selection */}
      <Box mt={2}>
        <Typography variant="subtitle2" gutterBottom>
          Gene Databases
        </Typography>

        {/* V Gene Database (Required) */}
        <FormControl fullWidth margin="normal" disabled={disabled} required>
          <InputLabel>V Gene Database *</InputLabel>
          <Select
            value={value.v_db}
            onChange={(e) => handleDatabaseChange('v_db', e.target.value)}
            label="V Gene Database *"
            error={!value.v_db}
          >
            {databases?.[selectedOrganism]?.V && (
              <MenuItem value={databases[selectedOrganism].V.path}>
                <Box>
                  <Typography variant="body2">
                    {databases[selectedOrganism].V.name}
                  </Typography>
                  {showDescriptions && (
                    <Typography variant="caption" color="text.secondary">
                      {databases[selectedOrganism].V.description}
                    </Typography>
                  )}
                </Box>
              </MenuItem>
            )}
          </Select>
        </FormControl>

        {/* D Gene Database (Optional) */}
        <FormControl fullWidth margin="normal" disabled={disabled || blastType === 'igblastp'}>
          <InputLabel>D Gene Database (Optional)</InputLabel>
          <Select
            value={value.d_db || ''}
            onChange={(e) => handleDatabaseChange('d_db', e.target.value || '')}
            label="D Gene Database (Optional)"
          >
            <MenuItem value="">
              <em>None (Light chains only)</em>
            </MenuItem>
            {databases?.[selectedOrganism]?.D && (
              <MenuItem value={databases[selectedOrganism].D.path}>
                <Box>
                  <Typography variant="body2">
                    {databases[selectedOrganism].D.name}
                  </Typography>
                  {showDescriptions && (
                    <Typography variant="caption" color="text.secondary">
                      {databases[selectedOrganism].D.description}
                    </Typography>
                  )}
                </Box>
              </MenuItem>
            )}
          </Select>
        </FormControl>

        {/* J Gene Database (Required) */}
        <FormControl fullWidth margin="normal" disabled={disabled || blastType === 'igblastp'} required={blastType === 'igblastn'}>
          <InputLabel>J Gene Database {blastType === 'igblastn' ? '*' : '(Not used for protein)'}</InputLabel>
          <Select
            value={value.j_db}
            onChange={(e) => handleDatabaseChange('j_db', e.target.value)}
            label={`J Gene Database ${blastType === 'igblastn' ? '*' : '(Not used for protein)'}`}
            error={blastType === 'igblastn' && !value.j_db}
          >
            {databases?.[selectedOrganism]?.J && (
              <MenuItem value={databases[selectedOrganism].J.path}>
                <Box>
                  <Typography variant="body2">
                    {databases[selectedOrganism].J.name}
                  </Typography>
                  {showDescriptions && (
                    <Typography variant="caption" color="text.secondary">
                      {databases[selectedOrganism].J.description}
                    </Typography>
                  )}
                </Box>
              </MenuItem>
            )}
          </Select>
        </FormControl>

        {/* C Gene Database (Optional) */}
        <FormControl fullWidth margin="normal" disabled={disabled || blastType === 'igblastp'}>
          <InputLabel>C Gene Database (Optional)</InputLabel>
          <Select
            value={value.c_db || ''}
            onChange={(e) => handleDatabaseChange('c_db', e.target.value || '')}
            label="C Gene Database (Optional)"
          >
            <MenuItem value="">
              <em>None</em>
            </MenuItem>
            {databases?.[selectedOrganism]?.C && (
              <MenuItem value={databases[selectedOrganism].C.path}>
                <Box>
                  <Typography variant="body2">
                    {databases[selectedOrganism].C.name}
                  </Typography>
                  {showDescriptions && (
                    <Typography variant="caption" color="text.secondary">
                      {databases[selectedOrganism].C.description}
                    </Typography>
                  )}
                </Box>
              </MenuItem>
            )}
          </Select>
        </FormControl>
      </Box>

      {/* Auto-select Button */}
      <Box mt={2}>
        <Button
          variant="outlined"
          onClick={handleAutoSelect}
          disabled={disabled || !selectedOrganism}
          fullWidth
        >
          Auto-select Best Databases
        </Button>
      </Box>

      {/* Selection Summary */}
      {value.v_db && (
        <Box mt={2}>
          <Typography variant="subtitle2" gutterBottom>
            Selected Databases:
          </Typography>
          <Box display="flex" flexWrap="wrap" gap={1}>
            {value.v_db && (
              <Chip label="V" color="primary" size="small" />
            )}
            {value.d_db && (
              <Chip label="D" color="secondary" size="small" />
            )}
            {value.j_db && (
              <Chip label="J" color="primary" size="small" />
            )}
            {value.c_db && (
              <Chip label="C" color="secondary" size="small" />
            )}
          </Box>
        </Box>
      )}
    </Box>
  );
});
