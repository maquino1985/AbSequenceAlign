#!/usr/bin/env python3
"""
Comprehensive script to fix mypy errors across the backend codebase.
This script addresses import issues, missing type annotations, and other mypy-related problems.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple


def fix_import_paths():
    """Fix import paths to use absolute imports consistently"""

    # Files that need import path fixes
    import_fixes = {
        # Pipeline files
        "application/pipelines/alignment_pipeline.py": [
            (
                r"from \.core\.exceptions import",
                "from backend.core.exceptions import",
            ),
            (
                r"from \.domain\.models import",
                "from backend.domain.models import",
            ),
        ],
        "application/pipelines/enhanced_annotation_pipeline.py": [
            (
                r"from \.core\.base_classes import",
                "from backend.core.base_classes import",
            ),
            (
                r"from \.core\.interfaces import",
                "from backend.core.interfaces import",
            ),
            (
                r"from \.domain\.models import",
                "from backend.domain.models import",
            ),
            (
                r"from \.domain\.entities import",
                "from backend.domain.entities import",
            ),
        ],
        # Service files
        "application/services/alignment_service.py": [
            (
                r"from \.core\.base_classes import",
                "from backend.core.base_classes import",
            ),
            (
                r"from \.core\.interfaces import",
                "from backend.core.interfaces import",
            ),
            (
                r"from \.core\.exceptions import",
                "from backend.core.exceptions import",
            ),
            (
                r"from \.domain\.entities import",
                "from backend.domain.entities import",
            ),
            (r"from \.logger import", "from backend.logger import"),
        ],
        # Annotation files
        "annotation/annotation_engine.py": [
            (
                r"from \.models\.models import",
                "from backend.models.models import",
            ),
        ],
        "annotation/alignment_engine.py": [
            (
                r"from backend\.models\.models import",
                "from backend.models.models import",
            ),
        ],
        "annotation/sequence_processor.py": [
            (r"from \.logger import", "from backend.logger import"),
        ],
        # MSA files
        "msa/msa_engine.py": [
            (
                r"from \.models\.models import",
                "from backend.models.models import",
            ),
        ],
    }

    for file_path, replacements in import_fixes.items():
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                content = f.read()

            for pattern, replacement in replacements:
                content = re.sub(pattern, replacement, content)

            with open(file_path, "w") as f:
                f.write(content)
            print(f"Fixed imports in {file_path}")


def add_missing_type_annotations():
    """Add missing type annotations to functions"""

    # Files that need type annotation fixes
    type_annotation_fixes = {
        # Pipeline files
        "application/pipelines/alignment_pipeline.py": [
            (
                r"def _setup_pipeline\(self\):",
                "def _setup_pipeline(self) -> None:",
            ),
            (
                r"def _validate_sequences\(self, sequences\):",
                "def _validate_sequences(self, sequences: List) -> List:",
            ),
            (
                r"def _prepare_sequences\(self, sequences\):",
                "def _prepare_sequences(self, sequences: List) -> List:",
            ),
            (
                r"def _perform_alignment\(self, sequences\):",
                "def _perform_alignment(self, sequences: List) -> Dict[str, Any]:",
            ),
            (
                r"def _process_alignment_result\(self, result\):",
                "def _process_alignment_result(self, result: Dict[str, Any]) -> Any:",
            ),
        ],
        # Service files
        "application/services/alignment_service.py": [
            (r"def __init__\(self\):", "def __init__(self) -> None:"),
            (
                r"def align_sequences\(self, sequences, algorithm",
                "def align_sequences(self, sequences: List, algorithm",
            ),
            (
                r"def _validate_sequences\(self, sequences\):",
                "def _validate_sequences(self, sequences: List) -> List:",
            ),
            (
                r"def _prepare_sequences\(self, sequences\):",
                "def _prepare_sequences(self, sequences: List) -> List:",
            ),
            (
                r"def _perform_alignment\(self, sequences, algorithm",
                "def _perform_alignment(self, sequences: List, algorithm",
            ),
            (
                r"def _process_alignment_result\(self, result\):",
                "def _process_alignment_result(self, result: Dict[str, Any]) -> Any:",
            ),
        ],
        # MSA files
        "msa/pssm_calculator.py": [
            (r"def __init__\(self\):", "def __init__(self) -> None:"),
        ],
    }

    for file_path, replacements in type_annotation_fixes.items():
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                content = f.read()

            for pattern, replacement in replacements:
                content = re.sub(pattern, replacement, content)

            with open(file_path, "w") as f:
                f.write(content)
            print(f"Added type annotations in {file_path}")


def fix_variable_annotations():
    """Add missing variable type annotations"""

    # Files that need variable annotation fixes
    variable_annotation_fixes = {
        "annotation/annotation_engine.py": [
            (r"chain_types = \{\}", "chain_types: Dict[str, str] = {}"),
            (r"isotypes = \{\}", "isotypes: Dict[str, str] = {}"),
            (r"species_counts = \{\}", "species_counts: Dict[str, int] = {}"),
        ],
        "msa/pssm_calculator.py": [
            (r"aa_counts = \{\}", "aa_counts: Dict[str, int] = {}"),
        ],
    }

    for file_path, replacements in variable_annotation_fixes.items():
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                content = f.read()

            for pattern, replacement in replacements:
                content = re.sub(pattern, replacement, content)

            with open(file_path, "w") as f:
                f.write(content)
            print(f"Added variable annotations in {file_path}")


def fix_test_files():
    """Fix test files by adding missing imports and type annotations"""

    # Add missing imports to test files
    test_import_fixes = {
        "tests/test_phase4_infrastructure_layer.py": [
            "from unittest.mock import Mock, patch, AsyncMock",
            "from backend.domain.models import ChainType, DomainType, NumberingScheme, RegionType",
        ],
        "tests/test_phase3_application_layer.py": [
            "from backend.domain.models import NumberingScheme, DomainType",
            "from backend.core.exceptions import ProcessingError",
        ],
        "tests/test_integration_full_architecture.py": [
            "from unittest.mock import Mock",
            "from backend.domain.models import ChainType",
            "from backend.core.exceptions import ValidationError",
        ],
        "tests/test_domain_refactoring.py": [
            "from backend.core.exceptions import ValidationError",
        ],
        "tests/test_biologic_integration.py": [
            "from unittest.mock import AsyncMock",
        ],
    }

    for file_path, imports in test_import_fixes.items():
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                content = f.read()

            # Add imports after existing imports
            import_section = content.split("\n\n")[0]
            for import_stmt in imports:
                if import_stmt not in import_section:
                    import_section += f"\n{import_stmt}"

            content = content.replace(content.split("\n\n")[0], import_section)

            with open(file_path, "w") as f:
                f.write(content)
            print(f"Fixed imports in {file_path}")


def fix_main_py():
    """Fix main.py import issues"""

    if os.path.exists("main.py"):
        with open("main.py", "r") as f:
            content = f.read()

        # Add missing imports
        content = content.replace(
            "from fastapi import FastAPI",
            """from fastapi import FastAPI
