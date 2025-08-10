import { renderHook, act } from '@testing-library/react';
import { useSequenceData } from '../useSequenceData';
import type { AnnotationResult } from '../../types/api';

describe('useSequenceData', () => {
  const mockAnnotationResult: AnnotationResult = {
    sequences: [
      {
        name: 'test_sequence',
        sequence: 'EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYAD',
        chain_type: 'H',
        isotype: 'IGHG1',
        species: 'human',
        germline: 'IGHV3-23*01',
        regions: {
          FR1: {
            name: 'FR1',
            start: 1,
            stop: 25,
            sequence: 'EVQLVESGGGLVQPGGSLRLSCAAS',
            domain_type: 'V'
          },
          CDR1: {
            name: 'CDR1',
            start: 26,
            stop: 33,
            sequence: 'GFTFSSYA',
            domain_type: 'V'
          },
          LINKER1: {
            name: 'LINKER1',
            start: 110,
            stop: 119,
            sequence: 'GGGGSGGGGG',
            preceding_linker: {
              sequence: 'GGGGSGGGGG',
              start: 110,
              end: 119
            }
          },
          CH1: {
            name: 'CH1',
            start: 120,
            stop: 220,
            sequence: 'ASTKGPSVFPLAPSSKSTSGGTAALGCLVKDYFPEPVTVSWNSGALTSGVHTFPAVLQSSGLYSLSSVVTVPSSSLGTQTYICNVNHKPSNTKVDKKV',
            domain_type: 'C',
            isotype: 'IGHG1'
          }
        }
      }
    ],
    numbering_scheme: 'imgt',
    total_sequences: 1,
    chain_types: { H: 1 },
    isotypes: { IGHG1: 1 },
    species: { human: 1 }
  };

  it('initializes with empty state', () => {
    const { result } = renderHook(() => useSequenceData());
    expect(result.current.sequences).toHaveLength(0);
    expect(result.current.selectedRegions).toHaveLength(0);
    expect(result.current.selectedPositions).toHaveLength(0);
  });

  it('processes annotation result correctly', () => {
    const { result } = renderHook(() => useSequenceData());

    act(() => {
      result.current.setSequences(mockAnnotationResult);
    });

    expect(result.current.sequences).toHaveLength(1);
    const sequence = result.current.sequences[0];
    expect(sequence.name).toBe('test_sequence');
    expect(sequence.chains).toHaveLength(1);

    const chain = sequence.chains[0];
    expect(chain.type).toBe('H');
    expect(chain.annotations).toHaveLength(4);

    // Check FR1 region
    const fr1 = chain.annotations.find(r => r.name === 'FR1');
    expect(fr1).toBeDefined();
    expect(fr1?.type).toBe('FR');
    expect(fr1?.details?.domain_type).toBe('V');

    // Check CDR1 region
    const cdr1 = chain.annotations.find(r => r.name === 'CDR1');
    expect(cdr1).toBeDefined();
    expect(cdr1?.type).toBe('CDR');
    expect(cdr1?.details?.domain_type).toBe('V');

    // Check linker region
    const linker = chain.annotations.find(r => r.name === 'LINKER1');
    expect(linker).toBeDefined();
    expect(linker?.type).toBe('LINKER');
    expect(linker?.details?.preceding_linker).toBeDefined();
    expect(linker?.details?.preceding_linker?.sequence).toBe('GGGGSGGGGG');

    // Check constant region
    const ch1 = chain.annotations.find(r => r.name === 'CH1');
    expect(ch1).toBeDefined();
    expect(ch1?.type).toBe('CONSTANT');
    expect(ch1?.details?.domain_type).toBe('C');
    expect(ch1?.details?.isotype).toBe('IGHG1');
  });

  it('handles region selection', () => {
    const { result } = renderHook(() => useSequenceData());

    act(() => {
      result.current.setSequences(mockAnnotationResult);
    });

    const fr1Id = result.current.sequences[0].chains[0].annotations[0].id;

    act(() => {
      result.current.selectRegion(fr1Id);
    });

    expect(result.current.selectedRegions).toContain(fr1Id);
    expect(result.current.selectedPositions).toHaveLength(25); // FR1 length

    // Deselect region
    act(() => {
      result.current.selectRegion(fr1Id);
    });

    expect(result.current.selectedRegions).not.toContain(fr1Id);
    expect(result.current.selectedPositions).toHaveLength(0);
  });

  it('handles position selection', () => {
    const { result } = renderHook(() => useSequenceData());

    act(() => {
      result.current.selectPosition(1);
    });

    expect(result.current.selectedPositions).toContain(1);

    act(() => {
      result.current.selectPosition(1);
    });

    expect(result.current.selectedPositions).not.toContain(1);
  });

  it('clears selection', () => {
    const { result } = renderHook(() => useSequenceData());

    act(() => {
      result.current.setSequences(mockAnnotationResult);
    });

    act(() => {
      result.current.selectPosition(1);
      result.current.selectRegion(result.current.sequences[0].chains[0].annotations[0].id);
    });

    expect(result.current.selectedPositions).not.toHaveLength(0);
    expect(result.current.selectedRegions).not.toHaveLength(0);

    act(() => {
      result.current.clearSelection();
    });

    expect(result.current.selectedPositions).toHaveLength(0);
    expect(result.current.selectedRegions).toHaveLength(0);
  });
});
