import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { SequenceAnnotation } from '../../../pages/SequenceAnnotation';
import { api } from '../../../../../services/api';

// Mock the API service
vi.mock('../../../../../services/api', () => ({
  api: {
    annotateSequencesV2: vi.fn()
  }
}));

describe('FeatureTable E2E Tests', () => {
  const mockApi = api as jest.Mocked<typeof api>;

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should populate feature table after successful API call', async () => {
    // Mock successful API response
    const mockApiResponse = {
      success: true,
      message: "Successfully annotated",
      data: {
        results: [
          {
            name: "Humira_Heavy",
            success: true,
            data: {
              sequence: {
                name: "Humira_Heavy",
                biologic_type: "antibody",
                chains: [
                  {
                    name: "heavy_chain",
                    chain_type: "HEAVY",
                    sequences: [
                      {
                        sequence_type: "PROTEIN",
                        sequence_data: "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS",
                        domains: [
                          {
                            domain_type: "V",
                            start_position: 1,
                            end_position: 117,
                            species: "human",
                            germline: "IGHV1-69*01/IGHJ4*01",
                            features: [
                              {
                                name: "CDR1",
                                feature_type: "CDR1",
                                value: "GFTFSYFA",
                                start_position: 26,
                                end_position: 33
                              },
                              {
                                name: "CDR2",
                                feature_type: "CDR2",
                                value: "ISGGGGNT",
                                start_position: 55,
                                end_position: 62
                              },
                              {
                                name: "CDR3",
                                feature_type: "CDR3",
                                value: "VRQTYGGFGYWGQGTLVTVSS",
                                start_position: 95,
                                end_position: 117
                              },
                              {
                                name: "FR1",
                                feature_type: "FR1",
                                value: "EVQLVESGGGLVQPGGSLRLSCAAS",
                                start_position: 1,
                                end_position: 25
                              },
                              {
                                name: "FR2",
                                feature_type: "FR2",
                                value: "MSWVRQAPGKGLEWVATIS",
                                start_position: 34,
                                end_position: 54
                              },
                              {
                                name: "FR3",
                                feature_type: "FR3",
                                value: "YYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYC",
                                start_position: 63,
                                end_position: 94
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
          ]
        }
      }
    };

    mockApi.annotateSequencesV2.mockResolvedValue(mockApiResponse);

    render(<SequenceAnnotation />);

    // Find the FASTA input and fill it
    const fastaInput = screen.getByRole('textbox');
    const fastaContent = `>Humira_Heavy
EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS`;
    
    fireEvent.change(fastaInput, { target: { value: fastaContent } });

    // Find and click the Start Analysis button
    const startButton = screen.getByRole('button', { name: /start analysis/i });
    fireEvent.click(startButton);

    // Wait for the API call to complete and results to render
    await waitFor(() => {
      expect(mockApi.annotateSequencesV2).toHaveBeenCalledWith({
        sequences: [
          {
            name: "Humira_Heavy",
            heavy_chain: "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS"
          }
        ],
        numbering_scheme: "imgt"
      });
    });

    // Wait for the feature table to appear
    await waitFor(() => {
      expect(screen.getByTestId('feature-table')).toBeInTheDocument();
    }, { timeout: 5000 });

    // Verify that regions are displayed in the feature table
    await waitFor(() => {
      expect(screen.getAllByText('CDR1')).toHaveLength(3); // SVG + table + chip
      expect(screen.getAllByText('CDR2')).toHaveLength(3);
      expect(screen.getAllByText('CDR3')).toHaveLength(3);
      expect(screen.getAllByText('FR1')).toHaveLength(3);
      expect(screen.getAllByText('FR2')).toHaveLength(3);
      expect(screen.getAllByText('FR3')).toHaveLength(3);
    });

    // Verify that sequence data is displayed
    expect(screen.getByText('GFTFSYFA')).toBeInTheDocument(); // CDR1 sequence
    expect(screen.getByText('ISGGGGNT')).toBeInTheDocument(); // CDR2 sequence
    expect(screen.getByText('VRQTYGGFGYWGQGTLVTVSS')).toBeInTheDocument(); // CDR3 sequence

    // Verify that details are displayed
    expect(screen.getAllByText('Domain: V')).toHaveLength(6); // One for each feature
  });

  it('should handle scFv sequences correctly', async () => {
    // Mock scFv API response
    const mockScFvResponse = {
      success: true,
      message: "Successfully annotated",
      data: {
        results: [
          {
            name: "test_scfv",
            success: true,
            data: {
              sequence: {
                name: "test_scfv",
                biologic_type: "antibody",
                chains: [
                  {
                    name: "scfv",
                    chain_type: "SCFV",
                    sequences: [
                      {
                        sequence_type: "PROTEIN",
                        sequence_data: "DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIKGGGGGSGGGGSGGGGSGGGGSQVQLKQSGAEVKKPGASVKVSCKASGYTFTDEYMNWVRQAPGKSLEWMGYINPNNGGADYNQKFQGRVTMTVDQSISTAYMELSRLRSDDSAVYFCARLGYSNPYFDFWGQGTLVKVSS",
                        domains: [
                          {
                            domain_type: "V",
                            start_position: 1,
                            end_position: 123,
                            species: "human",
                            germline: "IGKV1-27*01/IGKJ1*01",
                            features: [
                              {
                                name: "FR1",
                                feature_type: "FR1",
                                value: "DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK",
                                start_position: 1,
                                end_position: 123
                              }
                            ]
                          },
                          {
                            domain_type: "LINKER",
                            start_position: 124,
                            end_position: 143,
                            features: [
                              {
                                name: "LINKER",
                                feature_type: "LINKER",
                                value: "GGGGSGGGGSGGGGSGGGGS",
                                start_position: 124,
                                end_position: 143
                              }
                            ]
                          },
                          {
                            domain_type: "V",
                            start_position: 144,
                            end_position: 247,
                            species: "human",
                            germline: "IGHV1-69*01/IGHJ4*01",
                            features: [
                              {
                                name: "FR1",
                                feature_type: "FR1",
                                value: "QVQLKQSGAEVKKPGASVKVSCKASGYTFTDEYMNWVRQAPGKSLEWMGYINPNNGGADYNQKFQGRVTMTVDQSISTAYMELSRLRSDDSAVYFCARLGYSNPYFDFWGQGTLVKVSS",
                                start_position: 144,
                                end_position: 247
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
          ]
        }
      }
    };

    mockApi.annotateSequencesV2.mockResolvedValue(mockScFvResponse);

    render(<SequenceAnnotation />);

    // Input scFv sequence
    const fastaInput = screen.getByRole('textbox');
    const scFvContent = `>test_scfv
DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIKGGGGGSGGGGSGGGGSGGGGSQVQLKQSGAEVKKPGASVKVSCKASGYTFTDEYMNWVRQAPGKSLEWMGYINPNNGGADYNQKFQGRVTMTVDQSISTAYMELSRLRSDDSAVYFCARLGYSNPYFDFWGQGTLVKVSS`;
    
    fireEvent.change(fastaInput, { target: { value: scFvContent } });

    // Click Start Analysis
    const startButton = screen.getByRole('button', { name: /start analysis/i });
    fireEvent.click(startButton);

    // Wait for results
    await waitFor(() => {
      expect(screen.getByTestId('feature-table')).toBeInTheDocument();
    });

    // Verify scFv-specific regions
    await waitFor(() => {
      expect(screen.getAllByText('FR1')).toHaveLength(3); // SVG + table + chip
      expect(screen.getAllByText('LINKER')).toHaveLength(3);
    });

    // Verify linker sequence
    expect(screen.getByText('GGGGSGGGGSGGGGSGGGGS')).toBeInTheDocument();
  });

  it('should show error state when API call fails', async () => {
    // Mock API failure
    mockApi.annotateSequencesV2.mockRejectedValue(new Error('API Error'));

    render(<SequenceAnnotation />);

    // Input sequence
    const fastaInput = screen.getByRole('textbox');
    fireEvent.change(fastaInput, { target: { value: '>test\nEVQLVESGGGLVQPGGSLRLSCAAS' } });

    // Click Start Analysis
    const startButton = screen.getByRole('button', { name: /start analysis/i });
    fireEvent.click(startButton);

    // Wait for error message
    await waitFor(() => {
      expect(screen.getByTestId('error-message')).toBeInTheDocument();
    });

    // Verify no feature table is shown
    expect(screen.queryByTestId('feature-table')).not.toBeInTheDocument();
  });

  it('should show loading state during API call', async () => {
    // Mock delayed API response
    mockApi.annotateSequencesV2.mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({ success: true, data: { results: [{ name: "test", success: true, data: { sequence: { name: "test", biologic_type: "antibody", chains: [] } } }] } }), 100))
    );

    render(<SequenceAnnotation />);

    // Input sequence
    const fastaInput = screen.getByRole('textbox');
    fireEvent.change(fastaInput, { target: { value: '>test\nEVQLVESGGGLVQPGGSLRLSCAAS' } });

    // Click Start Analysis
    const startButton = screen.getByRole('button', { name: /start analysis/i });
    fireEvent.click(startButton);

    // Verify loading indicator appears
    expect(screen.getByTestId('loading-indicator')).toBeInTheDocument();

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByTestId('loading-indicator')).not.toBeInTheDocument();
    });
  });
});
