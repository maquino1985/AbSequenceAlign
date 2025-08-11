#!/usr/bin/env python3
"""
Script to fix type annotation issues across the backend codebase.
This script will add missing type annotations and fix type-related issues.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set


def fix_annotation_response_service():
    """Fix type annotations in annotation_response_service.py"""
    file_path = "application/services/annotation_response_service.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix missing type annotations
    fixes = [
        # Fix chain_types type annotation
        (
            r'def _calculate_chain_types\(\s*self,\s*processor:\s*AnarciResultProcessor\s*\)\s*->\s*Dict\[str,\s*int\]:\s*"""Calculate chain type statistics from processor results\."""\s*chain_types = {}',
            r'def _calculate_chain_types(\n        self, processor: AnarciResultProcessor\n    ) -> Dict[str, int]:\n        """Calculate chain type statistics from processor results."""\n        chain_types: Dict[str, int] = {}'
        ),
        # Fix isotypes type annotation
        (
            r'def _calculate_isotypes\(\s*self,\s*processor:\s*AnarciResultProcessor\s*\)\s*->\s*Dict\[str,\s*int\]:\s*"""Calculate isotype statistics from processor results\."""\s*isotypes = {}',
            r'def _calculate_isotypes(\n        self, processor: AnarciResultProcessor\n    ) -> Dict[str, int]:\n        """Calculate isotype statistics from processor results."""\n        isotypes: Dict[str, int] = {}'
        ),
        # Fix species type annotation
        (
            r'def _calculate_species\(\s*self,\s*processor:\s*AnarciResultProcessor\s*\)\s*->\s*Dict\[str,\s*int\]:\s*"""Calculate species statistics from processor results\."""\s*species = {}',
            r'def _calculate_species(\n        self, processor: AnarciResultProcessor\n    ) -> Dict[str, int]:\n        """Calculate species statistics from processor results."""\n        species: Dict[str, int] = {}'
        ),
    ]
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed type annotations in {file_path}")


def fix_biologic_service():
    """Fix type annotations in biologic_service.py"""
    file_path = "application/services/biologic_service.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix missing type annotations
    fixes = [
        # Fix _cache type annotation in CachedBiologicServiceImpl
        (
            r'class CachedBiologicServiceImpl\(BiologicServiceImpl\):\s*"""Biologic service with caching capabilities\."""\s*def __init__\(\s*self,\s*repository:\s*BiologicRepository = None,\s*processor:\s*BiologicProcessor = None,\s*\):\s*super\(\)\.__init__\(repository,\s*processor\)\s*self\._cache = {}',
            r'class CachedBiologicServiceImpl(BiologicServiceImpl):\n    """Biologic service with caching capabilities."""\n\n    def __init__(\n        self,\n        repository: BiologicRepository = None,\n        processor: BiologicProcessor = None,\n    ):\n        super().__init__(repository, processor)\n        self._cache: Dict[str, BiologicResponse] = {}'
        ),
    ]
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed type annotations in {file_path}")


def fix_core_base_classes():
    """Fix type annotations in core/base_classes.py"""
    file_path = "core/base_classes.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix ProcessingStatus enum usage
    fixes = [
        # Fix _set_status calls to use ProcessingStatus enum
        (
            r'self\._set_status\("running"\)',
            r'self._set_status(ProcessingStatus.RUNNING)'
        ),
        (
            r'self\._set_status\("completed"\)',
            r'self._set_status(ProcessingStatus.COMPLETED)'
        ),
        (
            r'self\._set_status\("failed"\)',
            r'self._set_status(ProcessingStatus.FAILED)'
        ),
    ]
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed type annotations in {file_path}")


def fix_processing_service():
    """Fix type annotations in processing_service.py"""
    file_path = "application/services/processing_service.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix list append issues
    fixes = [
        # Fix append calls to use proper types
        (
            r'error_messages\.append\(\{"error":\s*str\(e\)\}\)',
            r'error_messages.append(str(e))'
        ),
        (
            r'warning_messages\.append\(\{"warning":\s*str\(e\)\}\)',
            r'warning_messages.append(str(e))'
        ),
    ]
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed type annotations in {file_path}")


def main():
    """Main function to fix type annotations across the backend."""
    print("Fixing type annotations...")
    
    # Fix specific files with known issues
    fix_annotation_response_service()
    fix_biologic_service()
    fix_core_base_classes()
    fix_processing_service()
    
    print("Type annotation fixes completed!")


if __name__ == "__main__":
    main()
