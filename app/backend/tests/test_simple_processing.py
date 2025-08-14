"""
Simple test for the simplified processing service.
Tests the basic functionality without overengineering.
"""

import pytest
from backend.application.services.processing_service import SimpleProcessingService
from backend.application.factories import ProcessingServiceFactory
from backend.core.interfaces import ProcessingResult


class TestSimpleProcessingService:
    """Test the simplified processing service"""

    def test_service_creation(self):
        """Test creating a simple processing service"""
        service = SimpleProcessingService()
        assert service is not None
        assert len(service.get_active_jobs()) == 0

    def test_get_available_processors(self):
        """Test getting available processor types"""
        service = SimpleProcessingService()
        processors = service.get_available_processors()
        assert "annotation" in processors
        assert len(processors) == 1

    def test_process_sequences_basic(self):
        """Test basic sequence processing"""
        service = SimpleProcessingService()
        
        # Use a proper antibody sequence from existing tests
        sequences = {
            "test_seq": {
                "heavy_chain": "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS"
            }
        }
        
        result = service.process_sequences(sequences, "annotation")
        
        assert isinstance(result, ProcessingResult)
        assert result.success is True
        assert result.data is not None
        assert result.metadata["processor_type"] == "annotation"

    def test_process_sequences_invalid_type(self):
        """Test processing with invalid processor type"""
        service = SimpleProcessingService()
        
        sequences = {
            "test_seq": {
                "heavy_chain": "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS"
            }
        }
        
        result = service.process_sequences(sequences, "invalid_type")
        
        assert isinstance(result, ProcessingResult)
        assert result.success is False
        assert "Unknown processor type" in result.error


class TestProcessingServiceFactory:
    """Test the simple processing service factory"""

    def test_create_service(self):
        """Test creating a service through the factory"""
        service = ProcessingServiceFactory.create_service()
        assert isinstance(service, SimpleProcessingService)
        assert service.get_available_processors() == ["annotation"]
