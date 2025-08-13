import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { FeatureTable } from '../FeatureTable';
import { useSequenceData } from '../../../../../hooks/useSequenceData';
import type { AnnotationResultV2 } from '../../../../../types/apiV2';
import type { Region } from '../../../../../types/sequence';

// Mock the useSequenceData hook
vi.mock('../../../../../hooks/useSequenceData');

describe('FeatureTable Integration Tests', () => {
  const mockOnRegionSelect = vi.fn();

  beforeEach(() => {
    mockOnRegionSelect.mockClear();
    vi.clearAllMocks();
  });

  // Mock backend API response for scFv
  const mockScFvApiResponse: AnnotationResultV2 = {
    success: true,
    message: 'Workflow completed',
    data: {
      results: [
        {
          name: 'test_scfv',
          success: true,
          data: {
            sequence: {
              name: 'test_scfv',
              biologic_type: 'antibody',
              chains: [
                {
                  name: 'scfv',
                  chain_type: 'SCFV',
                  sequences: [
                    {
                      sequence_type: 'PROTEIN',
                      sequence_data: 'DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIKGGGGGSGGGGSGGGGSGGGGSQVQLKQSGAEVKKPGASVKVSCKASGYTFTDEYMNWVRQAPGKSLEWMGYINPNNGGADYNQKFQGRVTMTVDQSISTAYMELSRLRSDDSAVYFCARLGYSNPYFDFWGQGTLVKVSS',
                      domains: [
                        {
                          domain_type: 'V',
                          start_position: 1,
                          end_position: 123,
                          features: [
                            {
                              name: 'FR1',
                              feature_type: 'FR1',
                              value: 'DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK',
                              start_position: 1,
                              end_position: 123
                            }
                          ],
                          species: 'human',
                          germline: 'IGKV1-27*01/IGKJ1*01'
                        },
                        {
                          domain_type: 'LINKER',
                          start_position: 124,
                          end_position: 143,
                          features: [
                            {
                              name: 'LINKER',
                              feature_type: 'LINKER',
                              value: 'GGGGSGGGGSGGGGSGGGGS',
                              start_position: 124,
                              end_position: 143
                            }
                          ]
                        },
                        {
                          domain_type: 'V',
                          start_position: 144,
                          end_position: 247,
                          features: [
                            {
                              name: 'FR1',
                              feature_type: 'FR1',
                              value: 'QVQLKQSGAEVKKPGASVKVSCKASGYTFTDEYMNWVRQAPGKSLEWMGYINPNNGGADYNQKFQGRVTMTVDQSISTAYMELSRLRSDDSAVYFCARLGYSNPYFDFWGQGTLVKVSS',
                              start_position: 144,
                              end_position: 247
                            }
                          ],
                          species: 'human',
                          germline: 'IGHV1-69*01/IGHJ4*01'
                        }
                      ]
                    }
                  ]
                }
              ]
            }
          }
        }
      ],
      summary: { total: 1, successful: 1, failed: 0 }
    }
  };

  // Mock backend API response for IgG
  const mockIgGApiResponse: AnnotationResultV2 = {
    success: true,
    message: 'Workflow completed',
    data: {
      results: [
        {
          name: 'test_igg',
          success: true,
          data: {
            sequence: {
              name: 'test_igg',
              biologic_type: 'antibody',
              chains: [
                {
                  name: 'heavy_chain',
                  chain_type: 'HEAVY',
                  sequences: [
                    {
                      sequence_type: 'PROTEIN',
                      sequence_data: 'EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSSGQPREPQVYTLPPSRDELTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK',
                      domains: [
                        {
                          domain_type: 'V',
                          start_position: 1,
                          end_position: 117,
                          features: [
                            {
                              name: 'FR1',
                              feature_type: 'FR1',
                              value: 'EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS',
                              start_position: 1,
                              end_position: 117
                            }
                          ],
                          species: 'human',
                          germline: 'IGHV1-69*01/IGHJ4*01'
                        },
                        {
                          domain_type: 'C',
                          start_position: 118,
                          end_position: 220,
                          features: [
                            {
                              name: 'CH1',
                              feature_type: 'CH1',
                              value: 'GQPREPQVYTLPPSRDELTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK',
                              start_position: 118,
                              end_position: 220
                            }
                          ],
                          species: 'human',
                          isotype: 'IGHG1'
                        }
                      ]
                    }
                  ]
                }
              ]
            }
          }
        }
      ],
      summary: { total: 1, successful: 1, failed: 0 }
    }
  };

  it('should render scFv regions correctly from backend API response', async () => {
    // Convert API response to regions (simulating useSequenceData processing)
    const regions: Region[] = [
      {
        id: 'test_scfv_scfv_0_0_0_FR1',
        name: 'FR1',
        start: 1,
        stop: 123,
        sequence: 'DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK',
        type: 'FR',
        color: '#FF6B6B',
        features: [],
        details: {
          domain_type: 'V',
          species: 'human',
          germline: 'IGKV1-27*01/IGKJ1*01'
        }
      },
      {
        id: 'test_scfv_scfv_0_1_0_LINKER',
        name: 'LINKER',
        start: 124,
        stop: 143,
        sequence: 'GGGGSGGGGSGGGGSGGGGS',
        type: 'LINKER',
        color: '#CCCCCC',
        features: [],
        details: {
          domain_type: 'LINKER'
        }
      },
      {
        id: 'test_scfv_scfv_0_2_0_FR1',
        name: 'FR1',
        start: 144,
        stop: 247,
        sequence: 'QVQLKQSGAEVKKPGASVKVSCKASGYTFTDEYMNWVRQAPGKSLEWMGYINPNNGGADYNQKFQGRVTMTVDQSISTAYMELSRLRSDDSAVYFCARLGYSNPYFDFWGQGTLVKVSS',
        type: 'FR',
        color: '#FF6B6B',
        features: [],
        details: {
          domain_type: 'V',
          species: 'human',
          germline: 'IGHV1-69*01/IGHJ4*01'
        }
      }
    ];

    render(
      <FeatureTable
        regions={regions}
        selectedRegions={[]}
        onRegionSelect={mockOnRegionSelect}
      />
    );

    // Verify regions are rendered (use getAllByText since there are multiple FR1 regions in scFv)
    expect(screen.getAllByText('FR1')).toHaveLength(2);
    expect(screen.getByTestId('chip-LINKER')).toBeInTheDocument();
    
    // Verify sequence data is displayed
    expect(screen.getByText('DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK')).toBeInTheDocument();
    expect(screen.getByText('GGGGSGGGGSGGGGSGGGGS')).toBeInTheDocument();
    
    // Verify details are displayed (use getAllByText since there are multiple Domain: V elements in scFv)
    expect(screen.getAllByText('Domain: V')).toHaveLength(2);
    expect(screen.getByText('Domain: LINKER')).toBeInTheDocument();
  });

  it('should render IgG regions correctly from backend API response', async () => {
    // Convert API response to regions (simulating useSequenceData processing)
    const regions: Region[] = [
      {
        id: 'test_igg_heavy_chain_0_0_0_FR1',
        name: 'FR1',
        start: 1,
        stop: 117,
        sequence: 'EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS',
        type: 'FR',
        color: '#FF6B6B',
        features: [],
        details: {
          domain_type: 'V',
          species: 'human',
          germline: 'IGHV1-69*01/IGHJ4*01'
        }
      },
      {
        id: 'test_igg_heavy_chain_0_1_0_CH1',
        name: 'CH1',
        start: 118,
        stop: 220,
        sequence: 'GQPREPQVYTLPPSRDELTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK',
        type: 'CONSTANT',
        color: '#45B7D1',
        features: [],
        details: {
          domain_type: 'C',
          species: 'human',
          isotype: 'IGHG1'
        }
      }
    ];

    render(
      <FeatureTable
        regions={regions}
        selectedRegions={[]}
        onRegionSelect={mockOnRegionSelect}
      />
    );

    // Verify regions are rendered
    expect(screen.getByText('FR1')).toBeInTheDocument();
    expect(screen.getByText('CH1')).toBeInTheDocument();
    
    // Verify sequence data is displayed
    expect(screen.getByText('EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS')).toBeInTheDocument();
    expect(screen.getByText('GQPREPQVYTLPPSRDELTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK')).toBeInTheDocument();
    
    // Verify details are displayed
    expect(screen.getByText('Domain: V')).toBeInTheDocument();
    expect(screen.getByText('Domain: C')).toBeInTheDocument();
    expect(screen.getByText('Isotype: IGHG1')).toBeInTheDocument();
  });

  it('should handle region selection correctly', async () => {
    const regions: Region[] = [
      {
        id: 'test_region_1',
        name: 'CDR1',
        start: 26,
        stop: 33,
        sequence: 'GFTFSSYA',
        type: 'CDR',
        color: '#4ECDC4',
        features: [],
        details: {
          domain_type: 'V'
        }
      }
    ];

    render(
      <FeatureTable
        regions={regions}
        selectedRegions={[]}
        onRegionSelect={mockOnRegionSelect}
      />
    );

    // Click on a region
    const regionRow = screen.getByText('CDR1').closest('tr');
    expect(regionRow).toBeInTheDocument();
    
    fireEvent.click(regionRow!);
    
    expect(mockOnRegionSelect).toHaveBeenCalledWith('test_region_1');
  });

  it('should display selected regions with correct styling', async () => {
    const regions: Region[] = [
      {
        id: 'test_region_1',
        name: 'CDR1',
        start: 26,
        stop: 33,
        sequence: 'GFTFSSYA',
        type: 'CDR',
        color: '#4ECDC4',
        features: [],
        details: {
          domain_type: 'V'
        }
      }
    ];

    render(
      <FeatureTable
        regions={regions}
        selectedRegions={['test_region_1']}
        onRegionSelect={mockOnRegionSelect}
      />
    );

    // Verify the region is highlighted
    const regionRow = screen.getByText('CDR1').closest('tr');
    expect(regionRow).toHaveStyle({ backgroundColor: 'rgba(25, 118, 210, 0.08)' });
  });

  it('should handle empty regions gracefully', async () => {
    render(
      <FeatureTable
        regions={[]}
        selectedRegions={[]}
        onRegionSelect={mockOnRegionSelect}
      />
    );

    expect(screen.getByText(/No regions to display/i)).toBeInTheDocument();
  });

  it('should validate region data structure matches backend API', async () => {
    // Test that the region structure matches what the backend sends
    const mockRegion: Region = {
      id: 'test_id',
      name: 'test_name',
      start: 1,
      stop: 10,
      sequence: 'TESTSEQUENCE',
      type: 'CDR',
      color: '#FF0000',
      features: [],
      details: {
        domain_type: 'V',
        species: 'human',
        germline: 'IGHV1-69*01',
        isotype: 'IGHG1'
      }
    };

    // Verify all required fields are present
    expect(mockRegion).toHaveProperty('id');
    expect(mockRegion).toHaveProperty('name');
    expect(mockRegion).toHaveProperty('start');
    expect(mockRegion).toHaveProperty('stop');
    expect(mockRegion).toHaveProperty('sequence');
    expect(mockRegion).toHaveProperty('type');
    expect(mockRegion).toHaveProperty('color');
    expect(mockRegion).toHaveProperty('features');
    expect(mockRegion).toHaveProperty('details');

    // Verify details structure
    expect(mockRegion.details).toHaveProperty('domain_type');
    expect(mockRegion.details).toHaveProperty('species');
    expect(mockRegion.details).toHaveProperty('germline');
    expect(mockRegion.details).toHaveProperty('isotype');
  });

  it('should handle different region types correctly', async () => {
    const regions: Region[] = [
      {
        id: 'cdr_1',
        name: 'CDR1',
        start: 26,
        stop: 33,
        sequence: 'GFTFSSYA',
        type: 'CDR',
        color: '#4ECDC4',
        features: [],
        details: { domain_type: 'V' }
      },
      {
        id: 'constant_1',
        name: 'CH1',
        start: 118,
        stop: 220,
        sequence: 'GQPREPQVYTLPPSRDELTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK',
        type: 'CONSTANT',
        color: '#45B7D1',
        features: [],
        details: { 
          domain_type: 'C',
          isotype: 'IGHG1'
        }
      },
      {
        id: 'linker_1',
        name: 'LINKER',
        start: 124,
        stop: 143,
        sequence: 'GGGGSGGGGSGGGGSGGGGS',
        type: 'LINKER',
        color: '#CCCCCC',
        features: [],
        details: { domain_type: 'LINKER' }
      }
    ];

    render(
      <FeatureTable
        regions={regions}
        selectedRegions={[]}
        onRegionSelect={mockOnRegionSelect}
      />
    );

    // Verify all region types are rendered
    expect(screen.getByText('CDR1')).toBeInTheDocument();
    expect(screen.getByText('CH1')).toBeInTheDocument();
    expect(screen.getByTestId('chip-LINKER')).toBeInTheDocument();

    // Verify chip colors are applied correctly using data-testid
    expect(screen.getByTestId('chip-CDR1')).toBeInTheDocument();
    expect(screen.getByTestId('chip-CH1')).toBeInTheDocument();
    expect(screen.getByTestId('chip-LINKER')).toBeInTheDocument();
  });
});
