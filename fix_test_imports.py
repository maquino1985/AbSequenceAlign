#!/usr/bin/env python3
"""
Script to fix BiologicType imports in test files.
"""

import re

def fix_file(filename):
    """Fix BiologicType imports in a file"""
    with open(filename, 'r') as f:
        content = f.read()
    
    # Remove BiologicType from imports
    content = re.sub(
        r'from backend\.domain\.models import BiologicType, (.*)',
        r'from backend.domain.models import \1',
        content
    )
    content = re.sub(
        r'from backend\.domain\.models import (.*), BiologicType',
        r'from backend.domain.models import \1',
        content
    )
    
    # Replace BiologicType.ANTIBODY with "antibody"
    content = content.replace('BiologicType.ANTIBODY', '"antibody"')
    
    with open(filename, 'w') as f:
        f.write(content)
    
    print(f"Fixed {filename}")

# Fix all test files
test_files = [
    'app/backend/tests/test_commands.py',
    'app/backend/tests/test_handlers.py', 
    'app/backend/tests/test_services.py',
    'app/backend/tests/test_command_pattern_integration.py'
]

for file in test_files:
    fix_file(file)

print("All test files fixed!")
