"""
Integration tests for the complete command pattern implementation.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from backend.application.commands import ProcessAnnotationCommand
from backend.application.handlers import WorkflowHandler
from backend.application.services.annotation_service import AnnotationService
from backend.application.services.validation_service import ValidationService
from backend.application.services.response_service import ResponseService
from backend.application.services.biologic_service import BiologicService
from backend.core.interfaces import ProcessingResult
from backend.domain.entities import BiologicEntity, BiologicChain
from backend.domain.models import ChainType


class TestCommandPatternIntegration:
    """Integration tests for the command pattern"""

    @pytest.fixture
    def mock_services(self):
        """Create mock services for integration testing"""
        annotation_service = Mock(spec=AnnotationService)
        validation_service = Mock(spec=ValidationService)
        response_service = Mock(spec=ResponseService)
        biologic_service = Mock(spec=BiologicService)

        return (
            annotation_service,
            validation_service,
            response_service,
            biologic_service,
        )

    @pytest.fixture
    def handler(self, mock_services):
        """Create WorkflowHandler with mock services"""
        (
            annotation_service,
            validation_service,
            response_service,
            biologic_service,
        ) = mock_services
        return WorkflowHandler(
            annotation_service=annotation_service,
            validation_service=validation_service,
            response_service=response_service,
            biologic_service=biologic_service,
        )

    @pytest.fixture
    def mock_sequence(self):
        """Create a mock BiologicEntity"""
        sequence = Mock(spec=BiologicEntity)
        sequence.name = "test_antibody"
        sequence.biologic_type = "antibody"
        sequence.chains = []
        return sequence

    @pytest.mark.asyncio
    async def test_complete_annotation_workflow_success(
        self, handler, mock_services, mock_sequence
    ):
        """Test complete annotation workflow with success"""
        (
            annotation_service,
            validation_service,
            response_service,
            biologic_service,
        ) = mock_services

        # Mock service responses
        validation_service.validate_sequences.return_value = True
        annotation_service.annotate_sequence.return_value = ProcessingResult(
            success=True, data=mock_sequence
        )
        biologic_service.process_and_persist_biologic_entity = AsyncMock()
        response_service.format_workflow_response.return_value = {
            "success": True,
            "data": {
                "results": [{"name": "test_antibody", "success": True}],
                "summary": {"total": 1, "successful": 1, "failed": 0},
            },
        }

        # Create command
        command = ProcessAnnotationCommand(
            {
                "sequences": {"test_antibody": mock_sequence},
                "numbering_scheme": "imgt",
                "persist_to_database": True,
                "organism": "human",
            }
        )

        # Execute the workflow
        result = await handler.handle(command)

        # Verify the result
        assert result["success"] is True
        assert result["data"]["data"]["summary"]["total"] == 1
        assert result["data"]["data"]["summary"]["successful"] == 1
        assert result["data"]["data"]["summary"]["failed"] == 0

        # Verify service interactions
        validation_service.validate_sequences.assert_called_once_with(
            {"test_antibody": mock_sequence}
        )
        annotation_service.annotate_sequence.assert_called_once_with(
            mock_sequence, "imgt"
        )
        biologic_service.process_and_persist_biologic_entity.assert_called_once_with(
            mock_sequence, "human"
        )
        response_service.format_workflow_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_complete_annotation_workflow_without_persistence(
        self, handler, mock_services, mock_sequence
    ):
        """Test complete annotation workflow without persistence"""
        (
            annotation_service,
            validation_service,
            response_service,
            biologic_service,
        ) = mock_services

        # Mock service responses
        validation_service.validate_sequences.return_value = True
        annotation_service.annotate_sequence.return_value = ProcessingResult(
            success=True, data=mock_sequence
        )
        response_service.format_workflow_response.return_value = {
            "success": True,
            "data": {
                "results": [{"name": "test_antibody", "success": True}],
                "summary": {"total": 1, "successful": 1, "failed": 0},
            },
        }

        # Create command
        command = ProcessAnnotationCommand(
            {
                "sequences": {"test_antibody": mock_sequence},
                "numbering_scheme": "imgt",
                "persist_to_database": False,
            }
        )

        # Execute the workflow
        result = await handler.handle(command)

        # Verify the result
        assert result["success"] is True
        assert result["data"]["data"]["summary"]["total"] == 1
        assert result["data"]["data"]["summary"]["successful"] == 1

        # Verify service interactions
        validation_service.validate_sequences.assert_called_once_with(
            {"test_antibody": mock_sequence}
        )
        annotation_service.annotate_sequence.assert_called_once_with(
            mock_sequence, "imgt"
        )
        biologic_service.process_and_persist_biologic_entity.assert_not_called()
        response_service.format_workflow_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_complete_annotation_workflow_multiple_sequences(
        self, handler, mock_services
    ):
        """Test complete annotation workflow with multiple sequences"""
        (
            annotation_service,
            validation_service,
            response_service,
            biologic_service,
        ) = mock_services

        # Create multiple mock sequences
        seq1 = Mock(spec=BiologicEntity)
        seq1.name = "antibody_1"
        seq1.biologic_type = "antibody"
        seq1.chains = []

        seq2 = Mock(spec=BiologicEntity)
        seq2.name = "antibody_2"
        seq2.biologic_type = "antibody"
        seq2.chains = []

        # Mock service responses
        validation_service.validate_sequences.return_value = True
        annotation_service.annotate_sequence.side_effect = [
            ProcessingResult(success=True, data=seq1),
            ProcessingResult(success=True, data=seq2),
        ]
        biologic_service.process_and_persist_biologic_entity = AsyncMock()
        response_service.format_workflow_response.return_value = {
            "success": True,
            "data": {
                "results": [
                    {"name": "antibody_1", "success": True},
                    {"name": "antibody_2", "success": True},
                ],
                "summary": {"total": 2, "successful": 2, "failed": 0},
            },
        }

        # Create command
        command = ProcessAnnotationCommand(
            {
                "sequences": {"antibody_1": seq1, "antibody_2": seq2},
                "numbering_scheme": "imgt",
                "persist_to_database": True,
                "organism": "mouse",
            }
        )

        # Execute the workflow
        result = await handler.handle(command)

        # Verify the result
        assert result["success"] is True
        assert result["data"]["data"]["summary"]["total"] == 2
        assert result["data"]["data"]["summary"]["successful"] == 2
        assert result["data"]["data"]["summary"]["failed"] == 0

        # Verify service interactions
        validation_service.validate_sequences.assert_called_once_with(
            {"antibody_1": seq1, "antibody_2": seq2}
        )
        assert annotation_service.annotate_sequence.call_count == 2
        assert (
            biologic_service.process_and_persist_biologic_entity.call_count
            == 2
        )
        response_service.format_workflow_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_complete_annotation_workflow_partial_failure(
        self, handler, mock_services
    ):
        """Test complete annotation workflow with partial failures"""
        (
            annotation_service,
            validation_service,
            response_service,
            biologic_service,
        ) = mock_services

        # Create multiple mock sequences
        seq1 = Mock(spec=BiologicEntity)
        seq1.name = "antibody_1"
        seq1.biologic_type = "antibody"
        seq1.chains = []

        seq2 = Mock(spec=BiologicEntity)
        seq2.name = "antibody_2"
        seq2.biologic_type = "antibody"
        seq2.chains = []

        # Mock service responses
        validation_service.validate_sequences.return_value = True
        annotation_service.annotate_sequence.side_effect = [
            ProcessingResult(success=True, data=seq1),
            ProcessingResult(
                success=False, data=None, error="Annotation failed"
            ),
        ]
        biologic_service.process_and_persist_biologic_entity = AsyncMock()
        response_service.format_workflow_response.return_value = {
            "success": True,
            "data": {
                "results": [
                    {"name": "antibody_1", "success": True},
                    {
                        "name": "antibody_2",
                        "success": False,
                        "error": "Annotation failed",
                    },
                ],
                "summary": {"total": 2, "successful": 1, "failed": 1},
            },
        }

        # Create command
        command = ProcessAnnotationCommand(
            {
                "sequences": {"antibody_1": seq1, "antibody_2": seq2},
                "numbering_scheme": "imgt",
                "persist_to_database": True,
                "organism": "human",
            }
        )

        # Execute the workflow
        result = await handler.handle(command)

        # Verify the result
        assert result["success"] is True
        assert result["data"]["data"]["summary"]["total"] == 2
        assert result["data"]["data"]["summary"]["successful"] == 1
        assert result["data"]["data"]["summary"]["failed"] == 1

        # Verify service interactions
        validation_service.validate_sequences.assert_called_once_with(
            {"antibody_1": seq1, "antibody_2": seq2}
        )
        assert annotation_service.annotate_sequence.call_count == 2
        biologic_service.process_and_persist_biologic_entity.assert_called_once_with(
            seq1, "human"
        )
        response_service.format_workflow_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_complete_annotation_workflow_validation_failure(
        self, handler, mock_services, mock_sequence
    ):
        """Test complete annotation workflow with validation failure"""
        (
            annotation_service,
            validation_service,
            response_service,
            biologic_service,
        ) = mock_services

        # Mock validation failure
        validation_service.validate_sequences.return_value = False

        # Create command
        command = ProcessAnnotationCommand(
            {
                "sequences": {"test_antibody": mock_sequence},
                "numbering_scheme": "IMGT",
                "persist_to_database": False,
            }
        )

        # Execute the workflow
        result = await handler.handle(command)

        # Verify error response
        assert result["success"] is False
        assert result["error"] == "Invalid sequences data"

        # Verify no annotation or persistence calls
        annotation_service.annotate_sequence.assert_not_called()
        biologic_service.process_and_persist_biologic_entity.assert_not_called()
        response_service.format_workflow_response.assert_not_called()

    @pytest.mark.asyncio
    async def test_complete_annotation_workflow_command_failure(
        self, handler, mock_services
    ):
        """Test complete annotation workflow with command execution failure"""
        (
            annotation_service,
            validation_service,
            response_service,
            biologic_service,
        ) = mock_services

        # Create command that will fail validation
        command = ProcessAnnotationCommand(
            {"numbering_scheme": "IMGT"}  # Missing sequences
        )

        # Execute the workflow
        result = await handler.handle(command)

        # Verify error response
        assert result["success"] is False
        assert "Invalid annotation workflow request data" in result["error"]

        # Verify no service calls
        validation_service.validate_sequences.assert_not_called()
        annotation_service.annotate_sequence.assert_not_called()
        biologic_service.process_and_persist_biologic_entity.assert_not_called()
        response_service.format_workflow_response.assert_not_called()

    @pytest.mark.asyncio
    async def test_complete_annotation_workflow_different_numbering_schemes(
        self, handler, mock_services, mock_sequence
    ):
        """Test complete annotation workflow with different numbering schemes"""
        (
            annotation_service,
            validation_service,
            response_service,
            biologic_service,
        ) = mock_services

        numbering_schemes = ["IMGT", "KABAT", "CHOTHIA"]

        for scheme in numbering_schemes:
            # Reset mocks
            validation_service.reset_mock()
            annotation_service.reset_mock()
            biologic_service.reset_mock()
            response_service.reset_mock()

            # Mock service responses
            validation_service.validate_sequences.return_value = True
            annotation_service.annotate_sequence.return_value = (
                ProcessingResult(success=True, data=mock_sequence)
            )
            biologic_service.process_and_persist_biologic_entity = AsyncMock()
            response_service.format_workflow_response.return_value = {
                "success": True,
                "data": {
                    "results": [{"name": "test_antibody", "success": True}],
                    "summary": {"total": 1, "successful": 1, "failed": 0},
                },
            }

            # Create command with different numbering scheme
            command = ProcessAnnotationCommand(
                {
                    "sequences": {"test_antibody": mock_sequence},
                    "numbering_scheme": scheme,
                    "persist_to_database": False,
                }
            )

            # Execute the workflow
            result = await handler.handle(command)

            # Verify the result
            assert result["success"] is True

            # Verify annotation was called with correct numbering scheme (converted to lowercase)
            annotation_service.annotate_sequence.assert_called_once_with(
                mock_sequence, scheme.lower()
            )

    @pytest.mark.asyncio
    async def test_complete_annotation_workflow_exception_handling(
        self, handler, mock_services, mock_sequence
    ):
        """Test complete annotation workflow exception handling"""
        (
            annotation_service,
            validation_service,
            response_service,
            biologic_service,
        ) = mock_services

        # Mock validation to raise an exception
        validation_service.validate_sequences.side_effect = Exception(
            "Unexpected error"
        )

        # Create command
        command = ProcessAnnotationCommand(
            {
                "sequences": {"test_antibody": mock_sequence},
                "numbering_scheme": "IMGT",
                "persist_to_database": False,
            }
        )

        # Execute the workflow
        result = await handler.handle(command)

        # Verify error response
        assert result["success"] is False
        assert "Workflow handler error" in result["error"]
        assert "Unexpected error" in result["error"]

        # Verify no annotation or persistence calls
        annotation_service.annotate_sequence.assert_not_called()
        biologic_service.process_and_persist_biologic_entity.assert_not_called()
        response_service.format_workflow_response.assert_not_called()
