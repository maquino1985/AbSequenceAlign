#!/usr/bin/env python3
"""
Comprehensive performance benchmark for AbSequenceAlign operations.
Tests actual computational bottlenecks in antibody sequence analysis.
"""

import time
import sys
import statistics
import random
import string
from typing import List, Dict, Any, Tuple
import cProfile
import pstats
import io

# Import our core modules
from backend.domain.value_objects import AminoAcidSequence, RegionBoundary
from backend.domain.entities import AntibodySequence, AntibodyChain, AntibodyDomain
from backend.domain.models import ChainType, DomainType, RegionType, NumberingScheme
from backend.application.services.annotation_service import AnnotationService
from backend.application.services.alignment_service import AlignmentService


def generate_realistic_antibody_sequence() -> str:
    """Generate a realistic antibody sequence based on common patterns."""
    # Common antibody sequence patterns
    heavy_chain_pattern = "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMGWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCARDY"
    light_chain_pattern = "DIQMTQSPSSLSASVGDRVTITCRASQGIRNYLAWYQQKPGKAPKLLIYAASTLQSGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQRYNRAPYTFGQGTKVEIK"
    
    # Add some variation
    sequences = [heavy_chain_pattern, light_chain_pattern]
    base_seq = random.choice(sequences)
    
    # Add random mutations
    amino_acids = "ACDEFGHIKLMNPQRSTVWYX"
    mutated_seq = ""
    for char in base_seq:
        if random.random() < 0.1:  # 10% mutation rate
            mutated_seq += random.choice(amino_acids)
        else:
            mutated_seq += char
    
    return mutated_seq


def benchmark_sequence_parsing(sequences: List[str]) -> Dict[str, float]:
    """Benchmark sequence parsing and validation."""
    times = []
    
    for seq in sequences:
        start_time = time.perf_counter()
        
        # Parse sequence
        amino_acid_seq = AminoAcidSequence(seq)
        
        # Validate sequence
        length = len(amino_acid_seq)
        sequence_str = str(amino_acid_seq)
        upper_seq = amino_acid_seq.upper()
        
        # Count amino acids
        count_a = amino_acid_seq.count_amino_acid('A')
        count_g = amino_acid_seq.count_amino_acid('G')
        count_v = amino_acid_seq.count_amino_acid('V')
        
        # Extract substrings
        if length > 50:
            sub1 = amino_acid_seq.substring(0, 25)
            sub2 = amino_acid_seq.substring(25, 50)
            sub3 = amino_acid_seq.substring(length-25, length)
        
        end_time = time.perf_counter()
        times.append(end_time - start_time)
    
    return {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "min": min(times),
        "max": max(times),
        "std": statistics.stdev(times) if len(times) > 1 else 0
    }


