"""
Tests for domain refactoring with new biologic entities.
"""

import pytest

from backend.core.exceptions import ValidationError
from backend.domain.entities import (
    BiologicEntity,
    BiologicChain,
    BiologicSequence,
    BiologicDomain,
    BiologicFeature,
)
from backend.domain.models import (
    SequenceValidator,
    RegionCalculator,
    BiologicType,
    ChainType,
    DomainType,
    FeatureType,
)
from backend.domain.value_objects import (
    AminoAcidSequence,
    RegionBoundary,
    SequenceIdentifier,
    ConfidenceScore,
    AnnotationMetadata,
)


class TestValueObjects:
    """Test value objects functionality"""

    def test_amino_acid_sequence_creation(self):
        """Test creating valid amino acid sequences"""
        # Valid sequence
        seq = AminoAcidSequence("ACDEFGHIKLMNPQRSTVWY")
        assert str(seq) == "ACDEFGHIKLMNPQRSTVWY"
        assert len(seq) == 20

        # Sequence with X for unknown
        seq_with_x = AminoAcidSequence("ACDEFGHIKLMNPQRSTVWYX")
        assert "X" in str(seq_with_x)

    def test_amino_acid_sequence_validation(self):
        """Test amino acid sequence validation"""
        # Invalid characters
        with pytest.raises(ValidationError):
            AminoAcidSequence("ACDEFGHIKLMNPQRSTVWY123")

        # Empty sequence
        with pytest.raises(ValidationError):
            AminoAcidSequence("")

    def test_amino_acid_sequence_methods(self):
        """Test amino acid sequence methods"""
        seq = AminoAcidSequence("acdefghiklmnpqrstvwy")

        # Upper case
        upper_seq = seq.upper()
        assert str(upper_seq) == "ACDEFGHIKLMNPQRSTVWY"

        # Substring
        sub_seq = seq.substring(0, 5)
        assert str(sub_seq) == "acdef"

        # Contains
        assert seq.contains("def")
        assert not seq.contains("XYZ")

        # Count amino acid
        assert seq.count_amino_acid("A") == 1

    def test_region_boundary_creation(self):
        """Test creating valid region boundaries"""
        boundary = RegionBoundary(10, 20)
        assert boundary.start == 10
        assert boundary.end == 20
        assert boundary.length() == 11

    def test_region_boundary_validation(self):
        """Test region boundary validation"""
        # Invalid: start > end
        with pytest.raises(ValidationError):
            RegionBoundary(20, 10)

        # Invalid: negative values
        with pytest.raises(ValidationError):
            RegionBoundary(-1, 10)

    def test_region_boundary_methods(self):
        """Test region boundary methods"""
        boundary1 = RegionBoundary(10, 20)
        boundary2 = RegionBoundary(15, 25)
        boundary3 = RegionBoundary(30, 40)

        # Contains
        assert boundary1.contains(15)
        assert not boundary1.contains(25)

        # Overlaps
        assert boundary1.overlaps_with(boundary2)
        assert not boundary1.overlaps_with(boundary3)

        # Intersection
        intersection = boundary1.intersection(boundary2)
        assert intersection.start == 15
        assert intersection.end == 20

    def test_sequence_identifier_creation(self):
        """Test creating sequence identifiers"""
        identifier = SequenceIdentifier("TEST123", "test_source")
        assert str(identifier) == "test_source:TEST123"

    def test_confidence_score_creation(self):
        """Test creating confidence scores"""
        score = ConfidenceScore(0.95, "test_method")
        assert score.score == 0.95

    def test_confidence_score_validation(self):
        """Test confidence score validation"""
        # Valid scores
        ConfidenceScore(0.0, "test_method")
        ConfidenceScore(0.5, "test_method")
        ConfidenceScore(1.0, "test_method")

        # Invalid scores
        with pytest.raises(ValidationError):
            ConfidenceScore(-0.1, "test_method")

        with pytest.raises(ValidationError):
            ConfidenceScore(1.1, "test_method")

    def test_annotation_metadata_creation(self):
        """Test creating annotation metadata"""
        metadata = AnnotationMetadata(
            tool_version="1.3",
            timestamp="2023-01-01T00:00:00Z",
            parameters={"scheme": "imgt"},
        )
        assert metadata.tool_version == "1.3"
        assert metadata.timestamp == "2023-01-01T00:00:00Z"


