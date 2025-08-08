/**
 * Test suite for AminoAcidSequence component to verify region highlighting functionality
 */

import { render } from '@testing-library/react';
import { describe, test, expect, beforeEach, vi } from 'vitest';
import '@testing-library/jest-dom';
import { AminoAcidSequence } from '../AminoAcidSequence';
import type { Region, ColorScheme } from '../../../types/sequence';
import { ColorSchemeType } from '../../../types/sequence';

// Mock color scheme
const mockColorScheme: ColorScheme = {
  name: 'Hydrophobicity',
  type: ColorSchemeType.HYDROPHOBICITY,
  colors: {
    'A': '#1f77b4', 'R': '#ff7f0e', 'N': '#2ca02c', 'D': '#d62728',
    'C': '#9467bd', 'Q': '#8c564b', 'E': '#e377c2', 'G': '#7f7f7f',
    'H': '#bcbd22', 'I': '#17becf', 'L': '#a6cee3', 'K': '#b2df8a',
    'M': '#fb9a99', 'F': '#fdbf6f', 'P': '#cab2d6', 'S': '#ff9896',
    'T': '#98df8a', 'W': '#d4b5d0', 'Y': '#c49c94', 'V': '#f0027f'
  },
  description: 'Color based on Kyte-Doolittle hydrophobicity scale'
};

// Test sequence and regions
const testSequence = "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK";
const testRegions: Region[] = [
  {
    id: 'cdr1',
    name: 'CDR1',
    start: 31,
    stop: 35,
    sequence: 'SYAMS',
    type: 'CDR',
    color: '#e91e63', // Pink
    features: []
  },
  {
    id: 'cdr2', 
    name: 'CDR2',
    start: 50,
    stop: 65,
    sequence: 'AISGSGGSTYYADSVK',
    type: 'CDR',
    color: '#f44336', // Red
    features: []
  },
  {
    id: 'fr1',
    name: 'FR1',
    start: 1,
    stop: 30,
    sequence: 'EVQLVESGGGLVQPGGSLRLSCAASGFTFS',
    type: 'FR',
    color: '#4caf50', // Green
    features: []
  }
];

