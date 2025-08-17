import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { BlastSearchForm } from '../BlastSearchForm';

// Create a theme for Material-UI components
const theme = createTheme();

// Wrapper component to provide theme context
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={theme}>
    {children}
  </ThemeProvider>
);

describe('BlastSearchForm', () => {
  const mockOnSearch = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Dynamic Database Rendering', () => {
    it('should render database options from dynamic data', () => {
      const mockDatabases = {
        public: {
          swissprot: 'Swiss-Prot protein database',
          pdbaa: 'Protein Data Bank',
          '16S_ribosomal_RNA': '16S ribosomal RNA database'
        },
        custom: {
          custom_db: 'Custom database'
        },
        internal: {
          internal_protein: 'Internal protein sequences'
        }
      };

      render(
        <TestWrapper>
          <BlastSearchForm
            databases={mockDatabases}
            onSearch={mockOnSearch}
            loading={false}
          />
        </TestWrapper>
      );

      // Check that database options are rendered
      expect(screen.getByText('swissprot - Swiss-Prot protein database')).toBeInTheDocument();
      expect(screen.getByText('pdbaa - Protein Data Bank')).toBeInTheDocument();
      expect(screen.getByText('16S_ribosomal_RNA - 16S ribosomal RNA database')).toBeInTheDocument();
      expect(screen.getByText('Custom: custom_db - Custom database')).toBeInTheDocument();
      expect(screen.getByText('Internal: internal_protein - Internal protein sequences')).toBeInTheDocument();
    });

    it('should show loading state when databases are null', () => {
      render(
        <TestWrapper>
          <BlastSearchForm
            databases={null}
            onSearch={mockOnSearch}
            loading={false}
          />
        </TestWrapper>
      );

      expect(screen.getByText('Loading databases...')).toBeInTheDocument();
      expect(screen.getByText('Loading available databases...')).toBeInTheDocument();
    });

    it('should show empty state when no databases are available', () => {
      const emptyDatabases = {
        public: {},
        custom: {},
        internal: {}
      };

      render(
        <TestWrapper>
          <BlastSearchForm
            databases={emptyDatabases}
            onSearch={mockOnSearch}
            loading={false}
          />
        </TestWrapper>
      );

      expect(screen.getByText('No databases available')).toBeInTheDocument();
    });

    it('should show database count in helper text', () => {
      const mockDatabases = {
        public: {
          swissprot: 'Swiss-Prot protein database',
          pdbaa: 'Protein Data Bank'
        },
        custom: {},
        internal: {}
      };

      render(
        <TestWrapper>
          <BlastSearchForm
            databases={mockDatabases}
            onSearch={mockOnSearch}
            loading={false}
          />
        </TestWrapper>
      );

      expect(screen.getByText('Select a database to search against (2 available)')).toBeInTheDocument();
    });
  });

  describe('Single Select Database Functionality', () => {
    const mockDatabases = {
      public: {
        swissprot: 'Swiss-Prot protein database',
        pdbaa: 'Protein Data Bank'
      },
      custom: {},
      internal: {}
    };

    beforeEach(() => {
      render(
        <TestWrapper>
          <BlastSearchForm
            databases={mockDatabases}
            onSearch={mockOnSearch}
            loading={false}
          />
        </TestWrapper>
      );
    });

    it('should allow single database selection', async () => {
      // Open the database dropdown
      const databaseSelect = screen.getByLabelText('Database');
      fireEvent.mouseDown(databaseSelect);

      // Select swissprot
      const swissprotOption = screen.getByText('swissprot - Swiss-Prot protein database');
      fireEvent.click(swissprotOption);

      await waitFor(() => {
        expect(databaseSelect).toHaveValue('swissprot');
      });
    });

    it('should validate database selection before search', async () => {
      // Try to search without selecting a database
      const searchButton = screen.getByRole('button', { name: /search/i });
      fireEvent.click(searchButton);

      await waitFor(() => {
        expect(screen.getByText('Please select a database')).toBeInTheDocument();
      });

      expect(mockOnSearch).not.toHaveBeenCalled();
    });

    it('should call onSearch with selected database', async () => {
      // Select a database
      const databaseSelect = screen.getByLabelText('Database');
      fireEvent.mouseDown(databaseSelect);
      const swissprotOption = screen.getByText('swissprot - Swiss-Prot protein database');
      fireEvent.click(swissprotOption);

      // Fill in sequence
      const sequenceInput = screen.getByPlaceholderText(/enter your sequence/i);
      fireEvent.change(sequenceInput, {
        target: { value: 'DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK' }
      });

      // Submit search
      const searchButton = screen.getByRole('button', { name: /search/i });
      fireEvent.click(searchButton);

      await waitFor(() => {
        expect(mockOnSearch).toHaveBeenCalledWith({
          query_sequence: 'DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK',
          databases: ['swissprot'],
          blast_type: 'blastp',
          evalue: 1e-10,
          max_target_seqs: 10,
          searchType: 'public'
        });
      });
    });
  });

  describe('Search Type Functionality', () => {
    const mockDatabases = {
      public: {
        swissprot: 'Swiss-Prot protein database'
      },
      custom: {},
      internal: {}
    };

    beforeEach(() => {
      render(
        <TestWrapper>
          <BlastSearchForm
            databases={mockDatabases}
            onSearch={mockOnSearch}
            loading={false}
          />
        </TestWrapper>
      );
    });

    it('should show database selector only for public searches', () => {
      // Initially on public search type
      expect(screen.getByLabelText('Database')).toBeInTheDocument();

      // Switch to internal search type
      const searchTypeSelect = screen.getByLabelText('Search Type');
      fireEvent.mouseDown(searchTypeSelect);
      const internalOption = screen.getByText('Internal Database');
      fireEvent.click(internalOption);

      // Database selector should not be visible for internal searches
      expect(screen.queryByLabelText('Database')).not.toBeInTheDocument();
    });

    it('should call onSearch with correct search type', async () => {
      // Switch to internal search type
      const searchTypeSelect = screen.getByLabelText('Search Type');
      fireEvent.mouseDown(searchTypeSelect);
      const internalOption = screen.getByText('Internal Database');
      fireEvent.click(internalOption);

      // Fill in sequence
      const sequenceInput = screen.getByPlaceholderText(/enter your sequence/i);
      fireEvent.change(sequenceInput, {
        target: { value: 'DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK' }
      });

      // Submit search
      const searchButton = screen.getByRole('button', { name: /search/i });
      fireEvent.click(searchButton);

      await waitFor(() => {
        expect(mockOnSearch).toHaveBeenCalledWith({
          query_sequence: 'DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK',
          databases: [''],
          blast_type: 'blastp',
          evalue: 1e-10,
          max_target_seqs: 10,
          searchType: 'internal'
        });
      });
    });
  });

  describe('Form Validation', () => {
    const mockDatabases = {
      public: {
        swissprot: 'Swiss-Prot protein database'
      },
      custom: {},
      internal: {}
    };

    beforeEach(() => {
      render(
        <TestWrapper>
          <BlastSearchForm
            databases={mockDatabases}
            onSearch={mockOnSearch}
            loading={false}
          />
        </TestWrapper>
      );
    });

    it('should validate sequence input', async () => {
      // Try to search without sequence
      const searchButton = screen.getByRole('button', { name: /search/i });
      fireEvent.click(searchButton);

      await waitFor(() => {
        expect(screen.getByText('Please enter a sequence')).toBeInTheDocument();
      });

      expect(mockOnSearch).not.toHaveBeenCalled();
    });

    it('should validate database selection for public searches', async () => {
      // Fill in sequence but don't select database
      const sequenceInput = screen.getByPlaceholderText(/enter your sequence/i);
      fireEvent.change(sequenceInput, {
        target: { value: 'DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK' }
      });

      // Submit search
      const searchButton = screen.getByRole('button', { name: /search/i });
      fireEvent.click(searchButton);

      await waitFor(() => {
        expect(screen.getByText('Please select a database')).toBeInTheDocument();
      });

      expect(mockOnSearch).not.toHaveBeenCalled();
    });
  });

  describe('Loading State', () => {
    const mockDatabases = {
      public: {
        swissprot: 'Swiss-Prot protein database'
      },
      custom: {},
      internal: {}
    };

    it('should show loading state when loading is true', () => {
      render(
        <TestWrapper>
          <BlastSearchForm
            databases={mockDatabases}
            onSearch={mockOnSearch}
            loading={true}
          />
        </TestWrapper>
      );

      const searchButton = screen.getByRole('button', { name: /search/i });
      expect(searchButton).toBeDisabled();
    });

    it('should enable search button when loading is false', () => {
      render(
        <TestWrapper>
          <BlastSearchForm
            databases={mockDatabases}
            onSearch={mockOnSearch}
            loading={false}
          />
        </TestWrapper>
      );

      const searchButton = screen.getByRole('button', { name: /search/i });
      expect(searchButton).not.toBeDisabled();
    });
  });
});
