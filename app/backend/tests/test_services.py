"""
Tests for the new services in the command pattern implementation.
"""

import pytest
from unittest.mock import Mock

from backend.application.services.validation_service import ValidationService
from backend.application.services.response_service import ResponseService
from backend.core.interfaces import ProcessingResult
from backend.domain.entities import (
    BiologicEntity,
    BiologicChain,
    BiologicDomain,
    BiologicFeature,
)
from backend.domain.models import (
    BiologicType,
    ChainType,
    DomainType,
    FeatureType,
)


class TestValidationService:
    """Test ValidationService"""

    @pytest.fixture
    def validation_service(self):
        """Create ValidationService instance"""
        return ValidationService()

    @pytest.fixture
    def mock_chain(self):
        """Create a mock BiologicChain"""
        chain = Mock(spec=BiologicChain)
        chain.name = "test_chain"
        chain.chain_type = ChainType.HEAVY

        # Create a mock sequence
        mock_sequence = Mock()
        mock_sequence.sequence_type = "PROTEIN"
        mock_sequence.sequence_data = "ACDEFGHIKLMNPQRSTVWY"
        mock_sequence.domains = []

        chain.sequences = [mock_sequence]
        return chain

    @pytest.fixture
    def mock_sequence(self, mock_chain):
        """Create a mock BiologicEntity"""
        sequence = Mock(spec=BiologicEntity)
        sequence.name = "test_sequence"
        sequence.biologic_type = "antibody"
        sequence.chains = [mock_chain]
        sequence.metadata = {}
        return sequence

    def test_validate_sequence_success(
        self, validation_service, mock_sequence
    ):
        """Test successful sequence validation"""
        result = validation_service.validate_sequence(mock_sequence)
        assert result is True

    def test_validate_sequence_none(self, validation_service):
        """Test sequence validation with None"""
        result = validation_service.validate_sequence(None)
        assert result is False

    def test_validate_sequence_empty_name(
        self, validation_service, mock_chain
    ):
        """Test sequence validation with empty name"""
        sequence = Mock(spec=BiologicEntity)
        sequence.name = ""
        sequence.biologic_type = "antibody"
        sequence.chains = [mock_chain]
        sequence.metadata = {}

        result = validation_service.validate_sequence(sequence)
        assert result is False

    def test_validate_sequence_no_chains(self, validation_service):
        """Test sequence validation with no chains"""
        sequence = Mock(spec=BiologicEntity)
        sequence.name = "test_sequence"
        sequence.biologic_type = "antibody"
        sequence.chains = []
        sequence.metadata = {}

        result = validation_service.validate_sequence(sequence)
        assert result is False

    def test_validate_sequence_invalid_chain(self, validation_service):
        """Test sequence validation with invalid chain"""
        sequence = Mock(spec=BiologicEntity)
        sequence.name = "test_sequence"
        sequence.biologic_type = "antibody"
        sequence.chains = [None]  # Invalid chain
        sequence.metadata = {}

        result = validation_service.validate_sequence(sequence)
        assert result is False

    def test_validate_chain_success(self, validation_service, mock_chain):
        """Test successful chain validation"""
        result = validation_service.validate_chain(mock_chain)
        assert result is True

    def test_validate_chain_none(self, validation_service):
        """Test chain validation with None"""
        result = validation_service.validate_chain(None)
        assert result is False

    def test_validate_chain_empty_name(self, validation_service):
        """Test chain validation with empty name"""
        chain = Mock(spec=BiologicChain)
        chain.name = ""
        chain.chain_type = ChainType.HEAVY

        # Create a mock sequence
        mock_sequence = Mock()
        mock_sequence.sequence_type = "PROTEIN"
        mock_sequence.sequence_data = "ACDEFGHIKLMNPQRSTVWY"
        mock_sequence.domains = []

        chain.sequences = [mock_sequence]

        result = validation_service.validate_chain(chain)
        assert result is False

    def test_validate_chain_empty_sequence(self, validation_service):
        """Test chain validation with empty sequence"""
        chain = Mock(spec=BiologicChain)
        chain.name = "test_chain"
        chain.chain_type = ChainType.HEAVY
        chain.sequences = []

        result = validation_service.validate_chain(chain)
        assert result is False

    def test_validate_chain_invalid_sequence(self, validation_service):
        """Test chain validation with invalid sequence"""
        chain = Mock(spec=BiologicChain)
        chain.name = "test_chain"
        chain.chain_type = ChainType.HEAVY

        # Create a mock sequence with invalid data
        mock_sequence = Mock()
        mock_sequence.sequence_type = "PROTEIN"
        mock_sequence.sequence_data = "INVALID123"
        mock_sequence.domains = []

        chain.sequences = [mock_sequence]

        result = validation_service.validate_chain(chain)
        assert result is False

    def test_validate_amino_acid_sequence_success(self, validation_service):
        """Test successful amino acid sequence validation"""
        valid_sequences = [
            "ACDEFGHIKLMNPQRSTVWY",
            "ACDEFGHIKLMNPQRSTVWYACDEFGHIKLMNPQRSTVWY",
            "A",  # Single amino acid
            "ACDEFGHIKLMNPQRSTVWYACDEFGHIKLMNPQRSTVWYACDEFGHIKLMNPQRSTVWY",
        ]

        for sequence in valid_sequences:
            result = validation_service.validate_amino_acid_sequence(sequence)
            assert result is True, f"Failed for sequence: {sequence}"

    def test_validate_amino_acid_sequence_empty(self, validation_service):
        """Test amino acid sequence validation with empty sequence"""
        result = validation_service.validate_amino_acid_sequence("")
        assert result is False

    def test_validate_amino_acid_sequence_none(self, validation_service):
        """Test amino acid sequence validation with None"""
        result = validation_service.validate_amino_acid_sequence(None)
        assert result is False

    def test_validate_amino_acid_sequence_invalid_chars(
        self, validation_service
    ):
        """Test amino acid sequence validation with invalid characters"""
        invalid_sequences = [
            "ACDEFGHIKLMNPQRSTVWY1",  # Contains number
            "ACDEFGHIKLMNPQRSTVWY!",  # Contains special character
            "ACDEFGHIKLMNPQRSTVWY ",  # Contains space
            "ACDEFGHIKLMNPQRSTVWY\n",  # Contains newline
            "ACDEFGHIKLMNPQRSTVWY\t",  # Contains tab
        ]

        for sequence in invalid_sequences:
            result = validation_service.validate_amino_acid_sequence(sequence)
            assert result is False, f"Should fail for sequence: {sequence}"

    def test_validate_sequences_success(
        self, validation_service, mock_sequence
    ):
        """Test successful sequences validation"""
        sequences = {"seq1": mock_sequence, "seq2": mock_sequence}
        result = validation_service.validate_sequences(sequences)
        assert result is True

    def test_validate_sequences_empty(self, validation_service):
        """Test sequences validation with empty dict"""
        result = validation_service.validate_sequences({})
        assert result is False

    def test_validate_sequences_none(self, validation_service):
        """Test sequences validation with None"""
        result = validation_service.validate_sequences(None)
        assert result is False

    def test_validate_sequences_empty_name(
        self, validation_service, mock_sequence
    ):
        """Test sequences validation with empty sequence name"""
        sequences = {"": mock_sequence}
        result = validation_service.validate_sequences(sequences)
        assert result is False

    def test_validate_sequences_invalid_type(self, validation_service):
        """Test sequences validation with invalid sequence type"""
        sequences = {"seq1": "not_a_biologic_entity"}
        result = validation_service.validate_sequences(sequences)
        assert result is False

    def test_validate_request_data_success(self, validation_service):
        """Test successful request data validation"""
        request_data = {"sequences": {"seq1": "data"}}
        result = validation_service.validate_request_data(request_data)
        assert result is True

    def test_validate_request_data_empty(self, validation_service):
        """Test request data validation with empty data"""
        result = validation_service.validate_request_data({})
        assert result is False

    def test_validate_request_data_none(self, validation_service):
        """Test request data validation with None"""
        result = validation_service.validate_request_data(None)
        assert result is False

    def test_validate_request_data_missing_sequences(self, validation_service):
        """Test request data validation with missing sequences field"""
        request_data = {"other_field": "value"}
        result = validation_service.validate_request_data(request_data)
        assert result is False


