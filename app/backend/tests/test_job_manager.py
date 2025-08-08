import pytest
import time
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from backend.jobs.job_manager import JobManager
from backend.models.models import MSACreationRequest, MSAAnnotationRequest, MSAJobStatus, NumberingScheme, AlignmentMethod, SequenceInput


class TestJobManager:
    """Test cases for JobManager"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.job_manager = JobManager()
        
        # Create test request
        self.test_msa_request = MSACreationRequest(
            sequences=[
                SequenceInput(
                    name="test_seq_1",
                    heavy_chain="EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS"
                ),
                SequenceInput(
                    name="test_seq_2", 
                    heavy_chain="EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK"
                )
            ],
            alignment_method=AlignmentMethod.MUSCLE,
            numbering_scheme=NumberingScheme.IMGT
        )
        
        self.test_annotation_request = MSAAnnotationRequest(
            msa_id="test-msa-123",
            numbering_scheme=NumberingScheme.IMGT
        )
    
    def test_job_manager_initialization(self):
        """Test JobManager initialization"""
        assert self.job_manager is not None
        assert hasattr(self.job_manager, 'jobs')
        assert hasattr(self.job_manager, 'job_lock')
        assert hasattr(self.job_manager, 'msa_engine')
        assert hasattr(self.job_manager, 'annotation_engine')
    
    def test_create_msa_job(self):
        """Test creating MSA job"""
        job_id = self.job_manager.create_msa_job(self.test_msa_request)
        
        assert job_id is not None
        assert isinstance(job_id, str)
        assert len(job_id) > 0
        
        # Check that job was added to jobs dict
        job_status = self.job_manager.get_job_status(job_id)
        assert job_status is not None
        assert job_status.job_id == job_id
        assert job_status.status == "pending"
        assert job_status.progress == 0.0
        assert job_status.message == "Job created"
        assert job_status.created_at is not None
    
    def test_create_annotation_job(self):
        """Test creating annotation job"""
        job_id = self.job_manager.create_annotation_job(self.test_annotation_request)
        
        assert job_id is not None
        assert isinstance(job_id, str)
        assert len(job_id) > 0
        
        # Check that job was added to jobs dict
        job_status = self.job_manager.get_job_status(job_id)
        assert job_status is not None
        assert job_status.job_id == job_id
        assert job_status.status == "pending"
        assert job_status.progress == 0.0
        assert job_status.message == "Annotation job created"
        assert job_status.created_at is not None
    
    def test_get_job_status_nonexistent(self):
        """Test getting status of nonexistent job"""
        job_status = self.job_manager.get_job_status("nonexistent-job-id")
        assert job_status is None
    
    def test_update_job_status(self):
        """Test updating job status"""
        job_id = self.job_manager.create_msa_job(self.test_msa_request)
        
        # Update job status
        self.job_manager._update_job_status(job_id, "running", 0.5, "Processing...")
        
        job_status = self.job_manager.get_job_status(job_id)
        assert job_status.status == "running"
        assert job_status.progress == 0.5
        assert job_status.message == "Processing..."
    
    def test_update_job_status_completed(self):
        """Test updating job status to completed"""
        job_id = self.job_manager.create_msa_job(self.test_msa_request)
        
        # Update job status to completed
        self.job_manager._update_job_status(job_id, "completed", 1.0, "Job completed")
        
        job_status = self.job_manager.get_job_status(job_id)
        assert job_status.status == "completed"
        assert job_status.progress == 1.0
        assert job_status.message == "Job completed"
        assert job_status.completed_at is not None
    
    def test_update_job_status_failed(self):
        """Test updating job status to failed"""
        job_id = self.job_manager.create_msa_job(self.test_msa_request)
        
        # Update job status to failed
        self.job_manager._update_job_status(job_id, "failed", 0.0, "Job failed")
        
        job_status = self.job_manager.get_job_status(job_id)
        assert job_status.status == "failed"
        assert job_status.progress == 0.0
        assert job_status.message == "Job failed"
        assert job_status.completed_at is not None
    
    def test_update_job_status_nonexistent(self):
        """Test updating status of nonexistent job"""
        # Should not raise an exception
        self.job_manager._update_job_status("nonexistent-job-id", "running", 0.5, "Processing...")
    
    @patch('backend.jobs.job_manager.MSAEngine')
    @patch('backend.jobs.job_manager.MSAAnnotationEngine')
    def test_process_msa_job_success(self, mock_annotation_engine_class, mock_msa_engine_class):
        """Test successful MSA job processing"""
        # Mock MSA engine
        mock_msa_engine = MagicMock()
        mock_msa_engine.create_msa.return_value = MagicMock(
            msa_id="test-msa-result",
            sequences=[],
            alignment_matrix=[],
            consensus="",
            alignment_method=AlignmentMethod.MUSCLE,
            created_at="2023-01-01T00:00:00",
            metadata={}
        )
        mock_msa_engine_class.return_value = mock_msa_engine
        
        # Mock annotation engine
        mock_annotation_engine = MagicMock()
        mock_annotation_engine.annotate_msa.return_value = MagicMock(
            msa_id="test-msa-result",
            annotated_sequences=[],
            numbering_scheme=NumberingScheme.IMGT,
            region_mappings={}
        )
        mock_annotation_engine_class.return_value = mock_annotation_engine
        
        job_id = self.job_manager.create_msa_job(self.test_msa_request)
        
        # Simulate job processing
        self.job_manager._process_msa_job(job_id, self.test_msa_request)
        
        # Check final job status
        job_status = self.job_manager.get_job_status(job_id)
        assert job_status.status == "completed"
        assert job_status.progress == 1.0
        assert job_status.message == "MSA creation completed successfully"
        assert job_status.result is not None
        assert job_status.result["job_type"] == "msa_creation"
    
    @patch('backend.jobs.job_manager.MSAEngine')
    @patch('backend.jobs.job_manager.MSAAnnotationEngine')
    def test_process_msa_job_failure(self, mock_annotation_engine_class, mock_msa_engine_class):
        """Test MSA job processing with failure"""
        # Mock MSA engine to raise exception
        mock_msa_engine = MagicMock()
        mock_msa_engine.create_msa.side_effect = Exception("Test error")
        mock_msa_engine_class.return_value = mock_msa_engine
        
        job_id = self.job_manager.create_msa_job(self.test_msa_request)
        
        # Simulate job processing
        self.job_manager._process_msa_job(job_id, self.test_msa_request)
        
        # Check final job status
        job_status = self.job_manager.get_job_status(job_id)
        assert job_status.status == "failed"
        assert job_status.progress == 0.0
        assert "Test error" in job_status.message
    
    def test_process_msa_job_empty_sequences(self):
        """Test MSA job processing with empty sequences"""
        empty_request = MSACreationRequest(
            sequences=[],
            alignment_method=AlignmentMethod.MUSCLE,
            numbering_scheme=NumberingScheme.IMGT
        )
        
        job_id = self.job_manager.create_msa_job(empty_request)
        
        # Simulate job processing
        self.job_manager._process_msa_job(job_id, empty_request)
        
        # Check final job status
        job_status = self.job_manager.get_job_status(job_id)
        assert job_status.status == "failed"
        assert "No valid sequences provided" in job_status.message
    
    def test_process_annotation_job_success(self):
        """Test successful annotation job processing"""
        job_id = self.job_manager.create_annotation_job(self.test_annotation_request)
        
        # Simulate job processing
        self.job_manager._process_annotation_job(job_id, self.test_annotation_request)
        
        # Check final job status
        job_status = self.job_manager.get_job_status(job_id)
        assert job_status.status == "completed"
        assert job_status.progress == 1.0
        assert job_status.message == "Annotation completed successfully"
        assert job_status.result is not None
        assert job_status.result["job_type"] == "msa_annotation"
    
    def test_process_annotation_job_failure(self):
        """Test annotation job processing with failure"""
        job_id = self.job_manager.create_annotation_job(self.test_annotation_request)
        
        # Mock the job to fail
        with patch.object(self.job_manager, '_update_job_status') as mock_update:
            mock_update.side_effect = Exception("Test error")
            
            # Simulate job processing
            self.job_manager._process_annotation_job(job_id, self.test_annotation_request)
            
            # Check final job status
            job_status = self.job_manager.get_job_status(job_id)
            assert job_status.status == "failed"
            assert "Test error" in job_status.message
    
    def test_cleanup_old_jobs(self):
        """Test cleanup of old jobs"""
        # Create some jobs
        job_id_1 = self.job_manager.create_msa_job(self.test_msa_request)
        job_id_2 = self.job_manager.create_msa_job(self.test_msa_request)
        job_id_3 = self.job_manager.create_msa_job(self.test_msa_request)
        
        # Mark jobs as completed/failed
        self.job_manager._update_job_status(job_id_1, "completed", 1.0, "Completed")
        self.job_manager._update_job_status(job_id_2, "failed", 0.0, "Failed")
        # Leave job_id_3 as pending
        
        # Verify jobs exist
        assert self.job_manager.get_job_status(job_id_1) is not None
        assert self.job_manager.get_job_status(job_id_2) is not None
        assert self.job_manager.get_job_status(job_id_3) is not None
        
        # Clean up old jobs (should remove completed/failed jobs)
        self.job_manager.cleanup_old_jobs(max_age_hours=0)  # Clean up immediately
        
        # Verify completed/failed jobs are removed, pending job remains
        assert self.job_manager.get_job_status(job_id_1) is None
        assert self.job_manager.get_job_status(job_id_2) is None
        assert self.job_manager.get_job_status(job_id_3) is not None
    
    def test_job_manager_thread_safety(self):
        """Test that job manager is thread-safe"""
        import threading
        
        # Create multiple jobs simultaneously
        job_ids = []
        threads = []
        
        def create_job():
            job_id = self.job_manager.create_msa_job(self.test_msa_request)
            job_ids.append(job_id)
        
        # Create 10 jobs in parallel
        for _ in range(10):
            thread = threading.Thread(target=create_job)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all jobs were created successfully
        assert len(job_ids) == 10
        for job_id in job_ids:
            job_status = self.job_manager.get_job_status(job_id)
            assert job_status is not None
            assert job_status.status == "pending"
    
    def test_job_manager_concurrent_updates(self):
        """Test concurrent updates to job status"""
        import threading
        
        job_id = self.job_manager.create_msa_job(self.test_msa_request)
        
        def update_job(thread_id):
            for i in range(10):
                self.job_manager._update_job_status(
                    job_id, 
                    "running", 
                    i * 0.1, 
                    f"Thread {thread_id} update {i}"
                )
                time.sleep(0.01)  # Small delay
        
        # Create multiple threads updating the same job
        threads = []
        for i in range(5):
            thread = threading.Thread(target=update_job, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify job still exists and has valid status
        job_status = self.job_manager.get_job_status(job_id)
        assert job_status is not None
        assert job_status.status in ["pending", "running", "completed", "failed"]
        assert 0.0 <= job_status.progress <= 1.0
