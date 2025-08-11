#!/usr/bin/env python3
"""
Script to fix ProcessingResult usage in test files.
"""

import re

def fix_file(filename):
    """Fix ProcessingResult usage in a file"""
    with open(filename, 'r') as f:
        content = f.read()
    
    # Replace ProcessingResult with message parameter
    content = re.sub(
        r'ProcessingResult\(\s*success=True,\s*data=([^,]+),\s*message="([^"]+)"\s*\)',
        r'ProcessingResult(success=True, data=\1)',
        content
    )
    content = re.sub(
        r'ProcessingResult\(\s*success=False,\s*data=None,\s*message="([^"]+)"\s*\)',
        r'ProcessingResult(success=False, data=None, error="\1")',
        content
    )
    
    with open(filename, 'w') as f:
        f.write(content)
    
    print(f"Fixed {filename}")

# Fix all test files
test_files = [
    'app/backend/tests/test_handlers.py',
    'app/backend/tests/test_services.py',
    'app/backend/tests/test_command_pattern_integration.py'
]

for file in test_files:
    fix_file(file)

print("All ProcessingResult issues fixed!")
