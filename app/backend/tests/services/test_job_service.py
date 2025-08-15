import pytest
from unittest.mock import Mock, patch

from backend.models.models import MSAAnnotationRequest
from backend.services.job_service import JobService


@pytest.fixture
def job_service():
    return JobService()


@pytest.fixture
def mock_annotation_request():
    return MSAAnnotationRequest(
        msa_result={},
        numbering_scheme="imgt"
    )


def test_create_annotation_job(job_service, mock_annotation_request):
    with patch('backend.jobs.job_manager.job_manager') as mock_manager:
        mock_manager.create_annotation_job.return_value = "job123"
        
        job_id = job_service.create_annotation_job(mock_annotation_request)
        
        assert job_id == "job123"
        mock_manager.create_annotation_job.assert_called_once_with(mock_annotation_request)


def test_get_job_status_existing(job_service):
    with patch('backend.jobs.job_manager.job_manager') as mock_manager:
        mock_status = Mock(model_dump=lambda: {"status": "completed"})
        mock_manager.get_job_status.return_value = mock_status
        
        status = job_service.get_job_status("job123")
        
        assert status == {"status": "completed"}
        mock_manager.get_job_status.assert_called_once_with("job123")


def test_get_job_status_not_found(job_service):
    with patch('backend.jobs.job_manager.job_manager') as mock_manager:
        mock_manager.get_job_status.return_value = None
        
        status = job_service.get_job_status("nonexistent")
        
        assert status is None
        mock_manager.get_job_status.assert_called_once_with("nonexistent")


def test_list_jobs(job_service):
    with patch('backend.jobs.job_manager.job_manager') as mock_manager:
        mock_status1 = Mock(model_dump=lambda: {"id": "job1", "status": "completed"})
        mock_status2 = Mock(model_dump=lambda: {"id": "job2", "status": "pending"})
        mock_manager.jobs = {
            "job1": mock_status1,
            "job2": mock_status2
        }
        
        jobs = job_service.list_jobs()
        
        assert len(jobs) == 2
        assert any(job["id"] == "job1" and job["status"] == "completed" for job in jobs)
        assert any(job["id"] == "job2" and job["status"] == "pending" for job in jobs)
