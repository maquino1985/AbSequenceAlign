// MSA (Multiple Sequence Alignment) related types

// Define region type for MSA
export interface MSARegion {
  id: string;
  name: string;
  start: number;
  stop: number;
  sequence: string;
  color: string;
  type: 'CDR' | 'FR' | 'LIABILITY' | 'MUTATION';
  features: Array<{
    id: string;
    type: string;
    start: number;
    stop: number;
    description: string;
    color: string;
  }>;
  details?: {
    isotype?: string;
    domain_type?: string;
    preceding_linker?: {
      sequence: string;
      start: number;
      end: number;
    };
  };
}

// Define PSSM data type to match PSSMVisualization component
export interface PSSMData {
  position_frequencies: Array<Record<string, number>>;
  position_scores: Array<Record<string, number>>;
  conservation_scores: number[];
  quality_scores: number[];
  consensus: string;
  amino_acids: string[];
  alignment_length: number;
  num_sequences: number;
}

export interface MSAState {
  sequences: string[];
  alignmentMatrix: string[][];
  sequenceNames: string[];
  regions: MSARegion[];
  isLoading: boolean;
  error: string | null;
  msaId: string | null;
  jobId: string | null;
  jobStatus: 
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    any | null;
  msaResult: 
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    any | null;
  annotationResult: 
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    any | null;
  consensus: string;
  pssmData: PSSMData | null;
  selectedRegions: string[];
}
