#!/usr/bin/env python3
"""
Database Analysis Script

This script analyzes the current IgBLAST and BLAST database structure
to identify essential databases and redundancies.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Set
import re

def analyze_igblast_databases(data_dir: Path) -> Dict:
    """Analyze IgBLAST databases and identify patterns."""
    igblast_dir = data_dir / "igblast" / "internal_data"
    
    if not igblast_dir.exists():
        print(f"IgBLAST directory not found: {igblast_dir}")
        return {}
    
    # Find all .nhr files (database index files)
    nhr_files = list(igblast_dir.rglob("*.nhr"))
    
    databases = {
        "total_count": len(nhr_files),
        "by_organism": {},
        "by_gene_type": {},
        "duplicates": [],
        "redundant_mouse_strains": [],
        "essential_databases": []
    }
    
    # Analyze each database
    for nhr_file in nhr_files:
        db_name = nhr_file.stem
        relative_path = nhr_file.relative_to(igblast_dir)
        
        # Determine organism and gene type
        organism, gene_type = parse_database_name(db_name, relative_path)
        
        if organism and gene_type:
            if organism not in databases["by_organism"]:
                databases["by_organism"][organism] = {}
            if gene_type not in databases["by_organism"][organism]:
                databases["by_organism"][organism][gene_type] = []
            
            databases["by_organism"][organism][gene_type].append({
                "name": db_name,
                "path": str(relative_path),
                "full_path": str(nhr_file)
            })
            
            # Track by gene type
            if gene_type not in databases["by_gene_type"]:
                databases["by_gene_type"][gene_type] = []
            databases["by_gene_type"][gene_type].append({
                "name": db_name,
                "organism": organism,
                "path": str(relative_path)
            })
    
    # Identify duplicates and redundancies
    identify_duplicates_and_redundancies(databases)
    
    # Identify essential databases
    identify_essential_databases(databases)
    
    return databases

def parse_database_name(db_name: str, relative_path: Path) -> tuple:
    """Parse database name to determine organism and gene type."""
    organism = None
    gene_type = None
    
    # Check for gene type patterns
    if db_name.endswith(('_V', '.V')):
        gene_type = 'V'
    elif db_name.endswith(('_D', '.D')):
        gene_type = 'D'
    elif db_name.endswith(('_J', '.J')):
        gene_type = 'J'
    elif db_name.endswith(('_C', '.C')) or 'c_genes' in db_name:
        gene_type = 'C'
    
    # Check for organism patterns
    if 'human' in db_name.lower():
        organism = 'human'
    elif 'mouse' in db_name.lower():
        organism = 'mouse'
    elif 'rhesus' in db_name.lower():
        organism = 'rhesus'
    elif 'balbc' in db_name.lower():
        organism = 'mouse_balbc'
    elif 'C57BL' in db_name:
        organism = 'mouse_C57BL'
    elif 'C3H' in db_name:
        organism = 'mouse_C3H'
    elif 'DBA' in db_name:
        organism = 'mouse_DBA'
    elif 'CBA' in db_name:
        organism = 'mouse_CBA'
    elif 'AKR' in db_name:
        organism = 'mouse_AKR'
    elif 'A_J' in db_name:
        organism = 'mouse_A_J'
    elif '129S1' in db_name:
        organism = 'mouse_129S1'
    elif 'LEWES' in db_name:
        organism = 'mouse_LEWES'
    elif 'CAST' in db_name:
        organism = 'mouse_CAST'
    elif 'MRL' in db_name:
        organism = 'mouse_MRL'
    elif 'MSM' in db_name:
        organism = 'mouse_MSM'
    elif 'NOD' in db_name:
        organism = 'mouse_NOD'
    elif 'NOR' in db_name:
        organism = 'mouse_NOR'
    elif 'NZB' in db_name:
        organism = 'mouse_NZB'
    elif 'PWD' in db_name:
        organism = 'mouse_PWD'
    elif 'SJL' in db_name:
        organism = 'mouse_SJL'
    
    return organism, gene_type

def identify_duplicates_and_redundancies(databases: Dict):
    """Identify duplicate and redundant databases."""
    # Look for duplicates (same organism/gene type combinations)
    for organism, gene_types in databases["by_organism"].items():
        for gene_type, dbs in gene_types.items():
            if len(dbs) > 1:
                databases["duplicates"].append({
                    "organism": organism,
                    "gene_type": gene_type,
                    "databases": dbs
                })
    
    # Identify redundant mouse strain databases
    mouse_strains = [org for org in databases["by_organism"].keys() if org.startswith("mouse_")]
    if len(mouse_strains) > 1:
        databases["redundant_mouse_strains"] = mouse_strains

def identify_essential_databases(databases: Dict):
    """Identify essential databases to keep."""
    essential = []
    
    # Essential organisms: human, mouse (standard), rhesus
    essential_organisms = ['human', 'mouse', 'rhesus']
    
    for organism in essential_organisms:
        if organism in databases["by_organism"]:
            for gene_type, dbs in databases["by_organism"][organism].items():
                if dbs:
                    # Choose the best database for this organism/gene type
                    best_db = select_best_database(dbs, organism, gene_type)
                    essential.append(best_db)
    
    databases["essential_databases"] = essential

def select_best_database(databases: List[Dict], organism: str, gene_type: str) -> Dict:
    """Select the best database from multiple options."""
    if len(databases) == 1:
        return databases[0]
    
    # Prefer AIRR format databases
    airr_dbs = [db for db in databases if 'airr' in db['name'].lower()]
    if airr_dbs:
        return airr_dbs[0]
    
    # Prefer standard naming conventions
    standard_dbs = [db for db in databases if not any(strain in db['name'] for strain in ['C57BL', 'BALB', 'C3H', 'DBA'])]
    if standard_dbs:
        return standard_dbs[0]
    
    # Default to first database
    return databases[0]

def analyze_blast_databases(data_dir: Path) -> Dict:
    """Analyze BLAST databases."""
    blast_dir = data_dir / "blast"
    
    if not blast_dir.exists():
        print(f"BLAST directory not found: {blast_dir}")
        return {}
    
    databases = {
        "protein": [],
        "nucleotide": [],
        "total_size_mb": 0
    }
    
    # Find database files
    for db_file in blast_dir.rglob("*"):
        if db_file.is_file():
            # Determine database type
            if db_file.suffix in ['.phr', '.pin', '.psq']:
                db_name = db_file.stem
                if db_name not in [d['name'] for d in databases["protein"]]:
                    databases["protein"].append({
                        "name": db_name,
                        "path": str(db_file.relative_to(blast_dir)),
                        "size_mb": db_file.stat().st_size / (1024 * 1024)
                    })
            elif db_file.suffix in ['.nhr', '.nin', '.nsq']:
                db_name = db_file.stem
                if db_name not in [d['name'] for d in databases["nucleotide"]]:
                    databases["nucleotide"].append({
                        "name": db_name,
                        "path": str(db_file.relative_to(blast_dir)),
                        "size_mb": db_file.stat().st_size / (1024 * 1024)
                    })
    
    # Calculate total size
    for db_list in [databases["protein"], databases["nucleotide"]]:
        for db in db_list:
            databases["total_size_mb"] += db["size_mb"]
    
    return databases

def generate_cleanup_recommendations(igblast_analysis: Dict, blast_analysis: Dict) -> Dict:
    """Generate recommendations for database cleanup."""
    recommendations = {
        "databases_to_keep": [],
        "databases_to_remove": [],
        "estimated_space_saved_mb": 0,
        "reorganization_plan": []
    }
    
    # IgBLAST cleanup recommendations
    for organism, gene_types in igblast_analysis["by_organism"].items():
        for gene_type, dbs in gene_types.items():
            if len(dbs) > 1:
                # Keep the best one, remove others
                best_db = select_best_database(dbs, organism, gene_type)
                recommendations["databases_to_keep"].append(best_db)
                
                for db in dbs:
                    if db != best_db:
                        recommendations["databases_to_remove"].append(db)
    
    # Remove redundant mouse strain databases
    for organism in igblast_analysis["redundant_mouse_strains"]:
        if organism in igblast_analysis["by_organism"]:
            for gene_type, dbs in igblast_analysis["by_organism"][organism].items():
                for db in dbs:
                    recommendations["databases_to_remove"].append(db)
    
    return recommendations

def main():
    """Main analysis function."""
    data_dir = Path("data")
    
    print("=== IgBLAST Database Analysis ===")
    igblast_analysis = analyze_igblast_databases(data_dir)
    
    print(f"\nTotal IgBLAST databases found: {igblast_analysis['total_count']}")
    
    print("\n=== By Organism ===")
    for organism, gene_types in igblast_analysis["by_organism"].items():
        print(f"\n{organism}:")
        for gene_type, dbs in gene_types.items():
            print(f"  {gene_type}: {len(dbs)} databases")
            for db in dbs:
                print(f"    - {db['name']} ({db['path']})")
    
    print("\n=== Duplicates Found ===")
    for dup in igblast_analysis["duplicates"]:
        print(f"\n{dup['organism']} {dup['gene_type']} genes:")
        for db in dup["databases"]:
            print(f"  - {db['name']} ({db['path']})")
    
    print("\n=== Redundant Mouse Strains ===")
    for strain in igblast_analysis["redundant_mouse_strains"]:
        print(f"  - {strain}")
    
    print("\n=== Essential Databases ===")
    for db in igblast_analysis["essential_databases"]:
        print(f"  - {db['name']} ({db['path']})")
    
    print("\n=== BLAST Database Analysis ===")
    blast_analysis = analyze_blast_databases(data_dir)
    
    print(f"\nProtein databases: {len(blast_analysis['protein'])}")
    for db in blast_analysis["protein"]:
        print(f"  - {db['name']} ({db['size_mb']:.1f} MB)")
    
    print(f"\nNucleotide databases: {len(blast_analysis['nucleotide'])}")
    for db in blast_analysis["nucleotide"]:
        print(f"  - {db['name']} ({db['size_mb']:.1f} MB)")
    
    print(f"\nTotal BLAST database size: {blast_analysis['total_size_mb']:.1f} MB")
    
    # Generate recommendations
    recommendations = generate_cleanup_recommendations(igblast_analysis, blast_analysis)
    
    print("\n=== Cleanup Recommendations ===")
    print(f"Databases to keep: {len(recommendations['databases_to_keep'])}")
    print(f"Databases to remove: {len(recommendations['databases_to_remove'])}")
    
    # Save analysis to file
    analysis_result = {
        "igblast_analysis": igblast_analysis,
        "blast_analysis": blast_analysis,
        "recommendations": recommendations
    }
    
    with open("database_analysis_result.json", "w") as f:
        json.dump(analysis_result, f, indent=2)
    
    print(f"\nAnalysis saved to: database_analysis_result.json")

if __name__ == "__main__":
    main()
