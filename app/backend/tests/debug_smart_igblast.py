"""
Debug test for smart IgBLAST two-step process.
This test focuses on the chain type detection and appropriate database usage.
"""

import pytest
import requests
from backend.logger import logger


class TestSmartIgBlastDebug:
    """Debug tests for smart IgBLAST functionality."""

    @pytest.fixture
    def api_base_url(self):
        """API base URL for testing."""
        return "http://localhost:8000"

    def test_smart_igblast_heavy_chain_detection(self, api_base_url: str):
        """Test that heavy chain sequences are detected and use V/D/J databases."""
        logger.info("\n🧪 Testing Heavy Chain Detection")

        # Heavy chain nucleotide sequence (Humira)
        heavy_sequence = "GAAGTGCAGCTGGTGGAAAGCGGCGGCGGCCTGGTGCAGCCGGGCCGCAGCCTGCGCCTGAGCTGCGCGGCGAGCGGCTTTACCTTTGATGATTATGCGATGCATTGGGTGCGCCAGGCGCCGGGCAAAGGCCTGGAGTGGGTGAGCGCGATTACCTGGAACAGCGGCCATATTGATTATGCGGATAGCGTGGAAGGCCGCTTTACCATTAGCCGCGATAACGCGAAAAACAGCCTGTATCTGCAGATGAACAGCCTGCGCGCGGAAGATACCGCGGTGTATTATTGCGCGAAAGTGAGCTATCTGAGCACCGCGAGCAGCCTGGATTATTGGGGCCAGGGCACCCTGGTGACCGTGAGCAGCGCGAGCACCAAAGGCCCGAGCGTGTTTCCGCTGGCGCCGAGCAGCAAAAGCACCAGCGGCGGCACCGCGGCGCTGGGCTGCCTGGTGAAAGATTATTTTCCGGAACCGGTGACCGTGAGCTGGAACAGCGCGCGCTGACCAGCGGCGTGCATACCTTTCCGGCGGTGCTGCAGAGCAGCGGCCTGTATAGCCTGAGCAGCGTGGTGACCGTGCCGAGCAGCAGCCTGGGCACCCAGACCTATATTTGCAACGTGAACCATAAACCGAGCAACACCAAAGTGGATAAAAAAGTGGAACCGAAAAGCTGCGATAAAACCCATACCTGCCCGCCGTGCCCGGCGCCGGAACTGCTGGGCGGCCCGAGCGTGTTTCTGTTTCCGCCGAAACCGAAAGATACCCTGATGATTAGCCGCACCCCGGAAGTGACCTGCGTGGTGGTGGATGTGAGCCATGAAGATCCGGAAGTGAAATTTAACTGGTATGTGGATGGTGTGGAAGTGCATAACGCGAAAACCAAACCGCGCGAAGAACAGTATAACAGCACCTATCGCGTGGTGAGCGTGCTGACCGTGCTGCATCAGGATTGGCTGAACGGCAAAGAATATAAATGCAAAGTGAGCAACAAAGCGCTGCCGGCGCCGATTGAAAAAACCATTAGCAAAGCGAAGGCCAGCCGCGCGAACCGCAGGTGTATACCCTGCCGCCGAGCCGCGATGAACTGACCAAAAACCAGGTGAGCCTGACCTGCCTGGTGAAAGGCTTTTATCCGAGCGATATTGCGGTGGAATGGGAAAGCAACGGCCAGCCGGAAAACAACTATAAAACCACCCCGCCGGTGCTGGATAGCGATGGCAGCTTTTTTCTGTATAGCAAACTGACCGTGGATAAAAGCCGCTGGCAGCAGGGCAACGTGTTTAGCTGCAGCGTGATGCATGAAGCGCTGCATAACCATTATACCCAGAAAAGCCTGAGCCTGAGCCCGGGCAAA"

        request_data = {
            "query_sequence": heavy_sequence,
            "organism": "mouse",
            "blast_type": "igblastn",
            "evalue": 1e-10,
        }

        logger.info(
            f"📤 Sending request to {api_base_url}/api/v2/blast/search/antibody"
        )
        logger.info(f"🧬 Sequence length: {len(heavy_sequence)}")
        logger.info(f"🐭 Organism: mouse")

        try:
            response = requests.post(
                f"{api_base_url}/api/v2/blast/search/antibody",
                json=request_data,
                timeout=30,
            )

            logger.info(f"📥 Response status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                logger.info("✅ API call successful!")

                # Check if we got results
                if "data" in result and "results" in result["data"]:
                    results = result["data"]["results"]
                    logger.info(
                        f"📊 Total hits: {results.get('total_hits', 'N/A')}"
                    )

                    if results.get("hits"):
                        hit = results["hits"][0]
                        logger.info(f"🔍 V gene: {hit.get('v_gene', 'N/A')}")
                        logger.info(f"🔍 D gene: {hit.get('d_gene', 'N/A')}")
                        logger.info(f"🔍 J gene: {hit.get('j_gene', 'N/A')}")
                        logger.info(f"🔍 C gene: {hit.get('c_gene', 'N/A')}")
                        logger.info(
                            f"🔍 CDR3: {hit.get('cdr3_sequence', 'N/A')}"
                        )

                        # Check if D gene was found (indicating heavy chain detection)
                        d_gene = hit.get("d_gene")
                        if d_gene and d_gene != "N/A" and d_gene != "None":
                            logger.info(
                                "✅ Heavy chain detected - D gene found!"
                            )
                        else:
                            logger.info(
                                "❌ Heavy chain not properly detected - no D gene found"
                            )
                    else:
                        logger.info("❌ No hits returned")
                else:
                    logger.info(f"❌ Unexpected response structure: {result}")

            else:
                logger.info(f"❌ API call failed: {response.status_code}")
                logger.info(f"📄 Response: {response.text}")

        except Exception as e:
            logger.info(f"❌ Exception during API call: {e}")

    def test_smart_igblast_light_chain_detection(self, api_base_url: str):
        """Test that light chain sequences are detected and use V/J databases only."""
        logger.info("\n🧪 Testing Light Chain Detection")

        # Light chain nucleotide sequence
        light_sequence = "GACATCCAGATGACCCAGTCTCCATCCTCCCTGTCTGCATCTGTAGGAGACAGAGTCACCATCACTTGCCGGGCAAGTCAGGACATTAGAAATGATTTAGCTGGTATCAGCACAAACTGGAAACAGGGTGAATCTTCAAAGCTCCTATCTATACTGCATCCAACATGGGTCTGCAAAGTGGTTTACTGGGGTCAAGGAACCTCAGTCACCGTCTCCTCAG"

        request_data = {
            "query_sequence": light_sequence,
            "organism": "mouse",
            "blast_type": "igblastn",
            "evalue": 1e-10,
        }

        logger.info(
            f"📤 Sending request to {api_base_url}/api/v2/blast/search/antibody"
        )
        logger.info(f"🧬 Sequence length: {len(light_sequence)}")
        logger.info(f"🐭 Organism: mouse")

        try:
            response = requests.post(
                f"{api_base_url}/api/v2/blast/search/antibody",
                json=request_data,
                timeout=30,
            )

            logger.info(f"📥 Response status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                logger.info("✅ API call successful!")

                # Check if we got results
                if "data" in result and "results" in result["data"]:
                    results = result["data"]["results"]
                    logger.info(
                        f"📊 Total hits: {results.get('total_hits', 'N/A')}"
                    )

                    if results.get("hits"):
                        hit = results["hits"][0]
                        logger.info(f"🔍 V gene: {hit.get('v_gene', 'N/A')}")
                        logger.info(f"🔍 D gene: {hit.get('d_gene', 'N/A')}")
                        logger.info(f"🔍 J gene: {hit.get('j_gene', 'N/A')}")
                        logger.info(f"🔍 C gene: {hit.get('c_gene', 'N/A')}")
                        logger.info(
                            f"🔍 CDR3: {hit.get('cdr3_sequence', 'N/A')}"
                        )

                        # Check if D gene was NOT found (indicating light chain detection)
                        d_gene = hit.get("d_gene")
                        if not d_gene or d_gene == "N/A" or d_gene == "None":
                            logger.info(
                                "✅ Light chain detected - no D gene found!"
                            )
                        else:
                            logger.info(
                                "❌ Light chain not properly detected - D gene found when it shouldn't be"
                            )
                    else:
                        logger.info("❌ No hits returned")
                else:
                    logger.info(f"❌ Unexpected response structure: {result}")

            else:
                logger.info(f"❌ API call failed: {response.status_code}")
                logger.info(f"📄 Response: {response.text}")

        except Exception as e:
            logger.info(f"❌ Exception during API call: {e}")

    def test_direct_igblast_command_comparison(self):
        """Test direct IgBLAST commands to compare with API results."""
        logger.info("\n🧪 Testing Direct IgBLAST Commands")

        import subprocess

        # Test heavy chain sequence
        heavy_sequence = "GAAGTGCAGCTGGTGGAAAGCGGCGGCGGCCTGGTGCAGCCGGGCCGCAGCCTGCGCCTGAGCTGCGCGGCGAGCGGCTTTACCTTTGATGATTATGCGATGCATTGGGTGCGCCAGGCGCCGGGCAAAGGCCTGGAGTGGGTGAGCGCGATTACCTGGAACAGCGGCCATATTGATTATGCGGATAGCGTGGAAGGCCGCTTTACCATTAGCCGCGATAACGCGAAAAACAGCCTGTATCTGCAGATGAACAGCCTGCGCGCGGAAGATACCGCGGTGTATTATTGCGCGAAAGTGAGCTATCTGAGCACCGCGAGCAGCCTGGATTATTGGGGCCAGGGCACCCTGGTGACCGTGAGCAGCGCGAGCACCAAAGGCCCGAGCGTGTTTCCGCTGGCGCCGAGCAGCAAAAGCACCAGCGGCGGCACCGCGGCGCTGGGCTGCCTGGTGAAAGATTATTTTCCGGAACCGGTGACCGTGAGCTGGAACAGCGCGCGCTGACCAGCGGCGTGCATACCTTTCCGGCGGTGCTGCAGAGCAGCGGCCTGTATAGCCTGAGCAGCGTGGTGACCGTGCCGAGCAGCAGCCTGGGCACCCAGACCTATATTTGCAACGTGAACCATAAACCGAGCAACACCAAAGTGGATAAAAAAGTGGAACCGAAAAGCTGCGATAAAACCCATACCTGCCCGCCGTGCCCGGCGCCGGAACTGCTGGGCGGCCCGAGCGTGTTTCTGTTTCCGCCGAAACCGAAAGATACCCTGATGATTAGCCGCACCCCGGAAGTGACCTGCGTGGTGGTGGATGTGAGCCATGAAGATCCGGAAGTGAAATTTAACTGGTATGTGGATGGTGTGGAAGTGCATAACGCGAAAACCAAACCGCGCGAAGAACAGTATAACAGCACCTATCGCGTGGTGAGCGTGCTGACCGTGCTGCATCAGGATTGGCTGAACGGCAAAGAATATAAATGCAAAGTGAGCAACAAAGCGCTGCCGGCGCCGATTGAAAAAACCATTAGCAAAGCGAAGGCCAGCCGCGCGAACCGCAGGTGTATACCCTGCCGCCGAGCCGCGATGAACTGACCAAAAACCAGGTGAGCCTGACCTGCCTGGTGAAAGGCTTTTATCCGAGCGATATTGCGGTGGAATGGGAAAGCAACGGCCAGCCGGAAAACAACTATAAAACCACCCCGCCGGTGCTGGATAGCGATGGCAGCTTTTTTCTGTATAGCAAACTGACCGTGGATAAAAGCCGCTGGCAGCAGGGCAACGTGTTTAGCTGCAGCGTGATGCATGAAGCGCTGCATAACCATTATACCCAGAAAAGCCTGAGCCTGAGCCCGGGCAAA"

        logger.info("🔧 Testing direct IgBLAST command for heavy chain...")

        try:
            # Use echo to create the sequence directly in the container
            cmd = [
                "docker",
                "exec",
                "absequencealign-igblast",
                "bash",
                "-c",
                f"echo -e '>test\\n{heavy_sequence}' | igblastn -query /dev/stdin -organism mouse -germline_db_V /data/internal_data/mouse/mouse_gl_V -germline_db_D /data/internal_data/mouse/mouse_gl_D -germline_db_J /data/internal_data/mouse/mouse_gl_J -auxiliary_data /ncbi-igblast-1.22.0/optional_file/mouse_gl.aux -outfmt 7 -num_alignments_V 1 -num_alignments_D 1 -num_alignments_J 1",
            ]

            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=60
            )

            logger.info(f"📊 Direct command exit code: {result.returncode}")

            if result.returncode == 0:
                logger.info("✅ Direct IgBLAST command successful!")
                logger.info("📄 Output preview:")
                lines = result.stdout.split("\n")
                for i, line in enumerate(lines[:10]):
                    logger.info(f"   {i+1}: {line}")
                if len(lines) > 10:
                    logger.info(f"   ... and {len(lines) - 10} more lines")
            else:
                logger.info("❌ Direct IgBLAST command failed!")
                logger.info(f"📄 Error: {result.stderr}")

        except Exception as e:
            logger.info(f"❌ Exception during direct command test: {e}")
