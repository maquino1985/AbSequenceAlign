"""
Database configuration for AbSequenceAlign.
Handles configuration for different environments (development, test, production).
"""

import os
from typing import Dict, Any, Optional


class DatabaseConfig:
    """Database configuration class."""

    def __init__(self, environment: str = None):
        self.environment = environment or os.getenv(
            "ENVIRONMENT", "development"
        )
        self.config = self._get_config()

    def _get_config(self) -> Dict[str, Any]:
        """Get database configuration for the specified environment."""
        configs = {
            "development": {
                "host": os.getenv("DB_HOST", "localhost"),
                "port": int(os.getenv("DB_PORT", "5433")),
                "database": os.getenv("DB_NAME", "absequencealign_dev"),
                "username": os.getenv("DB_USER", "postgres"),
                "password": os.getenv("DB_PASSWORD", "password"),
                "pool_size": int(os.getenv("DB_POOL_SIZE", "20")),
                "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "30")),
                "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
                "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "3600")),
                "echo": os.getenv("DB_ECHO", "true").lower()
                == "true",  # Log SQL statements
                "echo_pool": os.getenv("DB_ECHO_POOL", "false").lower()
                == "true",
            },
            "test": {
                "host": os.getenv("DB_HOST", "localhost"),
                "port": int(os.getenv("DB_PORT", "5433")),
                "database": os.getenv(
                    "DB_NAME", "absequencealign_test"
                ),  # Allow override for test environment
                "username": os.getenv("DB_USER", "postgres"),
                "password": os.getenv("DB_PASSWORD", "password"),
                "pool_size": 5,  # Smaller pool for tests
                "max_overflow": 10,
                "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
                "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "3600")),
                "echo": False,  # Don't log SQL in tests
                "echo_pool": False,
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
                "echo": False,  # Don't log SQL in production
                "echo_pool": False,
            },
        }

        return configs.get(self.environment, configs["development"])

    def get_database_url(self) -> str:
        """Get the database URL for SQLAlchemy."""
        config = self.config
        return (
            f"postgresql+asyncpg://{config['username']}:{config['password']}"
            f"@{config['host']}:{config['port']}/{config['database']}"
        )

    def get_sync_database_url(self) -> str:
        """Get the synchronous database URL for Alembic."""
        config = self.config
        return (
            f"postgresql://{config['username']}:{config['password']}"
            f"@{config['host']}:{config['port']}/{config['database']}"
        )

    def get_engine_kwargs(self) -> Dict[str, Any]:
        """Get engine configuration kwargs."""
        config = self.config
        return {
            "pool_size": config["pool_size"],
            "max_overflow": config["max_overflow"],
            "pool_timeout": config["pool_timeout"],
            "pool_recycle": config["pool_recycle"],
            "echo": config["echo"],
            "echo_pool": config["echo_pool"],
        }


# Global configuration instances
development_config = DatabaseConfig("development")
test_config = DatabaseConfig("test")
production_config = DatabaseConfig("production")


def get_database_config(environment: Optional[str] = None) -> DatabaseConfig:
    """Get database configuration for specified environment."""
    if environment is None:
        environment = os.getenv("ENVIRONMENT", "development")

    if environment == "production":
        return production_config
    elif environment == "test":
        return test_config
    else:
        return development_config


# Convenience functions
def get_database_url(environment: Optional[str] = None) -> str:
    """Get database URL for specified environment."""
    config = get_database_config(environment)
    return config.get_database_url()


def get_sync_database_url(environment: Optional[str] = None) -> str:
    """Get synchronous database URL for specified environment."""
    config = get_database_config(environment)
    return config.get_sync_database_url()


def get_engine_kwargs(environment: Optional[str] = None) -> Dict[str, Any]:
    """Get engine kwargs for specified environment."""
    config = get_database_config(environment)
    return config.get_engine_kwargs()
