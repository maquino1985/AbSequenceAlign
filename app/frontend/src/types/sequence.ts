// Sequence and Visualization Types

export interface SequenceData {
  id: string;
  name: string;
  chains: ChainData[];
  species?: string;
}

export interface ChainData {
  id: string;
  type: string;
  sequence: string;
  annotations: Region[];
}

export interface Region {
  id: string;
  name: string;
  start: number;
  stop: number;
  sequence: string;
  type: 'CDR' | 'FR' | 'LIABILITY' | 'MUTATION' | 'LINKER' | 'CONSTANT';
  color: string;
  features: Feature[];
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

export interface Feature {
  id: string;
  type: FeatureType;
  start: number;
  stop: number;
  description: string;
  color: string;
  confidence?: number;
  source?: string;
}

export const FeatureType = {
  CDR: 'CDR',
  FR: 'FR',
  LIABILITY: 'LIABILITY',
  MUTATION: 'MUTATION',
  GLYCOSYLATION: 'GLYCOSYLATION',
  DISULFIDE: 'DISULFIDE',
  PTM: 'PTM',
  LINKER: 'LINKER',
  CONSTANT: 'CONSTANT'
} as const;

export type FeatureType = typeof FeatureType[keyof typeof FeatureType];

export interface AminoAcidData {
  position: number;
  aminoAcid: string;
  color: string;
  region?: Region;
  features: Feature[];
}

export interface ColorScheme {
  name: string;
  type: ColorSchemeType;
  colors: Record<string, string>;
  description: string;
}

export const ColorSchemeType = {
  HYDROPHOBICITY: 'hydrophobicity',
  CHARGE: 'charge',
  AMINO_ACID_TYPE: 'amino_acid_type',
  CONSERVATION: 'conservation',
  CUSTOM: 'custom'
} as const;

export type ColorSchemeType = typeof ColorSchemeType[keyof typeof ColorSchemeType];
