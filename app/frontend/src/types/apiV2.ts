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

// BLAST Types
export interface BlastHit {
  query_id: string;
  subject_id: string;
  identity: number;
  alignment_length: number;
  mismatches: number;
  gap_opens: number;
  query_start: number;
  query_end: number;
  subject_start: number;
  subject_end: number;
  evalue: number;
  bit_score: number;
  // Sequence alignment fields
  query_alignment?: string;
  subject_alignment?: string;
  blast_type?: string;
  // Source URL for the subject
  subject_url?: string;
}

export interface BlastQueryInfo {
  query_id: string;
  database?: string;
}

export interface BlastResult {
  blast_type: string;
  query_info: BlastQueryInfo;
  hits: BlastHit[];
  total_hits: number;
}

export interface BlastSearchResponse {
  success: boolean;
  message: string;
  data: {
    results: BlastResult;
    query_info?: {
      query_id: string;
      query_length?: number;
    };
    total_hits: number;
  };
}

// IgBLAST specific types
export interface IgBlastHit extends BlastHit {
  v_gene?: string;
  d_gene?: string;
  j_gene?: string;
  c_gene?: string;
  cdr3_start?: number;
  cdr3_end?: number;
  cdr3_sequence?: string;
  // Enhanced fields from advanced AIRR parsing
  productive?: string;
  locus?: string;
  complete_vdj?: boolean;
  stop_codon?: boolean;
  vj_in_frame?: boolean;
  fwr1_sequence?: string;
  cdr1_sequence?: string;
  fwr2_sequence?: string;
  cdr2_sequence?: string;
  fwr3_sequence?: string;
  junction_aa?: string;
  junction_length?: number;
}

export interface IgBlastResult extends BlastResult {
  hits: IgBlastHit[];
}

export interface IgBlastSearchResponse {
  success: boolean;
  message: string;
  data: {
    results: IgBlastResult;
    query_info?: {
      query_id: string;
      query_length?: number;
    };
    analysis_summary?: {
      best_v_gene?: string;
      best_d_gene?: string;
      best_j_gene?: string;
      best_c_gene?: string;
      cdr3_sequence?: string;
      cdr3_start?: number;
      cdr3_end?: number;
      junction_length?: number;
      productive_sequences?: number;
      unique_v_genes?: string[];
      unique_d_genes?: string[];
      unique_j_genes?: string[];
      locus?: string;
      fwr1_sequence?: string;
      cdr1_sequence?: string;
      fwr2_sequence?: string;
      cdr2_sequence?: string;
      fwr3_sequence?: string;
      junction_aa?: string;
      total_hits: number;
    };
    total_hits: number;
    // Enhanced AIRR result for advanced analysis
    airr_result?: AIRRAnalysisResult;
    // Legacy fields for backward compatibility
    summary?: {
      total_hits: number;
      best_identity: number;
      gene_assignments: {
        v_gene?: string;
        d_gene?: string;
        j_gene?: string;
        c_gene?: string;
      } | null;
      cdr3_info: {
        sequence: string;
        start: number;
        end: number;
      } | null;
    };
    cdr3_info?: {
      sequence: string;
      start: number;
      end: number;
    } | null;
    gene_assignments?: {
      v_gene?: string;
      d_gene?: string;
      j_gene?: string;
      c_gene?: string;
    } | null;
  };
}

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

// Enhanced BLAST and IgBLAST Types - extending existing interfaces

// AIRR Rearrangement Types (comprehensive)
export interface AIRRAlignment {
  start?: number;
  end?: number;
  sequence_alignment?: string;
  sequence_alignment_aa?: string;
  germline_alignment?: string;
  germline_alignment_aa?: string;
  score?: number;
  identity?: number;
  cigar?: string;
  support?: number;
}

export interface CDRRegion {
  sequence?: string;
  sequence_aa?: string;
  start?: number;
  end?: number;
}

export interface FrameworkRegion {
  sequence?: string;
  sequence_aa?: string;
  start?: number;
  end?: number;
}

export interface JunctionRegion {
  junction?: string;
  junction_aa?: string;
  junction_length?: number;
  junction_aa_length?: number;
  cdr3?: string;
  cdr3_aa?: string;
  cdr3_start?: number;
  cdr3_end?: number;
  np1?: string;
  np1_length?: number;
  np2?: string;
  np2_length?: number;
}

export interface AIRRRearrangement {
  sequence_id: string;
  sequence: string;
  sequence_aa?: string;
  locus?: string;
  productive?: string;
  stop_codon?: boolean;
  vj_in_frame?: boolean;
  v_frameshift?: string;
  rev_comp?: boolean;
  complete_vdj?: boolean;
  d_frame?: number;
  
  // Gene assignments
  v_call?: string;
  d_call?: string;
  j_call?: string;
  c_call?: string;
  
  // Sequence coordinates
  v_sequence_start?: number;
  v_sequence_end?: number;
  v_germline_start?: number;
  v_germline_end?: number;
  d_sequence_start?: number;
  d_sequence_end?: number;
  d_germline_start?: number;
  d_germline_end?: number;
  j_sequence_start?: number;
  j_sequence_end?: number;
  j_germline_start?: number;
  j_germline_end?: number;
  
  // Alignment details
  v_alignment?: AIRRAlignment;
  d_alignment?: AIRRAlignment;
  j_alignment?: AIRRAlignment;
  
  // Framework and CDR regions
  fwr1?: FrameworkRegion;
  cdr1?: CDRRegion;
  fwr2?: FrameworkRegion;
  cdr2?: CDRRegion;
  fwr3?: FrameworkRegion;
  fwr4?: FrameworkRegion;
  
  // Junction/CDR3 region
  junction_region?: JunctionRegion;
  
  // Full sequence alignments
  sequence_alignment?: string;
  germline_alignment?: string;
  sequence_alignment_aa?: string;
  germline_alignment_aa?: string;
}

export interface AIRRAnalysisResult {
  rearrangements: AIRRRearrangement[];
  total_sequences: number;
  productive_sequences: number;
  unique_v_genes: string[];
  unique_d_genes: string[];
  unique_j_genes: string[];
  analysis_metadata: Record<string, 
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    any>;
}




