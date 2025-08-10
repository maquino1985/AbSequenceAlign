"""
Tests for the domain model refactoring (Phase 2).
Verifies that value objects, entities, and domain services work correctly.
"""

import pytest

from backend.domain.value_objects import (
    AminoAcidSequence,
    RegionBoundary,
    SequenceIdentifier,
    ConfidenceScore,
    AnnotationMetadata,
)
from backend.domain.entities import (
    AntibodyRegion,
    AntibodyDomain,
    AntibodyChain,
    AntibodySequence,
)
from backend.domain.models import (
    ChainType,
    DomainType,
    RegionType,
    NumberingScheme,
    SequenceValidator,
    RegionCalculator,
)
from backend.core.exceptions import ValidationError, DomainError


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

        # Union
        union = boundary1.union(boundary2)
        assert union.start == 10
        assert union.end == 25

        # Adjacent
        boundary4 = RegionBoundary(21, 30)
        assert boundary1.is_adjacent_to(boundary4)

    def test_sequence_identifier_creation(self):
        """Test creating sequence identifiers"""
        seq_id = SequenceIdentifier("ABC123", "UniProt", "1.0")
        assert str(seq_id) == "UniProt:ABC123:1.0"

        seq_id_no_version = SequenceIdentifier("ABC123", "UniProt")
        assert str(seq_id_no_version) == "UniProt:ABC123"

    def test_confidence_score_creation(self):
        """Test creating confidence scores"""
        score = ConfidenceScore(0.85, "ANARCI")
        assert score.score == 0.85
        assert score.method == "ANARCI"
        assert score.is_high_confidence()
        assert not score.is_low_confidence()

    def test_confidence_score_validation(self):
        """Test confidence score validation"""
        # Invalid: score > 1.0
        with pytest.raises(ValidationError):
            ConfidenceScore(1.5, "ANARCI")

        # Invalid: score < 0.0
        with pytest.raises(ValidationError):
            ConfidenceScore(-0.1, "ANARCI")

    def test_annotation_metadata_creation(self):
        """Test creating annotation metadata"""
        metadata = AnnotationMetadata(
            tool_version="1.0.0",
            timestamp="2024-01-01T00:00:00",
            parameters={"scheme": "IMGT"},
            confidence_score=ConfidenceScore(0.9, "ANARCI"),
        )
        assert metadata.tool_version == "1.0.0"
        assert metadata.get_parameter("scheme") == "IMGT"


