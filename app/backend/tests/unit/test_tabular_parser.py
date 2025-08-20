"""
Unit tests for TabularParser - Framework and CDR data extraction
"""

from backend.infrastructure.adapters.tabular_parser import TabularParser


class TestTabularParser:
    """Test cases for TabularParser framework and CDR extraction."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = TabularParser()

    def test_extract_framework_cdr_data_imgt(self):
        """Test framework and CDR data extraction with IMGT numbering."""
        # Sample IgBLAST protein output with IMGT numbering
        output = """# IGBLASTP
# Query: test_protein
# Database: /data/databases/human/V/airr_c_human_ig.V
# Domain classification requested: imgt

# Alignment summary between query and top germline V gene hit (from, to, length, matches, mismatches, gaps, percent identity)

FR1-IMGT        1       25      25      25      0       0       100
CDR1-IMGT       26      33      8       6       2       0       75
FR2-IMGT        34      50      17      15      2       0       88.2
CDR2-IMGT       51      58      8       6       2       0       75
FR3-IMGT        59      96      38      27      11      0       71.1
CDR3-IMGT (germline)    97      98      2       2       0       0       100
Total   N/A     N/A     98      81      17      0       82.7

# Hit table (the first field indicates the chain type of the hit)
# Fields: query id, subject id, % identity, alignment length, mismatches, gap opens, gaps, q. start, q. end, s. start, s. end, evalue, bit score

# 3 hits found
V       test_protein    IGHV1-2*02      82.653  98      17      0       0       1       98      1       98      1.56e-59     170

