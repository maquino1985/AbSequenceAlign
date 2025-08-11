-- Database initialization script for AbSequenceAlign
-- This script sets up the database with UUIDv7 support and initial configuration

-- Enable UUID extension for UUIDv7 support
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom UUIDv7 function (simplified for PostgreSQL 15)
CREATE OR REPLACE FUNCTION uuid_generate_v7()
RETURNS uuid
AS $$
BEGIN
  -- For now, use uuid-ossp's uuid_generate_v4() as a placeholder
  -- We'll implement proper UUIDv7 when we upgrade to PostgreSQL 18+
  RETURN uuid_generate_v4();
END;
$$ LANGUAGE plpgsql;

-- Create custom enum types for our domain
CREATE TYPE chain_type_enum AS ENUM ('HEAVY', 'LIGHT', 'SINGLE_CHAIN');
CREATE TYPE domain_type_enum AS ENUM ('VARIABLE', 'CONSTANT', 'JOINING');
CREATE TYPE numbering_scheme_enum AS ENUM ('IMGT', 'KABAT', 'CHOTHIA');
CREATE TYPE region_type_enum AS ENUM ('FR1', 'CDR1', 'FR2', 'CDR2', 'FR3', 'CDR3', 'FR4');
CREATE TYPE feature_type_enum AS ENUM ('GENE', 'ALLELE', 'ISOTYPE', 'MUTATION', 'POST_TRANSLATIONAL');
CREATE TYPE job_type_enum AS ENUM ('ANNOTATION', 'ALIGNMENT', 'ANALYSIS');
CREATE TYPE job_status_enum AS ENUM ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED');

-- Create a function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Database initialization completed successfully';
    RAISE NOTICE 'UUIDv7 function created: uuid_generate_v7()';
    RAISE NOTICE 'Enum types created for domain modeling';
    RAISE NOTICE 'Updated timestamp trigger function created';
END $$;
