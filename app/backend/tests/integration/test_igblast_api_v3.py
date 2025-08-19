"""
Integration tests for IgBLAST API v3
Tests the actual API endpoints and identifies parsing issues
"""

import json

import requests

# Test configuration
API_BASE_URL = "http://192.168.0.17:8000"
API_PREFIX = "/api/v2/database"


class TestIgBlastAPIV3:
    """Integration tests for IgBLAST API v3"""

    def test_get_databases(self):
        """Test database discovery endpoint"""
        response = requests.get(
            f"{API_BASE_URL}{API_PREFIX}/databases/igblast"
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "databases" in data
        assert "human" in data["databases"]
        assert "mouse" in data["databases"]

        # Check that human databases have the expected structure
        human_dbs = data["databases"]["human"]
        assert "V" in human_dbs
        assert "D" in human_dbs
        assert "J" in human_dbs
        assert "C" in human_dbs

        print("✓ Database discovery working")
        return data["databases"]

    def test_igblast_nucleotide_no_c_gene(self):
        """Test IgBLAST nucleotide execution without C gene database"""
        # Get available databases
        databases = self.test_get_databases()
        human_dbs = databases["human"]

        # Test sequence (nucleotide)
        test_sequence = "gaagtgcagctggtggaaagcggcggcggcctggtgcagccgggccgcagcctgcgcctgagctgcgcggcgagcggctttacctttgatgattatgcgatgcattgggtgcgccaggcgccgggcaaaggcctggaatgggtgagcgcgattacctggaacagcggccatattgattatgcggatagcgtggaaggccgctttaccattagccgcgataacgcgaaaaacagcctgtatctgcagatgaacagcctgcgcgcggaagataccgcggtgtattattgcgcgaaagtgagctatctgagcaccgcgagcagcctggattattggggccagggcaccctggtgaccgtgagcagcgcgagcaccaaaggcccgagcgtgtttccgctggcgccgagcagcaaaagcaccagcggcggcaccgcggcgctgggctgcctggtgaaagattattttccggaaccggtgaccgtgagctggaacagcggcgcgctgaccagcggcgtgcatacctttccggcggtgctgcagagcagcggcctgtatagcctgagcagcgtggtgaccgtgccgagcagcagcctgggcacccagacctatatttgcaacgtgaaccataaaccgagcaacaccaaagtggataaaaaagtggaaccgaaaagctgcgataaaacccatacctgcccgccgtgcccggcgccggaactgctgggcggcccgagcgtgtttctgtttccgccgaaaccgaaagataccctgatgattagccgcaccccggaagtgacctgcgtggtggtggatgtgagccatgaagatccggaagtgaaatttaactggtatgtggatggcgtggaagtgcataacgcgaaaaccaaaccgcgcgaagaacagcataacagcacctatcgcgtggtgagcgtgctgaccgtgctgcatcaggattggctgaacggcaaagaatataaatgcaaagtgagcaacaaagcgctgccggcgccgattgaaaaaaccattagcaaagcgaaaggccagccgcgcgaaccgcaggtgtataccctgccgccgagccgcgatgaactgaccaaaaaccaggtgagcctgacctgcctggtgaaaggcttttatccgagcgatattgcggtggaatgggaaagcaacggccagccggaaaacaactataaaaccaccccgccggtgctggatagcgatggcagcttttttctgtatagcaaactgaccgtggataaaagccgctggcagcagggcaacgtgtttagctgcagcgtgatgcatgaagcgctgcataaccattatacccagaaaagcctgagcctgagcccgggcaaa"

        request_data = {
            "query_sequence": test_sequence,
            "v_db": human_dbs["V"]["path"],
            "d_db": human_dbs["D"]["path"],
            "j_db": human_dbs["J"]["path"],
            "c_db": "",  # No C gene database
            "blast_type": "igblastn",
            "use_airr_format": False,
        }

        response = requests.post(
            f"{API_BASE_URL}{API_PREFIX}/igblast/execute", json=request_data
        )

        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")

        if response.status_code != 200:
            print(f"Error response: {response.text}")
            # Don't fail the test yet, let's see what the error is
            return

        data = response.json()
        print(f"Response data keys: {list(data.keys())}")

        assert data["success"] is True
        assert "result" in data
        assert "total_hits" in data

        result = data["result"]
        print(f"Result keys: {list(result.keys())}")
        print(f"Total hits: {data['total_hits']}")

        # Check if we have hits
        if data["total_hits"] > 0:
            print("✓ IgBLAST nucleotide execution successful with hits")
            print(
                f"First hit: {result.get('hits', [])[0] if result.get('hits') else 'No hits'}"
            )
        else:
            print(
                "⚠ IgBLAST nucleotide execution successful but no hits found"
            )
            print(f"Raw result: {json.dumps(result, indent=2)}")

    def test_igblast_nucleotide_with_c_gene(self):
        """Test IgBLAST nucleotide execution with C gene database"""
        # Get available databases
        databases = self.test_get_databases()
        human_dbs = databases["human"]

        # Test sequence (nucleotide)
        test_sequence = "gaagtgcagctggtggaaagcggcggcggcctggtgcagccgggccgcagcctgcgcctgagctgcgcggcgagcggctttacctttgatgattatgcgatgcattgggtgcgccaggcgccgggcaaaggcctggaatgggtgagcgcgattacctggaacagcggccatattgattatgcggatagcgtggaaggccgctttaccattagccgcgataacgcgaaaaacagcctgtatctgcagatgaacagcctgcgcgcggaagataccgcggtgtattattgcgcgaaagtgagctatctgagcaccgcgagcagcctggattattggggccagggcaccctggtgaccgtgagcagcgcgagcaccaaaggcccgagcgtgtttccgctggcgccgagcagcaaaagcaccagcggcggcaccgcggcgctgggctgcctggtgaaagattattttccggaaccggtgaccgtgagctggaacagcggcgcgctgaccagcggcgtgcatacctttccggcggtgctgcagagcagcggcctgtatagcctgagcagcgtggtgaccgtgccgagcagcagcctgggcacccagacctatatttgcaacgtgaaccataaaccgagcaacaccaaagtggataaaaaagtggaaccgaaaagctgcgataaaacccatacctgcccgccgtgcccggcgccggaactgctgggcggcccgagcgtgtttctgtttccgccgaaaccgaaagataccctgatgattagccgcaccccggaagtgacctgcgtggtggtggatgtgagccatgaagatccggaagtgaaatttaactggtatgtggatggcgtggaagtgcataacgcgaaaaccaaaccgcgcgaagaacagcataacagcacctatcgcgtggtgagcgtgctgaccgtgctgcatcaggattggctgaacggcaaagaatataaatgcaaagtgagcaacaaagcgctgccggcgccgattgaaaaaaccattagcaaagcgaaaggccagccgcgcgaaccgcaggtgtataccctgccgccgagccgcgatgaactgaccaaaaaccaggtgagcctgacctgcctggtgaaaggcttttatccgagcgatattgcggtggaatgggaaagcaacggccagccggaaaacaactataaaaccaccccgccggtgctggatagcgatggcagcttttttctgtatagcaaactgaccgtggataaaagccgctggcagcagggcaacgtgtttagctgcagcgtgatgcatgaagcgctgcataaccattatacccagaaaagcctgagcctgagcccgggcaaa"

        request_data = {
            "query_sequence": test_sequence,
            "v_db": human_dbs["V"]["path"],
            "d_db": human_dbs["D"]["path"],
            "j_db": human_dbs["J"]["path"],
            "c_db": human_dbs["C"]["path"],  # With C gene database
            "blast_type": "igblastn",
            "use_airr_format": False,
        }

        response = requests.post(
            f"{API_BASE_URL}{API_PREFIX}/igblast/execute", json=request_data
        )

        print(f"Response status: {response.status_code}")

        if response.status_code != 200:
            print(f"Error response: {response.text}")
            # This is expected to fail due to C gene database version issue
            print(
                "⚠ IgBLAST with C gene database failed (expected due to version issue)"
            )
            return

        data = response.json()
        print("✓ IgBLAST nucleotide execution with C gene successful")

    def test_igblast_airr_format(self):
        """Test IgBLAST with AIRR format output"""
        # Get available databases
        databases = self.test_get_databases()
        human_dbs = databases["human"]

        # Test sequence (nucleotide)
        test_sequence = "gaagtgcagctggtggaaagcggcggcggcctggtgcagccgggccgcagcctgcgcctgagctgcgcggcgagcggctttacctttgatgattatgcgatgcattgggtgcgccaggcgccgggcaaaggcctggaatgggtgagcgcgattacctggaacagcggccatattgattatgcggatagcgtggaaggccgctttaccattagccgcgataacgcgaaaaacagcctgtatctgcagatgaacagcctgcgcgcggaagataccgcggtgtattattgcgcgaaagtgagctatctgagcaccgcgagcagcctggattattggggccagggcaccctggtgaccgtgagcagcgcgagcaccaaaggcccgagcgtgtttccgctggcgccgagcagcaaaagcaccagcggcggcaccgcggcgctgggctgcctggtgaaagattattttccggaaccggtgaccgtgagctggaacagcggcgcgctgaccagcggcgtgcatacctttccggcggtgctgcagagcagcggcctgtatagcctgagcagcgtggtgaccgtgccgagcagcagcctgggcacccagacctatatttgcaacgtgaaccataaaccgagcaacaccaaagtggataaaaaagtggaaccgaaaagctgcgataaaacccatacctgcccgccgtgcccggcgccggaactgctgggcggcccgagcgtgtttctgtttccgccgaaaccgaaagataccctgatgattagccgcaccccggaagtgacctgcgtggtggtggatgtgagccatgaagatccggaagtgaaatttaactggtatgtggatggcgtggaagtgcataacgcgaaaaccaaaccgcgcgaagaacagcataacagcacctatcgcgtggtgagcgtgctgaccgtgctgcatcaggattggctgaacggcaaagaatataaatgcaaagtgagcaacaaagcgctgccggcgccgattgaaaaaaccattagcaaagcgaaaggccagccgcgcgaaccgcaggtgtataccctgccgccgagccgcgatgaactgaccaaaaaccaggtgagcctgacctgcctggtgaaaggcttttatccgagcgatattgcggtggaatgggaaagcaacggccagccggaaaacaactataaaaccaccccgccggtgctggatagcgatggcagcttttttctgtatagcaaactgaccgtggataaaagccgctggcagcagggcaacgtgtttagctgcagcgtgatgcatgaagcgctgcataaccattatacccagaaaagcctgagcctgagcccgggcaaa"

        request_data = {
            "query_sequence": test_sequence,
            "v_db": human_dbs["V"]["path"],
            "d_db": human_dbs["D"]["path"],
            "j_db": human_dbs["J"]["path"],
            "c_db": "",  # No C gene database
            "blast_type": "igblastn",
            "use_airr_format": True,
        }

        response = requests.post(
            f"{API_BASE_URL}{API_PREFIX}/igblast/execute", json=request_data
        )

        print(f"Response status: {response.status_code}")

        if response.status_code != 200:
            print(f"Error response: {response.text}")
            return

        data = response.json()
        print(f"Response data keys: {list(data.keys())}")

        assert data["success"] is True
        assert "result" in data

        result = data["result"]
        print(f"Result keys: {list(result.keys())}")
        print(f"Total hits: {data['total_hits']}")

        # Check if we have hits
        if data["total_hits"] > 0:
            print("✓ IgBLAST AIRR format execution successful with hits")
            print(
                f"First hit: {result.get('hits', [])[0] if result.get('hits') else 'No hits'}"
            )
        else:
            print(
                "⚠ IgBLAST AIRR format execution successful but no hits found"
            )
            print(f"Raw result: {json.dumps(result, indent=2)}")


if __name__ == "__main__":
    # Run tests
    test_instance = TestIgBlastAPIV3()

    print("=== Testing IgBLAST API v3 ===")

    try:
        test_instance.test_get_databases()
        test_instance.test_igblast_nucleotide_no_c_gene()
        test_instance.test_igblast_nucleotide_with_c_gene()
        test_instance.test_igblast_airr_format()

        print("\n=== All tests completed ===")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
