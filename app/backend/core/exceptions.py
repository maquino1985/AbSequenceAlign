"""
Custom exceptions for the antibody sequence analysis system.
Provides specific error types for better error handling and debugging.
"""

from typing import Optional, Dict, Any, List


class AbSequenceAlignException(Exception):
    """Base exception for all AbSequenceAlign errors"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


# =============================================================================
# VALIDATION EXCEPTIONS
# =============================================================================


class ValidationError(AbSequenceAlignException):
    """Raised when input validation fails"""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        errors: Optional[List[str]] = None,
    ):
        details = {"field": field, "value": value, "errors": errors or []}
        super().__init__(message, details)


class SequenceValidationError(ValidationError):
    """Raised when sequence validation fails"""

    pass


class DomainValidationError(ValidationError):
    """Raised when domain validation fails"""

    pass


class DomainError(AbSequenceAlignException):
    """Raised when domain business rules are violated"""

    def __init__(
        self,
        message: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        business_rule: Optional[str] = None,
    ):
        details = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "business_rule": business_rule,
        }
        super().__init__(message, details)


class RegionValidationError(ValidationError):
    """Raised when region validation fails"""

    pass


# =============================================================================
# PROCESSING EXCEPTIONS
# =============================================================================


class ProcessingError(AbSequenceAlignException):
    """Base exception for processing errors"""

    def __init__(
        self,
        message: str,
        step: Optional[str] = None,
        input_data: Optional[Any] = None,
    ):
        details = {"step": step, "input_data": input_data}
        super().__init__(message, details)


class AnnotationError(ProcessingError):
    """Raised when annotation processing fails"""

    pass


class AlignmentError(ProcessingError):
    """Raised when alignment processing fails"""

    pass


class NumberingError(ProcessingError):
    """Raised when sequence numbering fails"""

    pass


class RegionAnnotationError(ProcessingError):
    """Raised when region annotation fails"""

    pass


# =============================================================================
# EXTERNAL TOOL EXCEPTIONS
# =============================================================================


class ExternalToolError(AbSequenceAlignException):
    """Base exception for external tool errors"""

    def __init__(
        self,
        message: str,
        tool_name: str,
        command: Optional[str] = None,
        exit_code: Optional[int] = None,
        stdout: Optional[str] = None,
        stderr: Optional[str] = None,
    ):
        details = {
            "tool_name": tool_name,
            "command": command,
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
        }
        super().__init__(message, details)


class ToolNotAvailableError(ExternalToolError):
    """Raised when an external tool is not available on the system"""

    pass


class ToolExecutionError(ExternalToolError):
    """Raised when an external tool execution fails"""

    pass


class AnarciError(ExternalToolError):
    """Raised when ANARCI tool fails"""

    pass


class HmmerError(ExternalToolError):
    """Raised when HMMER tool fails"""

    pass


class AlignmentToolError(ExternalToolError):
    """Raised when alignment tools (MUSCLE, MAFFT, etc.) fail"""

    pass


# =============================================================================
# PIPELINE EXCEPTIONS
# =============================================================================


class PipelineError(AbSequenceAlignException):
    """Base exception for pipeline errors"""

    def __init__(
        self,
        message: str,
        step_name: Optional[str] = None,
        pipeline_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        details = {
            "step_name": step_name,
            "pipeline_name": pipeline_name,
            "context": context or {},
        }
        super().__init__(message, details)


class PipelineStepError(PipelineError):
    """Raised when a specific pipeline step fails"""

    pass


class PipelineConfigurationError(PipelineError):
    """Raised when pipeline configuration is invalid"""

    pass


# =============================================================================
# FACTORY EXCEPTIONS
# =============================================================================


class FactoryError(AbSequenceAlignException):
    """Base exception for factory errors"""

    def __init__(
        self,
        message: str,
        factory_name: Optional[str] = None,
        requested_type: Optional[str] = None,
        available_types: Optional[List[str]] = None,
    ):
        details = {
            "factory_name": factory_name,
            "requested_type": requested_type,
            "available_types": available_types or [],
        }
        super().__init__(message, details)


class UnregisteredTypeError(FactoryError):
    """Raised when trying to create an unregistered type"""

    pass


class CreationError(FactoryError):
    """Raised when object creation fails"""

    pass


# =============================================================================
# REPOSITORY EXCEPTIONS
# =============================================================================


class RepositoryError(AbSequenceAlignException):
    """Base exception for repository errors"""

    def __init__(
        self,
        message: str,
        repository_name: Optional[str] = None,
        operation: Optional[str] = None,
        entity_id: Optional[str] = None,
    ):
        details = {
            "repository_name": repository_name,
            "operation": operation,
            "entity_id": entity_id,
        }
        super().__init__(message, details)


class EntityNotFoundError(RepositoryError):
    """Raised when an entity is not found"""

    pass


class DuplicateEntityError(RepositoryError):
    """Raised when trying to save a duplicate entity"""

    pass


class PersistenceError(RepositoryError):
    """Raised when data persistence fails"""

    pass


# =============================================================================
# CONFIGURATION EXCEPTIONS
# =============================================================================


class ConfigurationError(AbSequenceAlignException):
    """Raised when configuration is invalid or missing"""

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None,
        required_keys: Optional[List[str]] = None,
    ):
        details = {
            "config_key": config_key,
            "config_value": config_value,
            "required_keys": required_keys or [],
        }
        super().__init__(message, details)


class MissingConfigurationError(ConfigurationError):
    """Raised when required configuration is missing"""

    pass


class InvalidConfigurationError(ConfigurationError):
    """Raised when configuration values are invalid"""

    pass


# =============================================================================
# UTILITY EXCEPTIONS
# =============================================================================


class ConversionError(AbSequenceAlignException):
    """Raised when data conversion fails"""

    def __init__(
        self,
        message: str,
        source_type: Optional[str] = None,
        target_type: Optional[str] = None,
        value: Optional[Any] = None,
    ):
        details = {
            "source_type": source_type,
            "target_type": target_type,
            "value": value,
        }
        super().__init__(message, details)


class SerializationError(AbSequenceAlignException):
    """Raised when serialization/deserialization fails"""

    def __init__(
        self,
        message: str,
        format_type: Optional[str] = None,
        data: Optional[Any] = None,
    ):
        details = {"format_type": format_type, "data": data}
        super().__init__(message, details)


# =============================================================================
# ERROR UTILITIES
# =============================================================================


def create_validation_error(
    field: str, message: str, value: Any = None
) -> ValidationError:
    """Helper function to create validation errors"""
    return ValidationError(
        message=f"Validation failed for field '{field}': {message}",
        field=field,
        value=value,
    )


def create_processing_error(
    step: str, message: str, input_data: Any = None
) -> ProcessingError:
    """Helper function to create processing errors"""
    return ProcessingError(
        message=f"Processing failed at step '{step}': {message}",
        step=step,
        input_data=input_data,
    )


def create_tool_error(tool_name: str, message: str, **kwargs) -> ExternalToolError:
    """Helper function to create external tool errors"""
    return ExternalToolError(
        message=f"Tool '{tool_name}' failed: {message}",
        tool_name=tool_name,
        **kwargs,
    )
