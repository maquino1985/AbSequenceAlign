import uuid
import threading
import time
from typing import Dict, Optional
from datetime import datetime
from ..models.models import MSAJobStatus, MSACreationRequest, MSAAnnotationRequest
from ..msa.msa_engine import MSAEngine
from ..msa.msa_annotation import MSAAnnotationEngine


class JobManager:
    """Manages background jobs for MSA processing"""

    def __init__(self):
        self.jobs: Dict[str, MSAJobStatus] = {}
        self.job_lock = threading.Lock()
        self.msa_engine = MSAEngine()
        self.annotation_engine = MSAAnnotationEngine()

    def create_msa_job(self, request: MSACreationRequest) -> str:
        """Create a new MSA job"""
        job_id = str(uuid.uuid4())

        job_status = MSAJobStatus(
            job_id=job_id,
            status="pending",
            progress=0.0,
            message="Job created",
            created_at=datetime.now().isoformat(),
        )

        # Create thread before acquiring lock
        thread = threading.Thread(target=self._process_msa_job, args=(job_id, request))
        thread.daemon = True

        # Add job to dictionary under lock
        with self.job_lock:
            self.jobs[job_id] = job_status

        # Start thread after releasing lock
        thread.start()

        return job_id

    def create_annotation_job(self, request: MSAAnnotationRequest) -> str:
        """Create a new annotation job"""
        job_id = str(uuid.uuid4())

        job_status = MSAJobStatus(
            job_id=job_id,
            status="pending",
            progress=0.0,
            message="Annotation job created",
            created_at=datetime.now().isoformat(),
        )

        # Create thread before acquiring lock
        thread = threading.Thread(
            target=self._process_annotation_job, args=(job_id, request)
        )
        thread.daemon = True

        # Add job to dictionary under lock
        with self.job_lock:
            self.jobs[job_id] = job_status

        # Start thread after releasing lock
        thread.start()

        return job_id

    def get_job_status(self, job_id: str) -> Optional[MSAJobStatus]:
        """Get status of a job"""
        with self.job_lock:
            return self.jobs.get(job_id)

    def _update_job_status(
        self, job_id: str, status: str, progress: float, message: str
    ):
        """Update job status"""
        with self.job_lock:
            if job_id in self.jobs:
                # Don't update if job is already in a terminal state
                if self.jobs[job_id].status in ["completed", "failed"]:
                    return

                self.jobs[job_id].status = status
                self.jobs[job_id].progress = progress
                self.jobs[job_id].message = message
                if status in ["completed", "failed"]:
                    self.jobs[job_id].completed_at = datetime.now().isoformat()

    def _process_msa_job(self, job_id: str, request: MSACreationRequest):
        """Process MSA job in background"""
        try:
            # Add a small delay to ensure the job is created before we start processing
            time.sleep(0.1)

            # Update status to running
            self._update_job_status(job_id, "running", 0.1, "Starting MSA creation...")

            # Extract sequences
            sequences = []
            for seq_input in request.sequences:
                chains = seq_input.get_all_chains()
                for chain_name, sequence in chains.items():
                    sequences.append((f"{seq_input.name}_{chain_name}", sequence))

            if not sequences:
                raise ValueError("No valid sequences provided")

            # Update progress
            self._update_job_status(
                job_id, "running", 0.3, f"Aligning {len(sequences)} sequences..."
            )

            # Create MSA
            msa_result = self.msa_engine.create_msa(
                sequences=sequences, method=request.alignment_method
            )

            # Update progress
            self._update_job_status(
                job_id, "running", 0.7, "MSA created, preparing annotation..."
            )

            # Annotate sequences
            annotation_result = self.annotation_engine.annotate_msa(
                msa_result=msa_result, numbering_scheme=request.numbering_scheme
            )

            # Prepare result
            result = {
                "msa_result": msa_result.model_dump(),
                "annotation_result": annotation_result.model_dump(),
                "job_type": "msa_creation",
            }

            # Update job as completed
            with self.job_lock:
                if job_id in self.jobs:
                    self.jobs[job_id].result = result
                    self.jobs[job_id].status = "completed"
                    self.jobs[job_id].progress = 1.0
                    self.jobs[job_id].message = "MSA creation completed successfully"
                    self.jobs[job_id].completed_at = datetime.now().isoformat()

        except Exception as e:
            error_msg = f"MSA job failed: {str(e)}"
            with self.job_lock:
                if job_id in self.jobs:
                    self.jobs[job_id].status = "failed"
                    self.jobs[job_id].progress = 0.0
                    self.jobs[job_id].message = error_msg
                    self.jobs[job_id].completed_at = datetime.now().isoformat()
            print(f"Error in MSA job {job_id}: {e}")

    def _process_annotation_job(self, job_id: str, request: MSAAnnotationRequest):
        """Process annotation job in background"""
        try:
            # Add a small delay to ensure the job is created before we start processing
            time.sleep(0.1)

            # Update status to running
            self._update_job_status(job_id, "running", 0.1, "Starting annotation...")

            # For now, we'll need to retrieve the MSA result from storage
            # This would typically come from a database or cache
            # For now, we'll simulate this

            # Update progress
            self._update_job_status(job_id, "running", 0.5, "Annotating sequences...")

            # Simulate annotation (in real implementation, retrieve MSA from storage)
            # annotation_result = self.annotation_engine.annotate_msa(
            #     msa_result=retrieved_msa,
            #     numbering_scheme=request.numbering_scheme
            # )

            # For now, return a placeholder result
            result = {
                "msa_id": request.msa_id,
                "numbering_scheme": request.numbering_scheme.value,
                "job_type": "msa_annotation",
                "message": "Annotation completed (placeholder)",
            }

            # Update job as completed
            with self.job_lock:
                if job_id in self.jobs:
                    self.jobs[job_id].result = result
                    self.jobs[job_id].status = "completed"
                    self.jobs[job_id].progress = 1.0
                    self.jobs[job_id].message = "Annotation completed successfully"
                    self.jobs[job_id].completed_at = datetime.now().isoformat()

        except Exception as e:
            error_msg = f"Annotation job failed: {str(e)}"
            with self.job_lock:
                if job_id in self.jobs:
                    self.jobs[job_id].status = "failed"
                    self.jobs[job_id].progress = 0.0
                    self.jobs[job_id].message = error_msg
                    self.jobs[job_id].completed_at = datetime.now().isoformat()
            print(f"Error in annotation job {job_id}: {e}")

    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """Clean up old completed/failed jobs"""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)

        with self.job_lock:
            jobs_to_remove = []
            for job_id, job in self.jobs.items():
                if job.status in ["completed", "failed"]:
                    try:
                        job_time = datetime.fromisoformat(job.created_at).timestamp()
                        if job_time < cutoff_time:
                            jobs_to_remove.append(job_id)
                    except:
                        # If we can't parse the timestamp, remove the job
                        jobs_to_remove.append(job_id)

            for job_id in jobs_to_remove:
                del self.jobs[job_id]


# Global job manager instance
job_manager = JobManager()
