"""
Model validation utilities.

This module provides utilities to validate that Pydantic models are in sync
with their corresponding ORM models.
"""

from typing import Type, List, Set
from pydantic import BaseModel
from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeBase


def validate_model_compatibility(
    pydantic_model: Type[BaseModel], orm_model: Type[DeclarativeBase]
) -> None:
    """
    Validate that Pydantic model fields match ORM model columns.

    Args:
        pydantic_model: The Pydantic model class
        orm_model: The SQLAlchemy ORM model class

    Raises:
        ValueError: If there are mismatches between the models
    """
    pydantic_fields = set(pydantic_model.model_fields.keys())
    orm_columns = {c.name for c in inspect(orm_model).columns}

    missing_in_pydantic = orm_columns - pydantic_fields
    missing_in_orm = pydantic_fields - orm_columns

    if missing_in_pydantic:
        raise ValueError(
            f"ORM fields missing in Pydantic model {pydantic_model.__name__}: {missing_in_pydantic}"
        )
    if missing_in_orm:
        raise ValueError(
            f"Pydantic fields missing in ORM model {orm_model.__name__}: {missing_in_orm}"
        )


def get_orm_columns(orm_model: Type[DeclarativeBase]) -> Set[str]:
    """Get all column names from an ORM model."""
    return {c.name for c in inspect(orm_model).columns}


def get_pydantic_fields(pydantic_model: Type[BaseModel]) -> Set[str]:
    """Get all field names from a Pydantic model."""
    return set(pydantic_model.model_fields.keys())


def compare_models(
    pydantic_model: Type[BaseModel], orm_model: Type[DeclarativeBase]
) -> dict:
    """
    Compare Pydantic and ORM models and return detailed comparison.

    Returns:
        dict: Comparison results with missing fields and field types
    """
    pydantic_fields = get_pydantic_fields(pydantic_model)
    orm_columns = get_orm_columns(orm_model)

    missing_in_pydantic = orm_columns - pydantic_fields
    missing_in_orm = pydantic_fields - orm_columns
    common_fields = pydantic_fields & orm_columns

    return {
        "pydantic_model": pydantic_model.__name__,
        "orm_model": orm_model.__name__,
        "missing_in_pydantic": list(missing_in_pydantic),
        "missing_in_orm": list(missing_in_orm),
        "common_fields": list(common_fields),
        "is_compatible": len(missing_in_pydantic) == 0
        and len(missing_in_orm) == 0,
    }


def validate_all_models() -> List[dict]:
    """
    Validate all Pydantic models against their ORM counterparts.

    Returns:
        List of validation results for each model pair
    """
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

    model_pairs = [
        (BiologicResponse, Biologic),
        (BiologicAliasResponse, BiologicAlias),
        (ChainResponse, Chain),
        (SequenceResponse, Sequence),
        (ChainSequenceResponse, ChainSequence),
        (SequenceDomainResponse, SequenceDomain),
        (DomainFeatureResponse, DomainFeature),
    ]

    results = []
    for pydantic_model, orm_model in model_pairs:
        try:
            validate_model_compatibility(pydantic_model, orm_model)
            results.append(
                {
                    "pydantic_model": pydantic_model.__name__,
                    "orm_model": orm_model.__name__,
                    "status": "✅ Compatible",
                    "error": None,
                }
            )
        except ValueError as e:
            results.append(
                {
                    "pydantic_model": pydantic_model.__name__,
                    "orm_model": orm_model.__name__,
                    "status": "❌ Incompatible",
                    "error": str(e),
                }
            )

    return results


def print_validation_report(results: List[dict]) -> None:
    """Print a formatted validation report."""
    print("\n" + "=" * 60)
    print("MODEL COMPATIBILITY VALIDATION REPORT")
    print("=" * 60)

    all_compatible = True
    for result in results:
        status_icon = "✅" if "Compatible" in result["status"] else "❌"
        print(
            f"{status_icon} {result['pydantic_model']} ↔ {result['orm_model']}"
        )
        if result["error"]:
            print(f"   Error: {result['error']}")
            all_compatible = False

    print("\n" + "=" * 60)
    if all_compatible:
        print("🎉 ALL MODELS ARE COMPATIBLE!")
    else:
        print("⚠️  SOME MODELS HAVE COMPATIBILITY ISSUES")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    """Run validation when script is executed directly."""
    results = validate_all_models()
    print_validation_report(results)

    # Exit with error code if any models are incompatible
    incompatible_models = [r for r in results if "Incompatible" in r["status"]]
    if incompatible_models:
        exit(1)