from api.v1.endpoints import router as api_v1_router
from api.v2.endpoints import router as api_v2_router
from api.v2.database_endpoints import router as database_router""",
        )

        with open("main.py", "w") as f:
            f.write(content)
        print("Fixed main.py imports")


def fix_database_models():
    """Fix database model import issues"""

    # Fix seed_data.py imports
    if os.path.exists("database/seed_data.py"):
        with open("database/seed_data.py", "r") as f:
            content = f.read()

        content = content.replace(
            "from .models import (", "from backend.domain.models import ("
        )

        with open("database/seed_data.py", "w") as f:
            f.write(content)
        print("Fixed database/seed_data.py imports")


def create_missing_init_files():
    """Create missing __init__.py files to fix module import issues"""

    missing_init_dirs = [
        "core",
        "domain",
        "application",
        "application/services",
        "application/pipelines",
        "application/pipelines/steps",
        "application/factories",
        "application/processors",
        "application/strategies",
        "application/converters",
        "infrastructure",
        "infrastructure/adapters",
        "infrastructure/repositories",
        "models",
        "api",
        "api/v1",
        "api/v2",
        "annotation",
        "msa",
        "utils",
        "jobs",
        "presentation",
        "presentation/controllers",
        "presentation/dto",
    ]

    for dir_path in missing_init_dirs:
        init_file = Path(dir_path) / "__init__.py"
        if not init_file.exists():
            init_file.parent.mkdir(parents=True, exist_ok=True)
            init_file.touch()
            print(f"Created {init_file}")


def main():
    """Run all mypy fixes"""
    print("🔧 Starting comprehensive mypy error fixes...")

    # Create missing __init__.py files
    print("\n📁 Creating missing __init__.py files...")
    create_missing_init_files()

    # Fix import paths
    print("\n🔗 Fixing import paths...")
    fix_import_paths()

    # Add missing type annotations
    print("\n📝 Adding missing type annotations...")
    add_missing_type_annotations()

    # Fix variable annotations
    print("\n🏷️ Fixing variable annotations...")
    fix_variable_annotations()

    # Fix test files
    print("\n🧪 Fixing test files...")
    fix_test_files()

    # Fix main.py
    print("\n🏠 Fixing main.py...")
    fix_main_py()

    # Fix database models
    print("\n🗄️ Fixing database models...")
    fix_database_models()

    print("\n✅ Mypy error fixes completed!")
    print("\n💡 Next steps:")
    print("1. Run: conda run -n AbSequenceAlign mypy . --show-error-codes")
    print("2. Address any remaining errors manually")
    print("3. Run tests to ensure nothing was broken")


if __name__ == "__main__":
    main()
