# Database Implementation Plan for AbSequenceAlign

## Overview

This plan outlines the implementation of a robust database layer using PostgreSQL 18, UUIDv7 primary keys, SQLAlchemy ORM, and Alembic for migrations. The database will support our clean architecture by providing persistent storage for all business entities.

## Technology Stack

- **Database**: PostgreSQL 18 (latest version with UUIDv7 support)
- **ORM**: SQLAlchemy 2.0+ (modern async support)
- **Migrations**: Alembic
- **Primary Keys**: UUIDv7 (time-ordered, globally unique)
- **Connection Pooling**: SQLAlchemy async engine
- **Type Safety**: SQLAlchemy type annotations
- **Development Environment**: Docker containers for consistency

## Development Environment Setup

### Docker-Based PostgreSQL 18

**Decision**: Use Docker containers for PostgreSQL 18 development to ensure consistency with CI/CD.

**Benefits**:
- ✅ No local PostgreSQL installation required
- ✅ Consistent environment across development and CI/CD
- ✅ Easy to switch between different PostgreSQL versions
- ✅ Isolated development environment
- ✅ Easy cleanup and reset

### Docker Compose Configuration

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  postgres:
    image: postgres:18-alpine
    container_name: absequencealign-postgres-dev
    environment:
      POSTGRES_DB: absequencealign_dev
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --lc-collate=C --lc-ctype=C"
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init:/docker-entrypoint-initdb.d
    command: >
      postgres
      -c shared_preload_libraries='uuid-ossp'
      -c log_statement=all
      -c log_min_duration_statement=0
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d absequencealign_dev"]
      interval: 10s
      timeout: 5s
      retries: 5

  postgres_test:
    image: postgres:18-alpine
    container_name: absequencealign-postgres-test
    environment:
      POSTGRES_DB: absequencealign_test
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --lc-collate=C --lc-ctype=C"
    ports:
      - "5433:5432"
    volumes:
      - postgres_test_data:/var/lib/postgresql/data
    command: >
      postgres
      -c shared_preload_libraries='uuid-ossp'
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d absequencealign_test"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  postgres_test_data:
```

### Database Initialization Script

```sql
-- database/init/01-init.sql
-- Enable UUID extension for UUIDv7 support
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom UUIDv7 function
CREATE OR REPLACE FUNCTION uuid_generate_v7()
RETURNS uuid
AS $$
DECLARE
  v_time timestamp with time zone = NULL;
  v_secs bigint;
  v_msec bigint;
  v_usec bigint;
  v_timestamp bigint;
  v_timestamp_hex varchar;
  v_version bit(4) = '0111';
  v_variant bit(2) = '10';
  v_node_id bigint;
  v_node_hex varchar;
  v_random_hex varchar;
BEGIN
  -- Get current timestamp
  v_time := clock_timestamp();
  v_secs := EXTRACT(EPOCH FROM v_time);
  v_msec := EXTRACT(MILLISECONDS FROM v_time);
  v_usec := EXTRACT(MICROSECONDS FROM v_time);
  
  -- Calculate timestamp in milliseconds since Unix epoch
  v_timestamp := (v_secs * 1000) + (v_msec % 1000);
  
  -- Convert to hex and pad to 12 characters
  v_timestamp_hex := lpad(to_hex(v_timestamp), 12, '0');
  
  -- Generate random node ID (48 bits)
  v_node_id := floor(random() * (2^48 - 1));
  v_node_hex := lpad(to_hex(v_node_id), 12, '0');
  
  -- Generate random sequence number (14 bits)
  v_random_hex := lpad(to_hex(floor(random() * (2^14 - 1))), 4, '0');
  
  -- Construct UUIDv7
  RETURN (
    substr(v_timestamp_hex, 1, 8) || '-' ||
    substr(v_timestamp_hex, 9, 4) || '-' ||
    v_version || v_random_hex || '-' ||
    v_variant || substr(v_node_hex, 1, 6) || '-' ||
    substr(v_node_hex, 7, 12)
  )::uuid;
