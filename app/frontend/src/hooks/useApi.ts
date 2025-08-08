// Custom hook for API operations

import { useState, useCallback } from 'react';
import { api } from '../services/api';
import type { AnnotationRequest, AnnotationResult } from '../types/api';

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
      const response = await api.annotateSequences(request);
      
      if (response.success && response.data) {
        setAnnotationState({
          data: response.data.annotation_result,
          loading: false,
          error: null
        });
        return response.data.annotation_result;
      } else {
        throw new Error(response.error || 'Annotation failed');
      }
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
