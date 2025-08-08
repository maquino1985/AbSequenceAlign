// D3.js Visualization Types

import type { Region, Feature, ColorScheme } from './sequence';

export interface VisualizationData {
  sequenceId: string;
  chainId: string;
  sequence: string;
  regions: Region[];
  features: Feature[];
  colorScheme: ColorScheme;
  selectedRegions: string[];
}

export interface D3SequenceChartProps {
  data: VisualizationData[];
  width: number;
  height: number;
  onRegionClick: (region: Region) => void;
}

export interface DomainGraphicsProps {
  regions: Region[];
  sequenceLength: number;
  width: number;
  height: number;
  onRegionClick: (region: Region) => void;
  selectedRegions: string[];
  features: Feature[];
}

export interface SequenceViewerProps {
  sequence: string;
  regions: Region[];
  colorScheme: ColorScheme;
  onAminoAcidClick: (position: number, aminoAcid: string) => void;
  selectedPositions: number[];
  fontSize: number;
  showPositions: boolean;
}

export interface HighlightingSystem {
  selectedRegions: string[];
  selectedPositions: number[];
  highlightedTableRows: string[];
  highlightedSequencePositions: number[];
}

// D3 Scale types
export interface D3Scales {
  xScale: d3.ScaleLinear<number, number>;
  colorScale: d3.ScaleOrdinal<string, string>;
}
