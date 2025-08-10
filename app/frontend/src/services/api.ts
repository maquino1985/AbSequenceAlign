// API Service for backend communication

import axios from 'axios';
import type { 
  AnnotationRequest, 
  APIResponse, 
  AnnotationResult,
  MSACreationRequest,
  MSAAnnotationRequest
} from '../types/api';

// Configure axios defaults
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

const apiClientV2 = axios.create({
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

  // Annotate sequences
  annotateSequences: async (
    request: AnnotationRequest
  ): Promise<APIResponse<{ annotation_result: AnnotationResult }>> => {
    const response = await apiClient.post('/annotate', request);
    return response.data;
  },

  // V2 Annotate sequences (structured)
  annotateSequencesV2: async (
    request: import('../types/apiV2').AnnotationRequestV2
  ): Promise<import('../types/apiV2').AnnotationResultV2> => {
    const response = await apiClientV2.post('/annotate', request);
    return response.data;
  },

  // Upload sequences (for future use)
  uploadSequences: async (
    file: File
  ): Promise<APIResponse<{ dataset_id: string }>> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get datasets (for future use)
  getDatasets: async (): Promise<APIResponse<{ datasets: Record<string, unknown>[] }>> => {
    const response = await apiClient.get('/datasets');
    return response.data;
  },

  // MSA Methods
  uploadMSASequences: async (
    data: FormData
  ): Promise<APIResponse<{ sequences: any[]; validation_errors: string[] }>> => {
    const response = await apiClient.post('/msa-viewer/upload', data, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  createMSA: async (
    request: MSACreationRequest
  ): Promise<APIResponse<{ job_id?: string; msa_result?: any; annotation_result?: any; use_background: boolean }>> => {
    const response = await apiClient.post('/msa-viewer/create-msa', request);
    return response.data;
  },

  annotateMSA: async (
    request: MSAAnnotationRequest
  ): Promise<APIResponse<{ job_id: string; status: string }>> => {
    const response = await apiClient.post('/msa-viewer/annotate-msa', request);
    return response.data;
  },

  getJobStatus: async (
    jobId: string
  ): Promise<APIResponse<any>> => {
    const response = await apiClient.get(`/msa-viewer/job/${jobId}`);
    return response.data;
  },

  listJobs: async (): Promise<APIResponse<{ jobs: any[] }>> => {
    const response = await apiClient.get('/msa-viewer/jobs');
    return response.data;
  },
};

export default api;
