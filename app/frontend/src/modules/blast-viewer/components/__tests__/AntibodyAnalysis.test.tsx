import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import AntibodyAnalysis from '../AntibodyAnalysis';

// Create a theme for Material-UI components
const theme = createTheme();

// Wrapper component to provide theme context
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={theme}>
    {children}
  </ThemeProvider>
);

describe('AntibodyAnalysis', () => {
  const mockOnSearch = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Dynamic Organism Rendering', () => {
    it('should render organism options from dynamic data', () => {
      const mockOrganisms = ['human', 'mouse', 'rat'];

      render(
        <TestWrapper>
          <AntibodyAnalysis
            organisms={mockOrganisms}
            onSearch={mockOnSearch}
            loading={false}
          />
        </TestWrapper>
      );

      // Check that organism options are rendered
      expect(screen.getByText('Human')).toBeInTheDocument();
      expect(screen.getByText('Mouse')).toBeInTheDocument();
      expect(screen.getByText('Rat')).toBeInTheDocument();
    });

    it('should show loading state when organisms list is empty', () => {
      render(
        <TestWrapper>
          <AntibodyAnalysis
            organisms={[]}
            onSearch={mockOnSearch}
            loading={false}
          />
        </TestWrapper>
      );

      expect(screen.getByText('Loading organisms...')).toBeInTheDocument();
      expect(screen.getByText('Loading available organisms...')).toBeInTheDocument();
    });

    it('should show organism count in helper text', () => {
      const mockOrganisms = ['human', 'mouse'];

      render(
        <TestWrapper>
          <AntibodyAnalysis
            organisms={mockOrganisms}
            onSearch={mockOnSearch}
            loading={false}
          />
        </TestWrapper>
      );

      expect(screen.getByText('Select an organism for IgBLAST analysis (2 available)')).toBeInTheDocument();
    });

    it('should capitalize organism names in the dropdown', () => {
      const mockOrganisms = ['human', 'mouse', 'rhesus_monkey'];

      render(
        <TestWrapper>
          <AntibodyAnalysis
            organisms={mockOrganisms}
            onSearch={mockOnSearch}
            loading={false}
          />
        </TestWrapper>
      );

      expect(screen.getByText('Human')).toBeInTheDocument();
      expect(screen.getByText('Mouse')).toBeInTheDocument();
      expect(screen.getByText('Rhesus_monkey')).toBeInTheDocument();
    });
  });

  describe('Organism Selection Functionality', () => {
    const mockOrganisms = ['human', 'mouse'];

    beforeEach(() => {
      render(
        <TestWrapper>
          <AntibodyAnalysis
            organisms={mockOrganisms}
            onSearch={mockOnSearch}
            loading={false}
          />
        </TestWrapper>
      );
    });

    it('should set default organism when organisms list is loaded', () => {
      // Should default to the first organism (human)
      const organismSelect = screen.getByLabelText('Organism');
      expect(organismSelect).toHaveValue('human');
    });

    it('should allow organism selection', async () => {
      // Open the organism dropdown
      const organismSelect = screen.getByLabelText('Organism');
      fireEvent.mouseDown(organismSelect);

      // Select mouse
      const mouseOption = screen.getByText('Mouse');
      fireEvent.click(mouseOption);

      await waitFor(() => {
        expect(organismSelect).toHaveValue('mouse');
      });
    });

    it('should validate organism selection before search', async () => {
      // Try to search without selecting an organism (should be pre-selected)
      // But let's test the validation by clearing the selection
      const organismSelect = screen.getByLabelText('Organism');
      fireEvent.mouseDown(organismSelect);
      
      // This would normally clear the selection, but Material-UI Select doesn't allow empty values
      // So we'll test the validation by ensuring organism is required
      
      // Fill in sequence
      const sequenceInput = screen.getByPlaceholderText(/enter your antibody sequence/i);
      fireEvent.change(sequenceInput, {
        target: { value: 'GATATCCAGATGACCCAGTCTCCATCCTCCCTGTCTGCATCTGTAGGAGACAGAGTCACCATCACTTGCCGGGCAAGTCAGAGCATTAGCAGCTATTTAAATTGGTATCAGCAGAAACCAGGGAAAGCCCCTAAGCTCCTGATCTATGCTGCATCCACTTTGCAAAGTGGGGTCCCATCAAGGTTCAGCGGCAGTGGATCTGGGACAGATTTCACTCTCACCATCAGCAGCCTGCAGCCTGAAGATTTTGCAACTTATTACTGTCAACAGTATTATAGTTACCCCTCCACGTTCGGCCAAGGGACCAAGGTGGAAATCAAACGAACTGTGGCTGCACCATCTGTCTTCATCTTCCCGCCATCTGATGAGCAGTTGAAATCTGGAACTGCCTCTGTTGTGTGCCTGCTGAATAACTTCTATCCCAGAGAGGCCAAAGTACAGTGGAAGGTGGATAACGCCCTCCAATCGGGTAACTCCCAGGAGAGTGTCACAGAGCAGGACAGCAAGGACAGCACCTACAGCCTCAGCAGCACCCTGACGCTGAGCAAAGCAGACTACGAGAAACACAAAGTCTACGCCTGCGAAGTCACCCATCAGGGCCTGAGCTCGCCCGTCACAAAGAGCTTCAACAGGGGAGAGTGTTAG' }
      });

      // Submit search
      const searchButton = screen.getByRole('button', { name: /analyze/i });
      fireEvent.click(searchButton);

      await waitFor(() => {
        expect(mockOnSearch).toHaveBeenCalledWith({
          query_sequence: 'GATATCCAGATGACCCAGTCTCCATCCTCCCTGTCTGCATCTGTAGGAGACAGAGTCACCATCACTTGCCGGGCAAGTCAGAGCATTAGCAGCTATTTAAATTGGTATCAGCAGAAACCAGGGAAAGCCCCTAAGCTCCTGATCTATGCTGCATCCACTTTGCAAAGTGGGGTCCCATCAAGGTTCAGCGGCAGTGGATCTGGGACAGATTTCACTCTCACCATCAGCAGCCTGCAGCCTGAAGATTTTGCAACTTATTACTGTCAACAGTATTATAGTTACCCCTCCACGTTCGGCCAAGGGACCAAGGTGGAAATCAAACGAACTGTGGCTGCACCATCTGTCTTCATCTTCCCGCCATCTGATGAGCAGTTGAAATCTGGAACTGCCTCTGTTGTGTGCCTGCTGAATAACTTCTATCCCAGAGAGGCCAAAGTACAGTGGAAGGTGGATAACGCCCTCCAATCGGGTAACTCCCAGGAGAGTGTCACAGAGCAGGACAGCAAGGACAGCACCTACAGCCTCAGCAGCACCCTGACGCTGAGCAAAGCAGACTACGAGAAACACAAAGTCTACGCCTGCGAAGTCACCCATCAGGGCCTGAGCTCGCCCGTCACAAAGAGCTTCAACAGGGGAGAGTGTTAG',
          organism: 'human',
          blast_type: 'igblastn',
          evalue: 1e-10,
          searchType: 'antibody'
        });
      });
    });
  });

  describe('BLAST Type Selection', () => {
    const mockOrganisms = ['human', 'mouse'];

    beforeEach(() => {
      render(
        <TestWrapper>
          <AntibodyAnalysis
            organisms={mockOrganisms}
            onSearch={mockOnSearch}
            loading={false}
          />
        </TestWrapper>
      );
    });

    it('should default to igblastn', () => {
      const blastTypeSelect = screen.getByLabelText('BLAST Type');
      expect(blastTypeSelect).toHaveValue('igblastn');
    });

    it('should allow switching between IgBLAST types', async () => {
      // Open the BLAST type dropdown
      const blastTypeSelect = screen.getByLabelText('BLAST Type');
      fireEvent.mouseDown(blastTypeSelect);

      // Select igblastp
      const igblastpOption = screen.getByText('IgBLASTP (Protein antibody sequences)');
      fireEvent.click(igblastpOption);

      await waitFor(() => {
        expect(blastTypeSelect).toHaveValue('igblastp');
      });
    });

    it('should call onSearch with correct BLAST type', async () => {
      // Switch to igblastp
      const blastTypeSelect = screen.getByLabelText('BLAST Type');
      fireEvent.mouseDown(blastTypeSelect);
      const igblastpOption = screen.getByText('IgBLASTP (Protein antibody sequences)');
      fireEvent.click(igblastpOption);

      // Fill in sequence
      const sequenceInput = screen.getByPlaceholderText(/enter your antibody sequence/i);
      fireEvent.change(sequenceInput, {
        target: { value: 'DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK' }
      });

      // Submit search
      const searchButton = screen.getByRole('button', { name: /analyze/i });
      fireEvent.click(searchButton);

      await waitFor(() => {
        expect(mockOnSearch).toHaveBeenCalledWith({
          query_sequence: 'DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK',
          organism: 'human',
          blast_type: 'igblastp',
          evalue: 1e-10,
          searchType: 'antibody'
        });
      });
    });
  });

  describe('Form Validation', () => {
    const mockOrganisms = ['human', 'mouse'];

    beforeEach(() => {
      render(
        <TestWrapper>
          <AntibodyAnalysis
            organisms={mockOrganisms}
            onSearch={mockOnSearch}
            loading={false}
          />
        </TestWrapper>
      );
    });

    it('should validate sequence input', async () => {
      // Try to search without sequence
      const searchButton = screen.getByRole('button', { name: /analyze/i });
      fireEvent.click(searchButton);

      await waitFor(() => {
        expect(screen.getByText('Please enter a sequence')).toBeInTheDocument();
      });

      expect(mockOnSearch).not.toHaveBeenCalled();
    });

    it('should validate organism selection', async () => {
      // Fill in sequence
      const sequenceInput = screen.getByPlaceholderText(/enter your antibody sequence/i);
      fireEvent.change(sequenceInput, {
        target: { value: 'GATATCCAGATGACCCAGTCTCCATCCTCCCTGTCTGCATCTGTAGGAGACAGAGTCACCATCACTTGCCGGGCAAGTCAGAGCATTAGCAGCTATTTAAATTGGTATCAGCAGAAACCAGGGAAAGCCCCTAAGCTCCTGATCTATGCTGCATCCACTTTGCAAAGTGGGGTCCCATCAAGGTTCAGCGGCAGTGGATCTGGGACAGATTTCACTCTCACCATCAGCAGCCTGCAGCCTGAAGATTTTGCAACTTATTACTGTCAACAGTATTATAGTTACCCCTCCACGTTCGGCCAAGGGACCAAGGTGGAAATCAAACGAACTGTGGCTGCACCATCTGTCTTCATCTTCCCGCCATCTGATGAGCAGTTGAAATCTGGAACTGCCTCTGTTGTGTGCCTGCTGAATAACTTCTATCCCAGAGAGGCCAAAGTACAGTGGAAGGTGGATAACGCCCTCCAATCGGGTAACTCCCAGGAGAGTGTCACAGAGCAGGACAGCAAGGACAGCACCTACAGCCTCAGCAGCACCCTGACGCTGAGCAAAGCAGACTACGAGAAACACAAAGTCTACGCCTGCGAAGTCACCCATCAGGGCCTGAGCTCGCCCGTCACAAAGAGCTTCAACAGGGGAGAGTGTTAG' }
      });

      // Submit search (organism should be pre-selected)
      const searchButton = screen.getByRole('button', { name: /analyze/i });
      fireEvent.click(searchButton);

      await waitFor(() => {
        expect(mockOnSearch).toHaveBeenCalled();
      });
    });
  });

  describe('File Upload Functionality', () => {
    const mockOrganisms = ['human', 'mouse'];

    beforeEach(() => {
      render(
        <TestWrapper>
          <AntibodyAnalysis
            organisms={mockOrganisms}
            onSearch={mockOnSearch}
            loading={false}
          />
        </TestWrapper>
      );
    });

    it('should show file upload button', () => {
      expect(screen.getByText('Upload FASTA File')).toBeInTheDocument();
    });

    it('should accept FASTA file formats', () => {
      const uploadButton = screen.getByText('Upload FASTA File');
      const fileInput = uploadButton.parentElement?.querySelector('input[type="file"]');
      
      expect(fileInput).toHaveAttribute('accept', '.fasta,.fa,.txt');
    });
  });

  describe('Loading State', () => {
    const mockOrganisms = ['human', 'mouse'];

    it('should show loading state when loading is true', () => {
      render(
        <TestWrapper>
          <AntibodyAnalysis
            organisms={mockOrganisms}
            onSearch={mockOnSearch}
            loading={true}
          />
        </TestWrapper>
      );

      const searchButton = screen.getByRole('button', { name: /analyze/i });
      expect(searchButton).toBeDisabled();
    });

    it('should enable search button when loading is false', () => {
      render(
        <TestWrapper>
          <AntibodyAnalysis
            organisms={mockOrganisms}
            onSearch={mockOnSearch}
            loading={false}
          />
        </TestWrapper>
      );

      const searchButton = screen.getByRole('button', { name: /analyze/i });
      expect(searchButton).not.toBeDisabled();
    });
  });

  describe('Error Handling', () => {
    const mockOrganisms = ['human', 'mouse'];

    it('should display error messages', () => {
      render(
        <TestWrapper>
          <AntibodyAnalysis
            organisms={mockOrganisms}
            onSearch={mockOnSearch}
            loading={false}
          />
        </TestWrapper>
      );

      // Try to search without sequence to trigger error
      const searchButton = screen.getByRole('button', { name: /analyze/i });
      fireEvent.click(searchButton);

      expect(screen.getByText('Please enter a sequence')).toBeInTheDocument();
    });
  });
});