END;
$$ LANGUAGE plpgsql;
```

## Database Schema Design

### Core Entities

#### 1. Antibody Sequences (`antibody_sequences`)
```sql
- id: UUIDv7 (Primary Key)
- name: VARCHAR(255) NOT NULL
- description: TEXT
- created_at: TIMESTAMP WITH TIME ZONE DEFAULT NOW()
- updated_at: TIMESTAMP WITH TIME ZONE DEFAULT NOW()
- created_by: UUID (Foreign Key to users)
- is_public: BOOLEAN DEFAULT FALSE
- metadata: JSONB (flexible metadata storage)
```

#### 2. Antibody Chains (`antibody_chains`)
```sql
- id: UUIDv7 (Primary Key)
- antibody_sequence_id: UUIDv7 (Foreign Key)
- name: VARCHAR(100) NOT NULL
- chain_type: ENUM('HEAVY', 'LIGHT', 'SINGLE_CHAIN') NOT NULL
- sequence: TEXT NOT NULL
- sequence_length: INTEGER NOT NULL
- created_at: TIMESTAMP WITH TIME ZONE DEFAULT NOW()
- updated_at: TIMESTAMP WITH TIME ZONE DEFAULT NOW()
```

#### 3. Antibody Domains (`antibody_domains`)
```sql
- id: UUIDv7 (Primary Key)
- chain_id: UUIDv7 (Foreign Key)
- domain_type: ENUM('VARIABLE', 'CONSTANT', 'JOINING') NOT NULL
- numbering_scheme: ENUM('IMGT', 'KABAT', 'CHOTHIA') NOT NULL
- sequence: TEXT NOT NULL
- start_position: INTEGER NOT NULL
- end_position: INTEGER NOT NULL
- confidence_score: DECIMAL(3,2) (0.00-1.00)
- created_at: TIMESTAMP WITH TIME ZONE DEFAULT NOW()
- updated_at: TIMESTAMP WITH TIME ZONE DEFAULT NOW()
```

#### 4. Antibody Regions (`antibody_regions`)
```sql
- id: UUIDv7 (Primary Key)
- domain_id: UUIDv7 (Foreign Key)
- region_type: ENUM('FR1', 'CDR1', 'FR2', 'CDR2', 'FR3', 'CDR3', 'FR4') NOT NULL
- sequence: TEXT NOT NULL
- start_position: INTEGER NOT NULL
- end_position: INTEGER NOT NULL
- confidence_score: DECIMAL(3,2) (0.00-1.00)
- created_at: TIMESTAMP WITH TIME ZONE DEFAULT NOW()
- updated_at: TIMESTAMP WITH TIME ZONE DEFAULT NOW()
```

#### 5. Sequence Features (`sequence_features`)
```sql
- id: UUIDv7 (Primary Key)
- sequence_id: UUIDv7 (Foreign Key to antibody_sequences)
- feature_type: ENUM('GENE', 'ALLELE', 'ISOTYPE', 'MUTATION', 'POST_TRANSLATIONAL') NOT NULL
- name: VARCHAR(255) NOT NULL
- value: TEXT
- start_position: INTEGER
- end_position: INTEGER
- confidence_score: DECIMAL(3,2) (0.00-1.00)
- source: VARCHAR(100) (e.g., 'ANARCI', 'HMMER', 'MANUAL')
- metadata: JSONB
- created_at: TIMESTAMP WITH TIME ZONE DEFAULT NOW()
- updated_at: TIMESTAMP WITH TIME ZONE DEFAULT NOW()
```

#### 6. Processing Jobs (`processing_jobs`)
```sql
- id: UUIDv7 (Primary Key)
- sequence_id: UUIDv7 (Foreign Key)
- job_type: ENUM('ANNOTATION', 'ALIGNMENT', 'ANALYSIS') NOT NULL
- status: ENUM('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED') NOT NULL
- input_data: JSONB
- output_data: JSONB
- error_message: TEXT
- started_at: TIMESTAMP WITH TIME ZONE
- completed_at: TIMESTAMP WITH TIME ZONE
- created_at: TIMESTAMP WITH TIME ZONE DEFAULT NOW()
- updated_at: TIMESTAMP WITH TIME ZONE DEFAULT NOW()
```

#### 7. External Tool Results (`external_tool_results`)
```sql
- id: UUIDv7 (Primary Key)
- job_id: UUIDv7 (Foreign Key)
- tool_name: VARCHAR(100) NOT NULL (e.g., 'ANARCI', 'HMMER')
- tool_version: VARCHAR(50)
- input_data: JSONB
- output_data: JSONB
- execution_time: INTERVAL
- success: BOOLEAN NOT NULL
- error_details: JSONB
- created_at: TIMESTAMP WITH TIME ZONE DEFAULT NOW()
```

### Supporting Tables

#### 8. Users (`users`) - For future authentication
```sql
- id: UUIDv7 (Primary Key)
- email: VARCHAR(255) UNIQUE NOT NULL
- username: VARCHAR(100) UNIQUE NOT NULL
- created_at: TIMESTAMP WITH TIME ZONE DEFAULT NOW()
- updated_at: TIMESTAMP WITH TIME ZONE DEFAULT NOW()
```

#### 9. Database Migrations (`alembic_version`)
```sql
- version_num: VARCHAR(32) PRIMARY KEY
```

## Implementation Phases

### Phase 1: Docker Environment and Database Setup
1. **Docker Compose Setup**
   - Create `docker-compose.dev.yml` for development
   - Create `docker-compose.test.yml` for testing
   - Set up PostgreSQL 18 containers with UUIDv7 extension
   - Configure health checks and initialization scripts

2. **Database Configuration**
   - Configure SQLAlchemy for Docker environment
   - Set up connection pooling for development
   - Configure Alembic for Docker environment
   - Create database initialization scripts

3. **Development Scripts**
   - Create scripts to start/stop development database
   - Create scripts to reset development database
   - Create scripts to run database tests

### Phase 2: SQLAlchemy Setup and Infrastructure
1. **SQLAlchemy Configuration**
   - Install SQLAlchemy 2.0+ with async support
   - Configure async engine and session management
   - Set up connection pooling and retry logic
   - Configure for Docker environment

2. **Alembic Setup**
   - Initialize Alembic for migration management
   - Configure migration environment for Docker
   - Set up migration scripts
   - Create initial migration

3. **Base Infrastructure**
   - Create `BaseModel` with common fields (id, timestamps)
   - Implement UUIDv7 primary key generation
   - Add audit fields (created_at, updated_at)
   - Set up database session management

### Phase 3: Core Models Implementation
1. **Domain Models**
   - `AntibodySequence` model
   - `AntibodyChain` model
   - `AntibodyDomain` model
   - `AntibodyRegion` model
   - `SequenceFeature` model

2. **Processing Models**
   - `ProcessingJob` model
   - `ExternalToolResult` model

3. **Model Relationships**
   - Define foreign key relationships
   - Set up cascade behaviors
   - Configure eager loading strategies

### Phase 4: Repository Layer Implementation
1. **Base Repository Pattern**
   - Create `BaseRepository` with CRUD operations
   - Implement async repository methods
   - Add query optimization and pagination
   - Add transaction management

2. **Domain-Specific Repositories**
   - `AntibodySequenceRepository`
   - `AntibodyChainRepository`
   - `AntibodyDomainRepository`
   - `ProcessingJobRepository`

3. **Repository Integration**
   - Update existing services to use repositories
   - Implement transaction management
   - Add error handling and rollback logic

### Phase 5: Testing and Validation
1. **Database Testing Setup**
   - Set up test database container
   - Configure pytest for database testing
   - Create database fixtures and factories
   - Set up test data management

2. **Test Implementation**
   - Unit tests for models
   - Integration tests for repositories
   - Migration tests
   - Performance tests

3. **CI/CD Integration**
   - Update CI/CD pipeline for database testing
   - Add database container to GitHub Actions
   - Configure test database in CI/CD

### Phase 6: Migration and Data Management
1. **Initial Migration**
   - Create initial database schema
   - Add indexes for performance
   - Set up foreign key constraints
   - Test migration rollback

2. **Data Migration Strategy**
   - Plan migration from existing JSON files
   - Create data migration scripts
   - Validate data integrity
   - Test migration process

3. **Production Deployment**
   - Prepare production database setup
   - Create production migration scripts
   - Set up monitoring and backup

### Phase 7: Integration and Optimization
1. **Service Layer Integration**
   - Update `AnnotationService` to use database
   - Update `AlignmentService` to use database
   - Implement caching layer
   - Add database health checks

2. **Performance Optimization**
   - Add database indexes
   - Implement query optimization
   - Add connection pooling configuration
   - Monitor and tune performance

3. **Monitoring and Logging**
   - Add database performance monitoring
   - Implement query logging
   - Add health checks
   - Set up alerting

## File Structure

```
app/backend/
├── database/
│   ├── __init__.py
│   ├── config.py                 # Database configuration
│   ├── engine.py                 # SQLAlchemy engine setup
│   ├── session.py                # Session management
│   └── base.py                   # Base model classes
├── models/
│   ├── __init__.py
│   ├── antibody_sequence.py      # AntibodySequence model
│   ├── antibody_chain.py         # AntibodyChain model
│   ├── antibody_domain.py        # AntibodyDomain model
│   ├── antibody_region.py        # AntibodyRegion model
│   ├── sequence_feature.py       # SequenceFeature model
│   ├── processing_job.py         # ProcessingJob model
│   └── external_tool_result.py   # ExternalToolResult model
├── repositories/
│   ├── __init__.py
│   ├── base.py                   # Base repository
│   ├── antibody_sequence.py      # AntibodySequence repository
│   ├── antibody_chain.py         # AntibodyChain repository
│   ├── antibody_domain.py        # AntibodyDomain repository
│   └── processing_job.py         # ProcessingJob repository
├── migrations/
│   ├── env.py                    # Alembic environment
│   ├── script.py.mako            # Migration template
│   └── versions/                 # Migration files
├── tests/
│   ├── test_models.py            # Model tests
│   ├── test_repositories.py      # Repository tests
│   └── test_migrations.py        # Migration tests
└── scripts/
    ├── start_db.sh               # Start development database
    ├── stop_db.sh                # Stop development database
    ├── reset_db.sh               # Reset development database
    └── run_db_tests.sh           # Run database tests
