"""
Integration tests for the v2 API endpoints.
Tests the complete response structure to ensure frontend compatibility.
"""

import pytest
from fastapi.testclient import TestClient

from backend.domain.models import (
    NumberingScheme,
)
from backend.logger import logger
from backend.main import app
from backend.models.models_v2 import DomainType

client = TestClient(app)

# Test sequences
SCFV_SEQ = (
    "DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK"
    "GGGGGSGGGGSGGGGSGGGGS"
    "QVQLKQSGAEVKKPGASVKVSCKASGYTFTDEYMNWVRQAPGKSLEWMGYINPNNGGADYNQKFQGRVTMTVDQSISTAYMELSRLRSDDSAVYFCARLGYSNPYFDFWGQGTLVKVSS"
)

HEAVY_CHAIN_SEQ = "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS"

LIGHT_CHAIN_SEQ = "DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK"


def test_v2_health_check():
    """Test v2 health endpoint"""
    response = client.get("/api/v2/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"



def test_v2_annotate_multiple_sequences():
    """Test v2 annotation with multiple sequences"""
    request_data = {
        "sequences": [
            {"name": "seq1", "scfv": SCFV_SEQ},
            {
                "name": "seq2",
                "heavy_chain": HEAVY_CHAIN_SEQ,
                "light_chain": LIGHT_CHAIN_SEQ,
            },
        ],
        "numbering_scheme": NumberingScheme.IMGT.value,
    }

    response = client.post("/api/v2/annotate", json=request_data)
    assert response.status_code == 200

    data = response.json()

    # Verify multiple results
    assert len(data["data"]["results"]) == 2
    assert data["data"]["summary"]["total"] == 2
    assert data["data"]["summary"]["successful"] == 2

    # Verify each result has proper structure
    for result in data["data"]["results"]:
        assert result["success"] is True
        assert "data" in result
        assert "sequence" in result["data"]


def test_v2_annotate_case_insensitive_numbering():
    """Test that numbering scheme accepts valid lowercase values"""
    request_data = {
        "sequences": [{"name": "test_case", "scfv": SCFV_SEQ}],
        "numbering_scheme": "imgt",  # Lowercase - valid value
    }

    response = client.post("/api/v2/annotate", json=request_data)
    assert response.status_code == 200

    data = response.json()
    assert data["data"]["results"][0]["success"] is True


def test_v2_annotate_invalid_numbering():
    """Test that invalid numbering scheme returns error"""
    request_data = {
        "sequences": [{"name": "test_invalid", "scfv": SCFV_SEQ}],
        "numbering_scheme": "invalid_scheme",
    }

    response = client.post("/api/v2/annotate", json=request_data)
    assert response.status_code == 422  # Pydantic validation error
    error_detail = response.json()["detail"]
    # Check if it's a list of validation errors
    if isinstance(error_detail, list):
        error_messages = [error["msg"] for error in error_detail]
        assert any("Input should be" in msg for msg in error_messages)
    else:
        assert "Invalid numbering scheme" in error_detail


def test_v2_annotate_invalid_sequence():
    """Test that invalid sequence returns error"""
    request_data = {
        "sequences": [
            {
                "name": "test_invalid",
                "scfv": "INVALID123",  # Invalid amino acids
            }
        ],
        "numbering_scheme": "imgt",
    }

    response = client.post("/api/v2/annotate", json=request_data)
    assert response.status_code == 422  # Pydantic validation error
    error_detail = response.json()["detail"]
    # Check if it's a list of validation errors
    if isinstance(error_detail, list):
        error_messages = [error["msg"] for error in error_detail]
        assert any("Invalid amino acids" in msg for msg in error_messages)
    else:
        assert "Invalid amino acid" in error_detail


def test_v2_annotate_empty_sequences():
    """Test that empty sequences list returns error"""
    request_data = {
        "sequences": [],
        "numbering_scheme": NumberingScheme.IMGT.value,
    }

    response = client.post("/api/v2/annotate", json=request_data)
    assert response.status_code == 400  # Business logic validation error


def test_v2_annotate_missing_sequences():
    """Test that missing sequences field returns error"""
    request_data = {"numbering_scheme": NumberingScheme.IMGT.value}

    response = client.post("/api/v2/annotate", json=request_data)
    assert response.status_code == 422  # Pydantic validation error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
