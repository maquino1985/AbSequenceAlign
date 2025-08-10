export type DomainTypeV2 = 'V' | 'C' | 'LINKER';

// Define specific feature value types based on kind
export type RegionFeatureValue = 
  | { kind: 'sequence'; value: string }
  | { kind: 'isotype'; value: string }
  | { kind: 'species'; value: string }
  | { kind: 'germline'; value: string }
  | { kind: 'confidence'; value: number }
  | { kind: 'score'; value: number }
  | { kind: 'color'; value: string }
  | { kind: 'domain_type'; value: string }
  | { kind: 'start'; value: number }
  | { kind: 'stop'; value: number };

export interface RegionFeatureV2 {
  kind: string;
  value: string | number | boolean | null | undefined;
}

export interface RegionV2 {
  name: string;
  start: number;
  stop: number;
  features: RegionFeatureV2[];
}

// Define domain metadata structure
export interface DomainMetadataV2 {
  confidence?: number;
  score?: number;
  alignment_details?: {
    query_start?: number;
    query_end?: number;
    start?: number;
    end?: number;
    identity?: number;
    coverage?: number;
  };
  germlines?: string | string[];
  warnings?: string[];
  notes?: string;
}

export interface DomainV2 {
  domain_type: DomainTypeV2;
  start?: number;
  stop?: number;
  sequence?: string;
  regions: RegionV2[];
  isotype?: string;
  species?: string;
  metadata?: DomainMetadataV2;
}

export interface ChainV2 {
  name: string;
  sequence: string;
  domains: DomainV2[];
}

export interface SequenceV2 {
  name: string;
  original_sequence: string;
  chains: ChainV2[];
}

export interface AnnotationResultV2 {
  sequences: SequenceV2[];
  numbering_scheme: string;
  total_sequences: number;
  chain_types: Record<string, number>;
  isotypes: Record<string, number>;
  species: Record<string, number>;
}

export interface AnnotationRequestV2 {
  sequences: Array<{
    name: string;
    heavy_chain?: string;
    light_chain?: string;
    scfv?: string;
    custom_chains?: Record<string, string>;
  }>;
  numbering_scheme?: string;
}

// MSA Types for v2
export const AlignmentMethodV2 = {
  PAIRWISE_GLOBAL: 'pairwise_global',
  PAIRWISE_LOCAL: 'pairwise_local',
  MUSCLE: 'muscle',
  MAFFT: 'mafft',
  CLUSTALO: 'clustalo',
  CUSTOM_ANTIBODY: 'custom_antibody'
} as const;

export type AlignmentMethodV2 = typeof AlignmentMethodV2[keyof typeof AlignmentMethodV2];

export interface MSASequenceV2 {
  name: string;
  original_sequence: string;
  aligned_sequence: string;
  start_position: number;
  end_position: number;
  gaps: number[];
  annotations?: Array<{
    name: string;
    start: number;
    stop: number;
    sequence: string;
    color: string;
  }>;
}

// Define MSA metadata structure
export interface MSAMetadataV2 {
  total_sequences?: number;
  alignment_length?: number;
  consensus_quality?: number;
  gap_percentage?: number;
  identity_matrix?: number[][];
  method_parameters?: {
    gap_open?: number;
    gap_extend?: number;
    matrix?: string;
  };
  processing_time?: number;
  warnings?: string[];
  pssm_data?: {
    position_frequencies: Array<Record<string, number>>;
    position_scores: Array<Record<string, number>>;
    conservation_scores: number[];
    quality_scores: number[];
    consensus: string;
    amino_acids: string[];
    alignment_length: number;
    num_sequences: number;
  };
}

export interface MSAResultV2 {
  msa_id: string;
  sequences: MSASequenceV2[];
  alignment_matrix: string[][];
  consensus: string;
  alignment_method: AlignmentMethodV2;
  created_at: string;
  metadata: MSAMetadataV2;
}

export interface MSAAnnotationResultV2 {
  msa_id: string;
  annotated_sequences: MSASequenceV2[];
  numbering_scheme: string;
  region_mappings: Record<string, Array<{
    sequence_name: string;
    start: number;
    stop: number;
    sequence: string;
    color: string;
  }>>;
}

export interface MSACreationRequestV2 {
  sequences: Array<{
    name: string;
    heavy_chain?: string;
    light_chain?: string;
    scfv?: string;
    custom_chains?: Record<string, string>;
  }>;
  alignment_method?: AlignmentMethodV2;
  numbering_scheme?: string;
}

export interface MSAAnnotationRequestV2 {
  msa_id: string;
  numbering_scheme?: string;
}

// Define job result types
export type JobResultV2 = 
  | { type: 'msa'; data: MSAResultV2 }
  | { type: 'annotation'; data: MSAAnnotationResultV2 }
  | { type: 'error'; error: string };

export interface MSAJobStatusV2 {
  job_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  message: string;
  result?: JobResultV2;
  created_at: string;
  completed_at?: string;
}


