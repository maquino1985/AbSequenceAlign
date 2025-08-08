// Custom hook for sequence data management

import { useState, useCallback, useMemo } from 'react';
import type { SequenceData, Region, ColorScheme } from '../types/sequence';
import type { AnnotationResult } from '../types/api';
import { COLOR_SCHEMES, getRegionColor } from '../utils/colorUtils';
import { ColorSchemeType } from '../types/sequence';

interface SequenceDataState {
  sequences: SequenceData[];
  selectedRegions: string[];
  selectedPositions: number[];
  colorScheme: ColorScheme;
}

export const useSequenceData = () => {
  const [state, setState] = useState<SequenceDataState>({
    sequences: [],
    selectedRegions: [],
    selectedPositions: [],
    colorScheme: COLOR_SCHEMES[ColorSchemeType.HYDROPHOBICITY]
  });

  const setSequences = useCallback((annotationResult: AnnotationResult) => {
    // Convert API response to internal data structure
    const sequences: SequenceData[] = [];
    
    // Each sequence from the API should be treated as a separate sequence
    // (not grouped by name - each FASTA entry is independent)
    annotationResult.sequences.forEach((seqInfo, index) => {
      const regions: Region[] = [];
      
      if (seqInfo.regions) {
        Object.entries(seqInfo.regions).forEach(([regionName, regionData]) => {
          // Handle start/stop that might be arrays [position, ' '] from backend
          let start: number;
          let stop: number;
          
          if (Array.isArray(regionData.start)) {
            start = typeof regionData.start[0] === 'number' ? regionData.start[0] : parseInt(regionData.start[0]);
          } else {
            start = typeof regionData.start === 'string' ? parseInt(regionData.start) : regionData.start;
          }
          
          if (Array.isArray(regionData.stop)) {
            stop = typeof regionData.stop[0] === 'number' ? regionData.stop[0] : parseInt(regionData.stop[0]);
          } else {
            stop = typeof regionData.stop === 'string' ? parseInt(regionData.stop) : regionData.stop;
          }
          

          
          regions.push({
            id: `${seqInfo.name || `seq_${index}`}_${regionName}`,
            name: regionName,
            start,
            stop,
            sequence: regionData.sequence,
            type: regionName.startsWith('CDR') ? 'CDR' : 'FR',
            color: getRegionColor(regionName),
            features: []
          });
        });
      }

      // Each annotated sequence becomes one chain in one sequence
      const chain = {
        id: `${seqInfo.name || `seq_${index}`}_chain`,
        type: seqInfo.chain_type || 'Unknown',
        sequence: seqInfo.sequence,
        annotations: regions
      };

      sequences.push({
        id: seqInfo.name || `seq_${index}`,
        name: seqInfo.name || `Sequence ${index + 1}`,
        chains: [chain], // Each sequence has one chain
        species: seqInfo.species
      });
    });

    setState(prev => ({
      ...prev,
      sequences,
      selectedRegions: [],
      selectedPositions: []
    }));
  }, []);

  const selectRegion = useCallback((regionId: string) => {
    setState(prev => {
      const isSelected = prev.selectedRegions.includes(regionId);
      const newSelectedRegions = isSelected
        ? prev.selectedRegions.filter(id => id !== regionId)
        : [...prev.selectedRegions, regionId];
      
      // Find the region and update selected positions
      let newSelectedPositions = [...prev.selectedPositions];
      const region = prev.sequences
        .flatMap(seq => seq.chains)
        .flatMap(chain => chain.annotations)
        .find(r => r.id === regionId);
      
      if (region) {
        const regionPositions: number[] = [];
        for (let pos = region.start; pos <= region.stop; pos++) {
          regionPositions.push(pos);
        }
        
        if (isSelected) {
          // Remove region positions from selection
          newSelectedPositions = newSelectedPositions.filter(pos => !regionPositions.includes(pos));
        } else {
          // Add region positions to selection
          newSelectedPositions = [...new Set([...newSelectedPositions, ...regionPositions])];
        }
      }
      
      return {
        ...prev,
        selectedRegions: newSelectedRegions,
        selectedPositions: newSelectedPositions
      };
    });
  }, []);

  const selectPosition = useCallback((position: number) => {
    setState(prev => ({
      ...prev,
      selectedPositions: prev.selectedPositions.includes(position)
        ? prev.selectedPositions.filter(pos => pos !== position)
        : [...prev.selectedPositions, position]
    }));
  }, []);

  const setColorScheme = useCallback((colorScheme: ColorScheme) => {
    setState(prev => ({ ...prev, colorScheme }));
  }, []);

  const clearSelection = useCallback(() => {
    setState(prev => ({
      ...prev,
      selectedRegions: [],
      selectedPositions: []
    }));
  }, []);

  // Memoized derived data
  const allRegions = useMemo(() => {
    return state.sequences.flatMap(seq =>
      seq.chains.flatMap(chain => chain.annotations)
    );
  }, [state.sequences]);

  const regionStats = useMemo(() => {
    const stats: Record<string, number> = {};
    allRegions.forEach(region => {
      stats[region.name] = (stats[region.name] || 0) + 1;
    });
    return stats;
  }, [allRegions]);

  return {
    sequences: state.sequences,
    selectedRegions: state.selectedRegions,
    selectedPositions: state.selectedPositions,
    colorScheme: state.colorScheme,
    allRegions,
    regionStats,
    setSequences,
    selectRegion,
    selectPosition,
    setColorScheme,
    clearSelection
  };
};
