"""
Tests for command handlers in the command pattern implementation.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from backend.application.handlers import (
    BaseHandler,
    AnnotationHandler,
    WorkflowHandler,
)
from backend.application.commands import (
    AnnotateSequenceCommand,
    ProcessAnnotationCommand,
    CommandResult,
)
from backend.application.services.annotation_service import AnnotationService
from backend.application.services.validation_service import ValidationService
from backend.application.services.response_service import ResponseService
from backend.application.services.biologic_service import BiologicService
from backend.core.interfaces import ProcessingResult
from backend.domain.entities import BiologicEntity, BiologicChain
from backend.domain.models import ChainType


class TestBaseHandler:
    """Test BaseHandler abstract class"""

    def test_base_handler_creation(self):
        """Test creating a BaseHandler subclass"""

        class TestHandler(BaseHandler):
            async def handle(self, command):
                return {"success": True, "data": "test"}

        handler = TestHandler()
        assert handler is not None

    def test_create_error_response(self):
        """Test creating error response"""

        class TestHandler(BaseHandler):
            async def handle(self, command):
                return {"success": True, "data": "test"}

        handler = TestHandler()
        error_response = handler._create_error_response("Test error")

        assert error_response["success"] is False
        assert error_response["error"] == "Test error"
        assert error_response["data"] is None

    def test_create_success_response(self):
        """Test creating success response"""

        class TestHandler(BaseHandler):
            async def handle(self, command):
                return {"success": True, "data": "test"}

        handler = TestHandler()
        success_response = handler._create_success_response({"test": "data"})

        assert success_response["success"] is True
        assert success_response["error"] is None
        assert success_response["data"] == {"test": "data"}


class TestAnnotationHandler:
    """Test AnnotationHandler"""

    @pytest.fixture
    def mock_services(self):
        """Create mock services for testing"""
        annotation_service = Mock(spec=AnnotationService)
        validation_service = Mock(spec=ValidationService)
        response_service = Mock(spec=ResponseService)

        return annotation_service, validation_service, response_service

    @pytest.fixture
    def handler(self, mock_services):
        """Create AnnotationHandler with mock services"""
        annotation_service, validation_service, response_service = (
            mock_services
        )
        return AnnotationHandler(
            annotation_service=annotation_service,
            validation_service=validation_service,
            response_service=response_service,
        )

    @pytest.fixture
    def mock_sequence(self):
        """Create a mock BiologicEntity"""
        sequence = Mock(spec=BiologicEntity)
        sequence.name = "test_sequence"
        sequence.biologic_type = "antibody"
        sequence.chains = []
        return sequence

    @pytest.mark.asyncio
    async def test_handle_success(self, handler, mock_services, mock_sequence):
        """Test successful command handling"""
        annotation_service, validation_service, response_service = (
            mock_services
        )

        # Mock command execution
        command_result = CommandResult(
            success=True,
            data={"sequence": mock_sequence, "numbering_scheme": "IMGT"},
        )

        # Mock service responses
        validation_service.validate_sequence.return_value = True
        annotation_service.annotate_sequence.return_value = ProcessingResult(
            success=True, data=mock_sequence
        )
        response_service.format_annotation_response.return_value = {
            "success": True,
            "data": {"sequence": "annotated_data"},
        }

        # Create command
        command = AnnotateSequenceCommand(
            {"sequence": mock_sequence, "numbering_scheme": "IMGT"}
        )

        # Mock command.execute to return our result
        with patch.object(command, "execute", return_value=command_result):
            result = await handler.handle(command)

        # Verify the result
        assert result["success"] is True
        assert result["data"]["data"]["sequence"] == "annotated_data"

        # Verify service calls
        validation_service.validate_sequence.assert_called_once_with(
            mock_sequence
        )
        annotation_service.annotate_sequence.assert_called_once_with(
            mock_sequence, "IMGT"
        )
        response_service.format_annotation_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_command_execution_failure(
        self, handler, mock_services
    ):
        """Test handling when command execution fails"""
        annotation_service, validation_service, response_service = (
            mock_services
        )

        # Create command that will fail
        command = AnnotateSequenceCommand(
            {"numbering_scheme": "IMGT"}  # Missing sequence
        )

        result = await handler.handle(command)

        # Verify error response
        assert result["success"] is False
        assert "Invalid annotation request data" in result["error"]

        # Verify no service calls were made
        validation_service.validate_sequence.assert_not_called()
        annotation_service.annotate_sequence.assert_not_called()
        response_service.format_annotation_response.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_validation_failure(
        self, handler, mock_services, mock_sequence
    ):
        """Test handling when validation fails"""
        annotation_service, validation_service, response_service = (
            mock_services
        )

        # Mock command execution
        command_result = CommandResult(
            success=True,
            data={"sequence": mock_sequence, "numbering_scheme": "IMGT"},
        )

        # Mock validation failure
        validation_service.validate_sequence.return_value = False

        # Create command
        command = AnnotateSequenceCommand(
            {"sequence": mock_sequence, "numbering_scheme": "IMGT"}
        )

        # Mock command.execute to return our result
        with patch.object(command, "execute", return_value=command_result):
            result = await handler.handle(command)

        # Verify error response
        assert result["success"] is False
        assert result["error"] == "Invalid sequence data"

        # Verify validation was called but annotation was not
        validation_service.validate_sequence.assert_called_once_with(
            mock_sequence
        )
        annotation_service.annotate_sequence.assert_not_called()
        response_service.format_annotation_response.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_annotation_failure(
        self, handler, mock_services, mock_sequence
    ):
        """Test handling when annotation fails"""
        annotation_service, validation_service, response_service = (
            mock_services
        )

        # Mock command execution
        command_result = CommandResult(
            success=True,
            data={"sequence": mock_sequence, "numbering_scheme": "IMGT"},
        )

        # Mock service responses
        validation_service.validate_sequence.return_value = True
        annotation_service.annotate_sequence.return_value = ProcessingResult(
            success=False, data=None, error="Annotation failed"
        )

        # Create command
        command = AnnotateSequenceCommand(
            {"sequence": mock_sequence, "numbering_scheme": "IMGT"}
        )

        # Mock command.execute to return our result
        with patch.object(command, "execute", return_value=command_result):
            result = await handler.handle(command)

        # Verify error response
        assert result["success"] is False
        assert "Annotation failed" in result["error"]

        # Verify service calls
        validation_service.validate_sequence.assert_called_once_with(
            mock_sequence
        )
        annotation_service.annotate_sequence.assert_called_once_with(
            mock_sequence, "IMGT"
        )
        response_service.format_annotation_response.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_exception(
        self, handler, mock_services, mock_sequence
    ):
        """Test handling when an exception occurs"""
        annotation_service, validation_service, response_service = (
            mock_services
        )

        # Mock command execution
        command_result = CommandResult(
            success=True,
            data={"sequence": mock_sequence, "numbering_scheme": "IMGT"},
        )

        # Mock validation to raise an exception
        validation_service.validate_sequence.side_effect = Exception(
            "Test exception"
        )

        # Create command
        command = AnnotateSequenceCommand(
            {"sequence": mock_sequence, "numbering_scheme": "IMGT"}
        )

        # Mock command.execute to return our result
        with patch.object(command, "execute", return_value=command_result):
            result = await handler.handle(command)

        # Verify error response
        assert result["success"] is False
        assert "Annotation handler error" in result["error"]


class TestWorkflowHandler:
    """Test WorkflowHandler"""

    @pytest.fixture
    def mock_services(self):
        """Create mock services for testing"""
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
        sequence.name = "test_sequence"
        sequence.biologic_type = "antibody"
        sequence.chains = []
        return sequence

    @pytest.mark.asyncio
    async def test_handle_success(self, handler, mock_services, mock_sequence):
        """Test successful workflow handling"""
        (
            annotation_service,
            validation_service,
            response_service,
            biologic_service,
        ) = mock_services

        # Mock command execution
        command_result = CommandResult(
            success=True,
            data={
                "sequences": {"seq1": mock_sequence},
                "numbering_scheme": "IMGT",
                "persist_to_database": True,
                "organism": "human",
            },
        )

        # Mock service responses
        validation_service.validate_sequences.return_value = True
        annotation_service.annotate_sequence.return_value = ProcessingResult(
            success=True, data=mock_sequence
        )
        biologic_service.process_and_persist_biologic_entity = AsyncMock()
        response_service.format_workflow_response.return_value = {
            "success": True,
            "data": {"results": [{"name": "seq1", "success": True}]},
        }

        # Create command
        command = ProcessAnnotationCommand(
            {
                "sequences": {"seq1": mock_sequence},
                "numbering_scheme": "IMGT",
                "persist_to_database": True,
                "organism": "human",
            }
        )

        # Mock command.execute to return our result
        with patch.object(command, "execute", return_value=command_result):
            result = await handler.handle(command)

        # Verify the result
        assert result["success"] is True
        assert result["data"]["data"]["results"][0]["name"] == "seq1"
        assert result["data"]["data"]["results"][0]["success"] is True

        # Verify service calls
        validation_service.validate_sequences.assert_called_once_with(
            {"seq1": mock_sequence}
        )
        annotation_service.annotate_sequence.assert_called_once_with(
            mock_sequence, "IMGT"
        )
        biologic_service.process_and_persist_biologic_entity.assert_called_once_with(
            mock_sequence, "human"
        )
        response_service.format_workflow_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_command_execution_failure(
        self, handler, mock_services
    ):
        """Test handling when command execution fails"""
        (
            annotation_service,
            validation_service,
            response_service,
            biologic_service,
        ) = mock_services

        # Create command that will fail
        command = ProcessAnnotationCommand(
            {"numbering_scheme": "IMGT"}  # Missing sequences
        )

        result = await handler.handle(command)

        # Verify error response
        assert result["success"] is False
        assert "Invalid annotation workflow request data" in result["error"]

        # Verify no service calls were made
        validation_service.validate_sequences.assert_not_called()
        annotation_service.annotate_sequence.assert_not_called()
        biologic_service.process_and_persist_biologic_entity.assert_not_called()
        response_service.format_workflow_response.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_validation_failure(
        self, handler, mock_services, mock_sequence
    ):
        """Test handling when validation fails"""
        (
            annotation_service,
            validation_service,
            response_service,
            biologic_service,
        ) = mock_services

        # Mock command execution
        command_result = CommandResult(
            success=True,
            data={
                "sequences": {"seq1": mock_sequence},
                "numbering_scheme": "IMGT",
                "persist_to_database": False,
                "organism": None,
            },
        )

        # Mock validation failure
        validation_service.validate_sequences.return_value = False

        # Create command
        command = ProcessAnnotationCommand(
            {
                "sequences": {"seq1": mock_sequence},
                "numbering_scheme": "IMGT",
                "persist_to_database": False,
            }
        )

        # Mock command.execute to return our result
        with patch.object(command, "execute", return_value=command_result):
            result = await handler.handle(command)

        # Verify error response
        assert result["success"] is False
        assert result["error"] == "Invalid sequences data"

        # Verify validation was called but annotation was not
        validation_service.validate_sequences.assert_called_once_with(
            {"seq1": mock_sequence}
        )
        annotation_service.annotate_sequence.assert_not_called()
        biologic_service.process_and_persist_biologic_entity.assert_not_called()
        response_service.format_workflow_response.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_annotation_failure(
        self, handler, mock_services, mock_sequence
    ):
        """Test handling when annotation fails for a sequence"""
        (
            annotation_service,
            validation_service,
            response_service,
            biologic_service,
        ) = mock_services

        # Mock command execution
        command_result = CommandResult(
            success=True,
            data={
                "sequences": {"seq1": mock_sequence},
                "numbering_scheme": "IMGT",
                "persist_to_database": False,
                "organism": None,
            },
        )

        # Mock service responses
        validation_service.validate_sequences.return_value = True
        annotation_service.annotate_sequence.return_value = ProcessingResult(
            success=False, data=None, error="Annotation failed"
        )
        response_service.format_workflow_response.return_value = {
            "success": True,
            "data": {
                "results": [
                    {
                        "name": "seq1",
                        "success": False,
                        "error": "Annotation failed",
                    }
                ],
                "summary": {"total": 1, "successful": 0, "failed": 1},
            },
        }

        # Create command
        command = ProcessAnnotationCommand(
            {
                "sequences": {"seq1": mock_sequence},
                "numbering_scheme": "IMGT",
                "persist_to_database": False,
            }
        )

        # Mock command.execute to return our result
        with patch.object(command, "execute", return_value=command_result):
            result = await handler.handle(command)

        # Verify the result
        assert result["success"] is True
        assert result["data"]["data"]["summary"]["failed"] == 1

        # Verify service calls
        validation_service.validate_sequences.assert_called_once_with(
            {"seq1": mock_sequence}
        )
        annotation_service.annotate_sequence.assert_called_once_with(
            mock_sequence, "IMGT"
        )
        biologic_service.process_and_persist_biologic_entity.assert_not_called()
        response_service.format_workflow_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_multiple_sequences(self, handler, mock_services):
        """Test handling multiple sequences"""
        (
            annotation_service,
            validation_service,
            response_service,
            biologic_service,
        ) = mock_services

        # Create multiple mock sequences
        seq1 = Mock(spec=BiologicEntity)
        seq1.name = "seq1"
        seq2 = Mock(spec=BiologicEntity)
        seq2.name = "seq2"

        # Mock command execution
        command_result = CommandResult(
            success=True,
            data={
                "sequences": {"seq1": seq1, "seq2": seq2},
                "numbering_scheme": "IMGT",
                "persist_to_database": False,
                "organism": None,
            },
        )

        # Mock service responses
        validation_service.validate_sequences.return_value = True
        annotation_service.annotate_sequence.side_effect = [
            ProcessingResult(success=True, data=seq1),
            ProcessingResult(success=False, data=None, error="Failed"),
        ]
        response_service.format_workflow_response.return_value = {
            "success": True,
            "data": {
                "results": [
                    {"name": "seq1", "success": True},
                    {"name": "seq2", "success": False, "error": "Failed"},
                ],
                "summary": {"total": 2, "successful": 1, "failed": 1},
            },
        }

        # Create command
        command = ProcessAnnotationCommand(
            {
                "sequences": {"seq1": seq1, "seq2": seq2},
                "numbering_scheme": "IMGT",
                "persist_to_database": False,
            }
        )

        # Mock command.execute to return our result
        with patch.object(command, "execute", return_value=command_result):
            result = await handler.handle(command)

        # Verify the result
        assert result["success"] is True
        assert result["data"]["data"]["summary"]["total"] == 2
        assert result["data"]["data"]["summary"]["successful"] == 1
        assert result["data"]["data"]["summary"]["failed"] == 1

        # Verify service calls
        validation_service.validate_sequences.assert_called_once_with(
            {"seq1": seq1, "seq2": seq2}
        )
        assert annotation_service.annotate_sequence.call_count == 2
        biologic_service.process_and_persist_biologic_entity.assert_not_called()
        response_service.format_workflow_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_exception(
        self, handler, mock_services, mock_sequence
    ):
        """Test handling when an exception occurs"""
        (
            annotation_service,
            validation_service,
            response_service,
            biologic_service,
        ) = mock_services

        # Mock command execution
        command_result = CommandResult(
            success=True,
            data={
                "sequences": {"seq1": mock_sequence},
                "numbering_scheme": "IMGT",
                "persist_to_database": False,
                "organism": None,
            },
        )

        # Mock validation to raise an exception
        validation_service.validate_sequences.side_effect = Exception(
            "Test exception"
        )

        # Create command
        command = ProcessAnnotationCommand(
            {
                "sequences": {"seq1": mock_sequence},
                "numbering_scheme": "IMGT",
                "persist_to_database": False,
            }
        )

        # Mock command.execute to return our result
        with patch.object(command, "execute", return_value=command_result):
            result = await handler.handle(command)

        # Verify error response
        assert result["success"] is False
        assert "Workflow handler error" in result["error"]
