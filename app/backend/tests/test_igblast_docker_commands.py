"""
Debug script to test IgBLAST parsing directly.
"""

import subprocess


def test_direct_igblast_output():
    """Test direct IgBLAST output to see what format we get."""
    print("🧪 Testing Direct IgBLAST Output")

    # Heavy chain sequence
    heavy_sequence = "GAAGTGCAGCTGGTGGAAAGCGGCGGCGGCCTGGTGCAGCCGGGCCGCAGCCTGCGCCTGAGCTGCGCGGCGAGCGGCTTTACCTTTGATGATTATGCGATGCATTGGGTGCGCCAGGCGCCGGGCAAAGGCCTGGAGTGGGTGAGCGCGATTACCTGGAACAGCGGCCATATTGATTATGCGGATAGCGTGGAAGGCCGCTTTACCATTAGCCGCGATAACGCGAAAAACAGCCTGTATCTGCAGATGAACAGCCTGCGCGCGGAAGATACCGCGGTGTATTATTGCGCGAAAGTGAGCTATCTGAGCACCGCGAGCAGCCTGGATTATTGGGGCCAGGGCACCCTGGTGACCGTGAGCAGCGCGAGCACCAAAGGCCCGAGCGTGTTTCCGCTGGCGCCGAGCAGCAAAAGCACCAGCGGCGGCACCGCGGCGCTGGGCTGCCTGGTGAAAGATTATTTTCCGGAACCGGTGACCGTGAGCTGGAACAGCGCGCGCTGACCAGCGGCGTGCATACCTTTCCGGCGGTGCTGCAGAGCAGCGGCCTGTATAGCCTGAGCAGCGTGGTGACCGTGCCGAGCAGCAGCCTGGGCACCCAGACCTATATTTGCAACGTGAACCATAAACCGAGCAACACCAAAGTGGATAAAAAAGTGGAACCGAAAAGCTGCGATAAAACCCATACCTGCCCGCCGTGCCCGGCGCCGGAACTGCTGGGCGGCCCGAGCGTGTTTCTGTTTCCGCCGAAACCGAAAGATACCCTGATGATTAGCCGCACCCCGGAAGTGACCTGCGTGGTGGTGGATGTGAGCCATGAAGATCCGGAAGTGAAATTTAACTGGTATGTGGATGGTGTGGAAGTGCATAACGCGAAAACCAAACCGCGCGAAGAACAGTATAACAGCACCTATCGCGTGGTGAGCGTGCTGACCGTGCTGCATCAGGATTGGCTGAACGGCAAAGAATATAAATGCAAAGTGAGCAACAAAGCGCTGCCGGCGCCGATTGAAAAAACCATTAGCAAAGCGAAGGCCAGCCGCGCGAACCGCAGGTGTATACCCTGCCGCCGAGCCGCGATGAACTGACCAAAAACCAGGTGAGCCTGACCTGCCTGGTGAAAGGCTTTTATCCGAGCGATATTGCGGTGGAATGGGAAAGCAACGGCCAGCCGGAAAACAACTATAAAACCACCCCGCCGGTGCTGGATAGCGATGGCAGCTTTTTTCTGTATAGCAAACTGACCGTGGATAAAAGCCGCTGGCAGCAGGGCAACGTGTTTAGCTGCAGCGTGATGCATGAAGCGCTGCATAACCATTATACCCAGAAAAGCCTGAGCCTGAGCCCGGGCAAA"

    print("🔧 Testing with outfmt 7 (tabular)...")
    cmd_tabular = [
        "docker",
        "exec",
        "absequencealign-igblast",
        "bash",
        "-c",
        f"echo -e '>test\\n{heavy_sequence}' | igblastn -query /dev/stdin -organism mouse -germline_db_V /data/internal_data/mouse/mouse_gl_V -germline_db_D /data/internal_data/mouse/mouse_gl_D -germline_db_J /data/internal_data/mouse/mouse_gl_J -auxiliary_data /ncbi-igblast-1.22.0/optional_file/mouse_gl.aux -outfmt 7 -num_alignments_V 1 -num_alignments_D 1 -num_alignments_J 1",
    ]

    result_tabular = subprocess.run(
        cmd_tabular, capture_output=True, text=True, timeout=60
    )
    print(f"📊 Tabular output exit code: {result_tabular.returncode}")
    if result_tabular.returncode == 0:
        print("✅ Tabular output successful!")
        print("📄 Tabular output preview:")
        lines = result_tabular.stdout.split("\n")
        for i, line in enumerate(lines[:15]):
            print(f"   {i + 1}: {line}")
    else:
        print(f"❌ Tabular output failed: {result_tabular.stderr}")

    print("\n🔧 Testing with outfmt 19 (AIRR)...")
    cmd_airr = [
        "docker",
        "exec",
        "absequencealign-igblast",
        "bash",
        "-c",
        f"echo -e '>test\\n{heavy_sequence}' | igblastn -query /dev/stdin -organism mouse -germline_db_V /data/internal_data/mouse/mouse_gl_V -germline_db_D /data/internal_data/mouse/mouse_gl_D -germline_db_J /data/internal_data/mouse/mouse_gl_J -auxiliary_data /ncbi-igblast-1.22.0/optional_file/mouse_gl.aux -outfmt 19 -num_alignments_V 1 -num_alignments_D 1 -num_alignments_J 1",
    ]

    result_airr = subprocess.run(
        cmd_airr, capture_output=True, text=True, timeout=60
    )
    print(f"📊 AIRR output exit code: {result_airr.returncode}")
    if result_airr.returncode == 0:
        print("✅ AIRR output successful!")
        print("📄 AIRR output preview:")
        lines = result_airr.stdout.split("\n")
        for i, line in enumerate(lines[:15]):
            print(f"   {i + 1}: {line}")
    else:
        print(f"❌ AIRR output failed: {result_airr.stderr}")
