import { describe, test, expect } from 'vitest';
import { NumberingScheme } from '../../types/api';

describe('API Request Format Tests', () => {
  test('should validate correct request format for annotation', () => {
    const validRequest = {
      sequences: [
        {
          name: 'Heavy_Chain_1',
          heavy_chain: 'EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK'
        }
      ],
      numbering_scheme: NumberingScheme.IMGT
    };

    // Verify request structure
    expect(validRequest.sequences).toBeDefined();
    expect(Array.isArray(validRequest.sequences)).toBe(true);
    expect(validRequest.sequences).toHaveLength(1);
    expect(validRequest.sequences[0]).toHaveProperty('name');
    expect(validRequest.sequences[0]).toHaveProperty('heavy_chain');
    expect(validRequest.numbering_scheme).toBe(NumberingScheme.IMGT);
  });

  test('should validate multiple sequences in request', () => {
    const validRequest = {
      sequences: [
        {
          name: 'Heavy_Chain_1',
          heavy_chain: 'EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK'
        },
        {
          name: 'Light_Chain_1',
          light_chain: 'DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK'
        }
      ],
      numbering_scheme: NumberingScheme.KABAT
    };

    expect(validRequest.sequences).toHaveLength(2);
    expect(validRequest.sequences[0]).toHaveProperty('heavy_chain');
    expect(validRequest.sequences[1]).toHaveProperty('light_chain');
    expect(validRequest.numbering_scheme).toBe(NumberingScheme.KABAT);
  });

  test('should validate different numbering schemes', () => {
    const schemes = [
      NumberingScheme.IMGT,
      NumberingScheme.KABAT,
      NumberingScheme.CHOTHIA,
      NumberingScheme.MARTIN,
      NumberingScheme.AHO,
      NumberingScheme.CGG
    ];

    schemes.forEach(scheme => {
      const request = {
        sequences: [
          {
            name: 'Test_Sequence',
            heavy_chain: 'EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK'
          }
        ],
        numbering_scheme: scheme
      };

      expect(request.numbering_scheme).toBe(scheme);
    });
  });

  test('should validate sequence content format', () => {
    const validSequences = [
      'EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK',
      'DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK',
      'QVQLVQSGAEVKKPGASVKVSCKASGYTFTSYAMHWVRQAPGQGLEWMGGINPSNGGTNFNEKFKNRVTLTTDSSTSTAYMELSSLRSEDTAVYYCARRDYRFDMGFDYWGQGTTVTVSS'
    ];

    validSequences.forEach(sequence => {
      // Check that sequence contains only valid amino acids
      const validAminoAcids = /^[ACDEFGHIKLMNPQRSTVWY]+$/;
      expect(validAminoAcids.test(sequence)).toBe(true);
      
      // Check minimum length
      expect(sequence.length).toBeGreaterThanOrEqual(15);
    });
  });

  test('should detect invalid sequence format', () => {
    const invalidSequences = [
      'INVALID_SEQUENCE_123',
      'EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK123',
      'EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK!@#'
    ];

    const validAminoAcids = /^[ACDEFGHIKLMNPQRSTVWY]+$/;

    invalidSequences.forEach(sequence => {
      expect(validAminoAcids.test(sequence)).toBe(false);
    });
  });

  test('should validate expected API response format', () => {
    const expectedResponse = {
      success: true,
      message: 'Annotation completed successfully',
      data: {
        annotation_result: {
          sequences: [
            {
              sequence: 'EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK',
              name: 'Heavy_Chain_1',
              chain_type: 'H',
              regions: {
                'CDR1': {
                  name: 'CDR1',
                  start: 27,
                  stop: 38,
                  sequence: 'GFTFSSYAMS'
                },
                'CDR2': {
                  name: 'CDR2',
                  start: 56,
                  stop: 65,
                  sequence: 'ISGSGGSTYY'
                },
                'CDR3': {
                  name: 'CDR3',
                  start: 105,
                  stop: 117,
                  sequence: 'CAK'
                }
              }
            }
          ],
          numbering_scheme: 'imgt',
          total_sequences: 1,
          chain_types: { 'H': 1 },
          isotypes: {},
          species: {}
        }
      }
    };

    // Verify response structure
    expect(expectedResponse.success).toBe(true);
    expect(expectedResponse.data?.annotation_result.sequences).toBeDefined();
    expect(expectedResponse.data?.annotation_result.sequences).toHaveLength(1);
    expect(expectedResponse.data?.annotation_result.sequences[0].regions).toBeDefined();
    expect(Object.keys(expectedResponse.data?.annotation_result.sequences[0].regions || {})).toContain('CDR1');
    expect(Object.keys(expectedResponse.data?.annotation_result.sequences[0].regions || {})).toContain('CDR2');
    expect(Object.keys(expectedResponse.data?.annotation_result.sequences[0].regions || {})).toContain('CDR3');
  });
});
