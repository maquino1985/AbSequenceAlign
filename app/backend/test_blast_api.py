#!/usr/bin/env python3
"""
Simple test script for BLAST API endpoints
"""

import sys
import os

sys.path.append(".")

from fastapi.testclient import TestClient
from main import app


def test_blast_endpoints():
    """Test BLAST API endpoints"""
    client = TestClient(app)

    print("Testing BLAST API endpoints...")

    # Test health endpoint
    response = client.get("/api/v2/blast/health")
    print(f"Health endpoint: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")

    # Test databases endpoint
    response = client.get("/api/v2/blast/databases")
    print(f"Databases endpoint: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")

    # Test organisms endpoint
    response = client.get("/api/v2/blast/organisms")
    print(f"Organisms endpoint: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")

    print("BLAST API tests completed!")


if __name__ == "__main__":
    test_blast_endpoints()
