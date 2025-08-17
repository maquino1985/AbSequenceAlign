#!/usr/bin/env python3
"""
Debug script to test IgBLAST AIRR parsing with Humira sequences
"""

import sys

sys.path.append(".")

from app.backend.services.igblast_service import IgBlastService


def test_igblast_airr_parsing():
    """Test IgBLAST AIRR parsing with Humira sequences"""

    # Humira heavy chain nucleotide sequence (partial)
    humira_nuc = "AGGTGCAGCTGGTGCAGTCTGGGGCTGAGGTGAAGAAGCCTGGGGCCTCAGTGAAGGTCTCCTGCAAGGCTTCTGGATACACCTTCACCGGCTACTATATGCACTGGGTGCGACAGGCCCCTGGACAAGGGCTTGAGTGGATGGGATGGATCAACCCTAACAGTGGTGGCACAAACTATGCACAGAAGTTTCAGGGCAGGGTCACCATGACCAGGGACACGTCCATCAGCACAGCCTACATGGAGCTGAGCAGCCTGAGATCTGACGACACGGCCGTGTATTACTGTGCGAGAGAGGGGCCCTGGGACAGCTACTGGGGCCAAGGGACCACGGTCACCGTCTCCTCAG"

    # Humira heavy chain amino acid sequence
    humira_aa = "ELQLQESGPGLVKPSETLSLTCAVSGVSFSDYHWAWIRDPPGKGLEWIGDINHRGHTNYNPSLKSRVTVSIDTSKNQFSLKLSSVTAADTAVYFCARDFPNFIFDFWGQGTLVTVSSASTKGPSVFPLAPSSKSTSGGTAALGCLVKDYFPEPVTVSWNSGALTSGVHTFPAVLQSSGLYSLSSVVTVPSSSLGTQTYICNVNHKPSNTKVDEKVEPDSCDKTHTCPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVCTLPPSREEMTKNQVSLSCAVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLVSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK"

    print("Testing IgBLAST AIRR parsing...")

    try:
        # Initialize IgBLAST service
        igblast_service = IgBlastService()

        print("\n1. Testing nucleotide sequence (igblastn)...")
        print(f"Sequence length: {len(humira_nuc)}")

        # Test nucleotide sequence
        result_nuc = igblast_service.analyze_antibody_sequence(
            query_sequence=humira_nuc,
            organism="human",
            blast_type="igblastn",
            evalue=1e-10,
        )

        print(f"Result keys: {list(result_nuc.keys())}")
        print(f"Has AIRR result: {result_nuc.get('airr_result') is not None}")

        if result_nuc.get("airr_result"):
            airr_data = result_nuc["airr_result"]
            print(
                f"AIRR rearrangements: {len(airr_data.get('rearrangements', []))}"
            )

            for i, rearrangement in enumerate(
                airr_data.get("rearrangements", [])
            ):
                print(f"\nRearrangement {i+1}:")
                print(f"  V gene: {rearrangement.get('v_call')}")
                print(f"  D gene: {rearrangement.get('d_call')}")
                print(f"  J gene: {rearrangement.get('j_call')}")
                print(f"  C gene: {rearrangement.get('c_call')}")
                print(f"  Productive: {rearrangement.get('productive')}")

                junction = rearrangement.get("junction_region", {})
                if junction:
                    print(f"  CDR3 sequence: {junction.get('cdr3')}")
                    print(f"  CDR3 start: {junction.get('cdr3_start')}")
                    print(f"  CDR3 end: {junction.get('cdr3_end')}")

        print("\n2. Testing amino acid sequence (igblastp)...")
        print(f"Sequence length: {len(humira_aa)}")

        # Test amino acid sequence
        result_aa = igblast_service.analyze_antibody_sequence(
            query_sequence=humira_aa,
            organism="human",
            blast_type="igblastp",
            evalue=1e-10,
        )

        print(f"Result keys: {list(result_aa.keys())}")
        print(f"Has AIRR result: {result_aa.get('airr_result') is not None}")

        if result_aa.get("airr_result"):
            airr_data = result_aa["airr_result"]
            print(
                f"AIRR rearrangements: {len(airr_data.get('rearrangements', []))}"
            )

            for i, rearrangement in enumerate(
                airr_data.get("rearrangements", [])
            ):
                print(f"\nRearrangement {i+1}:")
                print(f"  V gene: {rearrangement.get('v_call')}")
                print(f"  D gene: {rearrangement.get('d_call')}")
                print(f"  J gene: {rearrangement.get('j_call')}")
                print(f"  C gene: {rearrangement.get('c_call')}")
                print(f"  Productive: {rearrangement.get('productive')}")

        # Check hits data
        print("\n3. Checking hits data...")
        hits_nuc = result_nuc.get("hits", [])
        print(f"Nucleotide hits: {len(hits_nuc)}")

        for i, hit in enumerate(hits_nuc):
            print(f"\nHit {i+1}:")
            print(f"  V gene: {hit.get('v_gene')}")
            print(f"  D gene: {hit.get('d_gene')}")
            print(f"  J gene: {hit.get('j_gene')}")
            print(f"  C gene: {hit.get('c_gene')}")
            print(f"  CDR3 sequence: {hit.get('cdr3_sequence')}")
            print(f"  CDR3 start: {hit.get('cdr3_start')}")
            print(f"  CDR3 end: {hit.get('cdr3_end')}")

        hits_aa = result_aa.get("hits", [])
        print(f"\nAmino acid hits: {len(hits_aa)}")

        for i, hit in enumerate(hits_aa):
            print(f"\nHit {i+1}:")
            print(f"  V gene: {hit.get('v_gene')}")
            print(f"  D gene: {hit.get('d_gene')}")
            print(f"  J gene: {hit.get('j_gene')}")
            print(f"  C gene: {hit.get('c_gene')}")
            print(f"  CDR3 sequence: {hit.get('cdr3_sequence')}")
            print(f"  CDR3 start: {hit.get('cdr3_start')}")
            print(f"  CDR3 end: {hit.get('cdr3_end')}")

    except Exception as e:
        print(f"Error testing IgBLAST: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_igblast_airr_parsing()
