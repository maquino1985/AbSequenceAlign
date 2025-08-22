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

      // Open the organism dropdown to see options
      const organismSelect = screen.getByLabelText('Organism');
      fireEvent.mouseDown(organismSelect);

      // Check that organism options are rendered in the dropdown
      expect(screen.getByRole('option', { name: 'Human' })).toBeInTheDocument();
      expect(screen.getByRole('option', { name: 'Mouse' })).toBeInTheDocument();
      expect(screen.getByRole('option', { name: 'Rat' })).toBeInTheDocument();
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

      // Note: The Select MenuItem text might not be accessible when disabled, so we check the FormHelperText
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

      // Open the organism dropdown to see options
      const organismSelect = screen.getByLabelText('Organism');
      fireEvent.mouseDown(organismSelect);

      expect(screen.getByRole('option', { name: 'Human' })).toBeInTheDocument();
      expect(screen.getByRole('option', { name: 'Mouse' })).toBeInTheDocument();
      expect(screen.getByRole('option', { name: 'Rhesus_monkey' })).toBeInTheDocument();
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
      // Check the hidden input value instead of the select element
      const hiddenInput = organismSelect.querySelector('input[type="hidden"]') || 
                         organismSelect.parentElement?.querySelector('input.MuiSelect-nativeInput');
      expect(hiddenInput).toHaveValue('human');
    });

    it('should allow organism selection', async () => {
      // Open the organism dropdown
      const organismSelect = screen.getByLabelText('Organism');
      fireEvent.mouseDown(organismSelect);

      // Select mouse
      const mouseOption = screen.getByText('Mouse');
      fireEvent.click(mouseOption);

      await waitFor(() => {
        // Check the hidden input value instead of the select element
        const hiddenInput = organismSelect.querySelector('input[type="hidden"]') || 
                           organismSelect.parentElement?.querySelector('input.MuiSelect-nativeInput');
        expect(hiddenInput).toHaveValue('mouse');
      });
    });

    it('should validate organism selection before search', async () => {
      // Fill in sequence
      const sequenceInput = screen.getByPlaceholderText(/enter your antibody sequence/i);
      fireEvent.change(sequenceInput, {
        target: { value: 'GATATCCAGATGACCCAGTCTCCATCCTCCCTGTCTGCATCTGTAGGAGACAGAGTCACCATCACTTGCCGGGCAAGTCAGAGCATTAGCAGCTATTTAAATTGGTATCAGCAGAAACCAGGGAAAGCCCCTAAGCTCCTGATCTATGCTGCATCCACTTTGCAAAGTGGGGTCCCATCAAGGTTCAGCGGCAGTGGATCTGGGACAGATTTCACTCTCACCATCAGCAGCCTGCAGCCTGAAGATTTTGCAACTTATTACTGTCAACAGTATTATAGTTACCCCTCCACGTTCGGCCAAGGGACCAAGGTGGAAATCAAACGAACTGTGGCTGCACCATCTGTCTTCATCTTCCCGCCATCTGATGAGCAGTTGAAATCTGGAACTGCCTCTGTTGTGTGCCTGCTGAATAACTTCTATCCCAGAGAGGCCAAAGTACAGTGGAAGGTGGATAACGCCCTCCAATCGGGTAACTCCCAGGAGAGTGTCACAGAGCAGGACAGCAAGGACAGCACCTACAGCCTCAGCAGCACCCTGACGCTGAGCAAAGCAGACTACGAGAAACACAAAGTCTACGCCTGCGAAGTCACCCATCAGGGCCTGAGCTCGCCCGTCACAAAGAGCTTCAACAGGGGAGAGTGTTAG' }
      });

      // Submit search
      const searchButton = screen.getByRole('button', { name: /run antibody analysis/i });
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
      // Check the hidden input value instead of the select element
      const hiddenInput = blastTypeSelect.querySelector('input[type="hidden"]') || 
                         blastTypeSelect.parentElement?.querySelector('input.MuiSelect-nativeInput');
      expect(hiddenInput).toHaveValue('igblastn');
    });

    it('should allow switching between IgBLAST types', async () => {
      // Open the BLAST type dropdown
      const blastTypeSelect = screen.getByLabelText('BLAST Type');
      fireEvent.mouseDown(blastTypeSelect);

      // Select igblastp
      const igblastpOption = screen.getByText('IgBLASTP (Protein antibody sequences)');
      fireEvent.click(igblastpOption);

      await waitFor(() => {
        // Check the hidden input value instead of the select element
        const hiddenInput = blastTypeSelect.querySelector('input[type="hidden"]') || 
                           blastTypeSelect.parentElement?.querySelector('input.MuiSelect-nativeInput');
        expect(hiddenInput).toHaveValue('igblastp');
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
      const searchButton = screen.getByRole('button', { name: /run antibody analysis/i });
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
      const searchButton = screen.getByRole('button', { name: /run antibody analysis/i });
      fireEvent.click(searchButton);

      await waitFor(() => {
        expect(screen.getByText(/Antibody sequence validation failed: Sequence cannot be empty/)).toBeInTheDocument();
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
      const searchButton = screen.getByRole('button', { name: /run antibody analysis/i });
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

      const searchButton = screen.getByRole('button', { name: /analyzing/i });
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

      const searchButton = screen.getByRole('button', { name: /run antibody analysis/i });
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
      const searchButton = screen.getByRole('button', { name: /run antibody analysis/i });
      fireEvent.click(searchButton);

      expect(screen.getByText(/Antibody sequence validation failed: Sequence cannot be empty/)).toBeInTheDocument();
    });
  });
});
