"""
Dependency injection container for managing application components.
Implements the Service Locator pattern and Dependency Injection.
"""

from typing import Dict, Any, Type, Optional, Callable
from functools import wraps
import inspect

from backend.logger import logger


class DependencyContainer:
    """Dependency injection container for managing application components"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
        self._config: Dict[str, Any] = {}
        logger.info("Dependency container initialized")
    
    def register_service(self, service_name: str, service_instance: Any) -> None:
        """Register a service instance"""
        self._services[service_name] = service_instance
        logger.debug(f"Registered service: {service_name}")
    
    def register_factory(self, service_name: str, factory: Callable) -> None:
        """Register a factory function for creating services"""
        self._factories[service_name] = factory
        logger.debug(f"Registered factory: {service_name}")
    
    def register_singleton(self, service_name: str, factory: Callable) -> None:
        """Register a singleton factory (creates instance once)"""
        self._factories[service_name] = factory
        logger.debug(f"Registered singleton factory: {service_name}")
    
    def register_config(self, key: str, value: Any) -> None:
        """Register configuration values"""
        self._config[key] = value
        logger.debug(f"Registered config: {key} = {value}")
    
    def get_service(self, service_name: str) -> Any:
        """Get a service instance"""
        # Check if service is already registered
        if service_name in self._services:
            return self._services[service_name]
        
        # Check if singleton exists
        if service_name in self._singletons:
            return self._singletons[service_name]
        
        # Check if factory exists
        if service_name in self._factories:
            factory = self._factories[service_name]
            
            # Check if it's a singleton (no parameters)
            if not inspect.signature(factory).parameters:
                if service_name not in self._singletons:
                    self._singletons[service_name] = factory()
                return self._singletons[service_name]
            else:
                # Regular factory - create new instance
                return factory()
        
        raise KeyError(f"Service '{service_name}' not found")
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self._config.get(key, default)
    
    def has_service(self, service_name: str) -> bool:
        """Check if a service is registered"""
        return (service_name in self._services or 
                service_name in self._factories or 
                service_name in self._singletons)
    
    def has_config(self, key: str) -> bool:
        """Check if a configuration key exists"""
        return key in self._config
    
    def resolve_dependencies(self, func: Callable) -> Callable:
        """Decorator to automatically inject dependencies into function parameters"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            sig = inspect.signature(func)
            params = sig.parameters
            
            # Resolve missing parameters from container
            resolved_kwargs = kwargs.copy()
            
            for param_name, param in params.items():
                if param_name not in resolved_kwargs and param_name != 'self':
                    # Try to get from container
                    if self.has_service(param_name):
                        resolved_kwargs[param_name] = self.get_service(param_name)
                    elif self.has_config(param_name):
                        resolved_kwargs[param_name] = self.get_config(param_name)
            
            return func(*args, **resolved_kwargs)
        
        return wrapper
    
    def create_instance(self, class_type: Type, **kwargs) -> Any:
        """Create an instance of a class with dependency injection"""
        # Get constructor signature
        sig = inspect.signature(class_type.__init__)
        params = sig.parameters
        
        # Resolve missing parameters from container
        resolved_kwargs = kwargs.copy()
        
        for param_name, param in params.items():
            if param_name not in resolved_kwargs and param_name != 'self':
                # Try to get from container
                if self.has_service(param_name):
                    resolved_kwargs[param_name] = self.get_service(param_name)
                elif self.has_config(param_name):
                    resolved_kwargs[param_name] = self.get_config(param_name)
        
        return class_type(**resolved_kwargs)
    
    def clear(self) -> None:
        """Clear all registered services and configurations"""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
        self._config.clear()
        logger.info("Dependency container cleared")
    
    def get_registered_services(self) -> Dict[str, str]:
        """Get a list of registered services"""
        services = {}
        
        # Add direct services
        for name in self._services:
            services[name] = "instance"
        
        # Add factories
        for name in self._factories:
            if name not in services:
                services[name] = "factory"
        
        # Add singletons
        for name in self._singletons:
            services[name] = "singleton"
        
        return services
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get all configuration values"""
        return self._config.copy()


# Global container instance
_container: Optional[DependencyContainer] = None


def get_container() -> DependencyContainer:
    """Get the global dependency container instance"""
    global _container
    if _container is None:
        _container = DependencyContainer()
    return _container


def register_service(service_name: str, service_instance: Any) -> None:
    """Register a service in the global container"""
    get_container().register_service(service_name, service_instance)


def register_factory(service_name: str, factory: Callable) -> None:
    """Register a factory in the global container"""
    get_container().register_factory(service_name, factory)


def register_singleton(service_name: str, factory: Callable) -> None:
    """Register a singleton factory in the global container"""
    get_container().register_singleton(service_name, factory)


def register_config(key: str, value: Any) -> None:
    """Register configuration in the global container"""
    get_container().register_config(key, value)


def get_service(service_name: str) -> Any:
    """Get a service from the global container"""
    return get_container().get_service(service_name)


def get_config(key: str, default: Any = None) -> Any:
    """Get configuration from the global container"""
    return get_container().get_config(key, default)


def inject_dependencies(func: Callable) -> Callable:
    """Decorator to inject dependencies from the global container"""
    return get_container().resolve_dependencies(func)


def create_instance(class_type: Type, **kwargs) -> Any:
    """Create an instance with dependency injection from the global container"""
    return get_container().create_instance(class_type, **kwargs)


# =============================================================================
# CONFIGURATION HELPERS
# =============================================================================


def configure_default_services(container: DependencyContainer) -> None:
    """Configure default services in the container"""
    
    # Register repositories
    from backend.infrastructure.repositories.sequence_repository import SequenceRepository
    container.register_factory("sequence_repository", lambda: SequenceRepository(
        storage_path=container.get_config("storage_path", "data/sequences")
    ))
    
    # Register adapters
    from backend.infrastructure.adapters.anarci_adapter import AnarciAdapter
    from backend.infrastructure.adapters.hmmer_adapter import HmmerAdapter
    container.register_factory("anarci_adapter", lambda: AnarciAdapter())
    container.register_factory("hmmer_adapter", lambda: HmmerAdapter())
    
    # Register application services
    from backend.application.services.annotation_service import AnnotationService
    from backend.application.services.alignment_service import AlignmentService
    from backend.application.services.processing_service import ProcessingService
    
    container.register_factory("annotation_service", lambda: AnnotationService())
    container.register_factory("alignment_service", lambda: AlignmentService())
    container.register_factory("processing_service", lambda: ProcessingService())
    
    # Register pipeline builders
    from backend.application.pipelines.pipeline_builder import (
        create_annotation_pipeline, create_alignment_pipeline
    )
    container.register_factory("annotation_pipeline_factory", lambda: create_annotation_pipeline)
    container.register_factory("alignment_pipeline_factory", lambda: create_alignment_pipeline)
    
    logger.info("Default services configured in dependency container")


def configure_development_services(container: DependencyContainer) -> None:
    """Configure services for development environment"""
    
    # Development-specific configuration
    container.register_config("environment", "development")
    container.register_config("debug", True)
    container.register_config("log_level", "DEBUG")
    
    # Use in-memory storage for development (only if not already set)
    if not container.has_config("storage_path"):
        container.register_config("storage_path", "data/dev/sequences")
    
    logger.info("Development services configured in dependency container")


def configure_production_services(container: DependencyContainer) -> None:
    """Configure services for production environment"""
    
    # Production-specific configuration
    container.register_config("environment", "production")
    container.register_config("debug", False)
    container.register_config("log_level", "INFO")
    
    # Use persistent storage for production
    container.register_config("storage_path", "data/prod/sequences")
    
    logger.info("Production services configured in dependency container")
