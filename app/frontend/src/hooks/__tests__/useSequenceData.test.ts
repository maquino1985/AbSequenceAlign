import { renderHook, act } from '@testing-library/react';
import { useSequenceData } from '../useSequenceData';

describe('useSequenceData', () => {
  it('initializes with empty state', () => {
    const { result } = renderHook(() => useSequenceData());

    expect(result.current.sequences).toEqual([]);
    expect(result.current.selectedRegions).toEqual([]);
    expect(result.current.selectedPositions).toEqual([]);
    expect(result.current.colorScheme.name).toBe('Hydrophobicity');
  });

  it('processes annotation result correctly', () => {
    const { result } = renderHook(() => useSequenceData());

    const mockAnnotationResult = {
      success: true,
      message: "Successfully annotated",
      data: {
        results: [
          {
            name: "Humira_Light",
            success: true,
            data: {
              sequence: {
                name: "Humira_Light",
                biologic_type: "antibody",
                chains: [
                  {
                    name: "light_chain",
                    chain_type: "LIGHT",
                    sequences: [
                      {
                        sequence_type: "PROTEIN",
                        sequence_data: "DIQMTQSPSSLSASVGDRVTITCRASQGIRNYLAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK",
                        domains: [
                          {
                            domain_type: "V",
                            start_position: 1,
                            end_position: 213,
                            species: "human",
                            germline: "IGKV1-27*01/IGKJ1*01",
                            features: [
                              {
                                name: "CDR1",
                                feature_type: "CDR1",
                                value: "QGI------RNY",
                                start_position: 27,
                                end_position: 38
                              },
                              {
                                name: "CDR2",
                                feature_type: "CDR2",
                                value: "AA-------S",
                                start_position: 56,
                                end_position: 65
                              },
                              {
                                name: "CDR3",
                                feature_type: "CDR3",
                                value: "QRYNR----APYT",
                                start_position: 105,
                                end_position: 117
                              },
                              {
                                name: "FR1",
                                feature_type: "FR1",
                                value: "DIQMTQSPSSLSASVGDRVTITCRAS",
                                start_position: 1,
                                end_position: 26
                              },
                              {
                                name: "FR2",
                                feature_type: "FR2",
                                value: "LAWYQQKPGKAPKLLIY",
                                start_position: 39,
                                end_position: 55
                              },
                              {
                                name: "FR3",
                                feature_type: "FR3",
                                value: "SLQSGVP-SRFSGSG--SGTDFTLTISSLQPEDVATYYC",
                                start_position: 66,
                                end_position: 104
                              },
                              {
                                name: "FR4",
                                feature_type: "FR4",
                                value: "FGQGTKVEIK",
                                start_position: 118,
                                end_position: 128
                              }
                            ]
                          }
                        ]
                      }
                    ]
                  }
                ]
              }
            }
          }
        ]
      }
    };

    act(() => {
      result.current.setSequencesV2(mockAnnotationResult);
    });

    expect(result.current.sequences).toHaveLength(1);
    expect(result.current.sequences[0].name).toBe("Humira_Light");
    expect(result.current.sequences[0].species).toBe("human");
    
    const chain = result.current.sequences[0].chains[0];
    expect(chain.type).toBe("LIGHT");
    expect(chain.annotations).toHaveLength(7); // 7 features: CDR1, CDR2, CDR3, FR1, FR2, FR3, FR4
    
    // Check that features are correctly processed
    const cdr1 = chain.annotations.find(a => a.name === "CDR1");
    expect(cdr1).toBeDefined();
    expect(cdr1?.type).toBe("CDR");
    expect(cdr1?.start).toBe(27);
    expect(cdr1?.stop).toBe(38);
    expect(cdr1?.sequence).toBe("QGI------RNY");
    expect(cdr1?.details?.species).toBe("human");
    expect(cdr1?.details?.germline).toBe("IGKV1-27*01/IGKJ1*01");
  });

  it('handles region selection', () => {
    const { result } = renderHook(() => useSequenceData());
    
    // First set up some data
    const mockAnnotationResult = {
      success: true,
      message: "Successfully annotated",
      data: {
        results: [
          {
            name: "test",
            success: true,
            data: {
              sequence: {
                name: "test",
                biologic_type: "antibody",
                chains: [
                  {
                    name: "test_chain",
                    chain_type: "LIGHT",
                    sequences: [
                      {
                        sequence_type: "PROTEIN",
                        sequence_data: "TEST",
                        domains: [
                          {
                            domain_type: "V",
                            start_position: 1,
                            end_position: 10,
                            features: [
                              {
                                name: "CDR1",
                                feature_type: "CDR1",
                                value: "TEST",
                                start_position: 1,
                                end_position: 4
                              }
                            ]
                          }
                        ]
                      }
                    ]
                  }
                ]
              }
            }
          }
        ]
      }
    };

    act(() => {
      result.current.setSequencesV2(mockAnnotationResult);
    });

    const regionId = result.current.sequences[0].chains[0].annotations[0].id;
    
    act(() => {
      result.current.selectRegion(regionId);
    });

    expect(result.current.selectedRegions).toContain(regionId);
    expect(result.current.selectedPositions).toEqual([1, 2, 3, 4]);
  });

  it('handles position selection', () => {
    const { result } = renderHook(() => useSequenceData());
    
    act(() => {
      result.current.selectPosition(5);
    });

    expect(result.current.selectedPositions).toContain(5);
  });

  it('clears selection', () => {
    const { result } = renderHook(() => useSequenceData());
    
    // Set up some selections
    act(() => {
      result.current.selectPosition(5);
      result.current.selectPosition(10);
    });

    expect(result.current.selectedPositions).toHaveLength(2);

    act(() => {
      result.current.clearSelection();
    });

    expect(result.current.selectedPositions).toHaveLength(0);
    expect(result.current.selectedRegions).toHaveLength(0);
  });
});
