#!/usr/bin/env python3
"""
Script to clean up unused imports across the backend codebase.
This script will remove unused imports and fix import-related issues.
"""

import os
import ast
from pathlib import Path
from typing import Set, List, Tuple


def find_unused_imports(file_path: str) -> List[Tuple[str, int, str]]:
    """Find unused imports in a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Find all imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append((alias.name, node.lineno, 'import'))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    full_name = f"{module}.{alias.name}" if module else alias.name
                    imports.append((full_name, node.lineno, 'from'))
        
        # Find all names used in the code
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                # Handle attribute access like 'typing.List'
                parts = []
                current = node
                while isinstance(current, ast.Attribute):
                    parts.append(current.attr)
                    current = current.value
                if isinstance(current, ast.Name):
                    parts.append(current.id)
                    parts.reverse()
                    used_names.add('.'.join(parts))
        
        # Find unused imports
        unused = []
        for import_name, lineno, import_type in imports:
            # Extract the base name (last part after dot)
            base_name = import_name.split('.')[-1]
            if base_name not in used_names and import_name not in used_names:
                unused.append((import_name, lineno, import_type))
        
        return unused
    
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []


def clean_file_imports(file_path: str) -> bool:
    """Clean unused imports from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        unused_imports = find_unused_imports(file_path)
        if not unused_imports:
            return False
        
        # Sort by line number in reverse order to avoid line number shifts
        unused_imports.sort(key=lambda x: x[1], reverse=True)
        
        # Remove unused imports
        for import_name, lineno, import_type in unused_imports:
            if 0 < lineno <= len(lines):
                # Remove the line (convert to 0-based index)
                del lines[lineno - 1]
        
        # Write back the cleaned content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"Cleaned {len(unused_imports)} unused imports from {file_path}")
        return True
    
    except Exception as e:
        print(f"Error cleaning {file_path}: {e}")
        return False


def main():
    """Main function to clean up imports across the backend."""
    backend_dir = Path(__file__).parent.parent
    
    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk(backend_dir):
        # Skip certain directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'migrations']]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"Found {len(python_files)} Python files to check")
    
    cleaned_count = 0
    for file_path in python_files:
        if clean_file_imports(file_path):
            cleaned_count += 1
    
    print(f"\nCleaned imports from {cleaned_count} files")


if __name__ == "__main__":
    main()
