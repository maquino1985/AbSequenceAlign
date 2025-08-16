"""
Database API endpoints for antibody sequence management.
Provides CRUD operations for antibody sequences and their related entities.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.engine import get_db_session
from backend.application.services.antibody_database_service import (
    AntibodyDatabaseService,
)
from backend.domain.models import ChainType
from backend.domain.entities import AntibodySequence
from backend.domain.value_objects import AminoAcidSequence, AnnotationMetadata
from backend.logger import logger

router = APIRouter()


@router.get("/antibodies")
async def list_antibody_sequences(
    limit: Optional[int] = Query(
        100, ge=1, le=1000, description="Maximum number of sequences to return"
    ),
    offset: Optional[int] = Query(
        0, ge=0, description="Number of sequences to skip"
    ),
    chain_type: Optional[str] = Query(
        None, description="Filter by chain type (HEAVY, LIGHT, SINGLE_CHAIN)"
    ),
    db_session: AsyncSession = Depends(get_db_session),
):
    """List all antibody sequences with optional filtering and pagination."""
    try:
        service = AntibodyDatabaseService(db_session)

        if chain_type:
            try:
                chain_type_enum = ChainType(chain_type.upper())
                result = await service.find_antibody_sequences_by_chain_type(
                    chain_type_enum, limit=limit, offset=offset
                )
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid chain type: {chain_type}. Must be one of: HEAVY, LIGHT, SINGLE_CHAIN",
                )
        else:
            result = await service.list_all_antibody_sequences(
                limit=limit, offset=offset
            )

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        # Convert domain entities to API response format
        sequences_data = []
        for sequence in result.data["antibody_sequences"]:
            sequences_data.append(
                {
                    "id": str(sequence.id),
                    "name": sequence.name,
                    "length": (
                        len(sequence.sequence.value)
                        if sequence.sequence
                        else 0
                    ),
                    "chains_count": len(sequence.chains),
                    "description": (
                        sequence.metadata.description
                        if sequence.metadata
                        else None
                    ),
                    "source": (
                        sequence.metadata.source if sequence.metadata else None
                    ),
                    "created_at": (
                        sequence.created_at.isoformat()
                        if hasattr(sequence, "created_at")
                        else None
                    ),
                }
            )

        return {
            "success": True,
            "data": {
                "sequences": sequences_data,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "total": result.metadata.get(
                        "total_count", len(sequences_data)
                    ),
                    "count": len(sequences_data),
                },
            },
            "metadata": result.metadata,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing antibody sequences: {e}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}"
        )


@router.get("/antibodies/{sequence_id}")
async def get_antibody_sequence(
    sequence_id: str, db_session: AsyncSession = Depends(get_db_session)
):
    """Get a specific antibody sequence by ID."""
    try:
        service = AntibodyDatabaseService(db_session)
        result = await service.find_antibody_sequence_by_id(sequence_id)

        if not result.success:
            if "not found" in result.error.lower():
                raise HTTPException(status_code=404, detail=result.error)
            else:
                raise HTTPException(status_code=500, detail=result.error)

        sequence = result.data["antibody_sequence"]

        # Convert to API response format
        sequence_data = {
            "id": str(sequence.id),
            "name": sequence.name,
            "sequence": sequence.sequence.value if sequence.sequence else None,
            "length": len(sequence.sequence.value) if sequence.sequence else 0,
            "description": (
                sequence.metadata.description if sequence.metadata else None
            ),
            "source": sequence.metadata.source if sequence.metadata else None,
            "chains": [],
        }

        # Add chain information
        for chain in sequence.chains:
            chain_data = {
                "name": chain.name,
                "chain_type": chain.chain_type.value,
                "numbering_scheme": chain.numbering_scheme.value,
                "sequence": chain.sequence.value if chain.sequence else None,
                "length": len(chain.sequence.value) if chain.sequence else 0,
                "domains": [],
                "features": [],
            }

            # Add domain information
            for domain in chain.domains:
                domain_data = {
                    "domain_type": domain.domain_type.value,
                    "sequence": (
                        domain.sequence.value if domain.sequence else None
                    ),
                    "start_position": (
                        domain.boundary.start if domain.boundary else None
                    ),
                    "end_position": (
                        domain.boundary.end if domain.boundary else None
                    ),
                    "confidence_score": (
                        domain.confidence_score.value
                        if domain.confidence_score
                        else None
                    ),
                    "regions": [],
                }

                # Add region information
                for region in domain.regions:
                    region_data = {
                        "region_type": region.region_type.value,
                        "sequence": (
                            region.sequence.value if region.sequence else None
                        ),
                        "start_position": (
                            region.boundary.start if region.boundary else None
                        ),
                        "end_position": (
                            region.boundary.end if region.boundary else None
                        ),
                        "confidence_score": (
                            region.confidence_score.value
                            if region.confidence_score
                            else None
                        ),
                    }
                    domain_data["regions"].append(region_data)

                chain_data["domains"].append(domain_data)

            # Add feature information
            for feature in chain.features:
                feature_data = {
                    "feature_type": feature.feature_type.value,
                    "name": feature.name,
                    "value": feature.value,
                    "start_position": (
                        feature.boundary.start if feature.boundary else None
                    ),
                    "end_position": (
                        feature.boundary.end if feature.boundary else None
                    ),
                    "confidence_score": (
                        feature.confidence_score.value
                        if feature.confidence_score
                        else None
                    ),
                }
                chain_data["features"].append(feature_data)

            sequence_data["chains"].append(chain_data)

        return {
            "success": True,
            "data": {"antibody_sequence": sequence_data},
            "metadata": result.metadata,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting antibody sequence {sequence_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}"
        )


@router.get("/antibodies/name/{sequence_name}")
async def get_antibody_sequence_by_name(
    sequence_name: str, db_session: AsyncSession = Depends(get_db_session)
):
    """Get a specific antibody sequence by name."""
    try:
        service = AntibodyDatabaseService(db_session)
        result = await service.find_antibody_sequence_by_name(sequence_name)

        if not result.success:
            if "not found" in result.error.lower():
                raise HTTPException(status_code=404, detail=result.error)
            else:
                raise HTTPException(status_code=500, detail=result.error)

        # Reuse the same logic as get_antibody_sequence
        sequence = result.data["antibody_sequence"]

        # Convert to API response format (same as above)
        sequence_data = {
            "id": str(sequence.id),
            "name": sequence.name,
            "sequence": sequence.sequence.value if sequence.sequence else None,
            "length": len(sequence.sequence.value) if sequence.sequence else 0,
            "description": (
                sequence.metadata.description if sequence.metadata else None
            ),
            "source": sequence.metadata.source if sequence.metadata else None,
            "chains": [],
        }

        # Add chain information (same logic as above)
        for chain in sequence.chains:
            chain_data = {
                "name": chain.name,
                "chain_type": chain.chain_type.value,
                "numbering_scheme": chain.numbering_scheme.value,
                "sequence": chain.sequence.value if chain.sequence else None,
                "length": len(chain.sequence.value) if chain.sequence else 0,
                "domains": [],
                "features": [],
            }

            # Add domain information
            for domain in chain.domains:
                domain_data = {
                    "domain_type": domain.domain_type.value,
                    "sequence": (
                        domain.sequence.value if domain.sequence else None
                    ),
                    "start_position": (
                        domain.boundary.start if domain.boundary else None
                    ),
                    "end_position": (
                        domain.boundary.end if domain.boundary else None
                    ),
                    "confidence_score": (
                        domain.confidence_score.value
                        if domain.confidence_score
                        else None
                    ),
                    "regions": [],
                }

                # Add region information
                for region in domain.regions:
                    region_data = {
                        "region_type": region.region_type.value,
                        "sequence": (
                            region.sequence.value if region.sequence else None
                        ),
                        "start_position": (
                            region.boundary.start if region.boundary else None
                        ),
                        "end_position": (
                            region.boundary.end if region.boundary else None
                        ),
                        "confidence_score": (
                            region.confidence_score.value
                            if region.confidence_score
                            else None
                        ),
                    }
                    domain_data["regions"].append(region_data)

                chain_data["domains"].append(domain_data)

            # Add feature information
            for feature in chain.features:
                feature_data = {
                    "feature_type": feature.feature_type.value,
                    "name": feature.name,
                    "value": feature.value,
                    "start_position": (
                        feature.boundary.start if feature.boundary else None
                    ),
                    "end_position": (
                        feature.boundary.end if feature.boundary else None
                    ),
                    "confidence_score": (
                        feature.confidence_score.value
                        if feature.confidence_score
                        else None
                    ),
                }
                chain_data["features"].append(feature_data)

            sequence_data["chains"].append(chain_data)

        return {
            "success": True,
            "data": {"antibody_sequence": sequence_data},
            "metadata": result.metadata,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error getting antibody sequence by name {sequence_name}: {e}"
        )
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}"
        )


@router.delete("/antibodies/{sequence_id}")
async def delete_antibody_sequence(
    sequence_id: str, db_session: AsyncSession = Depends(get_db_session)
):
    """Delete an antibody sequence by ID."""
    try:
        service = AntibodyDatabaseService(db_session)
        result = await service.delete_antibody_sequence(sequence_id)

        if not result.success:
            if "not found" in result.error.lower():
                raise HTTPException(status_code=404, detail=result.error)
            else:
                raise HTTPException(status_code=500, detail=result.error)

        return {
            "success": True,
            "message": f"Antibody sequence {sequence_id} deleted successfully",
            "data": {"deleted": True},
            "metadata": result.metadata,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting antibody sequence {sequence_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}"
        )


@router.get("/antibodies/statistics")
async def get_antibody_statistics(
    db_session: AsyncSession = Depends(get_db_session),
):
    """Get statistics about stored antibody sequences."""
    try:
        service = AntibodyDatabaseService(db_session)
        result = await service.get_antibody_sequence_statistics()

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        return {
            "success": True,
            "data": {"statistics": result.data["statistics"]},
            "metadata": result.metadata,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting antibody statistics: {e}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}"
        )


@router.post("/antibodies/save")
async def save_antibody_sequence(
    sequence_data: Dict[str, Any],
    db_session: AsyncSession = Depends(get_db_session),
):
    """Save an antibody sequence to the database."""
    try:
        # Validate required fields
        if not sequence_data.get("name"):
            raise HTTPException(
                status_code=400, detail="Sequence name is required"
            )

        if not sequence_data.get("sequence") and not sequence_data.get(
            "chains"
        ):
            raise HTTPException(
                status_code=400,
                detail="Either sequence or chains must be provided",
            )

        # Create domain entity from request data
        sequence = AntibodySequence(
            name=sequence_data["name"],
            sequence=(
                AminoAcidSequence(sequence_data["sequence"])
                if sequence_data.get("sequence")
                else None
            ),
            chains=[],  # Would be populated from chains data in a full implementation
            metadata=(
                AnnotationMetadata(
                    description=sequence_data.get("description"),
                    source=sequence_data.get("source"),
                )
                if sequence_data.get("description")
                or sequence_data.get("source")
                else None
            ),
        )

        service = AntibodyDatabaseService(db_session)
        result = await service.save_antibody_sequence(sequence)

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        saved_sequence = result.data["saved_sequence"]

        return {
            "success": True,
            "message": f"Antibody sequence {saved_sequence.name} saved successfully",
            "data": {
                "saved_sequence": {
                    "id": str(saved_sequence.id),
                    "name": saved_sequence.name,
                    "length": (
                        len(saved_sequence.sequence.value)
                        if saved_sequence.sequence
                        else 0
                    ),
                    "chains_count": len(saved_sequence.chains),
                }
            },
            "metadata": result.metadata,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving antibody sequence: {e}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}"
        )
