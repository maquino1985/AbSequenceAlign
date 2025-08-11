#!/usr/bin/env python3
"""
Script to fix type annotation issues across the backend codebase.
This script will add missing type annotations and fix type-related issues.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set


def fix_missing_imports():
    """Fix missing imports across the codebase"""
    
    # Fix domain entities
    fix_domain_entities()
    
    # Fix domain entities v2
    fix_domain_entities_v2()
    
    # Fix core base classes
    fix_core_base_classes()
    
    # Fix biologic strategies
    fix_biologic_strategies()
    
    # Fix annotation response service
    fix_annotation_response_service()
    
    # Fix biologic service
    fix_biologic_service()
    
    # Fix biologic repository
    fix_biologic_repository()
    
    # Fix processors
    fix_processors()
    
    # Fix factories
    fix_factories()
    
    # Fix converters
    fix_converters()
    
    # Fix MSA modules
    fix_msa_modules()
    
    # Fix API endpoints
    fix_api_endpoints()
    
    # Fix main.py
    fix_main_py()


def fix_domain_entities():
    """Fix missing imports in domain/entities.py"""
    file_path = "../domain/entities.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add missing imports
    if "from typing import TYPE_CHECKING" not in content:
        content = content.replace(
            "from typing import Dict, List, Optional, Any, Set, TYPE_CHECKING",
            "from typing import Dict, List, Optional, Any, Set, TYPE_CHECKING"
        )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed imports in {file_path}")


def fix_domain_entities_v2():
    """Fix missing imports in domain/entities_v2.py"""
    file_path = "../domain/entities_v2.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add missing imports at the top
    imports_to_add = """from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Set, Union, TYPE_CHECKING
"""
    
    if "from abc import ABC, abstractmethod" not in content:
        # Find the first import line and add before it
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('from ') or line.startswith('import '):
                lines.insert(i, imports_to_add.strip())
                break
        
        content = '\n'.join(lines)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed imports in {file_path}")


def fix_core_base_classes():
    """Fix missing imports in core/base_classes.py"""
    file_path = "../core/base_classes.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add missing imports
    imports_to_add = """from typing import List, Dict, Any, Generic, TypeVar, Optional, TypeVar
"""
    
    if "from typing import" not in content:
        # Find the first import line and add before it
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('from ') or line.startswith('import '):
                lines.insert(i, imports_to_add.strip())
                break
        
        content = '\n'.join(lines)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed imports in {file_path}")


def fix_biologic_strategies():
    """Fix missing imports in biologic_strategies.py"""
    file_path = "../application/strategies/biologic_strategies.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add missing imports
    imports_to_add = """import uuid
from typing import List, Dict, Any, Optional
"""
    
    if "import uuid" not in content:
        # Find the first import line and add before it
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('from ') or line.startswith('import '):
                lines.insert(i, imports_to_add.strip())
                break
        
        content = '\n'.join(lines)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed imports in {file_path}")


def fix_annotation_response_service():
    """Fix missing imports in annotation_response_service.py"""
    file_path = "../application/services/annotation_response_service.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add missing imports
    imports_to_add = """from typing import Dict, Any, List
"""
    
    if "from typing import Dict, Any, List" not in content:
        # Find the first import line and add before it
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('from ') or line.startswith('import '):
                lines.insert(i, imports_to_add.strip())
                break
        
        content = '\n'.join(lines)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed imports in {file_path}")


def fix_biologic_service():
    """Fix missing imports in biologic_service.py"""
    file_path = "../application/services/biologic_service.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add missing imports
    imports_to_add = """from backend.models.biologic_models import (
    BiologicCreate,
    BiologicResponse,
    BiologicUpdate,
)
from backend.database.models import Biologic
"""
    
    if "from backend.models.biologic_models import" not in content:
        # Find the first import line and add before it
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('from ') or line.startswith('import '):
                lines.insert(i, imports_to_add.strip())
                break
        
        content = '\n'.join(lines)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed imports in {file_path}")


def fix_biologic_repository():
    """Fix missing imports in biologic_repository.py"""
    file_path = "../infrastructure/repositories/biologic_repository.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add missing imports
    imports_to_add = """from sqlalchemy import select, and_
