import pytest
from unittest.mock import Mock, patch

from backend.models.models_v2 import DomainType
from backend.models.requests_v2 import AnnotationRequestV2, InputSequence
from backend.services.annotation_service import AnnotationService


@pytest.fixture
def annotation_service():
    return AnnotationService()


@pytest.fixture
def mock_domain():
    domain = Mock()
    domain.domain_type = "V"
    domain.sequence = "SEQUENCE"
    domain.alignment_details = {
        "query_start": 0,
        "query_end": 10
    }
    domain.regions = {
        "FR1": {
            "start": 0,
            "stop": 5,
            "sequence": "SEQFR1"
        },
        "CDR1": {
            "start": 6,
            "stop": 10,
            "sequence": "SEQCDR1"
        }
    }
    domain.isotype = "IgG"
    domain.species = "human"
    return domain


@pytest.fixture
def mock_chain(mock_domain):
    chain = Mock()
    chain.name = "Heavy"
    chain.sequence = "FULLSEQUENCE"
    chain.domains = [mock_domain]
    return chain


@pytest.fixture
def mock_result(mock_chain):
    result = Mock()
    result.biologic_name = "test_sequence"
    result.chains = [mock_chain]
    return result


@pytest.fixture
def mock_processor(mock_result):
    processor = Mock()
    processor.results = [mock_result]
    return processor


def test_map_domain_type():
    service = AnnotationService()
    
    assert service._map_domain_type("C") == DomainType.CONSTANT
    assert service._map_domain_type("LINKER") == DomainType.LINKER
    assert service._map_domain_type("V") == DomainType.VARIABLE
    assert service._map_domain_type("unknown") == DomainType.VARIABLE


def test_get_domain_positions():
    service = AnnotationService()
    
    # Test LINKER domain
    domain = Mock()
    domain.alignment_details = {"start": 0, "end": 10}
    start, stop = service._get_domain_positions(domain, DomainType.LINKER)
    assert start == 0
    assert stop == 10
    
    # Test VARIABLE domain
    domain.alignment_details = {"query_start": 5, "query_end": 15}
    start, stop = service._get_domain_positions(domain, DomainType.VARIABLE)
    assert start == 5
    assert stop == 15
    
    # Test no alignment details
    domain.alignment_details = None
    start, stop = service._get_domain_positions(domain, DomainType.VARIABLE)
    assert start is None
    assert stop is None


def test_process_region():
    service = AnnotationService()
    
    # Test dict region
    dict_region = {"start": 0, "stop": 5, "sequence": "SEQFR1"}
    start, stop, seq = service._process_region(dict_region)
    assert start == 1  # 0-based to 1-based
    assert stop == 6   # 0-based to 1-based
    assert seq == "SEQFR1"
    
    # Test object region
    region = Mock()
    region.start = 0
    region.stop = 5
    region.sequence = "SEQFR1"
    start, stop, seq = service._process_region(region)
    assert start == 1
    assert stop == 6
    assert seq == "SEQFR1"


def test_process_regions(mock_domain):
    service = AnnotationService()
    regions = service._process_regions(mock_domain)
    
    assert len(regions) == 2
    fr1 = next(r for r in regions if r.name == "FR1")
    cdr1 = next(r for r in regions if r.name == "CDR1")
    
    assert fr1.start == 1
    assert fr1.stop == 6
    assert fr1.features[0].value == "SEQFR1"
    
    assert cdr1.start == 7
    assert cdr1.stop == 11
    assert cdr1.features[0].value == "SEQCDR1"


def test_process_domain(mock_domain):
    service = AnnotationService()
    v2_domain = service._process_domain(mock_domain)
    
    assert v2_domain.domain_type == DomainType.VARIABLE
    assert v2_domain.sequence == "SEQUENCE"
    assert v2_domain.start == 0
    assert v2_domain.stop == 10
    assert len(v2_domain.regions) == 2
    assert v2_domain.isotype == "IgG"
    assert v2_domain.species == "human"


def test_process_chain(mock_chain):
    service = AnnotationService()
    v2_chain = service._process_chain(mock_chain)
    
    assert v2_chain.name == "Heavy"
    assert v2_chain.sequence == "FULLSEQUENCE"
    assert len(v2_chain.domains) == 1


def test_process_sequence(mock_result):
    service = AnnotationService()
    v2_sequence = service._process_sequence(mock_result)
    
    assert v2_sequence.name == "test_sequence"
    assert v2_sequence.original_sequence == "FULLSEQUENCE"
    assert len(v2_sequence.chains) == 1


def test_calculate_statistics(mock_processor):
    service = AnnotationService()
    chain_types, isotypes, species_counts = service._calculate_statistics(mock_processor)
    
    assert chain_types == {"IgG": 1}
    assert isotypes == {"IgG": 1}
    assert species_counts == {"human": 1}


@patch('backend.annotation.AnarciResultProcessor.AnarciResultProcessor')
def test_process_annotation_request(mock_anarci_cls, mock_processor):
    mock_anarci_cls.return_value = mock_processor
    service = AnnotationService()
    
    request = AnnotationRequestV2(
        sequences=[
            InputSequence(
                name="test",
                heavy_chain="SEQUENCE"
            )
        ],
        numbering_scheme="imgt"
    )
    
    result = service.process_annotation_request(request)
    
    assert result.numbering_scheme == "imgt"
    assert len(result.sequences) == 1
    assert result.total_sequences == 1
    assert result.chain_types == {"IgG": 1}
    assert result.isotypes == {"IgG": 1}
    assert result.species == {"human": 1}


def test_prepare_input_dict():
    service = AnnotationService()
    request = AnnotationRequestV2(
        sequences=[
            InputSequence(
                name="test",
                heavy_chain="SEQUENCE"
            )
        ],
        numbering_scheme="imgt"
    )
    
    input_dict = service._prepare_input_dict(request)
    assert "test" in input_dict
    assert input_dict["test"] == {"H": "SEQUENCE"}
