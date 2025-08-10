import pytest
from unittest.mock import patch, MagicMock
from backend.msa.msa_annotation import MSAAnnotationEngine
from backend.models.models import (
    MSAResult,
    MSASequence,
    MSAAnnotationResult,
    NumberingScheme,
)


class TestMSAAnnotationEngine:
    """Test cases for MSAAnnotationEngine"""

    def setup_method(self):
        """Set up test fixtures"""
        self.annotation_engine = MSAAnnotationEngine()

        # Create test MSA result
        self.test_msa_result = MSAResult(
            msa_id="test-msa-123",
            sequences=[
                MSASequence(
                    name="seq1",
                    original_sequence="EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS",
                    aligned_sequence="EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS",
                    start_position=0,
                    end_position=120,
                    gaps=[],
                ),
                MSASequence(
                    name="seq2",
                    original_sequence="EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK",
                    aligned_sequence="EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK---",
                    start_position=0,
                    end_position=123,
                    gaps=[120, 121, 122],
                ),
            ],
            alignment_matrix=[
                list(
                    "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS"
                ),
                list(
                    "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK---"
                ),
            ],
            consensus="EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS",
            alignment_method="muscle",
            created_at="2023-01-01T00:00:00",
            metadata={"num_sequences": 2, "alignment_length": 123},
        )

    def test_annotation_engine_initialization(self):
        """Test MSAAnnotationEngine initialization"""
        assert self.annotation_engine is not None
        assert hasattr(self.annotation_engine, "sequence_processor")

    @patch("backend.msa.msa_annotation.annotate_sequences_with_processor")
    def test_annotate_msa_success(self, mock_annotate):
        """Test successful MSA annotation"""
        # Mock annotation result
        mock_annotation_result = MagicMock()
        mock_annotation_result.sequences = [
            MagicMock(
                sequence="EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS",
                regions={
                    "FR1": {
                        "start": 0,
                        "stop": 25,
                        "sequence": "EVQLVESGGGLVQPGGSLRLSCAAS",
                    },
                    "CDR1": {"start": 26, "stop": 32, "sequence": "GFTFSY"},
                    "FR2": {"start": 33, "stop": 49, "sequence": "FAMSWVRQAPGKGLEW"},
                    "CDR2": {"start": 50, "stop": 56, "sequence": "VATISG"},
                    "FR3": {
                        "start": 57,
                        "stop": 85,
                        "sequence": "GGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYY",
                    },
                    "CDR3": {"start": 86, "stop": 98, "sequence": "CVRQTYGGFGY"},
                    "FR4": {"start": 99, "stop": 119, "sequence": "WGQGTLVTVSS"},
                },
            ),
            MagicMock(
                sequence="EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK",
                regions={
                    "FR1": {
                        "start": 0,
                        "stop": 25,
                        "sequence": "EVQLVESGGGLVQPGGSLRLSCAAS",
                    },
                    "CDR1": {"start": 26, "stop": 32, "sequence": "GFTFSS"},
                    "FR2": {"start": 33, "stop": 49, "sequence": "YAMSWVRQAPGKGLEW"},
                    "CDR2": {"start": 50, "stop": 56, "sequence": "VSAISG"},
                    "FR3": {
                        "start": 57,
                        "stop": 85,
                        "sequence": "SGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYY",
                    },
                    "CDR3": {"start": 86, "stop": 98, "sequence": "CAK"},
                    "FR4": {"start": 99, "stop": 119, "sequence": "WGQGTLVTVSS"},
                },
            ),
        ]
        mock_annotate.return_value = mock_annotation_result

        result = self.annotation_engine.annotate_msa(
            self.test_msa_result, NumberingScheme.IMGT
        )

        assert isinstance(result, MSAAnnotationResult)
        assert result.msa_id == "test-msa-123"
        assert result.numbering_scheme == NumberingScheme.IMGT
        assert len(result.annotated_sequences) == 2
        assert len(result.region_mappings) > 0

        # Check that regions are mapped correctly
        assert "FR1" in result.region_mappings
        assert "CDR1" in result.region_mappings
        assert "FR2" in result.region_mappings
        assert "CDR2" in result.region_mappings
        assert "FR3" in result.region_mappings
        assert "CDR3" in result.region_mappings
        assert "FR4" in result.region_mappings

    def test_extract_annotations(self):
        """Test _extract_annotations method"""
        # Create mock sequence info with regions
        mock_seq_info = MagicMock()
        mock_seq_info.regions = {
            "FR1": {"start": 0, "stop": 25, "sequence": "EVQLVESGGGLVQPGGSLRLSCAAS"},
            "CDR1": {"start": 26, "stop": 32, "sequence": "GFTFSY"},
            "FR2": {"start": 33, "stop": 49, "sequence": "FAMSWVRQAPGKGLEW"},
        }

        annotations = self.annotation_engine._extract_annotations(mock_seq_info)

        assert len(annotations) == 3
        assert annotations[0]["name"] == "FR1"
        assert annotations[0]["start"] == 0
        assert annotations[0]["stop"] == 25
        assert annotations[0]["sequence"] == "EVQLVESGGGLVQPGGSLRLSCAAS"
        assert annotations[0]["color"] is not None

        assert annotations[1]["name"] == "CDR1"
        assert annotations[2]["name"] == "FR2"

    def test_extract_annotations_no_regions(self):
        """Test _extract_annotations with no regions"""
        mock_seq_info = MagicMock()
        mock_seq_info.regions = None

        annotations = self.annotation_engine._extract_annotations(mock_seq_info)

        assert annotations == []

    def test_get_region_color(self):
        """Test _get_region_color method"""
        # Test known regions
        assert self.annotation_engine._get_region_color("FR1") == "#FF6B6B"
        assert self.annotation_engine._get_region_color("CDR1") == "#4ECDC4"
        assert self.annotation_engine._get_region_color("FR2") == "#45B7D1"
        assert self.annotation_engine._get_region_color("CDR2") == "#96CEB4"
        assert self.annotation_engine._get_region_color("FR3") == "#FFEAA7"
        assert self.annotation_engine._get_region_color("CDR3") == "#DDA0DD"
        assert self.annotation_engine._get_region_color("FR4") == "#98D8C8"

        # Test unknown region
        assert self.annotation_engine._get_region_color("UNKNOWN") == "#CCCCCC"

    def test_map_positions_to_alignment_exact_match(self):
        """Test _map_positions_to_alignment with exact match"""
        original_seq = "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS"
        aligned_seq = "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS"

        aligned_start, aligned_stop = (
            self.annotation_engine._map_positions_to_alignment(
                original_seq, aligned_seq, 0, 25
            )
        )

        assert aligned_start == 0
        assert aligned_stop == 25

    def test_map_positions_to_alignment_with_gaps(self):
        """Test _map_positions_to_alignment with gaps"""
        original_seq = "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK"
        aligned_seq = "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK---"

        aligned_start, aligned_stop = (
            self.annotation_engine._map_positions_to_alignment(
                original_seq, aligned_seq, 0, 25
            )
        )

        assert aligned_start == 0
        assert aligned_stop == 25

    def test_map_positions_to_alignment_mismatch(self):
        """Test _map_positions_to_alignment with sequence mismatch"""
        original_seq = "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS"
        aligned_seq = "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK---"

        aligned_start, aligned_stop = (
            self.annotation_engine._map_positions_to_alignment(
                original_seq, aligned_seq, 0, 25
            )
        )

        # Should return original positions when sequences don't match
        assert aligned_start == 0
        assert aligned_stop == 25

    def test_map_positions_to_alignment_empty_sequences(self):
        """Test _map_positions_to_alignment with empty sequences"""
        aligned_start, aligned_stop = (
            self.annotation_engine._map_positions_to_alignment("", "", 0, 25)
        )

        assert aligned_start == 0
        assert aligned_stop == 25

    def test_get_region_positions_in_alignment(self):
        """Test get_region_positions_in_alignment method"""
        # Create MSA result with annotations
        msa_result = MSAResult(
            msa_id="test-msa-123",
            sequences=[
                MSASequence(
                    name="seq1",
                    original_sequence="EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS",
                    aligned_sequence="EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS",
                    start_position=0,
                    end_position=120,
                    gaps=[],
                    annotations=[
                        {
                            "name": "CDR1",
                            "start": 26,
                            "stop": 32,
                            "sequence": "GFTFSY",
                            "color": "#4ECDC4",
                        },
                        {
                            "name": "CDR2",
                            "start": 50,
                            "stop": 56,
                            "sequence": "VATISG",
                            "color": "#96CEB4",
                        },
                    ],
                ),
                MSASequence(
                    name="seq2",
                    original_sequence="EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK",
                    aligned_sequence="EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK---",
                    start_position=0,
                    end_position=123,
                    gaps=[120, 121, 122],
                    annotations=[
                        {
                            "name": "CDR1",
                            "start": 26,
                            "stop": 32,
                            "sequence": "GFTFSS",
                            "color": "#4ECDC4",
                        },
                        {
                            "name": "CDR2",
                            "start": 50,
                            "stop": 56,
                            "sequence": "VSAISG",
                            "color": "#96CEB4",
                        },
                    ],
                ),
            ],
            alignment_matrix=[],
            consensus="",
            alignment_method="muscle",
            created_at="2023-01-01T00:00:00",
            metadata={},
        )

        region_positions = self.annotation_engine.get_region_positions_in_alignment(
            msa_result, "CDR1"
        )

        assert len(region_positions) == 2
        assert region_positions[0]["sequence_name"] == "seq1"
        assert region_positions[0]["original_start"] == 26
        assert region_positions[0]["original_stop"] == 32
        assert region_positions[0]["color"] == "#4ECDC4"

        assert region_positions[1]["sequence_name"] == "seq2"
        assert region_positions[1]["original_start"] == 26
        assert region_positions[1]["original_stop"] == 32
        assert region_positions[1]["color"] == "#4ECDC4"

    def test_get_region_positions_in_alignment_no_annotations(self):
        """Test get_region_positions_in_alignment with no annotations"""
        msa_result = MSAResult(
            msa_id="test-msa-123",
            sequences=[
                MSASequence(
                    name="seq1",
                    original_sequence="EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS",
                    aligned_sequence="EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS",
                    start_position=0,
                    end_position=120,
                    gaps=[],
                    annotations=None,
                )
            ],
            alignment_matrix=[],
            consensus="",
            alignment_method="muscle",
            created_at="2023-01-01T00:00:00",
            metadata={},
        )

        region_positions = self.annotation_engine.get_region_positions_in_alignment(
            msa_result, "CDR1"
        )

        assert region_positions == []

    def test_get_region_positions_in_alignment_region_not_found(self):
        """Test get_region_positions_in_alignment with region not found"""
        msa_result = MSAResult(
            msa_id="test-msa-123",
            sequences=[
                MSASequence(
                    name="seq1",
                    original_sequence="EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS",
                    aligned_sequence="EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS",
                    start_position=0,
                    end_position=120,
                    gaps=[],
                    annotations=[
                        {
                            "name": "CDR1",
                            "start": 26,
                            "stop": 32,
                            "sequence": "GFTFSY",
                            "color": "#4ECDC4",
                        }
                    ],
                )
            ],
            alignment_matrix=[],
            consensus="",
            alignment_method="muscle",
            created_at="2023-01-01T00:00:00",
            metadata={},
        )

        region_positions = self.annotation_engine.get_region_positions_in_alignment(
            msa_result, "CDR2"  # Region not present in annotations
        )

        assert region_positions == []
