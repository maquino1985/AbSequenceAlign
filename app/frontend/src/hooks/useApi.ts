// Custom hook for API operations

import { useState, useCallback } from 'react';
import { api } from '../services/api';
import type { AnnotationRequestV2, AnnotationResultV2 } from '../types/apiV2';

interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export const useApi = () => {
  const [annotationState, setAnnotationState] = useState<ApiState<AnnotationResultV2>>({
    data: null,
    loading: false,
    error: null
  });

  const annotateSequences = useCallback(async (request: AnnotationRequestV2) => {
    setAnnotationState({ data: null, loading: true, error: null });
    
    try {
      const response = await api.annotateSequencesV2(request);
      
      setAnnotationState({
        data: response,
        loading: false,
        error: null
      });
      return response;
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
