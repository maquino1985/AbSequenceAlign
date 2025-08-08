// API Types - matching the backend Pydantic models

export interface SequenceInput {
  name: string;
  heavy_chain?: string;
  light_chain?: string;
  scfv?: string;
  heavy_chain_1?: string;
  heavy_chain_2?: string;
  heavy_chain_3?: string;
  heavy_chain_4?: string;
  light_chain_1?: string;
  light_chain_2?: string;
  light_chain_3?: string;
  light_chain_4?: string;
  custom_chains?: Record<string, string>;
}

export interface AnnotationRequest {
  sequences: SequenceInput[];
  numbering_scheme?: NumberingScheme;
  chain_type?: ChainType;
}

export interface SequenceInfo {
  sequence: string;
  name?: string;
  chain_type?: string;
  isotype?: string;
  species?: string;
  germline?: string;
  regions?: Record<string, RegionData>;
}

export interface RegionData {
  name: string;
  start: number | string;
  stop: number | string;
  sequence: string;
}

export interface AnnotationResult {
  sequences: SequenceInfo[];
  numbering_scheme: NumberingScheme;
  total_sequences: number;
  chain_types: Record<string, number>;
  isotypes: Record<string, number>;
  species: Record<string, number>;
}

export interface APIResponse<T = Record<string, unknown>> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
}

export const NumberingScheme = {
  IMGT: 'imgt',
  KABAT: 'kabat',
  CHOTHIA: 'chothia',
  MARTIN: 'martin',
  AHO: 'aho',
  CGG: 'cgg'
} as const;

export type NumberingScheme = typeof NumberingScheme[keyof typeof NumberingScheme];

export const ChainType = {
  HEAVY: 'H',
  LIGHT: 'L',
  KAPPA: 'K',
  LAMBDA: 'L'
} as const;

export type ChainType = typeof ChainType[keyof typeof ChainType];

export const AlignmentMethod = {
  PAIRWISE_GLOBAL: 'pairwise_global',
  PAIRWISE_LOCAL: 'pairwise_local',
  MUSCLE: 'muscle',
  MAFFT: 'mafft',
  CLUSTALO: 'clustalo',
  CUSTOM_ANTIBODY: 'custom_antibody'
} as const;

export type AlignmentMethod = typeof AlignmentMethod[keyof typeof AlignmentMethod];
