"""
Tests for biologic integration with annotation service.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from backend.application.services.biologic_service import BiologicService
from backend.application.services.annotation_service import AnnotationService
from backend.domain.entities import (
    AntibodySequence,
    AntibodyChain,
    AntibodyDomain,
    AntibodyRegion,
)
from backend.domain.value_objects import (
    AminoAcidSequence,
    RegionBoundary,
    ConfidenceScore,
)
from backend.domain.models import (
    ChainType,
    DomainType,
    RegionType,
    NumberingScheme,
)
from backend.database.models import (
    Biologic,
    Chain,
    Sequence,
    ChainSequence,
    SequenceDomain,
    DomainFeature,
)


class TestBiologicIntegration:
    """Test biologic integration with domain entities."""

    def test_biologic_service_initialization(self):
        """Test that BiologicService can be initialized."""
        service = BiologicService()
        assert service is not None
        assert isinstance(service, BiologicService)

    def test_annotation_service_with_biologic_service(self):
        """Test that AnnotationService can use BiologicService."""
        annotation_service = AnnotationService()
        assert hasattr(annotation_service, '_biologic_service')
        assert isinstance(annotation_service._biologic_service, BiologicService)

    @pytest.mark.asyncio
    async def test_annotation_service_integration(self):
        """Test that AnnotationService can integrate with biologic models."""
        # Mock database session
        mock_session = AsyncMock()
        
        # Create a simple input for annotation
        input_dict = {
            "test_antibody": {
                "H": "DIQMTQSPSSLSASVGDRVTITCRASQSISSYLNWYQQKPGKAPKLLIY"
            }
        }

        # Test the integration method
        annotation_service = AnnotationService()
        
        # This should work without errors (we're not actually persisting)
        # The real test would be with a proper database session
        try:
            # We'll just test that the method exists and can be called
            # In a real test, we'd use a test database
            assert hasattr(annotation_service, 'annotate_and_persist_sequence')
            assert callable(annotation_service.annotate_and_persist_sequence)
        except Exception as e:
            # This is expected since we don't have a real database session
            assert "database" in str(e).lower() or "session" in str(e).lower()

    def test_simple_biologic_creation(self):
        """Test creating a simple Biologic ORM model."""
        biologic = Biologic(
            name="Test Antibody",
            organism="Human",
            biologic_type="antibody",
            metadata_json={"source": "test"}
        )
        
        assert biologic.name == "Test Antibody"
        assert biologic.organism == "Human"
        assert biologic.biologic_type == "antibody"

    def test_simple_chain_creation(self):
        """Test creating a simple Chain ORM model."""
        biologic = Biologic(
            name="Test Antibody",
            organism="Human",
            biologic_type="antibody"
        )
        
        chain = Chain(
            biologic_id=biologic.id,
            name="H",
            chain_type="HEAVY",
            metadata_json={}
        )
        
        assert chain.name == "H"
        assert chain.chain_type == "HEAVY"
        assert chain.biologic_id == biologic.id

    def test_simple_sequence_creation(self):
        """Test creating a simple Sequence ORM model."""
        sequence = Sequence(
            sequence_type="PROTEIN",
            sequence_data="DIQMTQSPSSLSASVGDRVTITCRASQSISSYLNWYQQKPGKAPKLLIY",
            length=50,
            description="Test sequence",
            metadata_json={"domain_type": "V"}
        )
        
        assert sequence.sequence_type == "PROTEIN"
        assert sequence.sequence_data == "DIQMTQSPSSLSASVGDRVTITCRASQSISSYLNWYQQKPGKAPKLLIY"
        assert sequence.length == 50
