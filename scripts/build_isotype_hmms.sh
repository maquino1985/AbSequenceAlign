#!/bin/bash
# Build HMM profiles for human antibody isotype constant regions
# Requirements: wget/curl, mafft, hmmbuild (HMMER)
# Output: data/isotype_hmms/*.hmm

set -e

# Create output directories
mkdir -p data/isotype_fastas data/isotype_msas data/isotype_hmms

# List of isotypes and their IMGT accession numbers (curated, human)
declare -A ISOTYPE_URLS=(
  [IGHG1]="https://www.uniprot.org/uniprotkb/P01857.fasta"
  [IGHG2]="https://www.uniprot.org/uniprotkb/P01859.fasta"
  [IGHG3]="https://www.uniprot.org/uniprotkb/P01860.fasta"
  [IGHG4]="https://www.uniprot.org/uniprotkb/P01861.fasta"
  [IGHA1]="https://www.uniprot.org/uniprotkb/P01876.fasta"
  [IGHA2]="https://www.uniprot.org/uniprotkb/P01877.fasta"
  [IGHE]="https://www.uniprot.org/uniprotkb/P01854.fasta"
  [IGHD]="https://www.uniprot.org/uniprotkb/P01880.fasta"
  [IGHM]="https://www.uniprot.org/uniprotkb/P01871.fasta"
)

# Download FASTA sequences for each isotype
for iso in "${!ISOTYPE_URLS[@]}"; do
  url="${ISOTYPE_URLS[$iso]}"
  fasta="data/isotype_fastas/${iso}.fasta"
  if [ ! -f "$fasta" ]; then
    echo "Downloading $iso sequence..."
    curl -sSL "$url" -o "$fasta"
  fi
  # For demonstration, you may want to add more alleles per isotype for a better HMM
  # (e.g., from IMGT or NCBI RefSeq)
done

# Align each isotype FASTA with MAFFT
for fasta in data/isotype_fastas/*.fasta; do
  msa="data/isotype_msas/$(basename "$fasta" .fasta).aln.fasta"
  if [ ! -f "$msa" ]; then
    echo "Aligning $(basename "$fasta") with MAFFT..."
    mafft --auto "$fasta" > "$msa"
  fi
done

# Build HMMs with hmmbuild
for msa in data/isotype_msas/*.aln.fasta; do
  hmm="data/isotype_hmms/$(basename "$msa" .aln.fasta).hmm"
  if [ ! -f "$hmm" ]; then
    echo "Building HMM for $(basename "$msa" .aln.fasta)..."
    hmmbuild "$hmm" "$msa"
  fi
done

echo "All isotype HMMs built in data/isotype_hmms/"