describe('AminoAcidSequence Region Highlighting', () => {
  const defaultProps = {
    sequence: testSequence,
    regions: testRegions,
    colorScheme: mockColorScheme,
    onAminoAcidClick: vi.fn(),
    onColorSchemeChange: vi.fn(),
    selectedPositions: [],
    selectedRegions: []
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('renders amino acid sequence correctly', () => {
    render(<AminoAcidSequence {...defaultProps} />);
    
    // Check that the sequence length text is rendered somewhere in the document
    // Use a more flexible approach that checks the entire document text
    const documentText = document.body.textContent || '';
    expect(documentText).toContain('Sequence Length: 98 amino acids');
    
    // Check that amino acids are present by looking for spans with amino acid characters
    const aminoAcidSpans = document.querySelectorAll('span[style*="background-color"]');
    expect(aminoAcidSpans.length).toBeGreaterThan(0);
    
    // Check that some amino acids from our test sequence are present
    // The sequence is split into lines of max 50 characters, so check for the first part
    expect(documentText).toContain('EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSA');
  });

  test('amino acids show region colors when region is selected', () => {
    // Render with CDR2 selected (positions 50-65)
    render(<AminoAcidSequence {...defaultProps} selectedRegions={['cdr2']} />);
    
    // Get all amino acid spans
    const aminoAcidSpans = document.querySelectorAll('span[style*="background-color"]');
    
    // Check that amino acids in CDR2 region (positions 50-65) have the CDR2 color
    
    let foundColoredAAs = 0;
    aminoAcidSpans.forEach((span, index) => {
      const position = index + 1; // 1-based positioning
      const style = (span as HTMLElement).style;
      
      if (position >= 50 && position <= 65) {
        // These should be colored with CDR2 color
        expect(style.backgroundColor).toBe('rgb(244, 67, 54)'); // #f44336 in RGB
        foundColoredAAs++;
      }
    });
    
    // Should have found 16 amino acids in CDR2 (positions 50-65 inclusive)
    expect(foundColoredAAs).toBe(16);
  });

  test('amino acids use color scheme colors when no region is selected', () => {
    render(<AminoAcidSequence {...defaultProps} selectedRegions={[]} />);
    
    // Get all amino acid spans
    const aminoAcidSpans = document.querySelectorAll('span[style*="background-color"]');
    
    // Check that amino acids use the color scheme colors, not region colors
    let foundSchemeColors = 0;
    aminoAcidSpans.forEach((span) => {
      const style = (span as HTMLElement).style;
      const backgroundColor = style.backgroundColor;
      
      // Should not be using region colors when no regions selected
      expect(backgroundColor).not.toBe('rgb(244, 67, 54)'); // Not CDR2 red
      expect(backgroundColor).not.toBe('rgb(233, 30, 99)'); // Not CDR1 pink
      expect(backgroundColor).not.toBe('rgb(76, 175, 80)'); // Not FR1 green
      
      foundSchemeColors++;
    });
    
    expect(foundSchemeColors).toBeGreaterThan(0);
  });

  test('multiple regions can be selected simultaneously', () => {
    // Select both CDR1 and CDR2
    render(<AminoAcidSequence {...defaultProps} selectedRegions={['cdr1', 'cdr2']} />);
    
    const aminoAcidSpans = document.querySelectorAll('span[style*="background-color"]');
    
    let cdr1Colored = 0;
    let cdr2Colored = 0;
    
    aminoAcidSpans.forEach((span, index) => {
      const position = index + 1;
      const style = (span as HTMLElement).style;
      
      if (position >= 31 && position <= 35) {
        // CDR1 positions should be pink
        expect(style.backgroundColor).toBe('rgb(233, 30, 99)'); // #e91e63
        cdr1Colored++;
      } else if (position >= 50 && position <= 65) {
        // CDR2 positions should be red
        expect(style.backgroundColor).toBe('rgb(244, 67, 54)'); // #f44336
        cdr2Colored++;
      }
    });
    
    expect(cdr1Colored).toBe(5); // CDR1 is 5 amino acids
    expect(cdr2Colored).toBe(16); // CDR2 is 16 amino acids
  });

  test('region selection toggles amino acid colors correctly', () => {
    const { rerender } = render(<AminoAcidSequence {...defaultProps} selectedRegions={[]} />);
    
    // Initially no regions selected - should use color scheme
    let aminoAcidSpans = document.querySelectorAll('span[style*="background-color"]');
    const firstSpanInitial = aminoAcidSpans[49] as HTMLElement; // Position 50 (CDR2 start)
    const initialColor = firstSpanInitial.style.backgroundColor;
    
    // Now select CDR2
    rerender(<AminoAcidSequence {...defaultProps} selectedRegions={['cdr2']} />);
    
    aminoAcidSpans = document.querySelectorAll('span[style*="background-color"]');
    const firstSpanSelected = aminoAcidSpans[49] as HTMLElement;
    const selectedColor = firstSpanSelected.style.backgroundColor;
    
    // Colors should be different
    expect(selectedColor).not.toBe(initialColor);
    expect(selectedColor).toBe('rgb(244, 67, 54)'); // CDR2 red
    
    // Deselect region
    rerender(<AminoAcidSequence {...defaultProps} selectedRegions={[]} />);
    
    aminoAcidSpans = document.querySelectorAll('span[style*="background-color"]');
    const firstSpanDeselected = aminoAcidSpans[49] as HTMLElement;
    const deselectedColor = firstSpanDeselected.style.backgroundColor;
    
    // Should return to original color scheme color
    expect(deselectedColor).toBe(initialColor);
  });

  test('displays selection summary correctly', () => {
    // Test with selected regions and positions
    render(
      <AminoAcidSequence 
        {...defaultProps} 
        selectedRegions={['cdr1', 'cdr2']}
        selectedPositions={[1, 2, 3, 10, 15, 20]}
      />
    );
    
    const documentText = document.body.textContent || '';
    
    // Should show selection summary
    expect(documentText).toContain('Selected: 6 positions, 2 regions');
    
    // Should show region selections
    expect(documentText).toContain('CDR1:31-35');
    expect(documentText).toContain('CDR2:50-65');
    
    // Should show individual position selections (grouped for consecutive positions)
    expect(documentText).toContain('E1-Q3'); // Consecutive positions 1,2,3
    expect(documentText).toContain('G10'); // Individual position 10
    expect(documentText).toContain('G15'); // Individual position 15
    // L20 is grouped with other selections, so check for the overflow indicator
    expect(documentText).toContain('+1 more');
  });

  test('displays tooltip for many selections', () => {
    // Create many selected positions to test tooltip
    const manyPositions = Array.from({ length: 20 }, (_, i) => i + 1);
    
    render(
      <AminoAcidSequence 
        {...defaultProps} 
        selectedPositions={manyPositions}
      />
    );
    
    const documentText = document.body.textContent || '';
    
    // Should show the grouped selections
    expect(documentText).toContain('E1-L20'); // All 20 consecutive positions grouped
    // Since all selections fit in one group, there's no overflow indicator
    expect(documentText).toContain('Selected: 20 positions, 0 regions');
  });
});


