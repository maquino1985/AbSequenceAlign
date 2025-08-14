"""
Factory for creating processing services.
"""

from backend.application.services.processing_service import SimpleProcessingService
from backend.core.interfaces import SimpleServiceFactory


class ProcessingServiceFactory(SimpleServiceFactory):
    """Simple factory for creating processing services"""

    def create_service(self, service_type: str = "simple", **kwargs) -> SimpleProcessingService:
        """Create a simple processing service"""
        return SimpleProcessingService()

    def get_available_service_types(self) -> list[str]:
        """Get list of available service types"""
        return ["simple"]

    @staticmethod
    def create_service() -> SimpleProcessingService:
        """Create a simple processing service (static method for convenience)"""
        return SimpleProcessingService()
