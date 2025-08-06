# Tests for sequence processing (FASTA parsing, validation, statistics)
import pytest
from Bio.SeqRecord import SeqRecord

from app.annotation.sequence_processor import SequenceProcessor


@pytest.fixture
def processor():
    return SequenceProcessor()


def test_parse_fasta_valid(processor):
    fasta = ">seq1\nACDEFGHIKLMNPQRSTVWY\n>seq2\nACDEFGHIKLMNPQRSTVWY"
    records = processor.parse_fasta(fasta)
    assert len(records) == 2
    assert all(isinstance(r, SeqRecord) for r in records)


def test_parse_fasta_invalid(processor):
    with pytest.raises(ValueError):
        processor.parse_fasta("")


def test_validate_sequence_valid(processor):
    valid, error = processor.validate_sequence("ACDEFGHIKLMNPQRSTVWY" * 6)
    assert valid
    assert error == ""


def test_validate_sequence_invalid(processor):
    valid, error = processor.validate_sequence("ACDEFGHIKLMNPQRSTVWYX")
    assert not valid
    assert "Invalid amino acids" in error


def test_validate_sequences_mixed(processor):
    seqs = ["ACDEFGHIKLMNPQRSTVWY" * 6, "ACDEFGHIKLMNPQRSTVWYX"]
    valid, errors = processor.validate_sequences(seqs)
    assert len(valid) == 1
    assert len(errors) == 1


def test_extract_sequences_from_fasta(processor):
    fasta = ">seq1\nACDEFGHIKLMNPQRSTVWY\n>seq2\nACDEFGHIKLMNPQRSTVWY"
    seqs = processor.extract_sequences_from_fasta(fasta)
    assert seqs == ["ACDEFGHIKLMNPQRSTVWY", "ACDEFGHIKLMNPQRSTVWY"]


def test_format_fasta(processor):
    seqs = ["ACDEFGHIKLMNPQRSTVWY"]
    fasta = processor.format_fasta(seqs, names=["test"])
    assert ">test" in fasta
    assert "ACDEFGHIKLMNPQRSTVWY" in fasta


def test_get_sequence_statistics(processor):
    seqs = ["ACDEFGHIKLMNPQRSTVWY" * 6, "ACDEFGHIKLMNPQRSTVWY" * 7]
    stats = processor.get_sequence_statistics(seqs)
    assert stats["total_sequences"] == 2
    assert stats["min_length"] == 120
    assert stats["max_length"] == 140
    assert stats["total_length"] == 260
