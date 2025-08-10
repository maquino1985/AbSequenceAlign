"""
Tests for JSON to FASTA conversion utilities
"""

from backend.utils.json_to_fasta import (
    json_seqs_to_fasta,
    json_seqs_to_fasta_simple,
)


class TestJsonToFasta:
    """Test cases for JSON to FASTA conversion"""

    def test_json_seqs_to_fasta_simple(self):
        """Test converting simple JSON sequences to FASTA"""
        json_data = {
            "heavy_chain_1": "ELQLQESGPGLVKPSETLSLTCAVSGVSFSDYHWAWIRDPPGKGLEWIGDINHRGHTNYNPSLKSRVTVSIDTSKNQFSLKLSSVTAADTAVYFCARDFPNFIFDFWGQGTLVTVSSASTKGPSVFPLAPSSKSTSGGTAALGCLVKDYFPEPVTVSWNSGALTSGVHTFPAVLQSSGLYSLSSVVTVPSSSLGTQTYICNVNHKPSNTKVDEKVEPDSCDKTHTCPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVCTLPPSREEMTKNQVSLSCAVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLVSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK",
            "light_chain_1": "DIQLTQSPGTLSLSPGERATLSCRASQSVSTYLAWYQKKPGQAPRLLIYGASKRATGIPDRFSGSGSGTDFTLTISRLEPEDFAVYYCQQYGDSPLTFGQGTKVEIKRTVAAPSVFIFPPSKKQLKSGTASVVCLLNNFYPREAKVQWKVDNALQSGNSQESVTEQDSKDSTYSLSSTLTLSKADYEKHKVYACEVTHQGLSSPVTKSFNRGEC",
            "heavy_chain_2": "EVQLVQSGAEVKKPGESLKISCKGSGYSFSNYWIGWVRKMPGKGLEWMGIIDPSNSYTRYSPSFQGQVTISADKSISTAYLQWSSLKASDTAMYYCARWYYKPFDVWGQGTLVTVSSASTKGPSVFPLAPSSKSTSGGTAALGCLVKDYFPEPVTVSWNSGALTSGVHTFPACLQSSGLYSLSSVVTVPSSSLGTQTYICNVNHKPSNTKVDKKVEPKSSDKTHTCPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSREEMTKNQVSLWCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK",
            "light_chain_2": "QSVLTQPPSVSGAPGQRVTISCTGSSSNIGSGYDVHWYQDLPGTAPKLLIYGNSKRPSGVPDRFSGSKSGTSASLAITGLQSEDEADYYCASWTDGLSLVVFGGGTKLTVLGQPKAAPSVTLFPPSSEELQANKADLVCLISDFYPGAVTVAWKADSSPVKAGVETCTPSKQSNNKYAASSYLSLTPEQWKSHRSYSCQVTHEGSTVEKTVAPTESS",
        }

        fasta_result = json_seqs_to_fasta_simple(json_data)

        # Check that all chains are present
        assert ">heavy_chain_1" in fasta_result
        assert ">light_chain_1" in fasta_result
        assert ">heavy_chain_2" in fasta_result
        assert ">light_chain_2" in fasta_result

        # Check that sequences are present (now as single lines)
        assert (
            "ELQLQESGPGLVKPSETLSLTCAVSGVSFSDYHWAWIRDPPGKGLEWIGDINHRGHTNYNPSLKSRVTVSIDTSKNQFSLKLSSVTAADTAVYFCARDFPNFIFDFWGQGTLVTVSS"
            in fasta_result
        )
        assert (
            "DIQLTQSPGTLSLSPGERATLSCRASQSVSTYLAWYQKKPGQAPRLLIYGASKRATGIPDRFSGSGSGTDFTLTISRLEPEDFAVYYCQQYGDSPLTFGQGTKVEIK"
            in fasta_result
        )

        # Check FASTA format (headers start with >)
        lines = fasta_result.split("\n")
        header_lines = [line for line in lines if line.startswith(">")]
        assert len(header_lines) == 4  # Should have 4 headers

        # Check that sequence lines don't start with >
        sequence_lines = [line for line in lines if line and not line.startswith(">")]
        assert len(sequence_lines) == 4  # Should have 4 sequence lines

    def test_json_seqs_to_fasta_with_names(self):
        """Test converting JSON sequences with names to FASTA"""
        json_data = [
            {
                "name": "igg_test",
                "heavy_chain": "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS",
                "light_chain": "DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK",
            },
            {
                "name": "kih_test",
                "heavy_chain_1": "ELQLQESGPGLVKPSETLSLTCAVSGVSFSDYHWAWIRDPPGKGLEWIGDINHRGHTNYNPSLKSRVTVSIDTSKNQFSLKLSSVTAADTAVYFCARDFPNFIFDFWGQGTLVTVSS",
                "heavy_chain_2": "ELQLQESGPGLVKPSETLSLTCAVSGVSFSDYHWAWIRDPPGKGLEWIGDINHRGHTNYNPSLKSRVTVSIDTSKNQFSLKLSSVTAADTAVYFCARDFPNFIFDFWGQGTLVTVSS",
                "light_chain_1": "DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK",
                "light_chain_2": "DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK",
            },
        ]

        fasta_result = json_seqs_to_fasta(json_data)

        # Check that named headers are present
        assert ">igg_test_heavy_chain" in fasta_result
        assert ">igg_test_light_chain" in fasta_result
        assert ">kih_test_heavy_chain_1" in fasta_result
        assert ">kih_test_heavy_chain_2" in fasta_result
        assert ">kih_test_light_chain_1" in fasta_result
        assert ">kih_test_light_chain_2" in fasta_result

        # Check that sequences are present (now as single lines)
        assert (
            "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS"
            in fasta_result
        )
        assert (
            "DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK"
            in fasta_result
        )

        # Check FASTA format structure
        lines = fasta_result.split("\n")
        header_lines = [line for line in lines if line.startswith(">")]
        assert (
            len(header_lines) == 6
        )  # Should have 6 headers (2 sequences × 3 chains each)

        # Check that sequence lines don't start with >
        sequence_lines = [line for line in lines if line and not line.startswith(">")]
        assert len(sequence_lines) == 6  # Should have 6 sequence lines

    def test_json_seqs_to_fasta_empty_input(self):
        """Test handling of empty input"""
        empty_data = {}
        fasta_result = json_seqs_to_fasta_simple(empty_data)
        assert fasta_result == ""

        empty_list = []
        fasta_result = json_seqs_to_fasta(empty_list)
        assert fasta_result == ""
