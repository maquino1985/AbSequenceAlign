// FASTA parsing utilities

export interface FastaSequence {
  id: string;
  description?: string;
  sequence: string;
}

export const parseFasta = (fastaContent: string): FastaSequence[] => {
  const sequences: FastaSequence[] = [];
  const lines = fastaContent.trim().split('\n');
  
  let currentSequence: FastaSequence | null = null;
  
  for (const line of lines) {
    const trimmedLine = line.trim();
    
    if (trimmedLine.startsWith('>')) {
      // Save previous sequence if exists
      if (currentSequence) {
        sequences.push(currentSequence);
      }
      
      // Start new sequence
      const headerParts = trimmedLine.substring(1).split(' ');
      const id = headerParts[0] || `seq_${sequences.length + 1}`;
      const description = headerParts.slice(1).join(' ') || undefined;
      
      currentSequence = {
        id,
        description,
        sequence: ''
      };
    } else if (trimmedLine && currentSequence) {
      // Add to current sequence
      currentSequence.sequence += trimmedLine;
    }
  }
  
  // Add the last sequence
  if (currentSequence) {
    sequences.push(currentSequence);
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
