"""
Simple processing service for sequence annotation.
Provides basic processing functionality without overengineering.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from backend.core.interfaces import ProcessingResult
from backend.core.exceptions import ProcessingError

from backend.logger import logger


@dataclass
class ProcessingProgress:
    """Simple progress tracking"""
    current_step: str
    total_steps: int
    completed_steps: int
    percentage: float
    message: str


class SimpleProcessingService:
    """Simple service for processing sequences"""

    def __init__(self):
        self.active_jobs: Dict[str, Any] = {}

    def process_sequences(
        self, 
        sequences: Dict[str, str], 
        processor_type: str = "annotation",
        **kwargs
    ) -> ProcessingResult:
        """Process sequences using the specified processor type"""
        try:
            if processor_type == "annotation":
                from backend.annotation.anarci_result_processor import AnarciResultProcessor
                processor = AnarciResultProcessor(sequences, **kwargs)
                result = processor.process(sequences, **kwargs)
                return ProcessingResult(
                    success=True,
                    data=result,
                    metadata={"processor_type": processor_type}
                )
            else:
                raise ProcessingError(f"Unknown processor type: {processor_type}")
                
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            return ProcessingResult(
                success=False,
                error=str(e),
                metadata={"processor_type": processor_type}
            )

    def get_available_processors(self) -> List[str]:
        """Get available processor types"""
        return ["annotation"]

    def get_active_jobs(self) -> Dict[str, Any]:
        """Get active processing jobs"""
        return self.active_jobs.copy()



