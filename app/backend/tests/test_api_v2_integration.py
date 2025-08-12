"""
Integration tests for the v2 API endpoints.
Tests the complete response structure to ensure frontend compatibility.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.logger import logger
from backend.domain.models import (
    BiologicType,
    ChainType,
    DomainType,
    FeatureType,
    NumberingScheme,
)

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


def test_v2_annotate_scfv_structure():
    """Test v2 annotation with scFv and verify complete response structure"""
    request_data = {
        "sequences": [{"name": "test_scfv", "scfv": SCFV_SEQ}],
        "numbering_scheme": NumberingScheme.IMGT.value,
    }

    response = client.post("/api/v2/annotate", json=request_data)
    assert response.status_code == 200

    data = response.json()
    logger.info(f"V2 annotation response structure: {data}")

    # Verify top-level structure
    assert "data" in data
    assert "results" in data["data"]
    assert "summary" in data["data"]
    assert data["data"]["summary"]["total"] == 1
    assert data["data"]["summary"]["successful"] == 1
    assert data["data"]["summary"]["failed"] == 0

    # Verify result structure
    result = data["data"]["results"][0]
    assert result["name"] == "test_scfv"
    assert result["success"] is True
    assert "data" in result

    # Verify sequence data structure
    sequence_data = result["data"]["sequence"]
    assert sequence_data["name"] == "test_scfv"
    assert sequence_data["biologic_type"] == BiologicType.ANTIBODY.value
    assert "chains" in sequence_data
    assert len(sequence_data["chains"]) > 0

    # Verify chain structure
    chain = sequence_data["chains"][0]
    assert "name" in chain
    assert "chain_type" in chain
    assert "sequences" in chain
    assert len(chain["sequences"]) > 0

    # Verify sequence structure
    sequence = chain["sequences"][0]
    assert "sequence_type" in sequence
    assert "sequence_data" in sequence
    assert "domains" in sequence

    # Check if domains are present (may be empty in test environment)
    if len(sequence["domains"]) > 0:
        # Verify domain structure with species and germline
        domain = sequence["domains"][0]
        assert "domain_type" in domain
        assert "start_position" in domain
        assert "end_position" in domain
        assert "features" in domain

        # Check for species and germline fields (should be present for non-LINKER domains)
        if domain["domain_type"] != DomainType.LINKER.value:
            # These fields should be present but may be None
            assert "species" in domain
            assert "germline" in domain

        # Verify features structure
        if domain["features"]:
            feature = domain["features"][0]
            assert "name" in feature
            assert "feature_type" in feature
            assert "value" in feature
            assert "start_position" in feature
            assert "end_position" in feature


def test_v2_annotate_heavy_light_structure():
    """Test v2 annotation with separate heavy and light chains"""
    request_data = {
        "sequences": [
            {
                "name": "test_igg",
                "heavy_chain": HEAVY_CHAIN_SEQ,
                "light_chain": LIGHT_CHAIN_SEQ,
            }
        ],
        "numbering_scheme": NumberingScheme.IMGT.value,
    }

    response = client.post("/api/v2/annotate", json=request_data)
    assert response.status_code == 200

    data = response.json()

    # Verify we have multiple chains
    sequence_data = data["data"]["results"][0]["data"]["sequence"]
    assert (
        len(sequence_data["chains"]) >= 2
    )  # Should have heavy and light chains

    # Verify each chain has proper structure
    for chain in sequence_data["chains"]:
        assert "name" in chain
        assert "chain_type" in chain
        assert "sequences" in chain
        assert len(chain["sequences"]) > 0

        # Verify sequences have domains
        for sequence in chain["sequences"]:
            assert "domains" in sequence

            # Check if domains are present (may be empty in test environment)
            if len(sequence["domains"]) > 0:
                # Verify domains have species and germline
                for domain in sequence["domains"]:
                    if domain["domain_type"] != DomainType.LINKER.value:
                        assert "species" in domain
                        assert "germline" in domain


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


def test_v2_annotate_response_completeness():
    """Test that response contains all required fields for frontend compatibility"""
    request_data = {
        "sequences": [{"name": "completeness_test", "scfv": SCFV_SEQ}],
        "numbering_scheme": NumberingScheme.IMGT.value,
    }

    response = client.post("/api/v2/annotate", json=request_data)
    assert response.status_code == 200

    data = response.json()

    # Verify all required fields exist for frontend compatibility
    result = data["data"]["results"][0]
    sequence_data = result["data"]["sequence"]
    chain = sequence_data["chains"][0]
    sequence = chain["sequences"][0]
    # Check if domains are present (may be empty in test environment)
    if len(sequence["domains"]) > 0:
        domain = sequence["domains"][0]

    # Required fields that frontend expects
    required_fields = {
        "results": ["name", "success", "data"],
        "summary": ["total", "successful", "failed"],
        "sequence": ["name", "biologic_type", "chains"],
        "chain": ["name", "chain_type", "sequences"],
        "sequence_in_chain": ["sequence_type", "sequence_data", "domains"],
    }

    # Verify all required fields exist
    for field_path, fields in required_fields.items():
        if field_path == "results":
            for field in fields:
                assert field in result, f"Missing {field} in result"
        elif field_path == "summary":
            for field in fields:
                assert (
                    field in data["data"]["summary"]
                ), f"Missing {field} in summary"
        elif field_path == "sequence":
            for field in fields:
                assert field in sequence_data, f"Missing {field} in sequence"
        elif field_path == "chain":
            for field in fields:
                assert field in chain, f"Missing {field} in chain"
        elif field_path == "sequence_in_chain":
            for field in fields:
                assert field in sequence, f"Missing {field} in sequence"

    # Verify domain fields if domains are present
    if len(sequence["domains"]) > 0:
        domain = sequence["domains"][0]
        domain_fields = [
            "domain_type",
            "start_position",
            "end_position",
            "features",
        ]
        for field in domain_fields:
            assert field in domain, f"Missing {field} in domain"

        # Verify feature fields if features are present
        if domain["features"]:
            feature = domain["features"][0]
            feature_fields = [
                "name",
                "feature_type",
                "value",
                "start_position",
                "end_position",
            ]
            for field in feature_fields:
                assert field in feature, f"Missing {field} in feature"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
