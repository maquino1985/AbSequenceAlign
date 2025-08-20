#!/usr/bin/env python3

import sys
import os
sys.path.append('/Users/aquinmx3/repos/AbSequenceAlign/app/backend')
os.chdir('/Users/aquinmx3/repos/AbSequenceAlign/app/backend')

from infrastructure.adapters.tabular_parser import TabularParser

# Sample IgBLAST output (from manual command)
test_output = """# IGBLASTN
# Query: query
# Database: /data/databases/human/V/airr_c_human_ig.V /data/databases/human/D/airr_c_human_igh.D /data/databases/human/J/airr_c_human_ig.J
# Domain classification requested: imgt

# V-(D)-J rearrangement summary for query sequence (Top V gene match, Top J gene match, Chain type, stop codon, V-J frame, Productive, Strand, V Frame shift).  Multiple equivalent top matches, if present, are separated by a comma.

IGKV1-27*02	IGKJ2*01	VK	No	In-frame	Yes	+	No

# V-(D)-J junction details based on top germline gene matches (V end, V-J junction, J start).  Note that possible overlapping nucleotides at VDJ junction (i.e, nucleotides that could be assigned to either rearranging gene) are indicated in parentheses (i.e., (TACT)) but are not included under the V, D, or J gene itself

GCGCC	N/A	GTATA

# Sub-region sequence details (nucleotide sequence, translation, start, end)
CDR3	CAGCGCTATAACCGCGCGCCGTATACC	QRYNRAPYT	265	291

# Alignment summary between query and top germline V gene hit (from, to, length, matches, mismatches, gaps, percent identity)
FR1-IMGT	1	78	78	51	27	0	65.4
CDR1-IMGT	79	96	18	16	2	0	88.9
FR2-IMGT	97	147	51	40	11	0	78.4
CDR2-IMGT	148	156	9	5	4	0	55.6
FR3-IMGT	157	264	108	76	32	0	70.4
CDR3-IMGT (germline)	265	284	20	13	7	0	65
Total	N/A	N/A	284	201	83	0	70.8

# Hit table (the first field indicates the chain type of the hit)
# Fields: query id, subject id, % identity, alignment length, mismatches, gap opens, gaps, q. start, q. end, s. start, s. end, evalue, bit score
# 6 hits found
V	query	IGKV1-27*02	70.775	284	83	0	0	1	284	1	284	7.06e-49	185
V	query	IGKV1-27*01	70.423	284	84	0	0	1	284	1	284	6.12e-48	182
V	query	IGKV1-16*02	70.182	275	82	0	0	1	275	1	275	1.35e-45	174
J	query	IGKJ2*01	81.579	38	7	0	0	285	322	2	39	4.17e-05	33.4
J	query	IGKJ2*03	83.871	31	5	0	0	292	322	9	39	1.58e-04	31.5
J	query	IGKJ2*04	83.871	31	5	0	0	292	322	9	39	1.58e-04	31.5

Total queries = 1
Total identifiable CDR3 = 1
Total unique clonotypes = 1

# BLAST processed 1 queries"""

query_sequence = "gatattcagatgacccagagcccgagcagcctgagcgcgagcgtgggcgatcgcgtgaccattacctgccgcgcgagccagggcattcgcaactatctggcgtggtatcagcagaaaccgggcaaagcgccgaaactgctgatttatgcggcgagcagcctgcagagcggcgtgccgagccgctttagcggcagcggcagcggcaccgattttaccctgaccattagcagcctgcagccggaagatgtggcgacctattattgccagcgctataaccgcgcgccgtatacctttggccagggcaccaaagtggaaattaaacgcaccgtggcggcgccgagcgtgtttatttttccgccgagcgatgaacagctgaaaagcggcaccgcgagcgtggtgtgcctgctgaacaacttttatccgcgcgaagcgaaagtgcagtggaaagtgaacgcgctgcagagcggcaacagccaggaaagcgtgaccgaacaggatagcaaagatagcacctatagcctgagcagcaccctgaccctgagcaaagcggattatgaaaaacataaagtgtatgcgtgcgaagtgacccatcagggcctgagcagcccggtgaccaaaagctttaaccgcggcgaatgc"

parser = TabularParser()
result = parser.parse(test_output, 'igblastn', query_sequence)

print("Analysis Summary Keys:", list(result['analysis_summary'].keys()))
print("\nFramework/CDR Data:")
for key, value in result['analysis_summary'].items():
    if 'fr' in key.lower() or 'cdr' in key.lower():
        print(f"  {key}: {value}")

print(f"\nTotal analysis_summary fields: {len(result['analysis_summary'])}")