class TestDomainEntities:
    """Test domain entities functionality"""

    def test_antibody_region_creation(self):
        """Test creating antibody regions"""
        sequence = AminoAcidSequence("ACDEFGHIKLMNPQRSTVWY")
        boundary = RegionBoundary(0, 19)

        region = AntibodyRegion(
            name="CDR1",
            region_type=RegionType.CDR1,
            boundary=boundary,
            sequence=sequence,
            numbering_scheme=NumberingScheme.IMGT,
        )

        assert region.name == "CDR1"
        assert region.region_type == RegionType.CDR1
        assert region.is_cdr_region()
        assert not region.is_fr_region()

    def test_antibody_domain_creation(self):
        """Test creating antibody domains"""
        sequence = AminoAcidSequence("ACDEFGHIKLMNPQRSTVWY")

        domain = AntibodyDomain(
            domain_type=DomainType.VARIABLE,
            sequence=sequence,
            numbering_scheme=NumberingScheme.IMGT,
        )

        assert domain.domain_type == DomainType.VARIABLE
        assert domain.is_variable_domain()
        assert not domain.is_constant_domain()
        assert len(domain.regions) == 0

    def test_antibody_domain_add_region(self):
        """Test adding regions to domains"""
        sequence = AminoAcidSequence("ACDEFGHIKLMNPQRSTVWY")
        domain = AntibodyDomain(
            domain_type=DomainType.VARIABLE,
            sequence=sequence,
            numbering_scheme=NumberingScheme.IMGT,
        )

        # Add a region
        region = AntibodyRegion(
            name="CDR1",
            region_type=RegionType.CDR1,
            boundary=RegionBoundary(0, 9),
            sequence=AminoAcidSequence("ACDEFGHIKL"),
            numbering_scheme=NumberingScheme.IMGT,
        )

        domain.add_region(region)
        assert len(domain.regions) == 1
        assert domain.has_region("CDR1")
        assert domain.get_region("CDR1") == region

    def test_antibody_chain_creation(self):
        """Test creating antibody chains"""
        sequence = AminoAcidSequence("ACDEFGHIKLMNPQRSTVWY")

        chain = AntibodyChain(
            name="Heavy", chain_type=ChainType.HEAVY, sequence=sequence
        )

        assert chain.name == "Heavy"
        assert chain.chain_type == ChainType.HEAVY
        assert chain.is_heavy_chain()
        assert not chain.is_light_chain()
        assert len(chain.domains) == 0

    def test_antibody_sequence_creation(self):
        """Test creating antibody sequences"""
        sequence = AntibodySequence(name="Test Antibody")

        assert sequence.name == "Test Antibody"
        assert len(sequence.chains) == 0
        assert not sequence.is_complete_antibody()
        assert not sequence.is_scfv()

    def test_antibody_sequence_add_chain(self):
        """Test adding chains to sequences"""
        sequence = AntibodySequence(name="Test Antibody")

        heavy_chain = AntibodyChain(
            name="Heavy",
            chain_type=ChainType.HEAVY,
            sequence=AminoAcidSequence("ACDEFGHIKLMNPQRSTVWY"),
        )

        light_chain = AntibodyChain(
            name="Light",
            chain_type=ChainType.LIGHT,
            sequence=AminoAcidSequence("ACDEFGHIKLMNPQRSTVWY"),
        )

        sequence.add_chain(heavy_chain)
        sequence.add_chain(light_chain)

        assert len(sequence.chains) == 2
        assert sequence.has_heavy_chain()
        assert sequence.has_light_chain()
        assert sequence.is_complete_antibody()

    def test_antibody_sequence_duplicate_chain_type(self):
        """Test that duplicate chain types are not allowed"""
        sequence = AntibodySequence(name="Test Antibody")

        heavy_chain1 = AntibodyChain(
            name="Heavy1",
            chain_type=ChainType.HEAVY,
            sequence=AminoAcidSequence("ACDEFGHIKLMNPQRSTVWY"),
        )

        heavy_chain2 = AntibodyChain(
            name="Heavy2",
            chain_type=ChainType.HEAVY,
            sequence=AminoAcidSequence("ACDEFGHIKLMNPQRSTVWY"),
        )

        sequence.add_chain(heavy_chain1)

        with pytest.raises(DomainError):
            sequence.add_chain(heavy_chain2)


class TestDomainServices:
    """Test domain services functionality"""

    def test_sequence_validator(self):
        """Test sequence validation service"""
        validator = SequenceValidator()

        # Valid sequence
        assert validator.validate_amino_acid_sequence("ACDEFGHIKLMNPQRSTVWY")

        # Invalid sequence
        assert not validator.validate_amino_acid_sequence(
            "ACDEFGHIKLMNPQRSTVWY123"
        )

        # Valid chain type
        assert validator.validate_chain_type("H")

        # Invalid chain type
        assert not validator.validate_chain_type("INVALID")

    def test_region_calculator(self):
        """Test region calculation service"""
        calculator = RegionCalculator()

        # Calculate boundary
        boundary = calculator.calculate_region_boundary(10, 20)
        assert boundary.start == 10
        assert boundary.end == 20

        # Extract sequence
        sequence = "ACDEFGHIKLMNPQRSTVWY"
        extracted = calculator.extract_region_sequence(sequence, boundary)
        assert (
            extracted == "ACDEFGHIKLMNPQRSTVWY"[10:21]
        )  # Extract positions 10-20 (inclusive)

        # Calculate overlap
        boundary1 = RegionBoundary(10, 20)
        boundary2 = RegionBoundary(15, 25)
        overlap = calculator.calculate_region_overlap(boundary1, boundary2)
        assert overlap == 6

        # Check adjacency
        boundary3 = RegionBoundary(21, 30)
        assert calculator.regions_are_adjacent(boundary1, boundary3)


if __name__ == "__main__":
    pytest.main([__file__])
