import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from backend.models.models import DatasetInfo, AlignmentResult, AnnotationResult
from backend.logger import logger

class DataStore:
    """Simple in-memory data store for managing datasets and results"""
    
    def __init__(self):
        self.datasets: Dict[str, Dict[str, Any]] = {}
        self.alignments: Dict[str, AlignmentResult] = {}
        self.annotations: Dict[str, AnnotationResult] = {}
    
    def create_dataset(self, sequences: List[str], metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new dataset
        
        Args:
            sequences: List of protein sequences
            metadata: Optional metadata
            
        Returns:
            Dataset ID
        """
        dataset_id = str(uuid.uuid4())
        
        self.datasets[dataset_id] = {
            "dataset_id": dataset_id,
            "sequences": sequences,
            "sequence_count": len(sequences),
            "created_at": datetime.now().isoformat(),
            "status": "uploaded",
            "metadata": metadata or {}
        }
        
        logger.info(f"Created dataset {dataset_id} with {len(sequences)} sequences")
        return dataset_id
    
    def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get dataset by ID"""
        return self.datasets.get(dataset_id)
    
    def get_dataset_info(self, dataset_id: str) -> Optional[DatasetInfo]:
        """Get dataset info as DatasetInfo object"""
        dataset = self.get_dataset(dataset_id)
        if not dataset:
            return None
        
        return DatasetInfo(
            dataset_id=dataset["dataset_id"],
            sequence_count=dataset["sequence_count"],
            created_at=dataset["created_at"],
            status=dataset["status"]
        )
    
    def update_dataset_status(self, dataset_id: str, status: str) -> bool:
        """Update dataset status"""
        if dataset_id not in self.datasets:
            return False
        
        self.datasets[dataset_id]["status"] = status
        return True
    
    def get_sequences(self, dataset_id: str) -> Optional[List[str]]:
        """Get sequences for a dataset"""
        dataset = self.get_dataset(dataset_id)
        return dataset.get("sequences") if dataset else None
    
    def store_alignment_result(self, dataset_id: str, alignment_result: AlignmentResult) -> bool:
        """Store alignment result"""
        if dataset_id not in self.datasets:
            return False
        
        self.alignments[dataset_id] = alignment_result
        self.update_dataset_status(dataset_id, "aligned")
        return True
    
    def get_alignment_result(self, dataset_id: str) -> Optional[AlignmentResult]:
        """Get alignment result for a dataset"""
        return self.alignments.get(dataset_id)
    
    def store_annotation_result(self, dataset_id: str, annotation_result: AnnotationResult) -> bool:
        """Store annotation result"""
        if dataset_id not in self.datasets:
            return False
        
        self.annotations[dataset_id] = annotation_result
        self.update_dataset_status(dataset_id, "annotated")
        return True
    
    def get_annotation_result(self, dataset_id: str) -> Optional[AnnotationResult]:
        """Get annotation result for a dataset"""
        return self.annotations.get(dataset_id)
    
    def delete_dataset(self, dataset_id: str) -> bool:
        """Delete dataset and all associated results"""
        if dataset_id not in self.datasets:
            return False
        
        # Remove dataset
        del self.datasets[dataset_id]
        
        # Remove associated results
        if dataset_id in self.alignments:
            del self.alignments[dataset_id]
        
        if dataset_id in self.annotations:
            del self.annotations[dataset_id]
        
        logger.info(f"Deleted dataset {dataset_id}")
        return True
    
    def list_datasets(self) -> List[DatasetInfo]:
        """List all datasets"""
        return [
            DatasetInfo(
                dataset_id=dataset["dataset_id"],
                sequence_count=dataset["sequence_count"],
                created_at=dataset["created_at"],
                status=dataset["status"]
            )
            for dataset in self.datasets.values()
        ]
    
    def get_dataset_statistics(self) -> Dict[str, Any]:
        """Get overall statistics"""
        total_datasets = len(self.datasets)
        total_sequences = sum(dataset["sequence_count"] for dataset in self.datasets.values())
        
        status_counts = {}
        for dataset in self.datasets.values():
            status = dataset["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_datasets": total_datasets,
            "total_sequences": total_sequences,
            "status_counts": status_counts,
            "alignments": len(self.alignments),
            "annotations": len(self.annotations)
        }


# Global data store instance
data_store = DataStore()