from backend.logger import logger
"""
    
    if "from sqlalchemy import select, and_" not in content:
        # Find the first import line and add before it
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('from ') or line.startswith('import '):
                lines.insert(i, imports_to_add.strip())
                break
        
        content = '\n'.join(lines)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed imports in {file_path}")


def fix_processors():
    """Fix missing imports in processor files"""
    files = [
        "../application/processors/strategy_biologic_processor.py",
        "../application/processors/biologic_processor.py"
    ]
    
    for file_path in files:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Add missing imports
        imports_to_add = """from typing import Dict, Any, Optional, List
from backend.core.exceptions import ValidationError
from backend.domain.entities import BiologicEntity
from backend.core.base_classes import AbstractBiologicProcessor
"""
        
        if "from backend.core.exceptions import ValidationError" not in content:
            # Find the first import line and add before it
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('from ') or line.startswith('import '):
                    lines.insert(i, imports_to_add.strip())
                    break
            
            content = '\n'.join(lines)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"Fixed imports in {file_path}")


def fix_factories():
    """Fix missing imports in factory files"""
    file_path = "../application/factories/biologic_factory.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add missing imports
    imports_to_add = """from typing import List, Dict, Any, Optional
"""
    
    if "from typing import List, Dict, Any, Optional" not in content:
        # Find the first import line and add before it
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('from ') or line.startswith('import '):
                lines.insert(i, imports_to_add.strip())
                break
        
        content = '\n'.join(lines)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed imports in {file_path}")


def fix_converters():
    """Fix missing imports in converter files"""
    file_path = "../application/converters/validation_biologic_converter.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add missing imports
    imports_to_add = """from typing import Dict, Any, List
"""
    
    if "from typing import Dict, Any, List" not in content:
        # Find the first import line and add before it
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('from ') or line.startswith('import '):
                lines.insert(i, imports_to_add.strip())
                break
        
        content = '\n'.join(lines)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed imports in {file_path}")


def fix_msa_modules():
    """Fix missing imports in MSA modules"""
    files = [
        "../msa/pssm_calculator.py",
        "../msa/msa_annotation.py",
        "../msa/msa_engine.py"
    ]
    
    for file_path in files:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Add missing imports
        if "pssm_calculator" in file_path:
            imports_to_add = """import numpy as np
"""
        elif "msa_annotation" in file_path:
            imports_to_add = """from typing import Dict, Any, List
"""
        elif "msa_engine" in file_path:
            imports_to_add = """from typing import Dict, Any, List
"""
        
        if "import numpy as np" not in content and "pssm_calculator" in file_path:
            # Find the first import line and add before it
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('from ') or line.startswith('import '):
                    lines.insert(i, imports_to_add.strip())
                    break
            
            content = '\n'.join(lines)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"Fixed imports in {file_path}")


def fix_api_endpoints():
    """Fix missing imports in API endpoints"""
    files = [
        "../api/v1/endpoints.py",
        "../api/v2/endpoints.py"
    ]
    
    for file_path in files:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Add missing imports
        if "v2" in file_path:
            imports_to_add = """from backend.models.models_v2 import V2AnnotationResult
"""
        else:
            imports_to_add = """from backend.models.models import AnnotationResult
"""
        
        if "V2AnnotationResult" not in content and "v2" in file_path:
            # Find the first import line and add before it
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('from ') or line.startswith('import '):
                    lines.insert(i, imports_to_add.strip())
                    break
            
            content = '\n'.join(lines)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"Fixed imports in {file_path}")


def fix_main_py():
    """Fix missing imports in main.py"""
    file_path = "../main.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add missing imports
    imports_to_add = """from backend.api.v1.endpoints import router as api_v1_router
from backend.api.v2.endpoints import router as api_v2_router
from backend.api.v2.database_endpoints import router as database_router
"""
    
    if "api_v1_router" not in content:
        # Find the first import line and add before it
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('from ') or line.startswith('import '):
                lines.insert(i, imports_to_add.strip())
                break
        
        content = '\n'.join(lines)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed imports in {file_path}")


def main():
    """Main function to fix type annotations across the backend."""
    print("Fixing type annotations and missing imports...")
    
    # Fix missing imports
    fix_missing_imports()
    
    print("Type annotation fixes completed!")


if __name__ == "__main__":
    main()