```

## Docker Development Commands

### Database Management
```bash
# Start development database
docker-compose -f docker-compose.dev.yml up -d postgres

# Start test database
docker-compose -f docker-compose.dev.yml up -d postgres_test

# Stop databases
docker-compose -f docker-compose.dev.yml down

# Reset development database
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d postgres

# View database logs
docker-compose -f docker-compose.dev.yml logs postgres

# Connect to database
docker exec -it absequencealign-postgres-dev psql -U postgres -d absequencealign_dev
```

### Alembic Commands
```bash
# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Run migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Check migration status
alembic current
```

## Dependencies

```yaml
# requirements.txt additions
sqlalchemy>=2.0.0
asyncpg>=0.29.0
alembic>=1.13.0
psycopg2-binary>=2.9.0
uuid7>=0.1.0
pytest-asyncio>=0.21.0
pytest-postgresql>=4.1.0
```

## Configuration

```python
# database/config.py
import os
from typing import Dict, Any

DATABASE_CONFIG = {
    "development": {
        "host": "localhost",
        "port": 5432,
        "database": "absequencealign_dev",
        "username": "postgres",
        "password": "password",
        "pool_size": 20,
        "max_overflow": 30,
        "pool_timeout": 30,
        "pool_recycle": 3600,
    },
    "test": {
        "host": "localhost",
        "port": 5433,
        "database": "absequencealign_test",
        "username": "postgres",
        "password": "password",
        "pool_size": 5,
        "max_overflow": 10,
        "pool_timeout": 30,
        "pool_recycle": 3600,
    },
    "production": {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "database": os.getenv("DB_NAME", "absequencealign"),
        "username": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", ""),
        "pool_size": int(os.getenv("DB_POOL_SIZE", "20")),
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "30")),
        "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
        "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "3600")),
    }
}

def get_database_config(environment: str = "development") -> Dict[str, Any]:
    """Get database configuration for specified environment."""
    return DATABASE_CONFIG.get(environment, DATABASE_CONFIG["development"])
```

## Next Steps

1. **Review and approve this updated plan**
2. **Create Docker Compose configuration**
3. **Set up PostgreSQL 18 containers with UUIDv7**
4. **Install and configure SQLAlchemy and Alembic**
5. **Create base model classes**
6. **Implement core domain models**
7. **Set up repository layer**
8. **Create initial migration**
9. **Integrate with existing services**

This implementation will provide a solid foundation for persistent storage while maintaining our clean architecture principles and supporting future scalability requirements. The Docker-based approach ensures consistency across development and CI/CD environments.
