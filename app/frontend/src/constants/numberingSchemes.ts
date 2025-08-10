export interface NumberingScheme {
  id: string;
  name: string;
  description: string;
  category: 'antibody' | 'general';
}

export const NUMBERING_SCHEMES: NumberingScheme[] = [
  {
    id: 'imgt',
    name: 'IMGT',
    description: 'International ImMunoGeneTics information system',
    category: 'antibody'
  },
  {
    id: 'kabat',
    name: 'Kabat',
    description: 'Kabat numbering scheme for antibody sequences',
    category: 'antibody'
  },
  {
    id: 'chothia',
    name: 'Chothia',
    description: 'Chothia numbering scheme for antibody sequences',
    category: 'antibody'
  },
  {
    id: 'cgg',
    name: 'CGG',
    description: 'CGG numbering scheme for antibody sequences',
    category: 'antibody'
  },
  {
    id: 'aho',
    name: 'AHO',
    description: 'AHO numbering scheme for antibody sequences',
    category: 'antibody'
  },
  {
    id: 'martin',
    name: 'Martin',
    description: 'Martin numbering scheme for antibody sequences',
    category: 'antibody'
  }
];

export const getNumberingSchemeById = (id: string): NumberingScheme | undefined => {
  return NUMBERING_SCHEMES.find(scheme => scheme.id === id);
};

export const getNumberingSchemesByCategory = (category: 'antibody' | 'general'): NumberingScheme[] => {
  return NUMBERING_SCHEMES.filter(scheme => scheme.category === category);
};

// Default numbering scheme
export const DEFAULT_NUMBERING_SCHEME = 'imgt';
