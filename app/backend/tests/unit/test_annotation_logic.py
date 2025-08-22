"""
Unit tests for complex annotation logic and object transformations.
Focus on testing business logic without heavy mocking.
"""

from unittest.mock import Mock

from backend.models.models_v2 import DomainType
from backend.services.annotation_service import AnnotationService


class TestAnnotationService:
    """Unit tests for AnnotationService complex logic."""

    def test_map_domain_type_all_cases(self):
        """Test domain type mapping covers all expected cases."""
        service = AnnotationService()

        # Test all known domain types
        assert service._map_domain_type("C") == DomainType.CONSTANT
        assert service._map_domain_type("LINKER") == DomainType.LINKER
        assert service._map_domain_type("V") == DomainType.VARIABLE

        # Test edge cases
        assert service._map_domain_type("") == DomainType.VARIABLE
        assert service._map_domain_type(None) == DomainType.VARIABLE
        assert service._map_domain_type("unknown") == DomainType.VARIABLE

    def test_get_domain_positions_structure(self):
        """Test domain position extraction logic."""
        service = AnnotationService()

        # Test LINKER domain position extraction
        domain = Mock()
        domain.alignment_details = {"start": 10, "end": 50}
        start, stop = service._get_domain_positions(domain, DomainType.LINKER)
        assert start == 10
        assert stop == 50

        # Test VARIABLE domain position extraction
        domain.alignment_details = {"query_start": 15, "query_end": 45}
        start, stop = service._get_domain_positions(
            domain, DomainType.VARIABLE
        )
        assert start == 15
        assert stop == 45

        # Test missing alignment details
        domain.alignment_details = None
        start, stop = service._get_domain_positions(
            domain, DomainType.VARIABLE
        )
        assert start is None
        assert stop is None

        # Test partial alignment details
        domain.alignment_details = {"query_start": 20}  # Missing query_end
        start, stop = service._get_domain_positions(
            domain, DomainType.VARIABLE
        )
        assert start == 20
        assert stop is None

    def test_region_processing_0_to_1_based_conversion(self):
        """Test critical 0-based to 1-based position conversion."""
        service = AnnotationService()

        # Test dict-based region (common case)
        dict_region = {
            "start": 0,
            "stop": 23,
            "sequence": "EVQLVESGGGLVQPGGSLRLSCA",
        }
        start, stop, seq = service._process_region(dict_region)
        assert start == 1  # 0 -> 1 (1-based)
        assert stop == 24  # 23 -> 24 (1-based)
        assert seq == "EVQLVESGGGLVQPGGSLRLSCA"

        # Test object-based region
        region = Mock()
        region.start = 24
        region.stop = 35
        region.sequence = "ASGFTFSSYAM"
        start, stop, seq = service._process_region(region)
        assert start == 25  # 24 -> 25 (1-based)
        assert stop == 36  # 35 -> 36 (1-based)
        assert seq == "ASGFTFSSYAM"

    def test_region_feature_structure(self):
        """Test region feature object creation."""
        service = AnnotationService()

        region = service._create_v2_region(
            "FR1", 1, 24, "EVQLVESGGGLVQPGGSLRLSCA"
        )

        assert region.name == "FR1"
        assert region.start == 1
        assert region.stop == 24
        assert len(region.features) == 1
        assert region.features[0].kind == "sequence"
        assert region.features[0].value == "EVQLVESGGGLVQPGGSLRLSCA"

    def test_statistics_calculation_logic(self):
        """Test statistics aggregation logic with various scenarios."""
        service = AnnotationService()

        # Mock processor with multiple results
        processor = Mock()

        # Result 1: Heavy chain with IgG
        result1 = Mock()
        chain1 = Mock()
        domain1 = Mock()
        domain1.domain_type = "V"
        domain1.isotype = "IgG"
        domain1.species = "human"
        chain1.domains = [domain1]
        result1.chains = [chain1]

        # Result 2: Light chain with IgA
        result2 = Mock()
        chain2 = Mock()
        domain2 = Mock()
        domain2.domain_type = "V"
        domain2.isotype = "IgA"
        domain2.species = "mouse"
        chain2.domains = [domain2]
        result2.chains = [chain2]

        # Result 3: Multiple domains, should only count primary (V)
        result3 = Mock()
        chain3 = Mock()
        domain3a = Mock()
        domain3a.domain_type = "V"
        domain3a.isotype = "IgG"
        domain3a.species = "human"
        domain3b = Mock()
        domain3b.domain_type = "C"
        domain3b.isotype = "IgM"  # Should be ignored
        domain3b.species = "rat"  # Should be ignored
        chain3.domains = [domain3a, domain3b]
        result3.chains = [chain3]

        processor.results = [result1, result2, result3]

        chain_types, isotypes, species_counts = service._calculate_statistics(
            processor
        )

        # Verify aggregation
        assert chain_types == {"IgG": 2, "IgA": 1}
        assert isotypes == {"IgG": 2, "IgA": 1}
        assert species_counts == {"human": 2, "mouse": 1}
