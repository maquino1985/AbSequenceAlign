#!/usr/bin/env python3
"""
Performance benchmark script to compare CPython vs PyPy for AbSequenceAlign operations.
"""

import time
import sys
import statistics
from typing import List, Dict, Any
import random
import string

# Import our core modules
from backend.domain.value_objects import AminoAcidSequence, RegionBoundary
from backend.domain.entities import AntibodySequence, AntibodyChain, AntibodyDomain
from backend.domain.models import ChainType, DomainType, RegionType, NumberingScheme
from backend.application.services.annotation_service import AnnotationService
from backend.application.services.alignment_service import AlignmentService


def generate_random_sequence(length: int) -> str:
    """Generate a random amino acid sequence."""
    amino_acids = "ACDEFGHIKLMNPQRSTVWYX"
    return ''.join(random.choice(amino_acids) for _ in range(length))


def create_test_sequences(count: int, min_length: int = 100, max_length: int = 500) -> List[str]:
    """Create a list of test sequences."""
    sequences = []
    for i in range(count):
        length = random.randint(min_length, max_length)
        sequences.append(generate_random_sequence(length))
    return sequences


def benchmark_sequence_creation(sequences: List[str]) -> Dict[str, float]:
    """Benchmark sequence object creation."""
    times = []
    
    for seq in sequences:
        start_time = time.perf_counter()
        
        # Create value objects
        amino_acid_seq = AminoAcidSequence(seq)
        boundary = RegionBoundary(0, len(seq) - 1)
        
        # Create domain entities
        domain = AntibodyDomain(
            domain_type=DomainType.VARIABLE,
            sequence=amino_acid_seq,
            numbering_scheme=NumberingScheme.IMGT
        )
        
        chain = AntibodyChain(
            name=f"TestChain_{len(times)}",
            chain_type=ChainType.HEAVY,
            sequence=amino_acid_seq
        )
        
        antibody_seq = AntibodySequence(
            name=f"TestSequence_{len(times)}",
            chains=[chain]
        )
        
        end_time = time.perf_counter()
        times.append(end_time - start_time)
    
    return {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "min": min(times),
        "max": max(times),
        "std": statistics.stdev(times) if len(times) > 1 else 0
    }


def benchmark_sequence_validation(sequences: List[str]) -> Dict[str, float]:
    """Benchmark sequence validation operations."""
    times = []
    
    for seq in sequences:
        start_time = time.perf_counter()
        
        # Validate sequence
        amino_acid_seq = AminoAcidSequence(seq)
        
        # Test various operations
        length = len(amino_acid_seq)
        sequence_str = str(amino_acid_seq)
        upper_seq = amino_acid_seq.upper()
        count_a = amino_acid_seq.count_amino_acid('A')
        
        end_time = time.perf_counter()
        times.append(end_time - start_time)
    
    return {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "min": min(times),
        "max": max(times),
        "std": statistics.stdev(times) if len(times) > 1 else 0
    }


def benchmark_alignment_operations(sequences: List[str]) -> Dict[str, float]:
    """Benchmark alignment operations."""
    times = []
    
    # Use pairs of sequences for alignment
    for i in range(0, len(sequences) - 1, 2):
        seq1 = sequences[i]
        seq2 = sequences[i + 1] if i + 1 < len(sequences) else sequences[0]
        
        start_time = time.perf_counter()
        
        # Create alignment service
        alignment_service = AlignmentService()
        
        # Simulate alignment operations
        # (Note: This is a simplified benchmark since we don't want to run actual external tools)
        seq1_obj = AminoAcidSequence(seq1)
        seq2_obj = AminoAcidSequence(seq2)
        
        # Test sequence operations
        len1 = len(seq1_obj)
        len2 = len(seq2_obj)
        combined_length = len1 + len2
        
        end_time = time.perf_counter()
        times.append(end_time - start_time)
    
    return {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "min": min(times),
        "max": max(times),
        "std": statistics.stdev(times) if len(times) > 1 else 0
    }


def run_benchmarks() -> Dict[str, Any]:
    """Run all benchmarks and return results."""
    print(f"Running benchmarks with {sys.implementation.name} {sys.version}")
    print("=" * 60)
    
    # Create test data
    print("Generating test sequences...")
    sequences = create_test_sequences(100, 200, 400)
    print(f"Generated {len(sequences)} test sequences")
    
    results = {}
    
    # Benchmark 1: Sequence Creation
    print("\nBenchmarking sequence creation...")
    results["sequence_creation"] = benchmark_sequence_creation(sequences)
    
    # Benchmark 2: Sequence Validation
    print("Benchmarking sequence validation...")
    results["sequence_validation"] = benchmark_sequence_validation(sequences)
    
    # Benchmark 3: Alignment Operations
    print("Benchmarking alignment operations...")
    results["alignment_operations"] = benchmark_alignment_operations(sequences)
    
    return results


def print_results(results: Dict[str, Any]) -> None:
    """Print benchmark results in a formatted way."""
    print("\n" + "=" * 60)
    print("BENCHMARK RESULTS")
    print("=" * 60)
    
    for benchmark_name, metrics in results.items():
        print(f"\n{benchmark_name.upper().replace('_', ' ')}:")
        print(f"  Mean:   {metrics['mean']:.6f}s")
        print(f"  Median: {metrics['median']:.6f}s")
        print(f"  Min:    {metrics['min']:.6f}s")
        print(f"  Max:    {metrics['max']:.6f}s")
        print(f"  Std:    {metrics['std']:.6f}s")


def main():
    """Main benchmark function."""
    try:
        results = run_benchmarks()
        print_results(results)
        
        # Save results to file for comparison
        import json
        from datetime import datetime
        
        result_data = {
            "timestamp": datetime.now().isoformat(),
            "python_implementation": sys.implementation.name,
            "python_version": sys.version,
            "platform": sys.platform,
            "results": results
        }
        
        filename = f"benchmark_results_{sys.implementation.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(result_data, f, indent=2)
        
        print(f"\nResults saved to: {filename}")
        
    except Exception as e:
        print(f"Benchmark failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