class TestDomainEntities:
    """Test domain entities functionality"""

    def test_biologic_feature_creation(self):
        """Test creating biologic features"""
        feature = BiologicFeature(
            feature_type="CDR1",
            name="CDR1",
            value="ACDEFGHIKLMNPQRSTVWY",
            start_position=0,
            end_position=19,
            confidence_score=95,
        )

        assert feature.name == "CDR1"
        assert feature.feature_type == "CDR1"
        assert feature.value == "ACDEFGHIKLMNPQRSTVWY"
        assert feature.start_position == 0
        assert feature.end_position == 19
        assert feature.confidence_score == 95
        assert feature.is_cdr_region()
        assert not feature.is_fr_region()

    def test_biologic_domain_creation(self):
        """Test creating biologic domains"""
        domain = BiologicDomain(
            domain_type=DomainType.VARIABLE,
            start_position=0,
            end_position=99,
            confidence_score=90,
        )

        assert domain.domain_type == DomainType.VARIABLE
        assert domain.is_variable_domain()
        assert not domain.is_constant_domain()
        assert len(domain.features) == 0
        assert domain.length == 100

    def test_biologic_domain_add_feature(self):
        """Test adding features to domains"""
        domain = BiologicDomain(
            domain_type=DomainType.VARIABLE,
            start_position=0,
            end_position=99,
            confidence_score=90,
        )

        # Add a feature
        feature = BiologicFeature(
            feature_type=FeatureType.CDR1,
            name="CDR1",
            value="ACDEFGHIKL",
            start_position=0,
            end_position=9,
            confidence_score=95,
        )

        domain.add_feature(feature)
        assert len(domain.features) == 1
        assert len(domain.get_features_by_type(FeatureType.CDR1)) == 1

    def test_biologic_sequence_creation(self):
        """Test creating biologic sequences"""
        sequence = BiologicSequence(
            sequence_type="PROTEIN", sequence_data="ACDEFGHIKLMNPQRSTVWY"
        )

        assert sequence.sequence_type == "PROTEIN"
        assert sequence.sequence_data == "ACDEFGHIKLMNPQRSTVWY"
        assert sequence.is_protein()
        assert not sequence.is_dna()
        assert len(sequence.domains) == 0
        assert sequence.length == 20

    def test_biologic_chain_creation(self):
        """Test creating biologic chains"""
        chain = BiologicChain(name="Heavy", chain_type=ChainType.HEAVY)

        assert chain.name == "Heavy"
        assert chain.chain_type == ChainType.HEAVY
        assert chain.is_heavy_chain()
        assert not chain.is_light_chain()
        assert len(chain.sequences) == 0

    def test_biologic_entity_creation(self):
        """Test creating biologic entities"""
        entity = BiologicEntity(
            name="Test Antibody", biologic_type=BiologicType.ANTIBODY
        )

        assert entity.name == "Test Antibody"
        assert entity.biologic_type == BiologicType.ANTIBODY
        assert len(entity.chains) == 0
        assert entity.is_antibody()
        assert not entity.is_protein()

    def test_biologic_entity_add_chain(self):
        """Test adding chains to biologic entities"""
        entity = BiologicEntity(name="Test Antibody", biologic_type="antibody")

        heavy_chain = BiologicChain(name="Heavy", chain_type=ChainType.HEAVY)

        light_chain = BiologicChain(name="Light", chain_type=ChainType.LIGHT)

        entity.add_chain(heavy_chain)
        entity.add_chain(light_chain)

        assert len(entity.chains) == 2
        assert len(entity.get_chains_by_type(ChainType.HEAVY)) == 1
        assert len(entity.get_chains_by_type(ChainType.LIGHT)) == 1


class TestDomainServices:
    """Test domain services functionality"""

    def test_sequence_validator(self):
        """Test sequence validator"""
        validator = SequenceValidator()

        # Valid protein sequence
        assert validator.is_valid_protein_sequence("ACDEFGHIKLMNPQRSTVWY")

        # Invalid protein sequence
        assert not validator.is_valid_protein_sequence(
            "ACDEFGHIKLMNPQRSTVWY123"
        )

        # Valid DNA sequence
        assert validator.is_valid_dna_sequence("ATCGATCGATCG")

        # Invalid DNA sequence
        assert not validator.is_valid_dna_sequence("ATCGATCGATCG123")

    def test_region_calculator(self):
        """Test region calculator"""
        calculator = RegionCalculator()

        # Calculate region boundaries
        sequence_length = 100
        region_start = 10
        region_end = 30

        boundary = calculator.calculate_boundary(
            region_start, region_end, sequence_length
        )
        assert boundary.start == 10
        assert boundary.end == 30
        assert boundary.length() == 21
