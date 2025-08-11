// Custom hook for sequence data management

import { useState, useCallback, useMemo } from 'react';
import type { SequenceData, Region, ColorScheme } from '../types/sequence';
import type { AnnotationResult } from '../types/api';
import type { AnnotationResultV2 } from '../types/apiV2';
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
          

          
          // Extract base region name without index
          const baseRegionName = regionName.split('_')[0];

          // Determine region type
          let regionType: Region['type'] = 'FR';
          if (baseRegionName.startsWith('CDR')) {
            regionType = 'CDR';
          } else if (regionData.domain_type === 'C') {
            regionType = 'CONSTANT';
          } else if (baseRegionName.startsWith('LINKER')) {
            regionType = 'LINKER';
          }

          regions.push({
            id: `${seqInfo.name || `seq_${index}`}_${regionName}`,
            name: baseRegionName,
            start,
            stop,
            sequence: regionData.sequence,
            type: regionType,
            color: getRegionColor(baseRegionName),
            features: [],
            details: {
              isotype: regionData.isotype,
              domain_type: regionData.domain_type,
              preceding_linker: regionData.preceding_linker
            }
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

  const setSequencesV2 = useCallback((annotationResult: AnnotationResultV2) => {
    const sequences: SequenceData[] = [];

    // Handle the new workflow response structure
    if (annotationResult.results) {
      annotationResult.results.forEach((result, seqIndex) => {
        if (result.success && result.data?.sequence) {
          const seqInfo = result.data.sequence;
          
          const chains = seqInfo.chains.map((chain, chainIdx) => {
            const annotations: Region[] = [];

            chain.sequences.forEach((sequence, seqIdx) => {
              sequence.domains.forEach((domain, domainIdx) => {
                const domainType = domain.domain_type;
                
                // Convert features to regions
                domain.features.forEach((feature, featureIdx) => {
                  const baseRegionName = feature.name;
                  let regionType: Region['type'] = 'FR';
                  if (domainType === 'LINKER') regionType = 'LINKER';
                  else if (domainType === 'C') regionType = 'CONSTANT';
                  else if (baseRegionName.startsWith('CDR')) regionType = 'CDR';

                  annotations.push({
                    id: `${seqInfo.name || `seq_${seqIndex}`}_${chain.name}_${seqIdx}_${domainIdx}_${featureIdx}_${baseRegionName}`,
                    name: baseRegionName,
                    start: feature.start_position,
                    stop: feature.end_position,
                    sequence: typeof feature.value === 'string' ? feature.value : '',
                    type: regionType,
                    color: getRegionColor(baseRegionName),
                    features: [],
                    details: {
                      isotype: undefined,
                      domain_type: domain.domain_type,
                    }
                  });
                });
              });
            });

            return {
              id: `${seqInfo.name || `seq_${seqIndex}`}_chain_${chainIdx}`,
              type: chain.chain_type,
              sequence: chain.sequences[0]?.sequence_data || '',
              annotations
            };
          });

          sequences.push({
            id: seqInfo.name || `seq_${seqIndex}`,
            name: seqInfo.name || `Sequence ${seqIndex + 1}`,
            chains,
            species: undefined
          });
        }
      });
    }

    setState((prev) => ({
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
    setSequencesV2,
    selectRegion,
    selectPosition,
    setColorScheme,
    clearSelection
  };
};
