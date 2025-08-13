"""
Factory for creating biologic services, processors, converters, and strategies.
Implements the Factory pattern for flexible component creation.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.base_classes import AbstractServiceFactory
from backend.core.interfaces import (
    BiologicService,
    BiologicProcessor,
    BiologicConverter,
    BiologicProcessingStrategy,
    BiologicValidationStrategy,
    BiologicServiceFactory as IBiologicServiceFactory,
)
from backend.infrastructure.repositories.biologic_repository import (
    BiologicRepositoryImpl,
)
from backend.application.converters.biologic_converter import (
    BiologicConverterImpl,
)
from backend.application.processors.biologic_processor import (
    BiologicProcessorImpl,
)
from backend.application.strategies.biologic_strategies import (
    AntibodyProcessingStrategy,
    ProteinProcessingStrategy,
    DNAProcessingStrategy,
    RNAProcessingStrategy,
    AntibodyValidationStrategy,
    ProteinValidationStrategy,
)
from backend.logger import logger


class BiologicServiceFactory(
    AbstractServiceFactory[BiologicService], IBiologicServiceFactory
):
    """Factory for creating biologic services and related components."""

    def __init__(self):
        super().__init__()
        self._logger = logger

    def _register_default_services(self) -> None:
        """Register default service types."""
        # Register service types
        self.register("default", self._create_default_service)
        self.register("with_cache", self._create_cached_service)
        self.register("with_validation", self._create_validation_service)

        self._logger.info("Registered default biologic service types")

    def create_service(self, service_type: str, **kwargs) -> BiologicService:
        """Create a biologic service of the specified type."""
        try:
            self._logger.debug(
                f"Creating biologic service of type: {service_type}"
            )

            if service_type == "default":
                return self._create_default_service(**kwargs)
            elif service_type == "with_cache":
                return self._create_cached_service(**kwargs)
            elif service_type == "with_validation":
                return self._create_validation_service(**kwargs)
            else:
                # Try to use the factory registry
                return self.create(service_type, **kwargs)

        except Exception as e:
            self._logger.error(
                f"Error creating biologic service of type {service_type}: {e}"
            )
            raise

    def create_processor(
        self, processor_type: str, **kwargs
    ) -> BiologicProcessor:
        """Create a biologic processor of the specified type."""
        try:
            self._logger.debug(
                f"Creating biologic processor of type: {processor_type}"
            )

            if processor_type == "default":
                return self._create_default_processor(**kwargs)
            elif processor_type == "with_strategies":
                return self._create_strategy_processor(**kwargs)
            else:
                raise ValueError(f"Unknown processor type: {processor_type}")

        except Exception as e:
            self._logger.error(
                f"Error creating biologic processor of type {processor_type}: {e}"
            )
            raise

    def create_converter(
        self, converter_type: str, **kwargs
    ) -> BiologicConverter:
        """Create a biologic converter of the specified type."""
        try:
            self._logger.debug(
                f"Creating biologic converter of type: {converter_type}"
            )

            if converter_type == "default":
                return self._create_default_converter(**kwargs)
            elif converter_type == "with_validation":
                return self._create_validation_converter(**kwargs)
            else:
                raise ValueError(f"Unknown converter type: {converter_type}")

        except Exception as e:
            self._logger.error(
                f"Error creating biologic converter of type {converter_type}: {e}"
            )
            raise

    def create_strategy(
        self, strategy_type: str, **kwargs
    ) -> BiologicProcessingStrategy:
        """Create a biologic processing strategy of the specified type."""
        try:
            self._logger.debug(
                f"Creating biologic strategy of type: {strategy_type}"
            )

            if strategy_type == "antibody":
                return AntibodyProcessingStrategy()
            elif strategy_type == "protein":
                return ProteinProcessingStrategy()
            elif strategy_type == "dna":
                return DNAProcessingStrategy()
            elif strategy_type == "rna":
                return RNAProcessingStrategy()
            else:
                raise ValueError(f"Unknown strategy type: {strategy_type}")

        except Exception as e:
            self._logger.error(
                f"Error creating biologic strategy of type {strategy_type}: {e}"
            )
            raise

    def get_available_service_types(self) -> List[str]:
        """Get list of available service types."""
        return ["default", "with_cache", "with_validation"]

    def get_available_processor_types(self) -> List[str]:
        """Get list of available processor types."""
        return ["default", "with_strategies"]

    def get_available_converter_types(self) -> List[str]:
        """Get list of available converter types."""
        return ["default", "with_validation"]

    def get_available_strategy_types(self) -> List[str]:
        """Get list of available strategy types."""
        return ["antibody", "protein", "dna", "rna"]

    def _create_default_service(self, **kwargs) -> BiologicService:
        """Create a default biologic service."""
        from backend.application.services.biologic_service import (
            BiologicServiceImpl,
        )

        session = kwargs.get("session")
        repository = BiologicRepositoryImpl(session) if session else None
        processor = self.create_processor("default", repository=repository)

        return BiologicServiceImpl(repository=repository, processor=processor)

    def _create_cached_service(self, **kwargs) -> BiologicService:
        """Create a biologic service with caching."""
        from backend.application.services.biologic_service import (
            CachedBiologicServiceImpl,
        )

        session = kwargs.get("session")
        repository = BiologicRepositoryImpl(session) if session else None
        processor = self.create_processor("default", repository=repository)

        return CachedBiologicServiceImpl(
            repository=repository, processor=processor
        )

    def _create_validation_service(self, **kwargs) -> BiologicService:
        """Create a biologic service with enhanced validation."""
        from backend.application.services.biologic_service import (
            ValidationBiologicServiceImpl,
        )

        session = kwargs.get("session")
        repository = BiologicRepositoryImpl(session) if session else None
        processor = self.create_processor(
            "with_strategies", repository=repository
        )

        return ValidationBiologicServiceImpl(
            repository=repository, processor=processor
        )

    def _create_default_processor(self, **kwargs) -> BiologicProcessor:
        """Create a default biologic processor."""
        repository = kwargs.get("repository")
        converter = self.create_converter("default")

        return BiologicProcessorImpl(
            repository=repository, converter=converter
        )

    def _create_strategy_processor(self, **kwargs) -> BiologicProcessor:
        """Create a biologic processor with strategy support."""
        from backend.application.processors.strategy_biologic_processor import (
            StrategyBiologicProcessorImpl,
        )

        repository = kwargs.get("repository")
        converter = self.create_converter("default")
        strategies = {
            "antibody": self.create_strategy("antibody"),
            "protein": self.create_strategy("protein"),
            "dna": self.create_strategy("dna"),
            "rna": self.create_strategy("rna"),
        }

        return StrategyBiologicProcessorImpl(
            repository=repository, converter=converter, strategies=strategies
        )

    def _create_default_converter(self, **kwargs) -> BiologicConverter:
        """Create a default biologic converter."""
        return BiologicConverterImpl()

    def _create_validation_converter(self, **kwargs) -> BiologicConverter:
        """Create a biologic converter with enhanced validation."""
        # Validation is now handled by ValidationService
        # Return the default converter
        return self._create_default_converter()


class BiologicComponentFactory:
    """Factory for creating biologic components with dependency injection."""

    def __init__(self, session: AsyncSession = None):
        self.session = session
        self.service_factory = BiologicServiceFactory()
        self._logger = logger

    def create_repository(self) -> BiologicRepositoryImpl:
        """Create a biologic repository."""
        return BiologicRepositoryImpl(self.session)

    def create_converter(self) -> BiologicConverterImpl:
        """Create a biologic converter."""
        return BiologicConverterImpl()

    def create_processor(self) -> BiologicProcessorImpl:
        """Create a biologic processor."""
        repository = self.create_repository()
        converter = self.create_converter()
        return BiologicProcessorImpl(
            repository=repository, converter=converter
        )

    def create_service(self, service_type: str = "default") -> BiologicService:
        """Create a biologic service."""
        return self.service_factory.create_service(
            service_type, session=self.session
        )

    def create_strategy(
        self, strategy_type: str
    ) -> BiologicProcessingStrategy:
        """Create a biologic processing strategy."""
        return self.service_factory.create_strategy(strategy_type)

    def create_validation_strategy(
        self, strategy_type: str
    ) -> BiologicValidationStrategy:
        """Create a biologic validation strategy."""
        if strategy_type == "antibody":
            return AntibodyValidationStrategy()
        elif strategy_type == "protein":
            return ProteinValidationStrategy()
        else:
            raise ValueError(
                f"Unknown validation strategy type: {strategy_type}"
            )

    def create_complete_stack(
        self, service_type: str = "default"
    ) -> Dict[str, Any]:
        """Create a complete stack of biologic components."""
        try:
            self._logger.debug("Creating complete biologic component stack")

            repository = self.create_repository()
            converter = self.create_converter()
            processor = self.create_processor()
            service = self.create_service(service_type)

            # Create strategies
            strategies = {
                "antibody": self.create_strategy("antibody"),
                "protein": self.create_strategy("protein"),
                "dna": self.create_strategy("dna"),
                "rna": self.create_strategy("rna"),
            }

            # Create validation strategies
            validation_strategies = {
                "antibody": self.create_validation_strategy("antibody"),
                "protein": self.create_validation_strategy("protein"),
            }

            stack = {
                "repository": repository,
                "converter": converter,
                "processor": processor,
                "service": service,
                "strategies": strategies,
                "validation_strategies": validation_strategies,
            }

            self._logger.debug(
                "Successfully created complete biologic component stack"
            )
            return stack

        except Exception as e:
            self._logger.error(
                f"Error creating complete biologic component stack: {e}"
            )
            raise


# Global factory instance for easy access
_global_factory: Optional[BiologicServiceFactory] = None


def get_biologic_service_factory() -> BiologicServiceFactory:
    """Get the global biologic service factory instance."""
    global _global_factory
    if _global_factory is None:
        _global_factory = BiologicServiceFactory()
    return _global_factory


def create_biologic_service(
    service_type: str = "default", session: AsyncSession = None
) -> BiologicService:
    """Create a biologic service using the global factory."""
    factory = get_biologic_service_factory()
    return factory.create_service(service_type, session=session)


def create_biologic_processor(
    processor_type: str = "default", session: AsyncSession = None
) -> BiologicProcessor:
    """Create a biologic processor using the global factory."""
    factory = get_biologic_service_factory()
    repository = BiologicRepositoryImpl(session) if session else None
    return factory.create_processor(processor_type, repository=repository)


def create_biologic_converter(
    converter_type: str = "default",
) -> BiologicConverter:
    """Create a biologic converter using the global factory."""
    factory = get_biologic_service_factory()
    return factory.create_converter(converter_type)


def create_biologic_strategy(strategy_type: str) -> BiologicProcessingStrategy:
    """Create a biologic strategy using the global factory."""
    factory = get_biologic_service_factory()
    return factory.create_strategy(strategy_type)
