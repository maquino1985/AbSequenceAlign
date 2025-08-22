#!/usr/bin/env python3

import subprocess
import tempfile
import os

def test_blast_command():
    # Test the exact command our adapter would run
    query_sequence = "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
    blast_type = "blastp"
    database = "swissprot"
    evalue = 10
    
    # Build the command exactly as our adapter does
    temp_file = f"/tmp/query_{os.getpid()}.fasta"
    blast_cmd = f"{blast_type} -query {temp_file} -db {database} -evalue {evalue} -outfmt '6 qseq sseq'"
    
    command = [
        "docker",
        "exec",
        "absequencealign-blast",
        "bash",
        "-c",
        f"echo -e '>query\\n{query_sequence}' > {temp_file} && {blast_cmd} && rm {temp_file}"
    ]
    
    print(f"Command: {' '.join(command)}")
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print(f"Return code: {result.returncode}")
        print(f"Stdout length: {len(result.stdout)}")
        print(f"Stderr: {result.stderr}")
        print(f"First 500 chars of stdout: {result.stdout[:500]}")
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            print(f"Number of output lines: {len(lines)}")
            if lines:
                print(f"First line: {lines[0]}")
                print(f"Fields in first line: {len(lines[0].split(chr(9)))}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_blast_command()
