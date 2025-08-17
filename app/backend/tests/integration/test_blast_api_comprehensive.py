"""
Comprehensive integration tests for BLAST and IgBLAST API functionality.

This test suite validates:
1. API returns all expected data for different sequence types
2. Frontend can properly handle all API response types
3. Full, partial, and no results scenarios
4. Type consistency between backend and frontend
"""

import pytest
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class TestSequence:
    """Test sequence with metadata for systematic testing."""

    name: str
    sequence: str
    sequence_type: str  # 'nucleotide' or 'protein'
    expected_results: Dict[str, Any]
    description: str
    category: str  # 'full', 'partial', 'none', 'edge_case'


class TestBlastAPIComprehensive:
    """Comprehensive test suite for BLAST API functionality."""

    @pytest.fixture
    def api_base_url(self):
        """API base URL for testing."""
        return "http://localhost:8000"

    @pytest.fixture
    def test_sequences(self):
        """Define comprehensive test sequences."""
        return [
            # Complete Humira heavy chain nucleotide - should return V/D/J/C/CDR3
            TestSequence(
                name="Humira_Heavy_Full_Nucleotide",
                sequence="gaagtgcagctggtggaaagcggcggcggcctggtgcagccgggccgcagcctgcgcctgagctgcgcggcgagcggctttacctttgatgattatgcgatgcattgggtgcgccaggcgccgggcaaaggcctggaatgggtgagcgcgattacctggaacagcggccatattgattatgcggatagcgtggaaggccgctttaccattagccgcgataacgcgaaaaacagcctgtatctgcagatgaacagcctgcgcgcggaagataccgcggtgtattattgcgcgaaagtgagctatctgagcaccgcgagcagcctggattattggggccagggcaccctggtgaccgtgagcagcgcgagcaccaaaggcccgagcgtgtttccgctggcgccgagcagcaaaagcaccagcggcggcaccgcggcgctgggctgcctggtgaaagattattttccggaaccggtgaccgtgagctggaacagcggcgcgctgaccagcggcgtgcatacctttccggcggtgctgcagagcagcggcctgtatagcctgagcagcgtggtgaccgtgccgagcagcagcctgggcacccagacctatatttgcaacgtgaaccataaaccgagcaacaccaaagtggataaaaaagtggaaccgaaaagctgcgataaaacccatacctgcccgccgtgcccggcgccggaactgctgggcggcccgagcgtgtttctgtttccgccgaaaccgaaagataccctgatgattagccgcaccccggaagtgacctgcgtggtggtggatgtgagccatgaagatccggaagtgaaatttaactggtatgtggatggcgtggaagtgcataacgcgaaaaccaaaccgcgcgaagaacagtataacagcacctatcgcgtggtgagcgtgctgaccgtgctgcatcaggattggctgaacggcaaagaatataaatgcaaagtgagcaacaaagcgctgccggcgccgattgaaaaaaccattagcaaagcgaaaggccagccgcgcgaaccgcaggtgtataccctgccgccgagccgcgatgaactgaccaaaaaccaggtgagcctgacctgcctggtgaaaggcttttatccgagcgatattgcggtggaatgggaaagcaacggccagccggaaaacaactataaaaccaccccgccggtgctggatagcgatggcagcttttttctgtatagcaaactgaccgtggataaaagccgctggcagcagggcaacgtgtttagctgcagcgtgatgcatgaagcgctgcataaccattatacccagaaaagcctgagcctgagcccgggcaaa",
                sequence_type="nucleotide",
                expected_results={
                    "v_gene": "IGHV3-9*01",
                    "d_gene": "IGHD1-26*01,IGHD5-5*01,IGHD6-13*01",
                    "j_gene": "IGHJ1*01",
                    "c_gene": "IGHG1",
                    "cdr3_sequence": "TTCTGAGCACCGCGAGCAGCCTGGATTAT",
                    "cdr3_start": 296,
                    "cdr3_end": 330,
                    "has_airr_data": True,
                },
                description="Complete Humira heavy chain nucleotide sequence - should return full V/D/J/C/CDR3 data",
                category="full",
            ),
            # Complete Humira heavy chain protein - should return V gene only (IgBLAST limitation)
            TestSequence(
                name="Humira_Heavy_Full_Protein",
                sequence="ELQLQESGPGLVKPSETLSLTCAVSGVSFSDYHWAWIRDPPGKGLEWIGDINHRGHTNYNPSLKSRVTVSIDTSKNQFSLKLSSVTAADTAVYFCARDFPNFIFDFWGQGTLVTVSSASTKGPSVFPLAPSSKSTSGGTAALGCLVKDYFPEPVTVSWNSGALTSGVHTFPAVLQSSGLYSLSSVVTVPSSSLGTQTYICNVNHKPSNTKVDEKVEPDSCDKTHTCPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVCTLPPSREEMTKNQVSLSCAVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLVSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK",
                sequence_type="protein",
                expected_results={
                    "v_gene": "IGHV4-34*01",  # Should match V gene family
                    "d_gene": None,  # IgBLAST protein doesn't detect D genes
                    "j_gene": None,  # IgBLAST protein doesn't detect J genes
                    "c_gene": None,  # IgBLAST protein doesn't detect C genes
                    "cdr3_sequence": None,  # No CDR3 for protein searches
                    "has_airr_data": False,  # No AIRR data for protein searches
                },
                description="Complete Humira heavy chain protein sequence - IgBLAST protein only detects V genes",
                category="partial",
            ),
            # Partial V gene only nucleotide sequence
            TestSequence(
                name="Partial_V_Gene_Nucleotide",
                sequence="CAGGTGCAGCTGGTGGAGTCTGGGGGAGGCGTGGTCCAGCCTGGGAGGTCCCTGAGACTCTCCTGTGCAGCCTCTGGATTCACCTTTAGCAGCTATGCCATGAGCTGGGTCCGCCAGGCTCCAGGCAAGGGGCTGGAGTGGGTGGCAGTTATATCATATGATGGAAGTAATAAATACTATGCAGACTCCGTGAAGGGCCGATTCACCATCTCCAGAGACAATTCCAAGAACACGCTGTATCTGCAAATGAACAGCCTGAGAGCCGAGGACACGGCTGTGTATTACTGTGCGAGAGA",
                sequence_type="nucleotide",
                expected_results={
                    "v_gene": "IGHV3-30*03",  # Actual result from API
                    "d_gene": None,  # May not have D gene for partial sequence
                    "j_gene": None,  # May not have J gene for partial sequence
                    "c_gene": None,  # May not have C gene for partial sequence
                    "cdr3_sequence": None,  # May not have CDR3 for partial sequence
                    "has_airr_data": True,  # Should have AIRR data even for partial
                },
                description="Partial V gene nucleotide sequence - may have limited gene assignments",
                category="partial",
            ),
            # Invalid nucleotide sequence
            TestSequence(
                name="Invalid_Nucleotide",
                sequence="INVALIDSEQUENCE123!@#",
                sequence_type="nucleotide",
                expected_results={
                    "error": "Invalid nucleotide characters",
                    "success": False,
                },
                description="Invalid nucleotide sequence with non-DNA characters",
                category="none",
            ),
            # Non-antibody protein sequence
            TestSequence(
                name="Non_Antibody_Protein",
                sequence="MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG",
                sequence_type="protein",
                expected_results={
                    "v_gene": None,  # Should not match antibody V genes
                    "d_gene": None,
                    "j_gene": None,
                    "c_gene": None,
                    "cdr3_sequence": None,
                    "has_airr_data": False,
                },
                description="Non-antibody protein sequence - should not match antibody genes",
                category="none",
            ),
            # Very short sequence
            TestSequence(
                name="Very_Short_Sequence",
                sequence="ATGCAG",
                sequence_type="nucleotide",
                expected_results={
                    "v_gene": None,  # Too short for meaningful analysis
                    "d_gene": None,
                    "j_gene": None,
                    "c_gene": None,
                    "cdr3_sequence": None,
                    "has_airr_data": True,  # API actually returns AIRR data even for short sequences
                },
                description="Very short nucleotide sequence - too short for analysis",
                category="edge_case",
            ),
            # Sequence with whitespace and newlines
            TestSequence(
                name="Sequence_With_Whitespace",
                sequence="  GAAGTGCAGCTGGTGGAAAGCGGCGGCGGCCTGGTGCAGCCGGGCCGCAGCCTGCGCCTGAGCTGCGCGGCGAGC\n  GGCTTTACCTTTGATGATTATGCGATGCATTGGGTGCGCCAGGCGCCGGGCAAAGGCCTGGAATGGGTGAGCGCG  ",
                sequence_type="nucleotide",
                expected_results={
                    "v_gene": "IGHV3-9*01",  # Should work after cleaning
                    "d_gene": None,  # Partial sequence
                    "j_gene": None,
                    "c_gene": None,
                    "cdr3_sequence": None,
                    "has_airr_data": True,
                },
                description="Nucleotide sequence with whitespace and newlines - should be cleaned",
                category="edge_case",
            ),
        ]

    def test_api_endpoint(
        self, api_base_url: str, test_sequence: TestSequence
    ) -> Dict[str, Any]:
        """Test API endpoint with the sequence."""
        try:
            # Determine blast type based on sequence type
            blast_type = (
                "igblastn"
                if test_sequence.sequence_type == "nucleotide"
                else "igblastp"
            )

            request_data = {
                "query_sequence": test_sequence.sequence,
                "organism": "human",
                "blast_type": blast_type,
                "evalue": 1e-10,
            }

            response = requests.post(
                f"{api_base_url}/api/v2/blast/search/antibody",
                json=request_data,
                timeout=30,
            )

            if response.status_code == 200:
                return {
                    "success": True,
                    "results": response.json(),
                    "error": None,
                    "status_code": response.status_code,
                }
            else:
                return {
                    "success": False,
                    "results": None,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "status_code": response.status_code,
                }

        except Exception as e:
            return {
                "success": False,
                "results": None,
                "error": str(e),
                "status_code": None,
            }

    def validate_api_response_structure(
        self, api_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate API response structure."""
        validation = {
            "isValid": True,
            "errors": [],
            "missingFields": [],
            "typeMismatches": [],
        }

        try:
            # Check required top-level fields
            required_fields = ["success", "message", "data"]
            for field in required_fields:
                if field not in api_response:
                    validation["missingFields"].append(field)
                    validation["isValid"] = False

            if not api_response.get("success", False):
                return (
                    validation  # Error responses may have different structure
                )

            # Validate data structure
            data = api_response.get("data", {})
            if not isinstance(data, dict):
                validation["isValid"] = False
                validation["errors"].append("data field must be an object")
                return validation

            # Check for results field
            if "results" not in data:
                validation["missingFields"].append("data.results")
                validation["isValid"] = False

            # Validate results structure if present
            results = data.get("results", {})
            if isinstance(results, dict):
                # Check for IgBLAST-specific fields
                if "blast_type" in results and results[
                    "blast_type"
                ].startswith("igblast"):
                    self._validate_igblast_result_structure(
                        results, validation
                    )
                else:
                    self._validate_blast_result_structure(results, validation)

            # Validate optional fields
            optional_fields = [
                "airr_result",
                "summary",
                "cdr3_info",
                "gene_assignments",
            ]
            for field in optional_fields:
                if field in data and data[field] is not None:
                    if not isinstance(data[field], (dict, list)):
                        validation["typeMismatches"].append(
                            {
                                "field": f"data.{field}",
                                "expected": "object or array",
                                "actual": type(data[field]).__name__,
                                "value": str(data[field])[:100],
                            }
                        )
                        validation["isValid"] = False

            return validation

        except Exception as e:
            validation["isValid"] = False
            validation["errors"].append(f"Validation error: {str(e)}")
            return validation

    def _validate_igblast_result_structure(
        self, results: Dict[str, Any], validation: Dict[str, Any]
    ):
        """Validate IgBLAST result structure."""
        required_fields = [
            "blast_type",
            "query_info",
            "hits",
            "analysis_summary",
            "total_hits",
        ]
        for field in required_fields:
            if field not in results:
                validation["missingFields"].append(f"results.{field}")
                validation["isValid"] = False

        # Validate hits array
        hits = results.get("hits", [])
        if not isinstance(hits, list):
            validation["isValid"] = False
            validation["errors"].append("results.hits must be an array")
        elif hits:
            # Validate first hit structure
            hit = hits[0]
            hit_fields = [
                "query_id",
                "subject_id",
                "identity",
                "alignment_length",
                "mismatches",
                "gap_opens",
                "query_start",
                "query_end",
                "subject_start",
                "subject_end",
                "evalue",
                "bit_score",
            ]
            for field in hit_fields:
                if field not in hit:
                    validation["missingFields"].append(
                        f"results.hits[0].{field}"
                    )
                    validation["isValid"] = False

    def _validate_blast_result_structure(
        self, results: Dict[str, Any], validation: Dict[str, Any]
    ):
        """Validate standard BLAST result structure."""
        required_fields = ["blast_type", "query_info", "hits", "total_hits"]
        for field in required_fields:
            if field not in results:
                validation["missingFields"].append(f"results.{field}")
                validation["isValid"] = False

    def extract_v_gene(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract V gene from response data."""
        try:
            # Try multiple possible locations
            if (
                "results" in data
                and "hits" in data["results"]
                and data["results"]["hits"]
            ):
                return data["results"]["hits"][0].get("v_gene")
            elif "hits" in data and data["hits"]:
                return data["hits"][0].get("v_gene")
            elif "summary" in data and "gene_assignments" in data["summary"]:
                return data["summary"]["gene_assignments"].get("v_gene")
            elif "gene_assignments" in data:
                return data["gene_assignments"].get("v_gene")
            return None
        except Exception:
            return None

    def extract_d_gene(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract D gene from response data."""
        try:
            if (
                "results" in data
                and "hits" in data["results"]
                and data["results"]["hits"]
            ):
                return data["results"]["hits"][0].get("d_gene")
            elif "hits" in data and data["hits"]:
                return data["hits"][0].get("d_gene")
            elif "summary" in data and "gene_assignments" in data["summary"]:
                return data["summary"]["gene_assignments"].get("d_gene")
            elif "gene_assignments" in data:
                return data["gene_assignments"].get("d_gene")
            return None
        except Exception:
            return None

    def extract_j_gene(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract J gene from response data."""
        try:
            if (
                "results" in data
                and "hits" in data["results"]
                and data["results"]["hits"]
            ):
                return data["results"]["hits"][0].get("j_gene")
            elif "hits" in data and data["hits"]:
                return data["hits"][0].get("j_gene")
            elif "summary" in data and "gene_assignments" in data["summary"]:
                return data["summary"]["gene_assignments"].get("j_gene")
            elif "gene_assignments" in data:
                return data["gene_assignments"].get("j_gene")
            return None
        except Exception:
            return None

    def extract_c_gene(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract C gene from response data."""
        try:
            if (
                "results" in data
                and "hits" in data["results"]
                and data["results"]["hits"]
            ):
                return data["results"]["hits"][0].get("c_gene")
            elif "hits" in data and data["hits"]:
                return data["hits"][0].get("c_gene")
            elif "summary" in data and "gene_assignments" in data["summary"]:
                return data["summary"]["gene_assignments"].get("c_gene")
            elif "gene_assignments" in data:
                return data["gene_assignments"].get("c_gene")
            return None
        except Exception:
            return None

    def extract_cdr3_sequence(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract CDR3 sequence from response data."""
        try:
            # Try multiple possible locations
            if (
                "results" in data
                and "hits" in data["results"]
                and data["results"]["hits"]
            ):
                return data["results"]["hits"][0].get("cdr3_sequence")
            elif "hits" in data and data["hits"]:
                return data["hits"][0].get("cdr3_sequence")
            elif "summary" in data:
                return data["summary"].get("cdr3_sequence")
            elif "cdr3_info" in data and data["cdr3_info"]:
                return data["cdr3_info"].get("sequence")
            return None
        except Exception:
            return None

    def has_airr_data(self, data: Dict[str, Any]) -> bool:
        """Check if AIRR data is available."""
        try:
            if "results" in data and "airr_result" in data["results"]:
                return data["results"]["airr_result"] is not None
            elif "airr_result" in data:
                return data["airr_result"] is not None
            return False
        except Exception:
            return False

    def check_gene_match(
        self, actual: Optional[str], expected: Optional[str]
    ) -> bool:
        """Check if gene assignments match expected values."""
        if expected is None:
            return actual is None
        if actual is None:
            return expected is None
        return expected in actual or actual in expected

    @pytest.mark.parametrize(
        "test_sequence",
        [
            "Humira_Heavy_Full_Nucleotide",
            "Humira_Heavy_Full_Protein",
            "Partial_V_Gene_Nucleotide",
            "Invalid_Nucleotide",
            "Non_Antibody_Protein",
            "Very_Short_Sequence",
            "Sequence_With_Whitespace",
        ],
    )
    def test_blast_api_comprehensive(
        self,
        api_base_url: str,
        test_sequences: List[TestSequence],
        test_sequence: str,
    ):
        """Comprehensive test for BLAST API functionality."""
        # Find the test sequence
        sequence_data = next(
            (seq for seq in test_sequences if seq.name == test_sequence), None
        )
        assert (
            sequence_data is not None
        ), f"Test sequence {test_sequence} not found"

        print(f"\n🧪 Testing: {sequence_data.name}")
        print(f"📝 {sequence_data.description}")
        print(f"🏷️  Category: {sequence_data.category}")
        print(f"🧬 Type: {sequence_data.sequence_type}")

        # Test API endpoint
        api_results = self.test_api_endpoint(api_base_url, sequence_data)

        # Validate API response structure
        if api_results["success"]:
            structure_validation = self.validate_api_response_structure(
                api_results["results"]
            )
            assert structure_validation[
                "isValid"
            ], f"API response structure validation failed: {structure_validation['errors']}"

        # Check expected results
        expected = sequence_data.expected_results

        if "error" in expected:
            # Expected to fail
            assert not api_results[
                "success"
            ], f"Expected failure but got success for {sequence_data.name}"
        else:
            # Expected to succeed
            assert api_results[
                "success"
            ], f"Expected success but got failure for {sequence_data.name}: {api_results.get('error')}"

            if api_results["success"]:
                api_data = api_results["results"]["data"]

                # Check V gene
                if "v_gene" in expected:
                    api_v = self.extract_v_gene(api_data)
                    assert self.check_gene_match(
                        api_v, expected["v_gene"]
                    ), f"V gene mismatch for {sequence_data.name}: expected {expected['v_gene']}, got {api_v}"

                # Check D gene
                if "d_gene" in expected:
                    api_d = self.extract_d_gene(api_data)
                    assert self.check_gene_match(
                        api_d, expected["d_gene"]
                    ), f"D gene mismatch for {sequence_data.name}: expected {expected['d_gene']}, got {api_d}"

                # Check J gene
                if "j_gene" in expected:
                    api_j = self.extract_j_gene(api_data)
                    assert self.check_gene_match(
                        api_j, expected["j_gene"]
                    ), f"J gene mismatch for {sequence_data.name}: expected {expected['j_gene']}, got {api_j}"

                # Check C gene
                if "c_gene" in expected:
                    api_c = self.extract_c_gene(api_data)
                    assert self.check_gene_match(
                        api_c, expected["c_gene"]
                    ), f"C gene mismatch for {sequence_data.name}: expected {expected['c_gene']}, got {api_c}"

                # Check CDR3 sequence
                if "cdr3_sequence" in expected:
                    api_cdr3 = self.extract_cdr3_sequence(api_data)
                    assert (
                        api_cdr3 == expected["cdr3_sequence"]
                    ), f"CDR3 sequence mismatch for {sequence_data.name}: expected {expected['cdr3_sequence']}, got {api_cdr3}"

                # Check AIRR data availability
                if "has_airr_data" in expected:
                    api_airr = self.has_airr_data(api_data)
                    assert (
                        api_airr == expected["has_airr_data"]
                    ), f"AIRR data availability mismatch for {sequence_data.name}: expected {expected['has_airr_data']}, got {api_airr}"

        print(f"✅ Test PASSED: {sequence_data.name}")

    def test_api_response_types_consistency(
        self, api_base_url: str, test_sequences: List[TestSequence]
    ):
        """Test that API responses have consistent types across all successful requests."""
        successful_responses = []

        for sequence_data in test_sequences:
            if "error" not in sequence_data.expected_results:
                api_results = self.test_api_endpoint(
                    api_base_url, sequence_data
                )
                if api_results["success"]:
                    successful_responses.append(api_results["results"])

        if len(successful_responses) < 2:
            pytest.skip(
                "Need at least 2 successful responses to test consistency"
            )

        # Check that all successful responses have the same structure
        first_response = successful_responses[0]
        first_keys = set(first_response.keys())

        for i, response in enumerate(successful_responses[1:], 1):
            response_keys = set(response.keys())
            assert (
                first_keys == response_keys
            ), f"Response {i} has different keys: {response_keys.symmetric_difference(first_keys)}"

            # Check data structure consistency
            if "data" in first_keys:
                first_data_keys = set(first_response["data"].keys())
                response_data_keys = set(response["data"].keys())
                assert (
                    first_data_keys == response_data_keys
                ), f"Response {i} data has different keys: {response_data_keys.symmetric_difference(first_data_keys)}"

        print(
            f"✅ API response type consistency test PASSED for {len(successful_responses)} responses"
        )