class TestResponseService:
    """Test ResponseService"""

    @pytest.fixture
    def response_service(self):
        """Create ResponseService instance"""
        return ResponseService()

    @pytest.fixture
    def mock_region(self):
        """Create a mock BiologicFeature (region)"""
        region = Mock(spec=BiologicFeature)
        region.name = "CDR1"
        region.feature_type = FeatureType.CDR1
        region.value = "ACDEFGHIKLMNPQRSTVWY"
        region.start_position = 1
        region.end_position = 20
        return region

    @pytest.fixture
    def mock_domain(self, mock_region):
        """Create a mock BiologicDomain"""
        domain = Mock(spec=BiologicDomain)
        domain.domain_type = DomainType.VARIABLE
        domain.start_position = 1
        domain.end_position = 40
        domain.features = [mock_region]
        return domain

    @pytest.fixture
    def mock_chain(self, mock_domain):
        """Create a mock BiologicChain"""
        chain = Mock(spec=BiologicChain)
        chain.name = "H"
        chain.chain_type = ChainType.HEAVY

        # Create a mock sequence with the domain
        mock_sequence = Mock()
        mock_sequence.sequence_type = "PROTEIN"
        mock_sequence.sequence_data = (
            "ACDEFGHIKLMNPQRSTVWYACDEFGHIKLMNPQRSTVWYACDEFGHIKLMNPQRSTVWY"
        )
        mock_sequence.domains = [mock_domain]

        chain.sequences = [mock_sequence]
        return chain

    @pytest.fixture
    def mock_sequence(self, mock_chain):
        """Create a mock BiologicEntity"""
        sequence = Mock(spec=BiologicEntity)
        sequence.name = "test_antibody"
        sequence.biologic_type = BiologicType.ANTIBODY
        sequence.chains = [mock_chain]
        return sequence

    def test_format_annotation_response_success(
        self, response_service, mock_sequence
    ):
        """Test successful annotation response formatting"""
        result = ProcessingResult(success=True, data=mock_sequence)

        response = response_service.format_annotation_response(result)

        assert response["success"] is True
        assert response["message"] == "Successfully annotated"
        assert "data" in response
        assert "sequence" in response["data"]
        assert response["data"]["sequence"]["name"] == "test_antibody"
        assert (
            response["data"]["sequence"]["biologic_type"]
            == BiologicType.ANTIBODY.value
        )
        assert len(response["data"]["sequence"]["chains"]) == 1

    def test_format_annotation_response_failure(self, response_service):
        """Test annotation response formatting with failure"""
        result = ProcessingResult(
            success=False, data=None, error="Annotation failed"
        )

        response = response_service.format_annotation_response(result)

        assert response["success"] is False
        assert response["error"] == "Annotation failed"
        assert response["data"] is None

    def test_format_annotation_response_exception(self, response_service):
        """Test annotation response formatting with exception"""
        result = ProcessingResult(
            success=True, data=None  # This will cause an exception
        )

        response = response_service.format_annotation_response(result)

        assert response["success"] is False
        assert "Response formatting error" in response["error"]

    def test_format_workflow_response_success(
        self, response_service, mock_sequence
    ):
        """Test successful workflow response formatting"""
        results = [
            {"name": "seq1", "success": True, "result": mock_sequence},
            {"name": "seq2", "success": False, "error": "Failed to annotate"},
        ]

        response = response_service.format_workflow_response(results)

        assert response["success"] is True
        assert response["message"] == "Workflow completed"
        assert "data" in response
        assert "results" in response["data"]
        assert "summary" in response["data"]
        assert response["data"]["summary"]["total"] == 2
        assert response["data"]["summary"]["successful"] == 1
        assert response["data"]["summary"]["failed"] == 1
        assert len(response["data"]["results"]) == 2

    def test_format_workflow_response_exception(self, response_service):
        """Test workflow response formatting with exception"""
        results = None  # This will cause an exception

        response = response_service.format_workflow_response(results)

        assert response["success"] is False
        assert "Workflow response formatting error" in response["error"]

    def test_create_error_response(self, response_service):
        """Test creating error response"""
        error_message = "Test error message"
        response = response_service.create_error_response(error_message)

        assert response["success"] is False
        assert response["error"] == error_message
        assert response["data"] is None

    def test_validate_response_data_success(self, response_service):
        """Test successful response data validation"""
        response_data = {"success": True, "data": "test"}
        result = response_service.validate_response_data(response_data)
        assert result is True

    def test_validate_response_data_empty(self, response_service):
        """Test response data validation with empty data"""
        result = response_service.validate_response_data({})
        assert result is False

    def test_validate_response_data_none(self, response_service):
        """Test response data validation with None"""
        result = response_service.validate_response_data(None)
        assert result is False

    def test_validate_response_data_missing_success(self, response_service):
        """Test response data validation with missing success field"""
        response_data = {"data": "test"}
        result = response_service.validate_response_data(response_data)
        assert result is False

    def test_validate_response_data_exception(self, response_service):
        """Test response data validation with exception"""
        # Pass something that will cause an exception
        result = response_service.validate_response_data(123)
        assert result is False
