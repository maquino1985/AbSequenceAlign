// API Service for backend communication

import axios from 'axios';
import type { 
  APIResponse
} from '../types/api';
import type {
  MSACreationRequestV2,
  MSAAnnotationRequestV2,
  MSAResultV2,
  MSAAnnotationResultV2,
  MSAJobStatusV2
} from '../types/apiV2';
import type {
  DatabaseDiscoveryResponse,
  DatabaseValidationResponse,
  DatabaseSuggestionResponse,
  IgBlastRequest,
  IgBlastResponse
} from '../types/database';

// Configure axios defaults
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v2`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});



// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

// API Methods
export const api = {
  // Health check
  health: async (): Promise<{ status: string }> => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // Database Discovery Methods
  getIgBlastDatabases: async (): Promise<DatabaseDiscoveryResponse> => {
    const response = await apiClient.get('/database/databases/igblast');
    return response.data;
  },

  getBlastDatabases: async (): Promise<APIResponse<
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    any>> => {
    const response = await apiClient.get('/blast/databases');
    return response.data;
  },

  validateDatabasePath: async (dbPath: string): Promise<DatabaseValidationResponse> => {
    const response = await apiClient.get('/database/databases/validate', {
      params: { path: dbPath }
    });
    return response.data;
  },

  getDatabaseSuggestion: async (organism: string, geneType: string): Promise<DatabaseSuggestionResponse> => {
    const response = await apiClient.get('/database/databases/suggestions', {
      params: { organism, gene_type: geneType }
    });
    return response.data;
  },

  // IgBLAST Execution
  executeIgBlast: async (request: IgBlastRequest): Promise<IgBlastResponse> => {
    const response = await apiClient.post('/database/igblast/execute', request);
    return response.data;
  },

  // V2 Annotate sequences (structured)
  annotateSequencesV2: async (
    request: import('../types/apiV2').AnnotationRequestV2
  ): Promise<import('../types/apiV2').AnnotationResultV2> => {
    const response = await apiClient.post('/annotate', request);
    return response.data;
  },

  // MSA Methods (using v2 API)
  uploadMSASequences: async (
    data: FormData
  ): Promise<APIResponse<{ sequences: Array<{ name: string; sequence: string }>; validation_errors: string[] }>> => {
    const response = await apiClient.post('/msa-viewer/upload', data, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  createMSA: async (
    request: MSACreationRequestV2
  ): Promise<APIResponse<{ job_id?: string; msa_result?: MSAResultV2; annotation_result?: MSAAnnotationResultV2; use_background: boolean }>> => {
    const response = await apiClient.post('/msa-viewer/create-msa', request);
    return response.data;
  },

  annotateMSA: async (
    request: MSAAnnotationRequestV2
  ): Promise<APIResponse<{ job_id: string; status: string }>> => {
    const response = await apiClient.post('/msa-viewer/annotate-msa', request);
    return response.data;
  },

  getJobStatus: async (
    jobId: string
  ): Promise<APIResponse<MSAJobStatusV2>> => {
    const response = await apiClient.get(`/msa-viewer/job/${jobId}`);
    return response.data;
  },

  listJobs: async (): Promise<APIResponse<{ jobs: MSAJobStatusV2[] }>> => {
    const response = await apiClient.get('/msa-viewer/jobs');
    return response.data;
  },

  // BLAST Methods
  searchPublicDatabases: async (request: Record<string, unknown>): Promise<APIResponse<Record<string, unknown>>> => {
    const response = await apiClient.post('/blast/search/public', request);
    return response.data;
  },

  searchInternalDatabase: async (request: Record<string, unknown>): Promise<APIResponse<Record<string, unknown>>> => {
    const response = await apiClient.post('/blast/search/internal', request);
    return response.data;
  },

  analyzeAntibodySequence: async (request: Record<string, unknown>): Promise<APIResponse<Record<string, unknown>>> => {
    const response = await apiClient.post('/blast/search/antibody', request);
    return response.data;
  },

  getSupportedOrganisms: async (): Promise<APIResponse<{ organisms: string[] }>> => {
    const response = await apiClient.get('/blast/organisms');
    return response.data;
  },

  uploadSequencesForBlast: async (data: FormData): Promise<APIResponse<Record<string, unknown>>> => {
    const response = await apiClient.post('/blast/upload', data, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

export default api;
