from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Real antibody sequences from test_anarci_result_processor.py
SCFV_SEQ = "DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK" \
          "GGGGGSGGGGSGGGGSGGGGS" \
          "QVQLKQSGAEVKKPGASVKVSCKASGYTFTDEYMNWVRQAPGKSLEWMGYINPNNGGADYNQKFQGRVTMTVDQSISTAYMELSRLRSDDSAVYFCARLGYSNPYFDFWGQGTLVKVSS"
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

def test_upload_and_annotate():
    # Use real antibody sequence for upload
    fasta = f">seq1\n{IGHG1_SEQ}"
    response = client.post(
        "/api/v1/upload",
        files={"file": ("test.fasta", fasta, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert "dataset_id" in data
    dataset_id = data["dataset_id"]
    # Test annotation endpoint with real antibody sequence
    response = client.post(
        "/api/v1/annotate",
        json={"sequences": [IGHG1_SEQ]}
    )
    assert response.status_code == 200
    result = response.json()["data"]["annotation_result"]
    assert result["total_sequences"] > 0
    assert result["numbering_scheme"] == "imgt"

def test_upload_invalid():
    # Invalid FASTA
    fasta = "not_a_fasta_sequence"
    response = client.post(
        "/api/v1/upload",
        files={"file": ("test.fasta", fasta, "text/plain")}
    )
    assert response.status_code == 400
    assert "Invalid FASTA format" in response.json()["detail"]

def test_annotate_invalid():
    # Invalid sequence
    response = client.post(
        "/api/v1/annotate",
        json={"sequences": ["12345"]}
    )
    assert response.status_code == 400
    assert "Sequence validation failed" in response.json()["detail"]

# Additional tests for /align, /dataset, /datasets, /alignment can be added as needed.
