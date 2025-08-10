from fastapi.testclient import TestClient
from backend.main import app
from backend.logger import logger
from backend.utils.json_to_fasta import json_seqs_to_fasta

client = TestClient(app)

# Real antibody sequences from test_anarci_result_processor.py
SCFV_SEQ = (
    "DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK"
    "GGGGGSGGGGSGGGGSGGGGS"
    "QVQLKQSGAEVKKPGASVKVSCKASGYTFTDEYMNWVRQAPGKSLEWMGYINPNNGGADYNQKFQGRVTMTVDQSISTAYMELSRLRSDDSAVYFCARLGYSNPYFDFWGQGTLVKVSS"
)
IGHG1_SEQ = "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSSAKTTAPSVYPLAPVCGDTTGSSVTLGCLVKGYFPEPVTLTWNSGSLSSGVHTFPAVLQSDLYTLSSSVTVTSSTWPSQSITCNVAHPASSTKVDKKIEPRGPTIKPCPPCKCPAPNLLGGPSVFIFPPKIKDVLMISLSPIVTCVVVDVSEDDPDVQISWFVNNVEVHTAQTQTHREDYNSTLRVVSALPIQHQDWMSGKEFKCKVNNKDLPAPIERTISKPKGSVRAPQVYVLPPPEEEMTKKQVTLTCMVTDFMPEDIYVEWTNNGKTELNYKNTEPVLDSDGSYFMYSKLRVEKKNWVERNSYSCSVVHEGLHNHHTTKSFSRTPGK"
KIH_SEQ = "ELQLQESGPGLVKPSETLSLTCAVSGVSFSDYHWAWIRDPPGKGLEWIGDINHRGHTNYNPSLKSRVTVSIDTSKNQFSLKLSSVTAADTAVYFCARDFPNFIFDFWGQGTLVTVSSASTKGPSVFPLAPSSKSTSGGTAALGCLVKDYFPEPVTVSWNSGALTSGVHTFPAVLQSSGLYSLSSVVTVPSSSLGTQTYICNVNHKPSNTKVDEKVEPDSCDKTHTCPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVCTLPPSREEMTKNQVSLSCAVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLVSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK"
TCR_SEQ = "DGGITQSPKYLFRKEGQNVTLSCEQNLNHDAMYWYRQDPGQGLRLIYYSQIVNDFQKGDIAEGYSVSREKKESFPLTVTSAQKNPTAFYLCASSRAGTGYNEQFFGPGTRLTVL"


def test_root():
    response = client.get("/api/v1/")
    assert response.status_code == 200
    assert response.json()["message"] == "AbSequenceAlign API"


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_upload_and_annotate(IGHG1_SEQ):
    fasta = json_seqs_to_fasta([IGHG1_SEQ])
    response = client.post(
        "/api/v1/upload", files={"file": ("test.fasta", fasta, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert "dataset_id" in data
    dataset_id = data["dataset_id"]
    response = client.post(
        "/api/v1/annotate",
        json={
            "sequences": [{"name": "IGHG1_SEQ", **IGHG1_SEQ}],
            "numbering_scheme": "cgg",
        },
    )
    logger.info(f"Annotation response: {response.json()}")
    assert response.status_code == 200
    result = response.json()["data"]["annotation_result"]
    assert result["total_sequences"] > 0
    assert result["numbering_scheme"] == "cgg"


def test_upload_invalid():
    # Invalid FASTA
    fasta = "not_a_fasta_sequence"
    response = client.post(
        "/api/v1/upload", files={"file": ("test.fasta", fasta, "text/plain")}
    )
    assert response.status_code == 400
    assert "Invalid FASTA format" in response.json()["detail"]


def test_annotate_invalid():
    # Invalid sequence - should be caught by Pydantic validation
    response = client.post(
        "/api/v1/annotate",
        json={"sequences": [{"name": "invalid_seq", "heavy_chain": "12345"}]},
    )
    assert response.status_code == 422  # Validation error from Pydantic
    assert "Invalid amino acids" in response.json()["detail"][0]["msg"]


def test_annotate_multiple_chains():
    """Test annotation with multiple chains per sequence"""
    response = client.post(
        "/api/v1/annotate",
        json={
            "sequences": [
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
            ],
            "numbering_scheme": "imgt",
        },
    )
    assert response.status_code == 200
    result = response.json()["data"]["annotation_result"]
    assert result["total_sequences"] > 0
    assert result["numbering_scheme"] == "imgt"


def test_annotate_with_custom_chains():
    """Test annotation with custom chain labels"""
    response = client.post(
        "/api/v1/annotate",
        json={
            "sequences": [
                {
                    "name": "custom_test",
                    "custom_chains": {
                        "custom_heavy": "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS",
                        "custom_light": "DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK",
                    },
                }
            ],
            "numbering_scheme": "imgt",
        },
    )
    assert response.status_code == 200
    result = response.json()["data"]["annotation_result"]
    assert result["total_sequences"] > 0
    assert result["numbering_scheme"] == "imgt"


# Additional tests for /align, /dataset, /datasets, /alignment can be added as needed.
