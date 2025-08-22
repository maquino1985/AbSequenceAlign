/**
 * React hook for database discovery and management
 */

import { useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';
import type {
  DatabaseDiscoveryResponse,
  DatabaseOption
} from '../types/database';

interface UseDatabaseDiscoveryReturn {
  databases: DatabaseDiscoveryResponse['databases'] | null;
  organisms: string[];
  geneTypes: string[];
  loading: boolean;
  error: string | null;
  refreshDatabases: () => Promise<void>;
  validateDatabase: (dbPath: string) => Promise<boolean>;
  getSuggestion: (organism: string, geneType: string) => Promise<DatabaseOption | null>;
  getDatabaseOptions: (organism: string, geneType: string) => DatabaseOption[];
}

export const useDatabaseDiscovery = (): UseDatabaseDiscoveryReturn => {
  const [databases, setDatabases] = useState<DatabaseDiscoveryResponse['databases'] | null>(null);
  const [organisms, setOrganisms] = useState<string[]>([]);
  const [geneTypes, setGeneTypes] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDatabases = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await api.getIgBlastDatabases();
      
      if (response.success) {
        setDatabases(response.databases);
        setOrganisms(response.organisms);
        setGeneTypes(response.gene_types);
      } else {
        setError('Failed to fetch databases');
      }
    } catch (err) {
      console.error('Error fetching databases:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch databases');
    } finally {
      setLoading(false);
    }
  }, []);

  const validateDatabase = useCallback(async (dbPath: string): Promise<boolean> => {
    try {
      const response = await api.validateDatabasePath(dbPath);
      return response.success && response.is_valid;
    } catch (err) {
      console.error('Error validating database:', err);
      return false;
    }
  }, []);

  const getSuggestion = useCallback(async (organism: string, geneType: string): Promise<DatabaseOption | null> => {
    try {
      const response = await api.getDatabaseSuggestion(organism, geneType);
      return response.success ? response.suggestion : null;
    } catch (err) {
      console.error('Error getting database suggestion:', err);
      return null;
    }
  }, []);

  const getDatabaseOptions = useCallback((organism: string, geneType: string): DatabaseOption[] => {
    if (!databases || !databases[organism] || !databases[organism][geneType]) {
      return [];
    }
    
    return [databases[organism][geneType]];
  }, [databases]);

  // Load databases on mount
  useEffect(() => {
    fetchDatabases();
  }, [fetchDatabases]);

  return {
    databases,
    organisms,
    geneTypes,
    loading,
    error,
    refreshDatabases: fetchDatabases,
    validateDatabase,
    getSuggestion,
    getDatabaseOptions
  };
};
