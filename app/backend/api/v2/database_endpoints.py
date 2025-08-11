"""
Database API endpoints for antibody sequence management.
Provides CRUD operations for antibody sequences and their related entities.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.engine import get_db_session
from backend.application.services.biologic_service import BiologicService
from backend.domain.entities import BiologicEntity
from backend.domain.value_objects import AnnotationMetadata
from backend.logger import logger

router = APIRouter(prefix="/api/v2/database", tags=["database"])


@router.get("/biologics")
async def list_biologics(
    limit: Optional[int] = Query(
        100, ge=1, le=1000, description="Maximum number of biologics to return"
    ),
    offset: Optional[int] = Query(
        0, ge=0, description="Number of biologics to skip"
    ),
    biologic_type: Optional[str] = Query(
        None,
        description="Filter by biologic type (antibody, protein, dna, rna)",
    ),
    db_session: AsyncSession = Depends(get_db_session),
):
    """List all biologics with optional filtering and pagination."""
    try:
        service = BiologicService(db_session)

        if biologic_type:
            # Filter by biologic type
            biologics = await service.search_biologics(
                {"biologic_type": biologic_type}
            )
        else:
            biologics = await service.list_biologics(
                limit=limit, offset=offset
            )

        # Convert to API response format
        biologics_data = []
        for biologic in biologics:
            biologics_data.append(
                {
                    "id": biologic.id,
                    "name": biologic.name,
                    "description": biologic.description,
                    "organism": biologic.organism,
                    "biologic_type": biologic.biologic_type,
                    "metadata": biologic.metadata,
                    "created_at": (
                        biologic.created_at.isoformat()
                        if biologic.created_at
                        else None
                    ),
                    "updated_at": (
                        biologic.updated_at.isoformat()
                        if biologic.updated_at
                        else None
                    ),
                }
            )

        return {
            "success": True,
            "data": {
                "biologics": biologics_data,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "total": len(biologics_data),
                    "count": len(biologics_data),
                },
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing antibody sequences: {e}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}"
        )


@router.get("/biologics/{biologic_id}")
async def get_biologic(
    biologic_id: str, db_session: AsyncSession = Depends(get_db_session)
):
    """Get a specific biologic by ID."""
    try:
        service = BiologicService(db_session)
        biologic = await service.get_biologic(biologic_id)

        if not biologic:
            raise HTTPException(status_code=404, detail="Biologic not found")

        # Convert to API response format
        biologic_data = {
            "id": biologic.id,
            "name": biologic.name,
            "description": biologic.description,
            "organism": biologic.organism,
            "biologic_type": biologic.biologic_type,
            "metadata": biologic.metadata,
            "chains": biologic.chains,
            "created_at": (
                biologic.created_at.isoformat()
                if biologic.created_at
                else None
            ),
            "updated_at": (
                biologic.updated_at.isoformat()
                if biologic.updated_at
                else None
            ),
        }

        return {
            "success": True,
            "data": {"biologic": biologic_data},
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting biologic {biologic_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}"
        )


@router.get("/antibodies/name/{sequence_name}")
async def get_antibody_sequence_by_name(
    sequence_name: str, db_session: AsyncSession = Depends(get_db_session)
):
    """Get a specific antibody sequence by name."""
    try:
        service = BiologicService(db_session)
        result = await service.find_biologic_by_name(sequence_name)

        if not result.success:
            if "not found" in result.error.lower():
                raise HTTPException(status_code=404, detail=result.error)
            else:
                raise HTTPException(status_code=500, detail=result.error)

        # Reuse the same logic as get_biologic
        biologic = result.data["biologic"]

        # Convert to API response format (same as above)
        biologic_data = {
            "id": str(biologic.id),
            "name": biologic.name,
            "biologic_type": biologic.biologic_type,
            "description": biologic.description,
            "metadata": biologic.metadata,
            "chains": [],
        }

        # Add chain information (same logic as above)
        for chain in biologic.chains:
            chain_data = {
                "name": chain.name,
                "chain_type": chain.chain_type,
                "sequences": [],
            }

            # Add sequence information
            for sequence in chain.sequences:
                sequence_data = {
                    "sequence_type": sequence.sequence_type,
                    "sequence_data": sequence.sequence_data,
                    "domains": [],
                }

                # Add domain information
                for domain in sequence.domains:
                    domain_data = {
                        "domain_type": domain.domain_type,
                        "start_position": domain.start_position,
                        "end_position": domain.end_position,
                        "confidence_score": domain.confidence_score,
                        "metadata": domain.metadata,
                        "features": [],
                    }

                    # Add feature information
                    for feature in domain.features:
                        feature_data = {
                            "feature_type": feature.feature_type,
                            "name": feature.name,
                            "value": feature.value,
                            "start_position": feature.start_position,
                            "end_position": feature.end_position,
                            "confidence_score": feature.confidence_score,
                            "metadata": feature.metadata,
                        }
                        domain_data["features"].append(feature_data)

                    sequence_data["domains"].append(domain_data)

                chain_data["sequences"].append(sequence_data)

            biologic_data["chains"].append(chain_data)

        return {"success": True, "data": biologic_data}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/antibodies/{sequence_id}")
async def delete_antibody_sequence(
    sequence_id: str, db_session: AsyncSession = Depends(get_db_session)
):
    """Delete an antibody sequence by ID."""
    try:
        service = BiologicService(db_session)
        result = await service.delete_biologic(sequence_id)

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
        service = BiologicService(db_session)
        result = await service.get_biologic_sequence_statistics()

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
        biologic = BiologicEntity(
            name=sequence_data["name"],
            biologic_type=sequence_data.get("biologic_type", "antibody"),
            description=sequence_data.get("description"),
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

        service = BiologicService(db_session)
        result = await service.save_biologic(biologic)

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        saved_biologic = result.data["saved_biologic"]

        return {
            "success": True,
            "message": f"Biologic {saved_biologic.name} saved successfully",
            "data": {
                "saved_biologic": {
                    "id": str(saved_biologic.id),
                    "name": saved_biologic.name,
                    "biologic_type": saved_biologic.biologic_type,
                    "chains_count": len(saved_biologic.chains),
                }
            },
            "metadata": result.metadata,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving biologic: {e}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}"
        )
