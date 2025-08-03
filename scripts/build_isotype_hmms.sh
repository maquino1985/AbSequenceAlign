#!/bin/bash
# Build HMM profiles for human antibody isotype constant regions
# Requirements: wget/curl, mafft, hmmbuild (HMMER)
# Output: data/isotype_hmms/*.hmm

set -e

# Create output directories
mkdir -p data/isotype_fastas data/isotype_msas data/isotype_hmms

# List of IMGT FTP URLs for all human constant region alleles per isotype
IMGT_BASE="https://www.imgt.org/download/GENE-DB/IMGTGENEDB-GENE-ALLELE-ProteinSequences/Homo_sapiens"
declare -A ISOTYPE_IMGT_FILES=(
  [IGHG1]="IGHG1_prot.fa"
  [IGHG2]="IGHG2_prot.fa"
  [IGHG3]="IGHG3_prot.fa"
  [IGHG4]="IGHG4_prot.fa"
  [IGHA1]="IGHA1_prot.fa"
  [IGHA2]="IGHA2_prot.fa"
  [IGHE]="IGHE_prot.fa"
  [IGHD]="IGHD_prot.fa"
  [IGHM]="IGHM_prot.fa"
)

# Skip downloading if data/isotype_fastas directory exists
if [ -d "data/isotype_fastas" ]; then
  echo "data/isotype_fastas directory exists, skipping download."
else
  # Download FASTA sequences for each isotype from IMGT (all alleles)
  for iso in "${!ISOTYPE_IMGT_FILES[@]}"; do
    imgt_file="${ISOTYPE_IMGT_FILES[$iso]}"
    url="$IMGT_BASE/$imgt_file"
    fasta="data/isotype_fastas/${iso}.fasta"
    if [ ! -f "$fasta" ]; then
      echo "Downloading $iso alleles from IMGT..."
      curl -sSL "$url" -o "$fasta"
    fi
  done
fi

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
