# Tests for DataStore (dataset creation, retrieval, deletion, statistics)
import pytest
from backend.data_store import DataStore

@pytest.fixture
def store():
    return DataStore()

def test_create_and_get_dataset(store):
    seqs = [
        # Human IGHV1-69*01 heavy chain variable region (canonical, truncated for test)
        "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAR"
    ]
    dataset_id = store.create_dataset(seqs)
    dataset = store.get_dataset(dataset_id)
    assert dataset is not None
    assert dataset["dataset_id"] == dataset_id
    assert dataset["sequence_count"] == 1

def test_get_dataset_info(store):
    seqs = [
        # Human IGKV1-39*01 kappa light chain variable region (canonical, truncated for test)
        "DIQMTQSPSSLSASVGDRVTITCRASQDISNYLNWYQQKPGKAPKLLIYAASSLQSGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQQYNSYPLTFGQGTKVEIK"
    ]
    dataset_id = store.create_dataset(seqs)
    info = store.get_dataset_info(dataset_id)
    assert info is not None
    assert info.dataset_id == dataset_id
    assert info.sequence_count == 1

def test_update_dataset_status(store):
    seqs = [
        # Human IGHV3-23*01 heavy chain variable region (canonical, truncated for test)
        "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAR"
    ]
    dataset_id = store.create_dataset(seqs)
    assert store.update_dataset_status(dataset_id, "processed")
    dataset = store.get_dataset(dataset_id)
    assert dataset["status"] == "processed"

def test_delete_dataset(store):
    seqs = [
        # Human IGKV3-20*01 kappa light chain variable region (canonical, truncated for test)
        "DIQMTQSPSSLSASVGDRVTITCRASQDISNYLNWYQQKPGKAPKLLIYAASSLQSGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQQYNSYPLTFGQGTKVEIK"
    ]
    dataset_id = store.create_dataset(seqs)
    assert store.delete_dataset(dataset_id)
    assert store.get_dataset(dataset_id) is None

def test_list_datasets(store):
    seqs = [
        # Human IGHV1-2*02 heavy chain variable region (canonical, truncated for test)
        "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAR"
    ]
    store.create_dataset(seqs)
    datasets = store.list_datasets()
    assert len(datasets) == 1

def test_get_dataset_statistics(store):
    seqs = [
        # Human IGKV1-5*01 kappa light chain variable region (canonical, truncated for test)
        "DIQMTQSPSSLSASVGDRVTITCRASQDISNYLNWYQQKPGKAPKLLIYAASSLQSGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQQYNSYPLTFGQGTKVEIK"
    ]
    store.create_dataset(seqs)
    stats = store.get_dataset_statistics()
    assert stats["total_datasets"] == 1
    assert stats["total_sequences"] == 1
