export type DomainTypeV2 = 'V' | 'C' | 'LINKER';

export interface RegionFeatureV2 {
  kind: string;
  value: any;
}

export interface RegionV2 {
  name: string;
  start: number;
  stop: number;
  features: RegionFeatureV2[];
}

export interface DomainV2 {
  domain_type: DomainTypeV2;
  start?: number;
  stop?: number;
  sequence?: string;
  regions: RegionV2[];
  isotype?: string;
  species?: string;
  metadata?: Record<string, any>;
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


