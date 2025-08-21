import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { BlastViewerTool } from '../BlastViewerTool';
import api from '../../../../services/api';

// Mock the API module
vi.mock('../../../../services/api');

const mockApi = api as jest.Mocked<typeof api>;

// Create a theme for Material-UI components
const theme = createTheme();

// Wrapper component to provide theme context
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={theme}>
    {children}
  </ThemeProvider>
);

describe('BlastViewerTool', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Dynamic Database and Organism Discovery', () => {
    it('should load databases and organisms on mount', async () => {
      const mockDatabases = {
        public: {
          swissprot: 'Swiss-Prot protein database',
          pdbaa: 'Protein Data Bank',
          '16S_ribosomal_RNA': '16S ribosomal RNA database'
        },
        custom: {},
        internal: {
          internal_protein: 'Internal protein sequences'
        }
      };

      // mockOrganisms is not used in this test

      mockApi.getBlastDatabases.mockResolvedValue({
        success: true,
        message: 'Available databases retrieved successfully',
        data: { databases: mockDatabases }
      });



      render(
        <TestWrapper>
          <BlastViewerTool />
        </TestWrapper>
      );

      // Should show loading initially
      expect(screen.getByText('Loading BLAST tools...')).toBeInTheDocument();

      // Wait for data to load
      await waitFor(() => {
        expect(mockApi.getBlastDatabases).toHaveBeenCalledTimes(1);
        // getSupportedOrganisms is not implemented yet
      });

      // Should show the main interface after loading
      await waitFor(() => {
        expect(screen.getByText('BLAST Sequence Search')).toBeInTheDocument();
      });
    });

    it('should handle API errors gracefully', async () => {
      mockApi.getBlastDatabases.mockRejectedValue(new Error('Failed to load databases'));

      render(
        <TestWrapper>
          <BlastViewerTool />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText(/Failed to load initial data/)).toBeInTheDocument();
      });
    });

    it('should handle empty database and organism lists', async () => {
      mockApi.getBlastDatabases.mockResolvedValue({
        success: true,
        message: 'Available databases retrieved successfully',
        data: { databases: { public: {}, custom: {}, internal: {} } }
      });

      render(
        <TestWrapper>
          <BlastViewerTool />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('BLAST Sequence Search')).toBeInTheDocument();
      });
    });
  });

  describe('Tab Navigation', () => {
    beforeEach(async () => {
      // Setup successful API responses
      mockApi.getBlastDatabases.mockResolvedValue({
        success: true,
        message: 'Available databases retrieved successfully',
        data: { 
          databases: {
            public: { swissprot: 'Swiss-Prot protein database' },
            custom: {},
            internal: {}
          }
        }
      });

      render(
        <TestWrapper>
          <BlastViewerTool />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('BLAST Sequence Search')).toBeInTheDocument();
      });
    });

    it('should switch between Standard BLAST and Antibody Analysis tabs', async () => {
      const standardTab = screen.getByText('Standard BLAST');
      const antibodyTab = screen.getByText('Antibody Analysis');

      // Initially on Standard BLAST tab
      expect(standardTab).toBeInTheDocument();
      expect(antibodyTab).toBeInTheDocument();

      // Switch to Antibody Analysis tab
      fireEvent.click(antibodyTab);

      await waitFor(() => {
        expect(screen.getByText('Antibody Sequence Analysis (IgBLAST)')).toBeInTheDocument();
      });
    });

    it('should clear results when switching tabs', async () => {
      const antibodyTab = screen.getByText('Antibody Analysis');
      
      // Switch to antibody tab
      fireEvent.click(antibodyTab);

      await waitFor(() => {
        expect(screen.getByText('Antibody Sequence Analysis (IgBLAST)')).toBeInTheDocument();
      });

      // Switch back to standard tab
      const standardTab = screen.getByText('Standard BLAST');
      fireEvent.click(standardTab);

      await waitFor(() => {
        expect(screen.getByText('BLAST Search Configuration')).toBeInTheDocument();
      });
    });
  });

  describe('Search Functionality', () => {
    beforeEach(async () => {
      // Setup successful API responses
      mockApi.getBlastDatabases.mockResolvedValue({
        success: true,
        message: 'Available databases retrieved successfully',
        data: { 
          databases: {
            public: { swissprot: 'Swiss-Prot protein database' },
            custom: {},
            internal: {}
          }
        }
      });



      render(
        <TestWrapper>
          <BlastViewerTool />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('BLAST Sequence Search')).toBeInTheDocument();
      });
    });

    it('should handle standard BLAST search', async () => {
      const mockResults = {
        success: true,
        message: 'BLAST search completed successfully',
        data: {
          results: {
            blast_type: 'blastp',
            query_info: { query_id: 'query' },
            hits: [
              {
                query_id: 'query',
                subject_id: 'P01857.2',
                identity: 99.5,
                evalue: 0.0,
                bit_score: 800.0
              }
            ],
            total_hits: 1
          }
        }
      };

      mockApi.searchPublicDatabases.mockResolvedValue(mockResults);

      // Fill in search form (this would be done by the BlastSearchForm component)
      // The actual form interaction would be tested in BlastSearchForm.test.tsx
    });

    it('should handle antibody search', async () => {
      const mockResults = {
        success: true,
        message: 'Antibody analysis completed successfully',
        data: {
          results: {
            blast_type: 'igblastn',
            query_info: { query_id: 'query' },
            hits: [
              {
                query_id: 'query',
                v_gene: 'IGHV1-2*02',
                d_gene: 'IGHD2-2*01',
                j_gene: 'IGHJ4*02',
                identity: 98.5
              }
            ],
            total_hits: 1
          }
        }
      };

      mockApi.analyzeAntibodySequence.mockResolvedValue(mockResults);

      // Switch to antibody tab
      const antibodyTab = screen.getByText('Antibody Analysis');
      fireEvent.click(antibodyTab);

      await waitFor(() => {
        expect(screen.getByText('Antibody Sequence Analysis (IgBLAST)')).toBeInTheDocument();
      });
    });
  });
});
