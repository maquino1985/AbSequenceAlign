#!/usr/bin/env python3

# Test the CDR3 extraction from sub-region details
test_line = "CDR3    GCGAAAGTGAGCTATCTGAGCACCGCGAGCAGCCTGGATTAT      AKVSYLSTASSLDY  289     330"

parts = test_line.split()
print(f"Parts: {parts}")
print(f"Length: {len(parts)}")

if len(parts) >= 5 and parts[0] == "CDR3":
    cdr3_sequence = parts[1]
    cdr3_aa = parts[2] if len(parts) > 2 else None
    cdr3_start = int(parts[3]) if len(parts) > 3 else None
    cdr3_end = int(parts[4]) if len(parts) > 4 else None
    
    result = {
        "cdr3_sequence": cdr3_sequence,
        "cdr3_aa": cdr3_aa,
        "cdr3_start": cdr3_start,
        "cdr3_end": cdr3_end,
    }
    print(f"Extracted CDR3 data: {result}")
else:
    print("Failed to extract CDR3 data")
