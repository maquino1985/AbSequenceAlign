"""
Processor factory for creating different types of processors.
Implements the Factory pattern to provide a clean way to create processors.
"""

import logging
from typing import Dict, Type

from backend.core.interfaces import Processor
from ...core.base_classes import AbstractFactory
from ...core.interfaces import BiologicProcessor


class ProcessorFactory(AbstractFactory[BiologicProcessor]):
    """Factory for creating processors"""

    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(self.__class__.__name__)
        self._register_default_processors()

    def _register_default_processors(self) -> None:
        """Register default processor types"""
        # TODO: Register processors when they are implemented
        pass

    def create_annotation_processor(self, **kwargs):
        """Create an annotation processor"""
        return self.create("annotation", **kwargs)

    def create_alignment_processor(self, **kwargs):
        """Create an alignment processor"""
        return self.create("alignment", **kwargs)

    def create_numbering_processor(self, **kwargs):
        """Create a numbering processor"""
        return self.create("numbering", **kwargs)

    def get_available_processors(self) -> Dict[str, Type[Processor]]:
        """Get all available processor types"""
        return self._registry.copy()

    def is_processor_available(self, processor_type: str) -> bool:
        """Check if a processor type is available"""
        return processor_type in self._registry


class PipelineFactory(AbstractFactory):
    """Factory for creating processing pipelines"""

    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(self.__class__.__name__)
        self._register_default_pipelines()

    def _register_default_pipelines(self) -> None:
        """Register default pipeline types"""
        # TODO: Register pipelines when they are implemented
        pass

    def create_annotation_pipeline(self, **kwargs):
        """Create an annotation pipeline"""
        return self.create("annotation", **kwargs)

    def create_alignment_pipeline(self, **kwargs):
        """Create an alignment pipeline"""
        return self.create("alignment", **kwargs)

    def get_available_pipelines(self) -> Dict[str, Type]:
        """Get all available pipeline types"""
        return self._registry.copy()


class AdapterFactory(AbstractFactory):
    """Factory for creating external tool adapters"""

    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(self.__class__.__name__)
        self._register_default_adapters()

    def _register_default_adapters(self) -> None:
        """Register default adapter types"""
        from ...infrastructure.adapters.anarci_adapter import AnarciAdapter
        from ...infrastructure.adapters.hmmer_adapter import HmmerAdapter

        self.register("anarci", AnarciAdapter)
        self.register("hmmer", HmmerAdapter)

    def create_anarci_adapter(self, **kwargs):
        """Create an ANARCI adapter"""
        return self.create("anarci", **kwargs)

    def create_hmmer_adapter(self, **kwargs):
        """Create an HMMER adapter"""
        return self.create("hmmer", **kwargs)

    def get_available_adapters(self) -> Dict[str, Type]:
        """Get all available adapter types"""
        return self._registry.copy()


class ServiceFactory(AbstractFactory):
    """Factory for creating application services"""

    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(self.__class__.__name__)
        self._register_default_services()

    def _register_default_services(self) -> None:
        """Register default service types"""
        # TODO: Register services when they are implemented
        pass

    def create_annotation_service(self, **kwargs):
        """Create an annotation service"""
        return self.create("annotation", **kwargs)

    def create_alignment_service(self, **kwargs):
        """Create an alignment service"""
        return self.create("alignment", **kwargs)

    def create_processing_service(self, **kwargs):
        """Create a processing service"""
        return self.create("processing", **kwargs)

    def get_available_services(self) -> Dict[str, Type]:
        """Get all available service types"""
        return self._registry.copy()


# Global factory instances
processor_factory = ProcessorFactory()
pipeline_factory = PipelineFactory()
adapter_factory = AdapterFactory()
service_factory = ServiceFactory()


def get_processor_factory() -> ProcessorFactory:
    """Get the global processor factory instance"""
    return processor_factory


def get_pipeline_factory() -> PipelineFactory:
    """Get the global pipeline factory instance"""
    return pipeline_factory


def get_adapter_factory() -> AdapterFactory:
    """Get the global adapter factory instance"""
    return adapter_factory


def get_service_factory() -> ServiceFactory:
    """Get the global service factory instance"""
    return service_factory