def benchmark_domain_analysis(sequences: List[str]) -> Dict[str, float]:
    """Benchmark domain analysis operations."""
    times = []
    
    for seq in sequences:
        start_time = time.perf_counter()
        
        # Create sequence object
        amino_acid_seq = AminoAcidSequence(seq)
        
        # Simulate domain analysis
        domains = []
        seq_length = len(amino_acid_seq)
        
        # Create multiple domains
        if seq_length > 100:
            # Variable domain (first 100-120 residues)
            var_start = 0
            var_end = min(120, seq_length // 2)
            var_seq = amino_acid_seq.substring(var_start, var_end)
            var_domain = AntibodyDomain(
                domain_type=DomainType.VARIABLE,
                sequence=var_seq,
                numbering_scheme=NumberingScheme.IMGT
            )
            domains.append(var_domain)
            
            # Constant domain (remaining residues)
            if seq_length > var_end:
                const_seq = amino_acid_seq.substring(var_end, seq_length)
                const_domain = AntibodyDomain(
                    domain_type=DomainType.CONSTANT,
                    sequence=const_seq,
                    numbering_scheme=NumberingScheme.IMGT
                )
                domains.append(const_domain)
        
        # Analyze domain boundaries
        for domain in domains:
            domain_length = len(domain.sequence)
            domain_str = str(domain.sequence)
            domain_type = domain.domain_type
        
        end_time = time.perf_counter()
        times.append(end_time - start_time)
    
    return {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "min": min(times),
        "max": max(times),
        "std": statistics.stdev(times) if len(times) > 1 else 0
    }


def benchmark_chain_processing(sequences: List[str]) -> Dict[str, float]:
    """Benchmark chain processing operations."""
    times = []
    
    for i, seq in enumerate(sequences):
        start_time = time.perf_counter()
        
        # Create chain
        amino_acid_seq = AminoAcidSequence(seq)
        chain_type = ChainType.HEAVY if i % 2 == 0 else ChainType.LIGHT
        
        chain = AntibodyChain(
            name=f"Chain_{i}",
            chain_type=chain_type,
            sequence=amino_acid_seq
        )
        
        # Process chain
        chain_length = len(chain.sequence)
        chain_type_str = chain.chain_type.value
        chain_name = chain.name
        
        # Add domains to chain
        if chain_length > 100:
            # Split into domains
            mid_point = chain_length // 2
            var_seq = chain.sequence.substring(0, mid_point)
            const_seq = chain.sequence.substring(mid_point, chain_length)
            
            var_domain = AntibodyDomain(
                domain_type=DomainType.VARIABLE,
                sequence=var_seq,
                numbering_scheme=NumberingScheme.IMGT
            )
            
            const_domain = AntibodyDomain(
                domain_type=DomainType.CONSTANT,
                sequence=const_seq,
                numbering_scheme=NumberingScheme.IMGT
            )
            
            chain.domains = [var_domain, const_domain]
        
        end_time = time.perf_counter()
        times.append(end_time - start_time)
    
    return {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "min": min(times),
        "max": max(times),
        "std": statistics.stdev(times) if len(times) > 1 else 0
    }


def benchmark_antibody_assembly(sequences: List[str]) -> Dict[str, float]:
    """Benchmark antibody sequence assembly."""
    times = []
    
    # Process sequences in pairs (heavy + light chains)
    for i in range(0, len(sequences) - 1, 2):
        heavy_seq = sequences[i]
        light_seq = sequences[i + 1] if i + 1 < len(sequences) else sequences[0]
        
        start_time = time.perf_counter()
        
        # Create heavy chain
        heavy_amino_seq = AminoAcidSequence(heavy_seq)
        heavy_chain = AntibodyChain(
            name=f"Heavy_{i}",
            chain_type=ChainType.HEAVY,
            sequence=heavy_amino_seq
        )
        
        # Create light chain
        light_amino_seq = AminoAcidSequence(light_seq)
        light_chain = AntibodyChain(
            name=f"Light_{i}",
            chain_type=ChainType.LIGHT,
            sequence=light_amino_seq
        )
        
        # Assemble antibody
        antibody = AntibodySequence(
            name=f"Antibody_{i}",
            chains=[heavy_chain, light_chain]
        )
        
        # Analyze antibody
        total_chains = len(antibody.chains)
        total_length = sum(len(chain.sequence) for chain in antibody.chains)
        chain_types = [chain.chain_type.value for chain in antibody.chains]
        
        end_time = time.perf_counter()
        times.append(end_time - start_time)
    
    return {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "min": min(times),
        "max": max(times),
        "std": statistics.stdev(times) if len(times) > 1 else 0
    }


def benchmark_string_operations(sequences: List[str]) -> Dict[str, float]:
    """Benchmark string operations that are common in sequence analysis."""
    times = []
    
    for seq in sequences:
        start_time = time.perf_counter()
        
        # String operations
        upper_seq = seq.upper()
        lower_seq = seq.lower()
        
        # Count operations
        count_a = seq.count('A')
        count_g = seq.count('G')
        count_v = seq.count('V')
        count_c = seq.count('C')
        count_w = seq.count('W')
        
        # Find operations
        pos_a = seq.find('A')
        pos_g = seq.find('G')
        pos_v = seq.find('V')
        
        # Replace operations
        replaced_seq = seq.replace('X', 'A').replace('Z', 'G')
        
        # Split operations
        if len(seq) > 50:
            parts = [seq[i:i+10] for i in range(0, len(seq), 10)]
        
        # Join operations
        if len(seq) > 50:
            joined_seq = ''.join(parts)
        
        end_time = time.perf_counter()
        times.append(end_time - start_time)
    
    return {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "min": min(times),
        "max": max(times),
        "std": statistics.stdev(times) if len(times) > 1 else 0
    }


def run_comprehensive_benchmarks() -> Dict[str, Any]:
    """Run all comprehensive benchmarks."""
    print(f"Running comprehensive benchmarks with {sys.implementation.name} {sys.version}")
    print("=" * 80)
    
    # Create realistic test data
    print("Generating realistic antibody sequences...")
    sequences = [generate_realistic_antibody_sequence() for _ in range(50)]
    print(f"Generated {len(sequences)} realistic antibody sequences")
    
    results = {}
    
    # Benchmark 1: Sequence Parsing
    print("\nBenchmarking sequence parsing and validation...")
    results["sequence_parsing"] = benchmark_sequence_parsing(sequences)
    
    # Benchmark 2: Domain Analysis
    print("Benchmarking domain analysis...")
    results["domain_analysis"] = benchmark_domain_analysis(sequences)
    
    # Benchmark 3: Chain Processing
    print("Benchmarking chain processing...")
    results["chain_processing"] = benchmark_chain_processing(sequences)
    
    # Benchmark 4: Antibody Assembly
    print("Benchmarking antibody assembly...")
    results["antibody_assembly"] = benchmark_antibody_assembly(sequences)
    
    # Benchmark 5: String Operations
    print("Benchmarking string operations...")
    results["string_operations"] = benchmark_string_operations(sequences)
    
    return results


def print_comprehensive_results(results: Dict[str, Any]) -> None:
    """Print comprehensive benchmark results."""
    print("\n" + "=" * 80)
    print("COMPREHENSIVE BENCHMARK RESULTS")
    print("=" * 80)
    
    for benchmark_name, metrics in results.items():
        print(f"\n{benchmark_name.upper().replace('_', ' ')}:")
        print(f"  Mean:   {metrics['mean']:.6f}s")
        print(f"  Median: {metrics['median']:.6f}s")
        print(f"  Min:    {metrics['min']:.6f}s")
        print(f"  Max:    {metrics['max']:.6f}s")
        print(f"  Std:    {metrics['std']:.6f}s")


def profile_critical_path() -> None:
    """Profile the critical path of our application."""
    print("\n" + "=" * 80)
    print("PROFILING CRITICAL PATH")
    print("=" * 80)
    
    # Create a realistic antibody sequence
    seq = generate_realistic_antibody_sequence()
    
    # Profile the critical path
    pr = cProfile.Profile()
    pr.enable()
    
    # Simulate critical path
    amino_acid_seq = AminoAcidSequence(seq)
    chain = AntibodyChain(
        name="TestChain",
        chain_type=ChainType.HEAVY,
        sequence=amino_acid_seq
    )
    
    # Add domains
    if len(seq) > 100:
        var_seq = amino_acid_seq.substring(0, 100)
        const_seq = amino_acid_seq.substring(100, len(seq))
        
        var_domain = AntibodyDomain(
            domain_type=DomainType.VARIABLE,
            sequence=var_seq,
            numbering_scheme=NumberingScheme.IMGT
        )
        
        const_domain = AntibodyDomain(
            domain_type=DomainType.CONSTANT,
            sequence=const_seq,
            numbering_scheme=NumberingScheme.IMGT
        )
        
        chain.domains = [var_domain, const_domain]
    
    antibody = AntibodySequence(
        name="TestAntibody",
        chains=[chain]
    )
    
    pr.disable()
    
    # Print profiling results
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(20)  # Top 20 functions
    print(s.getvalue())


def main():
    """Main benchmark function."""
    try:
        # Run comprehensive benchmarks
        results = run_comprehensive_benchmarks()
        print_comprehensive_results(results)
        
        # Profile critical path
        profile_critical_path()
        
        # Save results
        import json
        from datetime import datetime
        
        result_data = {
            "timestamp": datetime.now().isoformat(),
            "python_implementation": sys.implementation.name,
            "python_version": sys.version,
            "platform": sys.platform,
            "results": results
        }
        
        filename = f"comprehensive_benchmark_{sys.implementation.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(result_data, f, indent=2)
        
        print(f"\nResults saved to: {filename}")
        
    except Exception as e:
        print(f"Benchmark failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
