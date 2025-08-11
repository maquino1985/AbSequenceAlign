"""
Tests for model compatibility between Pydantic and ORM models.

These tests ensure that Pydantic models are kept in sync with their corresponding ORM models.
Run these tests whenever you update either Pydantic or ORM models.
"""

import pytest
from backend.utils.pydantic_validator import (
    validate_model_compatibility,
    validate_all_models,
    compare_models,
)
from backend.models.biologic_models import (
    BiologicResponse,
    BiologicAliasResponse,
    ChainResponse,
    SequenceResponse,
    ChainSequenceResponse,
    SequenceDomainResponse,
    DomainFeatureResponse,
)
from backend.database.models import (
    Biologic,
    BiologicAlias,
    Chain,
    Sequence,
    ChainSequence,
    SequenceDomain,
    DomainFeature,
)


class TestModelCompatibility:
    """Test that Pydantic models match their ORM counterparts."""

    def test_biologic_model_compatibility(self):
        """Test BiologicResponse matches Biologic ORM model."""
        validate_model_compatibility(BiologicResponse, Biologic)

    def test_biologic_alias_model_compatibility(self):
        """Test BiologicAliasResponse matches BiologicAlias ORM model."""
        validate_model_compatibility(BiologicAliasResponse, BiologicAlias)

    def test_chain_model_compatibility(self):
        """Test ChainResponse matches Chain ORM model."""
        validate_model_compatibility(ChainResponse, Chain)

    def test_sequence_model_compatibility(self):
        """Test SequenceResponse matches Sequence ORM model."""
        validate_model_compatibility(SequenceResponse, Sequence)

    def test_chain_sequence_model_compatibility(self):
        """Test ChainSequenceResponse matches ChainSequence ORM model."""
        validate_model_compatibility(ChainSequenceResponse, ChainSequence)

    def test_sequence_domain_model_compatibility(self):
        """Test SequenceDomainResponse matches SequenceDomain ORM model."""
        validate_model_compatibility(SequenceDomainResponse, SequenceDomain)

    def test_domain_feature_model_compatibility(self):
        """Test DomainFeatureResponse matches DomainFeature ORM model."""
        validate_model_compatibility(DomainFeatureResponse, DomainFeature)

    def test_all_models_compatibility(self):
        """Test all model pairs are compatible."""
        results = validate_all_models()

        incompatible_models = [
            r for r in results if "Incompatible" in r["status"]
        ]

        if incompatible_models:
            # Print detailed information about incompatible models
            print("\nIncompatible models found:")
            for result in incompatible_models:
                print(f"  {result['pydantic_model']} ↔ {result['orm_model']}")
                print(f"    Error: {result['error']}")

            pytest.fail(
                f"Found {len(incompatible_models)} incompatible model pairs"
            )


class TestModelComparison:
    """Test model comparison utilities."""

    def test_compare_biologic_models(self):
        """Test detailed comparison of Biologic models."""
        comparison = compare_models(BiologicResponse, Biologic)

        assert comparison["pydantic_model"] == "BiologicResponse"
        assert comparison["orm_model"] == "Biologic"
        assert comparison["is_compatible"] is True
        assert len(comparison["missing_in_pydantic"]) == 0
        assert len(comparison["missing_in_orm"]) == 0
        assert len(comparison["common_fields"]) > 0

    def test_compare_chain_models(self):
        """Test detailed comparison of Chain models."""
        comparison = compare_models(ChainResponse, Chain)

        assert comparison["pydantic_model"] == "ChainResponse"
        assert comparison["orm_model"] == "Chain"
        assert comparison["is_compatible"] is True
        assert len(comparison["missing_in_pydantic"]) == 0
        assert len(comparison["missing_in_orm"]) == 0
        assert len(comparison["common_fields"]) > 0


class TestModelFieldValidation:
    """Test specific field validations."""

    def test_biologic_required_fields(self):
        """Test that BiologicResponse has all required fields from Biologic ORM."""
        biologic_fields = {
            "id",
            "name",
            "description",
            "organism",
            "biologic_type",
            "metadata_json",
            "created_at",
            "updated_at",
        }

        response_fields = set(BiologicResponse.model_fields.keys())

        # Check that all ORM fields are present in Pydantic model
        missing_fields = biologic_fields - response_fields
        assert (
            len(missing_fields) == 0
        ), f"Missing fields in BiologicResponse: {missing_fields}"

    def test_chain_required_fields(self):
        """Test that ChainResponse has all required fields from Chain ORM."""
        chain_fields = {
            "id",
            "biologic_id",
            "name",
            "chain_type",
            "metadata_json",
            "created_at",
            "updated_at",
        }

        response_fields = set(ChainResponse.model_fields.keys())

        # Check that all ORM fields are present in Pydantic model
        missing_fields = chain_fields - response_fields
        assert (
            len(missing_fields) == 0
        ), f"Missing fields in ChainResponse: {missing_fields}"

    def test_sequence_required_fields(self):
        """Test that SequenceResponse has all required fields from Sequence ORM."""
        sequence_fields = {
            "id",
            "sequence_type",
            "sequence_data",
            "length",
            "description",
            "metadata_json",
            "created_at",
            "updated_at",
        }

        response_fields = set(SequenceResponse.model_fields.keys())

        # Check that all ORM fields are present in Pydantic model
        missing_fields = sequence_fields - response_fields
        assert (
            len(missing_fields) == 0
        ), f"Missing fields in SequenceResponse: {missing_fields}"


if __name__ == "__main__":
    """Run model compatibility tests directly."""
    pytest.main([__file__, "-v"])
