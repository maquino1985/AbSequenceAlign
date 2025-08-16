from typing import List, Dict, Optional
from backend.jobs.job_manager import job_manager
from backend.models.models import MSAAnnotationRequest


class JobService:
    @staticmethod
    def create_annotation_job(request: MSAAnnotationRequest) -> str:
        """Create a background job for MSA annotation"""
        return job_manager.create_annotation_job(request)

    @staticmethod
    def get_job_status(job_id: str) -> Optional[Dict]:
        """Get the status of a specific job"""
        job_status = job_manager.get_job_status(job_id)
        if job_status:
            return job_status.model_dump()
        return None

    @staticmethod
    def list_jobs() -> List[Dict]:
        """List all jobs"""
        jobs = []
        for job_id, job_status in job_manager.jobs.items():
            jobs.append(job_status.model_dump())
        return jobs
