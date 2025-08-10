// Color scheme constants for amino acid and region coloring

import type { ColorScheme } from '../types/sequence';
import { ColorSchemeType } from '../types/sequence';

// Predefined color schemes
export const COLOR_SCHEMES: Record<ColorSchemeType, ColorScheme> = {
  [ColorSchemeType.HYDROPHOBICITY]: {
    name: 'Hydrophobicity',
    type: ColorSchemeType.HYDROPHOBICITY,
    colors: {
      'A': '#1f77b4', 'R': '#ff7f0e', 'N': '#2ca02c', 'D': '#d62728',
      'C': '#9467bd', 'Q': '#8c564b', 'E': '#e377c2', 'G': '#7f7f7f',
      'H': '#bcbd22', 'I': '#17becf', 'L': '#a6cee3', 'K': '#b2df8a',
      'M': '#fb9a99', 'F': '#fdbf6f', 'P': '#cab2d6', 'S': '#ff9896',
      'T': '#98df8a', 'W': '#d4b5d0', 'Y': '#c49c94', 'V': '#f0027f'
    },
    description: 'Color based on Kyte-Doolittle hydrophobicity scale'
  },
  [ColorSchemeType.CHARGE]: {
    name: 'Charge',
    type: ColorSchemeType.CHARGE,
    colors: {
      'R': '#ff6b6b', 'K': '#ff6b6b', 'H': '#ff6b6b', // Positive
      'D': '#4ecdc4', 'E': '#4ecdc4', // Negative
      'A': '#95a5a6', 'N': '#95a5a6', 'C': '#95a5a6', 'Q': '#95a5a6', 
      'G': '#95a5a6', 'I': '#95a5a6', 'L': '#95a5a6', 'M': '#95a5a6',
      'F': '#95a5a6', 'P': '#95a5a6', 'S': '#95a5a6', 'T': '#95a5a6',
      'W': '#95a5a6', 'Y': '#95a5a6', 'V': '#95a5a6' // Neutral
    },
    description: 'Color based on amino acid charge (positive, negative, neutral)'
  },
  [ColorSchemeType.AMINO_ACID_TYPE]: {
    name: 'Amino Acid Type',
    type: ColorSchemeType.AMINO_ACID_TYPE,
    colors: {
      // Hydrophobic
      'A': '#ffeb3b', 'V': '#ffeb3b', 'I': '#ffeb3b', 'L': '#ffeb3b', 
      'M': '#ffeb3b', 'F': '#ffeb3b', 'W': '#ffeb3b', 'P': '#ffeb3b',
      // Polar
      'S': '#4caf50', 'T': '#4caf50', 'N': '#4caf50', 'Q': '#4caf50',
      'Y': '#4caf50', 'C': '#4caf50',
      // Charged
      'R': '#f44336', 'K': '#f44336', 'H': '#f44336', 'D': '#2196f3', 'E': '#2196f3',
      // Special
      'G': '#9e9e9e'
    },
    description: 'Color based on amino acid chemical properties'
  },
  [ColorSchemeType.CONSERVATION]: {
    name: 'Conservation',
    type: ColorSchemeType.CONSERVATION,
    colors: {},
    description: 'Color based on sequence conservation (requires multiple sequences)'
  },
  [ColorSchemeType.CUSTOM]: {
    name: 'Custom',
    type: ColorSchemeType.CUSTOM,
    colors: {},
    description: 'User-defined color scheme'
  }
};

// Region colors - more distinct and vibrant
export const REGION_COLORS = {
  CDR1: '#e91e63',  // Pink
  CDR2: '#f44336',  // Red
  CDR3: '#9c27b0',  // Purple
  FR1: '#4caf50',   // Green
  FR2: '#2196f3',   // Blue
  FR3: '#ff9800',   // Orange
  FR4: '#607d8b',   // Blue Grey
  LIABILITY: '#d32f2f',      // Dark Red
  MUTATION: '#ff5722',       // Deep Orange
  GLYCOSYLATION: '#673ab7',  // Deep Purple
  DISULFIDE: '#ffeb3b',      // Yellow
  PTM: '#795548'             // Brown
};

// Default color scheme
export const DEFAULT_COLOR_SCHEME = COLOR_SCHEMES[ColorSchemeType.HYDROPHOBICITY];

// Utility functions
export const getAminoAcidColor = (
  aminoAcid: string, 
  colorScheme: ColorScheme
): string => {
  return colorScheme.colors[aminoAcid.toUpperCase()] || '#cccccc';
};

export const getRegionColor = (regionType: string): string => {
  return REGION_COLORS[regionType as keyof typeof REGION_COLORS] || '#cccccc';
};

export const generateGradient = (
  startColor: string, 
  endColor: string, 
  steps: number
): string[] => {
  const start = hexToRgb(startColor);
  const end = hexToRgb(endColor);
  
  if (!start || !end) return [startColor];
  
  const colors: string[] = [];
  
  for (let i = 0; i < steps; i++) {
    const ratio = i / (steps - 1);
    const r = Math.round(start.r + ratio * (end.r - start.r));
    const g = Math.round(start.g + ratio * (end.g - start.g));
    const b = Math.round(start.b + ratio * (end.b - start.b));
    
    colors.push(rgbToHex(r, g, b));
  }
  
  return colors;
};

const hexToRgb = (hex: string): { r: number; g: number; b: number } | null => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : null;
};

const rgbToHex = (r: number, g: number, b: number): string => {
  return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
};
