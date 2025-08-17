// FASTA parsing utilities

export interface FastaSequence {
  id: string;
  description?: string;
  sequence: string;
}

export const parseFasta = (fastaContent: string): FastaSequence[] => {
  if (!fastaContent || fastaContent.trim().length === 0) {
    throw new Error('Empty FASTA content provided');
  }

  const sequences: FastaSequence[] = [];
  const lines = fastaContent.trim().split(/\r?\n/); // Handle both Unix and Windows line endings
  
  let currentSequence: FastaSequence | null = null;
  let lineNumber = 0;
  
  for (const line of lines) {
    lineNumber++;
    const trimmedLine = line.trim();
    
    // Skip empty lines
    if (!trimmedLine) {
      continue;
    }
    
    if (trimmedLine.startsWith('>')) {
      // Save previous sequence if exists
      if (currentSequence) {
        if (!currentSequence.sequence) {
          throw new Error(`Sequence "${currentSequence.id}" has no sequence data (line ${lineNumber - 1})`);
        }
        sequences.push(currentSequence);
      }
      
      // Start new sequence
      const headerContent = trimmedLine.substring(1).trim();
      if (!headerContent) {
        throw new Error(`Empty header found at line ${lineNumber}`);
      }
      
      const headerParts = headerContent.split(/\s+/);
      const id = headerParts[0] || `seq_${sequences.length + 1}`;
      const description = headerParts.slice(1).join(' ') || undefined;
      
      currentSequence = {
        id,
        description,
        sequence: ''
      };
    } else if (currentSequence) {
      // Validate sequence line contains only valid characters
      const cleanLine = trimmedLine.replace(/\s/g, '').toUpperCase();
      const validAminoAcids = /^[ACDEFGHIKLMNPQRSTVWY]+$/;
      
      if (!validAminoAcids.test(cleanLine)) {
        const invalidChars = [...cleanLine].filter(char => !/[ACDEFGHIKLMNPQRSTVWY]/.test(char));
        throw new Error(`Invalid amino acids found in sequence "${currentSequence.id}" at line ${lineNumber}: ${[...new Set(invalidChars)].join(', ')}`);
      }
      
      // Add to current sequence
      currentSequence.sequence += cleanLine;
    } else {
      throw new Error(`Sequence data found without header at line ${lineNumber}: "${trimmedLine}"`);
    }
  }
  
  // Add the last sequence
  if (currentSequence) {
    if (!currentSequence.sequence) {
      throw new Error(`Sequence "${currentSequence.id}" has no sequence data`);
    }
    sequences.push(currentSequence);
  }
  
  if (sequences.length === 0) {
    throw new Error('No valid sequences found in FASTA content');
  }
  
  return sequences;
};

export const generateFasta = (sequences: FastaSequence[]): string => {
  return sequences
    .map(seq => {
      const header = seq.description 
        ? `>${seq.id} ${seq.description}`
        : `>${seq.id}`;
      return `${header}\n${seq.sequence}`;
    })
    .join('\n\n');
};

export const validateSequence = (sequence: string): { isValid: boolean; errors: string[] } => {
  const errors: string[] = [];
  
  // Check for empty sequence
  if (!sequence.trim()) {
    errors.push('Sequence cannot be empty');
    return { isValid: false, errors };
  }
  
  // Clean sequence
  const cleanSeq = sequence.replace(/\s/g, '').toUpperCase();
  
  // Check for valid amino acids
  const validAminoAcids = new Set('ACDEFGHIKLMNPQRSTVWY');
  const invalidChars = [...cleanSeq].filter(char => !validAminoAcids.has(char));
  
  if (invalidChars.length > 0) {
    errors.push(`Invalid amino acids found: ${[...new Set(invalidChars)].join(', ')}`);
  }
  
  // Check minimum length
  if (cleanSeq.length < 15) {
    errors.push(`Sequence too short (${cleanSeq.length} AA). Minimum 15 AA required.`);
  }
  
  return { isValid: errors.length === 0, errors };
};
