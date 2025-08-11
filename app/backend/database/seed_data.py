"""
Data seeding script for AbSequenceAlign database.
Populates lookup tables with initial values.
"""

import asyncio
import os
import sys

from sqlalchemy import text

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.engine import get_database_engine
from database.models import (
    ChainType,
    DomainType,
    NumberingScheme,
    RegionType,
    FeatureType,
    JobType,
    JobStatus,
)


async def seed_lookup_tables(environment: str = "development"):
    """Seed lookup tables with initial data."""
    print(f"Seeding lookup tables for environment: {environment}...")

    engine = get_database_engine(environment)
    async with engine.session_factory() as session:
        try:
            # Seed Chain Types
            chain_types = [
                ChainType(
                    code="HEAVY",
                    name="Heavy Chain",
                    description="Heavy chain of an antibody",
                ),
                ChainType(
                    code="LIGHT",
                    name="Light Chain",
                    description="Light chain of an antibody",
                ),
                ChainType(
                    code="SINGLE_CHAIN",
                    name="Single Chain",
                    description="Single chain antibody",
                ),
            ]

            for chain_type in chain_types:
                result = await session.execute(
                    text("SELECT id FROM chain_types WHERE code = :code"),
                    {"code": chain_type.code},
                )
                existing = result.fetchone()
                if not existing:
                    session.add(chain_type)
                    print(f"✅ Added chain type: {chain_type.code}")

            # Seed Domain Types
            domain_types = [
                DomainType(
                    code="VARIABLE",
                    name="Variable Domain",
                    description="Variable domain of an antibody",
                ),
                DomainType(
                    code="CONSTANT",
                    name="Constant Domain",
                    description="Constant domain of an antibody",
                ),
                DomainType(
                    code="JOINING",
                    name="Joining Region",
                    description="Joining region of an antibody",
                ),
            ]

            for domain_type in domain_types:
                result = await session.execute(
                    text("SELECT id FROM domain_types WHERE code = :code"),
                    {"code": domain_type.code},
                )
                existing = result.fetchone()
                if not existing:
                    session.add(domain_type)
                    print(f"✅ Added domain type: {domain_type.code}")

            # Seed Numbering Schemes
            numbering_schemes = [
                NumberingScheme(
                    code="IMGT",
                    name="IMGT Numbering",
                    description="IMGT numbering scheme",
                ),
                NumberingScheme(
                    code="KABAT",
                    name="Kabat Numbering",
                    description="Kabat numbering scheme",
                ),
                NumberingScheme(
                    code="CHOTHIA",
                    name="Chothia Numbering",
                    description="Chothia numbering scheme",
                ),
            ]

            for numbering_scheme in numbering_schemes:
                result = await session.execute(
                    text(
                        "SELECT id FROM numbering_schemes WHERE code = :code"
                    ),
                    {"code": numbering_scheme.code},
                )
                existing = result.fetchone()
                if not existing:
                    session.add(numbering_scheme)
                    print(
                        f"✅ Added numbering scheme: {numbering_scheme.code}"
                    )

            # Seed Region Types
            region_types = [
                RegionType(
                    code="FR1",
                    name="Framework Region 1",
                    description="Framework region 1",
                ),
                RegionType(
                    code="CDR1",
                    name="Complementarity-Determining Region 1",
                    description="CDR1 region",
                ),
                RegionType(
                    code="FR2",
                    name="Framework Region 2",
                    description="Framework region 2",
                ),
                RegionType(
                    code="CDR2",
                    name="Complementarity-Determining Region 2",
                    description="CDR2 region",
                ),
                RegionType(
                    code="FR3",
                    name="Framework Region 3",
                    description="Framework region 3",
                ),
                RegionType(
                    code="CDR3",
                    name="Complementarity-Determining Region 3",
                    description="CDR3 region",
                ),
                RegionType(
                    code="FR4",
                    name="Framework Region 4",
                    description="Framework region 4",
                ),
            ]

            for region_type in region_types:
                result = await session.execute(
                    text("SELECT id FROM region_types WHERE code = :code"),
                    {"code": region_type.code},
                )
                existing = result.fetchone()
                if not existing:
                    session.add(region_type)
                    print(f"✅ Added region type: {region_type.code}")

            # Seed Feature Types
            feature_types = [
                FeatureType(
                    code="GENE", name="Gene", description="Gene information"
                ),
                FeatureType(
                    code="ALLELE",
                    name="Allele",
                    description="Allele information",
                ),
                FeatureType(
                    code="ISOTYPE",
                    name="Isotype",
                    description="Antibody isotype",
                ),
                FeatureType(
                    code="MUTATION",
                    name="Mutation",
                    description="Sequence mutation",
                ),
                FeatureType(
                    code="POST_TRANSLATIONAL",
                    name="Post-Translational Modification",
                    description="Post-translational modification",
                ),
            ]

            for feature_type in feature_types:
                result = await session.execute(
                    text("SELECT id FROM feature_types WHERE code = :code"),
                    {"code": feature_type.code},
                )
                existing = result.fetchone()
                if not existing:
                    session.add(feature_type)
                    print(f"✅ Added feature type: {feature_type.code}")

            # Seed Job Types
            job_types = [
                JobType(
                    code="ANNOTATION",
                    name="Sequence Annotation",
                    description="Antibody sequence annotation",
                ),
                JobType(
                    code="ALIGNMENT",
                    name="Sequence Alignment",
                    description="Sequence alignment analysis",
                ),
                JobType(
                    code="ANALYSIS",
                    name="Sequence Analysis",
                    description="General sequence analysis",
                ),
            ]

            for job_type in job_types:
                result = await session.execute(
                    text("SELECT id FROM job_types WHERE code = :code"),
                    {"code": job_type.code},
                )
                existing = result.fetchone()
                if not existing:
                    session.add(job_type)
                    print(f"✅ Added job type: {job_type.code}")

            # Seed Job Statuses
            job_statuses = [
                JobStatus(
                    code="PENDING",
                    name="Pending",
                    description="Job is pending execution",
                ),
                JobStatus(
                    code="RUNNING",
                    name="Running",
                    description="Job is currently running",
                ),
                JobStatus(
                    code="COMPLETED",
                    name="Completed",
                    description="Job completed successfully",
                ),
                JobStatus(
                    code="FAILED",
                    name="Failed",
                    description="Job failed to complete",
                ),
                JobStatus(
                    code="CANCELLED",
                    name="Cancelled",
                    description="Job was cancelled",
                ),
            ]

            for job_status in job_statuses:
                result = await session.execute(
                    text("SELECT id FROM job_statuses WHERE code = :code"),
                    {"code": job_status.code},
                )
                existing = result.fetchone()
                if not existing:
                    session.add(job_status)
                    print(f"✅ Added job status: {job_status.code}")

            await session.commit()
            print("✅ All lookup tables seeded successfully!")

        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding data: {e}")
            raise


async def main():
    """Main function."""
    import sys

    # Get environment from command line argument or use default
    environment = sys.argv[1] if len(sys.argv) > 1 else "development"

    try:
        await seed_lookup_tables(environment)
    except Exception as e:
        print(f"❌ Failed to seed data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
