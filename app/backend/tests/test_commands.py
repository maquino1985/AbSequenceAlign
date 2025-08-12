"""
Tests for command objects in the command pattern implementation.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from backend.application.commands import (
    BaseCommand,
    AnnotateSequenceCommand,
    AlignSequencesCommand,
    ProcessAnnotationCommand,
    CommandResult,
)
from backend.domain.entities import (
    BiologicEntity,
    BiologicChain,
    BiologicSequence,
)
from backend.domain.models import ChainType, DomainType


class TestCommandResult:
    """Test CommandResult dataclass"""

    def test_command_result_creation(self):
        """Test creating a CommandResult"""
        result = CommandResult(
            success=True,
            data={"test": "data"},
            error=None,
            execution_time=1.5,
            metadata={"key": "value"},
        )

        assert result.success is True
        assert result.data == {"test": "data"}
        assert result.error is None
        assert result.execution_time == 1.5
        assert result.metadata == {"key": "value"}

    def test_command_result_error(self):
        """Test creating a CommandResult with error"""
        result = CommandResult(
            success=False, data=None, error="Test error", execution_time=0.5
        )

        assert result.success is False
        assert result.data is None
        assert result.error == "Test error"
        assert result.execution_time == 0.5


class TestBaseCommand:
    """Test BaseCommand abstract class"""

    def test_base_command_creation(self):
        """Test creating a BaseCommand subclass"""

        class TestCommand(BaseCommand):
            def validate(self) -> bool:
                return True

            def execute(self) -> CommandResult:
                return CommandResult(success=True, data={"test": "data"})

        command = TestCommand({"test": "request"})
        assert command.request_data == {"test": "request"}
        assert command.execution_start is None
        assert command.execution_end is None

    def test_get_execution_time(self):
        """Test getting execution time"""

        class TestCommand(BaseCommand):
            def validate(self) -> bool:
                return True

            def execute(self) -> CommandResult:
                return CommandResult(success=True, data={"test": "data"})

        command = TestCommand({"test": "request"})

        # No execution time when not executed
        assert command.get_execution_time() is None

        # Set execution times
        command.execution_start = datetime(2023, 1, 1, 12, 0, 0)
        command.execution_end = datetime(2023, 1, 1, 12, 0, 1)

        assert command.get_execution_time() == 1.0

    def test_string_representation(self):
        """Test string representation of command"""

        class TestCommand(BaseCommand):
            def validate(self) -> bool:
                return True

            def execute(self) -> CommandResult:
                return CommandResult(success=True, data={"test": "data"})

        command = TestCommand({"test": "request"})
        assert str(command) == "TestCommand(data={'test': 'request'})"
        assert repr(command) == "TestCommand(data={'test': 'request'})"


class TestAnnotateSequenceCommand:
    """Test AnnotateSequenceCommand"""

    def test_annotate_sequence_command_creation(self):
        """Test creating AnnotateSequenceCommand"""
        request_data = {
            "sequence": Mock(spec=BiologicEntity),
            "numbering_scheme": "IMGT",
        }

        command = AnnotateSequenceCommand(request_data)
        assert command.request_data == request_data
        assert command.sequence is None
        assert command.numbering_scheme == "IMGT"

    def test_validate_success(self):
        """Test successful validation"""
        request_data = {
            "sequence": Mock(spec=BiologicEntity),
            "numbering_scheme": "IMGT",
        }

        command = AnnotateSequenceCommand(request_data)
        assert command.validate() is True
        assert command.numbering_scheme == "IMGT"

    def test_validate_missing_sequence(self):
        """Test validation with missing sequence"""
        request_data = {"numbering_scheme": "IMGT"}

        command = AnnotateSequenceCommand(request_data)
        assert command.validate() is False

    def test_validate_invalid_numbering_scheme(self):
        """Test validation with invalid numbering scheme"""
        request_data = {
            "sequence": Mock(spec=BiologicEntity),
            "numbering_scheme": "INVALID",
        }

        command = AnnotateSequenceCommand(request_data)
        assert command.validate() is False

    def test_validate_valid_numbering_schemes(self):
        """Test validation with all valid numbering schemes"""
        valid_schemes = ["IMGT", "KABAT", "CHOTHIA"]

        for scheme in valid_schemes:
            request_data = {
                "sequence": Mock(spec=BiologicEntity),
                "numbering_scheme": scheme,
            }

            command = AnnotateSequenceCommand(request_data)
            assert command.validate() is True
            assert command.numbering_scheme == scheme

    def test_execute_success(self):
        """Test successful command execution"""
        mock_sequence = Mock(spec=BiologicEntity)
        request_data = {"sequence": mock_sequence, "numbering_scheme": "IMGT"}

        command = AnnotateSequenceCommand(request_data)
        result = command.execute()

        assert result.success is True
        assert result.data["sequence"] == mock_sequence
        assert result.data["numbering_scheme"] == "IMGT"
        assert result.metadata["command_type"] == "annotate_sequence"
        assert result.execution_time is not None

    def test_execute_validation_failure(self):
        """Test command execution with validation failure"""
        request_data = {"numbering_scheme": "IMGT"}  # Missing sequence

        command = AnnotateSequenceCommand(request_data)
        result = command.execute()

        assert result.success is False
        assert "Invalid annotation request data" in result.error

    def test_execute_conversion_not_implemented(self):
        """Test command execution with non-BiologicEntity sequence"""
        request_data = {
            "sequence": {"name": "test", "sequence": "ABCDEF"},
            "numbering_scheme": "IMGT",
        }

        command = AnnotateSequenceCommand(request_data)
        result = command.execute()

        assert result.success is False
        assert "conversion not implemented" in result.error


class TestAlignSequencesCommand:
    """Test AlignSequencesCommand"""

    def test_align_sequences_command_creation(self):
        """Test creating AlignSequencesCommand"""
        request_data = {
            "sequences": [
                Mock(spec=BiologicEntity),
                Mock(spec=BiologicEntity),
            ],
            "strategy": "multiple",
        }

        command = AlignSequencesCommand(request_data)
        assert command.request_data == request_data
        assert command.sequences == []
        assert command.alignment_strategy == "multiple"
        assert command.region_type is None

    def test_validate_success(self):
        """Test successful validation"""
        request_data = {
            "sequences": [
                Mock(spec=BiologicEntity),
                Mock(spec=BiologicEntity),
            ],
            "strategy": "multiple",
        }

        command = AlignSequencesCommand(request_data)
        assert command.validate() is True
        assert command.alignment_strategy == "multiple"

    def test_validate_missing_sequences(self):
        """Test validation with missing sequences"""
        request_data = {"strategy": "multiple"}

        command = AlignSequencesCommand(request_data)
        assert command.validate() is False

    def test_validate_insufficient_sequences(self):
        """Test validation with insufficient sequences"""
        request_data = {
            "sequences": [Mock(spec=BiologicEntity)],  # Only 1 sequence
            "strategy": "multiple",
        }

        command = AlignSequencesCommand(request_data)
        assert command.validate() is False

    def test_validate_invalid_strategy(self):
        """Test validation with invalid strategy"""
        request_data = {
            "sequences": [
                Mock(spec=BiologicEntity),
                Mock(spec=BiologicEntity),
            ],
            "strategy": "invalid",
        }

        command = AlignSequencesCommand(request_data)
        assert command.validate() is False

    def test_validate_valid_strategies(self):
        """Test validation with all valid strategies"""
        valid_strategies = ["pairwise", "multiple", "region_specific"]

        for strategy in valid_strategies:
            request_data = {
                "sequences": [
                    Mock(spec=BiologicEntity),
                    Mock(spec=BiologicEntity),
                ],
                "strategy": strategy,
            }

            command = AlignSequencesCommand(request_data)
            assert command.validate() is True
            assert command.alignment_strategy == strategy

    def test_validate_valid_region_types(self):
        """Test validation with valid region types"""
        valid_region_types = ["CDR", "FR", "full"]

        for region_type in valid_region_types:
            request_data = {
                "sequences": [
                    Mock(spec=BiologicEntity),
                    Mock(spec=BiologicEntity),
                ],
                "region_type": region_type,
            }

            command = AlignSequencesCommand(request_data)
            assert command.validate() is True
            assert command.region_type == region_type

    def test_validate_invalid_region_type(self):
        """Test validation with invalid region type"""
        request_data = {
            "sequences": [
                Mock(spec=BiologicEntity),
                Mock(spec=BiologicEntity),
            ],
            "region_type": "invalid",
        }

        command = AlignSequencesCommand(request_data)
        assert command.validate() is False

    def test_execute_success(self):
        """Test successful command execution"""
        mock_sequences = [Mock(spec=BiologicEntity), Mock(spec=BiologicEntity)]
        request_data = {
            "sequences": mock_sequences,
            "strategy": "multiple",
            "region_type": "CDR",
        }

        command = AlignSequencesCommand(request_data)
        result = command.execute()

        assert result.success is True
        assert result.data["sequences"] == mock_sequences
        assert result.data["strategy"] == "multiple"
        assert result.data["region_type"] == "CDR"
        assert result.metadata["command_type"] == "align_sequences"
        assert result.metadata["sequence_count"] == 2
        assert result.execution_time is not None


class TestProcessAnnotationCommand:
    """Test ProcessAnnotationCommand"""

    def test_process_annotation_command_creation(self):
        """Test creating ProcessAnnotationCommand"""
        request_data = {
            "sequences": {"seq1": Mock(spec=BiologicEntity)},
            "numbering_scheme": "ImGt",
            "persist_to_database": True,
            "organism": "human",
        }

        command = ProcessAnnotationCommand(request_data)
        assert command.request_data == request_data
        assert command.sequences == {}
        assert command.numbering_scheme == "imgt"  # Default value
        assert command.persist_to_database is False
        assert command.organism is None

    def test_validate_success(self):
        """Test successful validation"""
        request_data = {
            "sequences": {"seq1": Mock(spec=BiologicEntity)},
            "numbering_scheme": "IMGT",
            "persist_to_database": True,
            "organism": "human",
        }

        command = ProcessAnnotationCommand(request_data)
        assert command.validate() is True
        assert command.numbering_scheme == "imgt"
        assert command.persist_to_database is True
        assert command.organism == "human"

    def test_validate_missing_sequences(self):
        """Test validation with missing sequences"""
        request_data = {"numbering_scheme": "IMGT"}

        command = ProcessAnnotationCommand(request_data)
        assert command.validate() is False

    def test_validate_empty_sequences(self):
        """Test validation with empty sequences"""
        request_data = {"sequences": {}, "numbering_scheme": "imgt"}

        command = ProcessAnnotationCommand(request_data)
        assert command.validate() is False

    def test_validate_invalid_numbering_scheme(self):
        """Test validation with invalid numbering scheme"""
        request_data = {
            "sequences": {"seq1": Mock(spec=BiologicEntity)},
            "numbering_scheme": "INVALID",
        }

        command = ProcessAnnotationCommand(request_data)
        assert command.validate() is False

    def test_validate_case_insensitive_numbering_schemes(self):
        """Test validation with different case variations"""
        valid_variations = ["IMGT", "imgt", "ImGt", "Kabat", "CHOTHIA"]

        for scheme in valid_variations:
            request_data = {
                "sequences": {"seq1": Mock(spec=BiologicEntity)},
                "numbering_scheme": scheme,
            }
            command = ProcessAnnotationCommand(request_data)
            assert command.validate() is True, f"Failed for scheme: {scheme}"
            assert command.numbering_scheme == scheme.lower()

    def test_execute_success(self):
        """Test successful command execution"""
        mock_sequences = {"seq1": Mock(spec=BiologicEntity)}
        request_data = {
            "sequences": mock_sequences,
            "numbering_scheme": "imgt",
            "persist_to_database": True,
            "organism": "human",
        }

        command = ProcessAnnotationCommand(request_data)
        result = command.execute()

        assert result.success is True
        assert result.data["sequences"] == mock_sequences
        assert result.data["numbering_scheme"] == "imgt"
        assert result.data["persist_to_database"] is True
        assert result.data["organism"] == "human"
        assert result.metadata["command_type"] == "process_annotation"
        assert result.metadata["sequence_count"] == 1
        assert result.execution_time is not None

    def test_execute_validation_failure(self):
        """Test command execution with validation failure"""
        request_data = {"numbering_scheme": "imgt"}  # Missing sequences

        command = ProcessAnnotationCommand(request_data)
        result = command.execute()

        assert result.success is False
        assert "Invalid annotation workflow request data" in result.error
