// Custom hook for API operations

import { useState, useCallback } from 'react';
import { api } from '../services/api';
import type { AnnotationRequest, AnnotationResult } from '../types/api';
import type { AnnotationRequestV2, AnnotationResultV2 } from '../types/apiV2';

interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export const useApi = () => {
  const [annotationState, setAnnotationState] = useState<ApiState<AnnotationResult>>({
    data: null,
    loading: false,
    error: null
  });

  const annotateSequences = useCallback(async (request: AnnotationRequest) => {
    setAnnotationState({ data: null, loading: true, error: null });
    
    try {
      const response = await api.annotateSequencesV2(request as AnnotationRequestV2);
      
      // Convert v2 response to v1 format for compatibility
      const v1Result: AnnotationResult = {
        sequences: response.sequences.map(seq => ({
          sequence: seq.original_sequence,
          name: seq.name,
          regions: seq.chains.reduce((acc, chain) => {
            chain.domains.forEach(domain => {
              domain.regions.forEach(region => {
                acc[region.name] = {
                  name: region.name,
                  start: region.start,
                  stop: region.stop,
                  sequence: domain.sequence || '',
                  domain_type: domain.domain_type,
                  isotype: domain.isotype
                };
              });
            });
            return acc;
          }, {} as Record<string, any>)
        })),
        numbering_scheme: response.numbering_scheme as any,
        total_sequences: response.total_sequences,
        chain_types: {},
        isotypes: {},
        species: {}
      };
      
      setAnnotationState({
        data: v1Result,
        loading: false,
        error: null
      });
      return v1Result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setAnnotationState({
        data: null,
        loading: false,
        error: errorMessage
      });
      throw error;
    }
  }, []);

  const checkHealth = useCallback(async () => {
    try {
      const response = await api.health();
      return response.status === 'healthy';
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }, []);

  return {
    annotation: annotationState,
    annotateSequences,
    checkHealth
  };
};
