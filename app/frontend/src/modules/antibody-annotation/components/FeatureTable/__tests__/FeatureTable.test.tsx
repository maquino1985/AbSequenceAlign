import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { vi } from 'vitest';
import { FeatureTable } from '../FeatureTable';
import type { Region } from '../../../../../types/sequence';

describe('FeatureTable', () => {
  const mockRegions: Region[] = [
    {
      id: 'seq1_FR1',
      name: 'FR1',
      start: 1,
      stop: 25,
      sequence: 'EVQLVESGGGLVQPGGSLRLSCAAS',
      type: 'FR',
      color: '#FF6B6B',
      features: []
    },
    {
      id: 'seq1_CDR1',
      name: 'CDR1',
      start: 26,
      stop: 33,
      sequence: 'GFTFSSYA',
      type: 'CDR',
      color: '#4ECDC4',
      features: []
    },
    {
      id: 'seq1_CONSTANT',
      name: 'CH1',
      start: 120,
      stop: 220,
      sequence: 'ASTKGPSVFPLAPSSKSTSGGTAALGCLVKDYFPEPVTVSWNSGALTSGVHTFPAVLQSSGLYSLSSVVTVPSSSLGTQTYICNVNHKPSNTKVDKKV',
      type: 'CONSTANT',
      color: '#45B7D1',
      features: [],
      details: {
        isotype: 'IGHG1',
        domain_type: 'C'
      }
    },
    {
      id: 'seq1_LINKER',
      name: 'LINKER1',
      start: 110,
      stop: 119,
      sequence: 'GGGGSGGGGG',
      type: 'LINKER',
      color: '#CCCCCC',
      features: [],
      details: {
        preceding_linker: {
          sequence: 'GGGGSGGGGG',
          start: 110,
          end: 119
        }
      }
    }
  ];

  const mockOnRegionSelect = vi.fn();

  beforeEach(() => {
    mockOnRegionSelect.mockClear();
  });

  it('renders empty state when no regions provided', () => {
    render(
      <FeatureTable
        regions={[]}
        selectedRegions={[]}
        onRegionSelect={mockOnRegionSelect}
      />
    );

    expect(screen.getByText(/No regions to display/i)).toBeInTheDocument();
  });

  it('renders all regions with correct information', () => {
    render(
      <FeatureTable
        regions={mockRegions}
        selectedRegions={[]}
        onRegionSelect={mockOnRegionSelect}
      />
    );

    // Check region names
    expect(screen.getByText('FR1')).toBeInTheDocument();
    expect(screen.getByText('CDR1')).toBeInTheDocument();
    expect(screen.getByText('CH1')).toBeInTheDocument();
    expect(screen.getByText('LINKER1')).toBeInTheDocument();

    // Check region types
    expect(screen.getByText('FR')).toBeInTheDocument();
    expect(screen.getByText('CDR')).toBeInTheDocument();
    expect(screen.getByText('CONSTANT')).toBeInTheDocument();
    expect(screen.getByText('LINKER')).toBeInTheDocument();

    // Check sequences
    expect(screen.getByText('EVQLVESGGGLVQPGGSLRLSCAAS')).toBeInTheDocument();
    expect(screen.getByText('GFTFSSYA')).toBeInTheDocument();
    expect(screen.getByText('GGGGSGGGGG')).toBeInTheDocument();
  });

  it('displays constant region details', () => {
    render(
      <FeatureTable
        regions={mockRegions}
        selectedRegions={[]}
        onRegionSelect={mockOnRegionSelect}
      />
    );

    expect(screen.getByText('Isotype: IGHG1')).toBeInTheDocument();
    expect(screen.getByText('Domain: C')).toBeInTheDocument();
  });

  it('displays linker details', () => {
    render(
      <FeatureTable
        regions={mockRegions}
        selectedRegions={[]}
        onRegionSelect={mockOnRegionSelect}
      />
    );

    expect(screen.getByText('Linker: 10 aa')).toBeInTheDocument();
  });

  it('handles region selection', () => {
    render(
      <FeatureTable
        regions={mockRegions}
        selectedRegions={[]}
        onRegionSelect={mockOnRegionSelect}
      />
    );

    // Click on FR1 row
    fireEvent.click(screen.getByText('FR1'));
    expect(mockOnRegionSelect).toHaveBeenCalledWith('seq1_FR1');

    // Click on CDR1 row
    fireEvent.click(screen.getByText('CDR1'));
    expect(mockOnRegionSelect).toHaveBeenCalledWith('seq1_CDR1');
  });

  it('highlights selected regions', () => {
    render(
      <FeatureTable
        regions={mockRegions}
        selectedRegions={['seq1_FR1']}
        onRegionSelect={mockOnRegionSelect}
      />
    );

    // Find the FR1 row and check its background color
    const fr1Row = screen.getByText('FR1').closest('tr');
    expect(fr1Row).toHaveStyle({ backgroundColor: 'rgba(25, 118, 210, 0.08)' });
  });
});
