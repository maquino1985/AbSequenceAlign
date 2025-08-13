from backend.models.models import (
    AlignmentMethod,
    NumberingScheme,
)
from backend.msa.msa_annotation import MSAAnnotationEngine
from backend.msa.msa_engine import MSAEngine
from backend.msa.pssm_calculator import PSSMCalculator
from backend.models.models import *
from backend.msa.msa_annotation import *
from backend.msa.msa_engine import *
from backend.msa.pssm_calculator import *


class TestEnhancedMSA:
    """Test enhanced MSA functionality with PSSM and region annotation"""

    def setup_method(self) -> None:
        """Set up test fixtures"""
        self.msa_engine = MSAEngine()
        self.annotation_engine = MSAAnnotationEngine()
        self.pssm_calculator = PSSMCalculator()

        # Test sequences
        self.test_sequences = [
            (
                "seq1",
                "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS",
            ),
            (
                "seq2",
                "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK",
            ),
            (
                "seq3",
                "ELQLQESGPGLVKPSETLSLTCAVSGVSFSDYHWAWIRDPPGKGLEWIGDINHRGHTNYNPSLKSRVTVSIDTSKNQFSLKLSSVTAADTAVYFCARDFPNFIFDFWGQGTLVTVSS",
            ),
        ]

    def test_enhanced_msa_creation(self) -> None:
        """Test MSA creation with enhanced features"""
        # Create MSA
        msa_result = self.msa_engine.create_msa(
            sequences=self.test_sequences, method=AlignmentMethod.MUSCLE
        )

        # Verify basic MSA structure
        assert msa_result is not None
        assert msa_result.msa_id is not None
        assert len(msa_result.sequences) == 3
        assert msa_result.consensus is not None
        assert len(msa_result.consensus) > 0

        # Verify PSSM data in metadata
        assert "pssm_data" in msa_result.metadata
        pssm_data = msa_result.metadata["pssm_data"]
        assert "position_frequencies" in pssm_data
        assert "position_scores" in pssm_data
        assert "conservation_scores" in pssm_data
        assert "consensus" in pssm_data
        assert "amino_acids" in pssm_data

    def test_pssm_calculation(self) -> None:
        """Test PSSM calculation functionality"""
        # Create alignment matrix
        alignment_matrix = [
            list(
                "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS"
            ),
            list(
                "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK---"
            ),
            list(
                "ELQLQESGPGLVKPSETLSLTCAVSGVSFSDYHWAWIRDPPGKGLEWIGDINHRGHTNYNPSLKSRVTVSIDTSKNQFSLKLSSVTAADTAVYFCARDFPNFIFDFWGQGTLVTVSS"
            ),
        ]

        # Calculate PSSM
        pssm_data = self.pssm_calculator.calculate_pssm(alignment_matrix)

        # Verify PSSM structure
        assert pssm_data is not None
        assert "position_frequencies" in pssm_data
        assert "position_scores" in pssm_data
        assert "conservation_scores" in pssm_data
        assert "consensus" in pssm_data
        assert "amino_acids" in pssm_data
        assert "alignment_length" in pssm_data
        assert "num_sequences" in pssm_data

        # Verify data integrity
        assert (
            len(pssm_data["position_frequencies"])
            == pssm_data["alignment_length"]
        )
        assert (
            len(pssm_data["position_scores"]) == pssm_data["alignment_length"]
        )
        assert (
            len(pssm_data["conservation_scores"])
            == pssm_data["alignment_length"]
        )
        assert len(pssm_data["consensus"]) == pssm_data["alignment_length"]
        assert pssm_data["num_sequences"] == 3

        # Verify amino acid coverage
        assert len(pssm_data["amino_acids"]) == 20  # Standard amino acids
        assert "A" in pssm_data["amino_acids"]
        assert "R" in pssm_data["amino_acids"]

    def test_enhanced_msa_annotation(self) -> None:
        """Test MSA annotation with region information"""
        # Create MSA first
        msa_result = self.msa_engine.create_msa(
            sequences=self.test_sequences, method=AlignmentMethod.MUSCLE
        )

        # Annotate MSA
        annotation_result = self.annotation_engine.annotate_msa(
            msa_result=msa_result, numbering_scheme=NumberingScheme.IMGT
        )

        # Verify annotation structure
        assert annotation_result is not None
        assert annotation_result.annotated_sequences is not None
        assert annotation_result.region_mappings is not None
        assert annotation_result.numbering_scheme == NumberingScheme.IMGT

        # Verify annotated sequences are present
        assert len(annotation_result.annotated_sequences) > 0

        # Check that annotated sequences have required fields
        for seq in annotation_result.annotated_sequences:
            assert seq.name is not None
            assert seq.original_sequence is not None
            assert seq.aligned_sequence is not None
            assert seq.annotations is not None

    def test_region_mapping_to_aligned_sequences(self) -> None:
        """Test that region positions are correctly mapped to aligned sequences"""
        # Create MSA with gaps
        sequences_with_gaps = [
            (
                "seq1",
                "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS",
            ),
            (
                "seq2",
                "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK",
            ),
        ]

        msa_result = self.msa_engine.create_msa(
            sequences=sequences_with_gaps, method=AlignmentMethod.MUSCLE
        )

        # Annotate
        annotation_result = self.annotation_engine.annotate_msa(
            msa_result=msa_result, numbering_scheme=NumberingScheme.IMGT
        )

        # Verify that regions are mapped to aligned positions
        for seq in annotation_result.annotated_sequences:
            for annotation in seq.annotations:
                assert annotation["start"] >= 0
                assert annotation["stop"] >= annotation["start"]
                assert annotation["stop"] < len(msa_result.consensus)

    def test_consensus_quality(self) -> None:
        """Test consensus sequence quality and conservation scores"""
        # Create MSA
        msa_result = self.msa_engine.create_msa(
            sequences=self.test_sequences, method=AlignmentMethod.MUSCLE
        )

        # Get PSSM data
        pssm_data = msa_result.metadata["pssm_data"]

        # Verify conservation scores
        conservation_scores = pssm_data["conservation_scores"]
        assert len(conservation_scores) == len(msa_result.consensus)

        # All conservation scores should be between 0 and 1
        for score in conservation_scores:
            assert 0 <= score <= 1

        # Verify consensus quality
        consensus = pssm_data["consensus"]
        assert len(consensus) == len(msa_result.consensus)

        # Consensus should contain valid amino acids
        valid_aas = set("ACDEFGHIKLMNPQRSTVWY")
        for aa in consensus:
            assert aa in valid_aas or aa == "-"

    def test_pssm_position_summary(self) -> None:
        """Test PSSM position summary functionality"""
        # Create alignment matrix
        alignment_matrix = [
            list(
                "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS"
            ),
            list(
                "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK---"
            ),
        ]

        # Calculate PSSM
        pssm_data = self.pssm_calculator.calculate_pssm(alignment_matrix)

        # Get position summary
        position_summary = self.pssm_calculator.get_position_summary(
            pssm_data, 0
        )

        # Verify position summary structure
        assert "position" in position_summary
        assert "conservation" in position_summary
        assert "top_frequencies" in position_summary
        assert "top_scores" in position_summary
        assert "consensus_aa" in position_summary

        assert position_summary["position"] == 0
        assert 0 <= position_summary["conservation"] <= 1
        assert len(position_summary["top_frequencies"]) <= 5
        assert len(position_summary["top_scores"]) <= 5

    def test_region_pssm(self) -> None:
        """Test region-specific PSSM calculation"""
        # Create alignment matrix
        alignment_matrix = [
            list(
                "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS"
            ),
            list(
                "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK---"
            ),
        ]

        # Calculate PSSM
        pssm_data = self.pssm_calculator.calculate_pssm(alignment_matrix)

        # Get region PSSM (positions 0-10)
        region_pssm = self.pssm_calculator.get_region_pssm(pssm_data, 0, 10)

        # Verify region PSSM structure
        assert "start_position" in region_pssm
        assert "end_position" in region_pssm
        assert "length" in region_pssm
        assert "average_conservation" in region_pssm
        assert "position_frequencies" in region_pssm
        assert "position_scores" in region_pssm
        assert "conservation_scores" in region_pssm

        assert region_pssm["start_position"] == 0
        assert region_pssm["end_position"] == 10
        assert region_pssm["length"] == 10
        assert 0 <= region_pssm["average_conservation"] <= 1
        assert len(region_pssm["position_frequencies"]) == 10
        assert len(region_pssm["position_scores"]) == 10
        assert len(region_pssm["conservation_scores"]) == 10

    def test_empty_pssm(self) -> None:
        """Test PSSM calculation with empty alignment"""
        empty_matrix: List[Any] = []
        pssm_data = self.pssm_calculator.calculate_pssm(empty_matrix)

        # Verify empty PSSM structure
        assert pssm_data is not None
        assert pssm_data["position_frequencies"] == []
        assert pssm_data["position_scores"] == []
        assert pssm_data["conservation_scores"] == []
        assert pssm_data["consensus"] == ""
        assert pssm_data["alignment_length"] == 0
        assert pssm_data["num_sequences"] == 0

    def test_msa_with_single_sequence(self) -> None:
        """Test MSA creation with single sequence"""
        single_sequence = [
            (
                "seq1",
                "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS",
            )
        ]

        msa_result = self.msa_engine.create_msa(
            sequences=single_sequence, method=AlignmentMethod.MUSCLE
        )

        # Verify single sequence MSA
        assert msa_result is not None
        assert len(msa_result.sequences) == 1
        assert msa_result.consensus == single_sequence[0][1]

        # PSSM should still be calculated
        pssm_data = msa_result.metadata["pssm_data"]
        assert len(pssm_data["conservation_scores"]) == len(
            single_sequence[0][1]
        )

        # All conservation scores should be 1.0 for single sequence
        for score in pssm_data["conservation_scores"]:
            assert score == 1.0
