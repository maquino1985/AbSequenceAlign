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

  const setSequencesV2 = useCallback((annotationResult: any) => {
    console.log('setSequencesV2 called with:', annotationResult);
    const sequences: SequenceData[] = [];

    // Handle the v2 backend response structure
    // The backend returns: { success: true, data: { results: [{ data: { sequence: { chains: [{ domains: [{ regions: [...] }] }] } } }] } }
    
    if (annotationResult.success && annotationResult.data?.results?.length > 0) {
      console.log('Processing results array:', annotationResult.data.results);
      
      // Process each result in the array
      annotationResult.data.results.forEach((result: any, index: number) => {
        if (result.success && result.data?.sequence) {
          console.log(`Processing sequence ${index}:`, result.data.sequence);
          const seqInfo = result.data.sequence;
          
          const chains = seqInfo.chains.map((chain: any, chainIdx: number) => {
            const annotations: Region[] = [];

            // Process domains directly from the chain
            chain.domains.forEach((domain: any, domainIdx: number) => {
              const domainType = domain.domain_type;
              console.log(`Processing domain ${domainIdx}:`, domain);
              
              // Process regions from the domain
              if (domain.regions && Array.isArray(domain.regions)) {
                domain.regions.forEach((region: any, regionIdx: number) => {
                  const regionName = region.name;
                  let regionType: Region['type'] = 'FR';
                  
                  // Determine region type based on name and domain type
                  if (domainType === 'LINKER') {
                    regionType = 'LINKER';
                  } else if (domainType === 'C') {
                    regionType = 'CONSTANT';
                  } else if (regionName.startsWith('CDR')) {
                    regionType = 'CDR';
                  } else if (regionName.startsWith('FR')) {
                    regionType = 'FR';
                  }

                  annotations.push({
                    id: `${seqInfo.name || 'sequence'}_${chain.name}_${domainIdx}_${regionIdx}_${regionName}`,
                    name: regionName,
                    start: region.start,
                    stop: region.stop,
                    sequence: region.sequence || '',
                    type: regionType,
                    color: getRegionColor(regionName),
                    features: [],
                    details: {
                      isotype: domain.isotype,
                      domain_type: domain.domain_type,
                      species: domain.species,
                      germline: domain.germlines,
                    }
                  });
                });
              }

              // Create placeholder regions for domains without regions (constant and linker domains)
              if (!domain.regions || domain.regions.length === 0) {
                let regionType: Region['type'] = 'FR';
                let regionName = 'Unknown';
                
                if (domainType === 'LINKER') {
                  regionType = 'LINKER';
                  regionName = 'LINKER';
                } else if (domainType === 'C') {
                  regionType = 'CONSTANT';
                  regionName = 'CONSTANT';
                }

                // Only create placeholder regions for LINKER and C domains
                if (domainType === 'LINKER' || domainType === 'C') {
                  annotations.push({
                    id: `${seqInfo.name || 'sequence'}_${chain.name}_${domainIdx}_placeholder_${regionName}`,
                    name: regionName,
                    start: domain.start || 0,
                    stop: domain.stop || 0,
                    sequence: domain.sequence || '',
                    type: regionType,
                    color: getRegionColor(regionName),
                    features: [],
                    details: {
                      isotype: domain.isotype,
                      domain_type: domain.domain_type,
                      species: domain.species,
                      germline: domain.germlines,
                    }
                  });
                }
              }
            });

            return {
              id: `${seqInfo.name || 'sequence'}_chain_${chainIdx}`,
              type: chain.name, // Use chain name as type
              sequence: chain.sequence || '',
              annotations
            };
          });

          // Extract species from the first domain that has it
          let sequenceSpecies: string | undefined;
          for (const chain of chains) {
            for (const annotation of chain.annotations) {
              if (annotation.details?.species) {
                sequenceSpecies = annotation.details.species;
                break;
              }
            }
            if (sequenceSpecies) break;
          }

          sequences.push({
            id: seqInfo.name || `sequence_${index}`,
            name: seqInfo.name || `Sequence ${index + 1}`,
            chains,
            species: sequenceSpecies
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