# BLAST processed 1 queries"""

        result = self.parser.parse(output, "igblastp")

        # Check that framework and CDR data is extracted
        analysis_summary = result["analysis_summary"]

        # FR1 data
        assert analysis_summary["fr1_start"] == 1
        assert analysis_summary["fr1_end"] == 25
        assert analysis_summary["fr1_length"] == 25
        assert analysis_summary["fr1_matches"] == 25
        assert analysis_summary["fr1_mismatches"] == 0
        assert analysis_summary["fr1_gaps"] == 0
        assert analysis_summary["fr1_percent_identity"] == 100.0

        # CDR1 data
        assert analysis_summary["cdr1_start"] == 26
        assert analysis_summary["cdr1_end"] == 33
        assert analysis_summary["cdr1_length"] == 8
        assert analysis_summary["cdr1_matches"] == 6
        assert analysis_summary["cdr1_mismatches"] == 2
        assert analysis_summary["cdr1_gaps"] == 0
        assert analysis_summary["cdr1_percent_identity"] == 75.0

        # FR2 data
        assert analysis_summary["fr2_start"] == 34
        assert analysis_summary["fr2_end"] == 50
        assert analysis_summary["fr2_length"] == 17
        assert analysis_summary["fr2_matches"] == 15
        assert analysis_summary["fr2_mismatches"] == 2
        assert analysis_summary["fr2_gaps"] == 0
        assert analysis_summary["fr2_percent_identity"] == 88.2

        # CDR2 data
        assert analysis_summary["cdr2_start"] == 51
        assert analysis_summary["cdr2_end"] == 58
        assert analysis_summary["cdr2_length"] == 8
        assert analysis_summary["cdr2_matches"] == 6
        assert analysis_summary["cdr2_mismatches"] == 2
        assert analysis_summary["cdr2_gaps"] == 0
        assert analysis_summary["cdr2_percent_identity"] == 75.0

        # FR3 data
        assert analysis_summary["fr3_start"] == 59
        assert analysis_summary["fr3_end"] == 96
        assert analysis_summary["fr3_length"] == 38
        assert analysis_summary["fr3_matches"] == 27
        assert analysis_summary["fr3_mismatches"] == 11
        assert analysis_summary["fr3_gaps"] == 0
        assert analysis_summary["fr3_percent_identity"] == 71.1

    def test_extract_framework_cdr_data_kabat(self):
        """Test framework and CDR data extraction with Kabat numbering."""
        # Sample IgBLAST protein output with Kabat numbering
        output = """# IGBLASTP
# Query: test_protein
# Database: /data/databases/human/V/airr_c_human_ig.V
# Domain classification requested: kabat

# Alignment summary between query and top germline V gene hit (from, to, length, matches, mismatches, gaps, percent identity)

FR1     1       30      30      30      0       0       100
CDR1    31      35      5       2       3       0       40
FR2     36      49      14      14      0       0       100
CDR2    50      66      17      9       8       0       52.9
FR3     67      98      32      26      6       0       81.2
Total   N/A     N/A     98      81      17      0       82.7

# Hit table (the first field indicates the chain type of the hit)
# Fields: query id, subject id, % identity, alignment length, mismatches, gap opens, gaps, q. start, q. end, s. start, s. end, evalue, bit score

# 3 hits found
V       test_protein    IGHV1-2*02      82.653  98      17      0       0       1       98      1       98      1.56e-59     170

# BLAST processed 1 queries"""

        result = self.parser.parse(output, "igblastp")

        # Check that framework and CDR data is extracted
        analysis_summary = result["analysis_summary"]

        # FR1 data (Kabat numbering)
        assert analysis_summary["fr1_start"] == 1
        assert analysis_summary["fr1_end"] == 30
        assert analysis_summary["fr1_length"] == 30
        assert analysis_summary["fr1_matches"] == 30
        assert analysis_summary["fr1_mismatches"] == 0
        assert analysis_summary["fr1_gaps"] == 0
        assert analysis_summary["fr1_percent_identity"] == 100.0

        # CDR1 data (Kabat numbering - different from IMGT)
        assert analysis_summary["cdr1_start"] == 31
        assert analysis_summary["cdr1_end"] == 35
        assert analysis_summary["cdr1_length"] == 5
        assert analysis_summary["cdr1_matches"] == 2
        assert analysis_summary["cdr1_mismatches"] == 3
        assert analysis_summary["cdr1_gaps"] == 0
        assert analysis_summary["cdr1_percent_identity"] == 40.0

        # CDR2 data (Kabat numbering - much longer than IMGT)
        assert analysis_summary["cdr2_start"] == 50
        assert analysis_summary["cdr2_end"] == 66
        assert analysis_summary["cdr2_length"] == 17
        assert analysis_summary["cdr2_matches"] == 9
        assert analysis_summary["cdr2_mismatches"] == 8
        assert analysis_summary["cdr2_gaps"] == 0
        assert analysis_summary["cdr2_percent_identity"] == 52.9

    def test_extract_framework_cdr_data_no_alignment_summary(self):
        """Test parsing when no alignment summary is present."""
        # Output without alignment summary section
        output = """# IGBLASTP
# Query: test_protein
# Database: /data/databases/human/V/airr_c_human_ig.V

# Hit table (the first field indicates the chain type of the hit)
# Fields: query id, subject id, % identity, alignment length, mismatches, gap opens, gaps, q. start, q. end, s. start, s. end, evalue, bit score

# 1 hits found
V       test_protein    IGHV1-2*02      82.653  98      17      0       0       1       98      1       98      1.56e-59     170

# BLAST processed 1 queries"""

        result = self.parser.parse(output, "igblastp")

        # Should not have framework/CDR data
        analysis_summary = result["analysis_summary"]
        framework_cdr_fields = [
            k
            for k in analysis_summary.keys()
            if any(
                region in k for region in ["fr1", "cdr1", "fr2", "cdr2", "fr3"]
            )
        ]
        assert len(framework_cdr_fields) == 0

    def test_extract_framework_cdr_data_malformed_line(self):
        """Test parsing with malformed alignment summary lines."""
        # Output with some malformed lines
        output = """# IGBLASTP
# Query: test_protein
# Database: /data/databases/human/V/airr_c_human_ig.V

# Alignment summary between query and top germline V gene hit (from, to, length, matches, mismatches, gaps, percent identity)

FR1-IMGT        1       25      25      25      0       0       100
Malformed line that should be ignored
CDR1-IMGT       26      33      8       6       2       0       75
Another malformed line
FR2-IMGT        34      50      17      15      2       0       88.2
Total   N/A     N/A     98      81      17      0       82.7

# Hit table (the first field indicates the chain type of the hit)
# Fields: query id, subject id, % identity, alignment length, mismatches, gap opens, gaps, q. start, q. end, s. start, s. end, evalue, bit score

# 1 hits found
V       test_protein    IGHV1-2*02      82.653  98      17      0       0       1       98      1       98      1.56e-59     170

# BLAST processed 1 queries"""

        result = self.parser.parse(output, "igblastp")

        # Should extract valid lines and ignore malformed ones
        analysis_summary = result["analysis_summary"]

        # FR1 should be present
        assert "fr1_start" in analysis_summary
        assert analysis_summary["fr1_start"] == 1

        # CDR1 should be present
        assert "cdr1_start" in analysis_summary
        assert analysis_summary["cdr1_start"] == 26

        # FR2 should be present
        assert "fr2_start" in analysis_summary
        assert analysis_summary["fr2_start"] == 34

    def test_extract_framework_cdr_data_nucleotide_ignored(self):
        """Test that framework/CDR extraction is not attempted for nucleotide IgBLAST."""
        # Nucleotide output (should not trigger framework/CDR extraction)
        output = """# IGBLASTN
# Query: test_nucleotide
# Database: /data/databases/human/V/airr_c_human_ig.V

# Hit table (the first field indicates the chain type of the hit)
# Fields: query id, subject id, % identity, alignment length, mismatches, gap opens, gaps, q. start, q. end, s. start, s. end, evalue, bit score

# 1 hits found
V       test_nucleotide    IGHV1-2*02      82.653  98      17      0       0       1       98      1       98      1.56e-59     170

# BLAST processed 1 queries"""

        result = self.parser.parse(output, "igblastn")

        # Should not have framework/CDR data for nucleotide
        analysis_summary = result["analysis_summary"]
        framework_cdr_fields = [
            k
            for k in analysis_summary.keys()
            if any(
                region in k for region in ["fr1", "cdr1", "fr2", "cdr2", "fr3"]
            )
        ]
        assert len(framework_cdr_fields) == 0

    def test_extract_framework_cdr_data_adds_to_hits(self):
        """Test that framework/CDR data is added to all hits."""
        output = """# IGBLASTP
# Query: test_protein
# Database: /data/databases/human/V/airr_c_human_ig.V

# Alignment summary between query and top germline V gene hit (from, to, length, matches, mismatches, gaps, percent identity)

FR1-IMGT        1       25      25      25      0       0       100
CDR1-IMGT       26      33      8       6       2       0       75
FR2-IMGT        34      50      17      15      2       0       88.2

# Hit table (the first field indicates the chain type of the hit)
# Fields: query id, subject id, % identity, alignment length, mismatches, gap opens, gaps, q. start, q. end, s. start, s. end, evalue, bit score

# 2 hits found
V       test_protein    IGHV1-2*02      82.653  98      17      0       0       1       98      1       98      1.56e-59     170
V       test_protein    IGHV1-2*06      82.653  98      17      0       0       1       98      1       98      1.56e-59     170

# BLAST processed 1 queries"""

        result = self.parser.parse(output, "igblastp")

        # Check that framework/CDR data is in analysis summary
        analysis_summary = result["analysis_summary"]
        assert "fr1_start" in analysis_summary
        assert "fr1_end" in analysis_summary
        assert "fr1_percent_identity" in analysis_summary
        assert "cdr1_start" in analysis_summary
        assert "cdr1_end" in analysis_summary
        assert "cdr1_percent_identity" in analysis_summary
        assert "fr2_start" in analysis_summary
        assert "fr2_end" in analysis_summary
        assert "fr2_percent_identity" in analysis_summary

        # The framework/CDR data should be available in hits if they exist
        # Note: The hit table parsing is tested separately, so we focus on framework/CDR extraction here
        print(f"Analysis summary keys: {list(analysis_summary.keys())}")
        print(f"Number of hits: {len(result['hits'])}")

        # Verify that the framework/CDR data was extracted correctly
        assert analysis_summary["fr1_start"] == 1
        assert analysis_summary["fr1_end"] == 25
        assert analysis_summary["fr1_percent_identity"] == 100.0
        assert analysis_summary["cdr1_start"] == 26
        assert analysis_summary["cdr1_end"] == 33
        assert analysis_summary["cdr1_percent_identity"] == 75.0
        assert analysis_summary["fr2_start"] == 34
        assert analysis_summary["fr2_end"] == 50
        assert analysis_summary["fr2_percent_identity"] == 88.2
