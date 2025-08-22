#!/usr/bin/env python3
"""
Database Reorganization Script

This script reorganizes the IgBLAST and BLAST databases according to the plan:
1. Keep only essential databases
2. Organize into clean directory structure
3. Create database metadata file
4. Remove redundant databases
"""

import json
import shutil
import os
from pathlib import Path
from typing import Dict, List
import argparse

def create_new_directory_structure(base_dir: Path):
    """Create the new organized directory structure."""
    new_structure = [
        "data/igblast/databases/human/V",
        "data/igblast/databases/human/D", 
        "data/igblast/databases/human/J",
        "data/igblast/databases/human/C",
        "data/igblast/databases/mouse/V",
        "data/igblast/databases/mouse/D",
        "data/igblast/databases/mouse/J", 
        "data/igblast/databases/mouse/C",
        "data/igblast/databases/rhesus/V",
        "data/igblast/databases/rhesus/J",
        "data/blast/protein/swissprot",
        "data/blast/protein/pdb",
        "data/blast/nucleotide/refseq_select_rna",
        "data/blast/nucleotide/taxonomy"
    ]
    
    for dir_path in new_structure:
        full_path = base_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {full_path}")

def get_essential_databases() -> Dict:
    """Define the essential databases to keep."""
    return {
        "human": {
            "V": {
                "source": "data/igblast/internal_data/human/airr_c_human_ig.V",
                "dest": "data/igblast/databases/human/V/airr_c_human_ig.V",
                "name": "Human V Genes",
                "description": "Human immunoglobulin V gene database (AIRR format)"
            },
            "D": {
                "source": "data/igblast/internal_data/human/airr_c_human_igh.D", 
                "dest": "data/igblast/databases/human/D/airr_c_human_igh.D",
                "name": "Human D Genes",
                "description": "Human immunoglobulin D gene database (AIRR format)"
            },
            "J": {
                "source": "data/igblast/internal_data/human/airr_c_human_ig.J",
                "dest": "data/igblast/databases/human/J/airr_c_human_ig.J", 
                "name": "Human J Genes",
                "description": "Human immunoglobulin J gene database (AIRR format)"
            },
            "C": {
                "source": "data/igblast/internal_data/ncbi_human_c_genes",
                "dest": "data/igblast/databases/human/C/ncbi_human_c_genes",
                "name": "Human C Genes",
                "description": "Human immunoglobulin C gene database"
            }
        },
        "mouse": {
            "V": {
                "source": "data/igblast/internal_data/mouse/mouse_gl_V",
                "dest": "data/igblast/databases/mouse/V/mouse_gl_V",
                "name": "Mouse V Genes", 
                "description": "Mouse immunoglobulin V gene database"
            },
            "D": {
                "source": "data/igblast/internal_data/mouse/mouse_gl_D",
                "dest": "data/igblast/databases/mouse/D/mouse_gl_D",
                "name": "Mouse D Genes",
                "description": "Mouse immunoglobulin D gene database"
            },
            "J": {
                "source": "data/igblast/internal_data/mouse/mouse_gl_J",
                "dest": "data/igblast/databases/mouse/J/mouse_gl_J",
                "name": "Mouse J Genes",
                "description": "Mouse immunoglobulin J gene database"
            },
            "C": {
                "source": "data/igblast/internal_data/mouse_c_genes",
                "dest": "data/igblast/databases/mouse/C/mouse_c_genes",
                "name": "Mouse C Genes",
                "description": "Mouse immunoglobulin C gene database"
            }
        },
        "rhesus": {
            "V": {
                "source": "data/igblast/internal_data/rhesus_monkey_V",
                "dest": "data/igblast/databases/rhesus/V/rhesus_monkey_V",
                "name": "Rhesus V Genes",
                "description": "Rhesus monkey immunoglobulin V gene database"
            },
            "J": {
                "source": "data/igblast/internal_data/rhesus_monkey_J",
                "dest": "data/igblast/databases/rhesus/J/rhesus_monkey_J",
                "name": "Rhesus J Genes", 
                "description": "Rhesus monkey immunoglobulin J gene database"
            }
        }
    }

def copy_database_files(base_dir: Path, essential_dbs: Dict) -> List[str]:
    """Copy essential database files to new structure."""
    copied_files = []
    
    for organism, gene_types in essential_dbs.items():
        for gene_type, db_info in gene_types.items():
            source_path = base_dir / db_info["source"]
            dest_path = base_dir / db_info["dest"]
            
            # Copy all related database files
            source_dir = source_path.parent
            source_name = source_path.name
            
            if source_dir.exists():
                # Find all files with the same base name
                for file_path in source_dir.glob(f"{source_name}.*"):
                    dest_file = dest_path.parent / file_path.name
                    try:
                        shutil.copy2(file_path, dest_file)
                        copied_files.append(str(dest_file))
                        print(f"Copied: {file_path} -> {dest_file}")
                    except Exception as e:
                        print(f"Error copying {file_path}: {e}")
            else:
                print(f"Warning: Source directory not found: {source_dir}")
    
    return copied_files

def create_database_metadata(base_dir: Path, essential_dbs: Dict) -> Dict:
    """Create database metadata file."""
    metadata = {
        "igblast_databases": {},
        "blast_databases": {
            "protein": {
                "swissprot": {
                    "name": "Swiss-Prot Protein Database",
                    "path": "data/blast/protein/swissprot",
                    "description": "Curated protein sequence database",
                    "type": "protein"
                },
                "pdb": {
                    "name": "PDB Protein Database",
                    "path": "data/blast/protein/pdb", 
                    "description": "Protein Data Bank sequences",
                    "type": "protein"
                }
            },
            "nucleotide": {
                "refseq_select_rna": {
                    "name": "RefSeq Select RNA",
                    "path": "data/blast/nucleotide/refseq_select_rna",
                    "description": "RefSeq Select RNA sequences",
                    "type": "nucleotide"
                }
            }
        }
    }
    
    # Add IgBLAST databases
    for organism, gene_types in essential_dbs.items():
        metadata["igblast_databases"][organism] = {}
        for gene_type, db_info in gene_types.items():
            metadata["igblast_databases"][organism][gene_type] = {
                "name": db_info["name"],
                "path": db_info["dest"],
                "description": db_info["description"],
                "organism": organism,
                "gene_type": gene_type
            }
    
    # Save metadata file
    metadata_path = base_dir / "data/igblast/database_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Created database metadata: {metadata_path}")
    return metadata

def backup_old_structure(base_dir: Path):
    """Create a backup of the old database structure."""
    backup_dir = base_dir / "data/igblast/internal_data_backup"
    old_dir = base_dir / "data/igblast/internal_data"
    
    if old_dir.exists():
        try:
            shutil.copytree(old_dir, backup_dir)
            print(f"Created backup: {backup_dir}")
        except Exception as e:
            print(f"Error creating backup: {e}")

def cleanup_old_structure(base_dir: Path, dry_run: bool = False):
    """Remove old database structure after backup."""
    old_dir = base_dir / "data/igblast/internal_data"
    
    if old_dir.exists():
        if dry_run:
            print(f"Would remove: {old_dir}")
        else:
            try:
                shutil.rmtree(old_dir)
                print(f"Removed old structure: {old_dir}")
            except Exception as e:
                print(f"Error removing old structure: {e}")

def reorganize_blast_databases(base_dir: Path):
    """Reorganize BLAST databases."""
    blast_dir = base_dir / "data/blast"
    
    # Move protein databases
    protein_dirs = {
        "swissprot": blast_dir / "swissprot",
        "pdb": blast_dir / "pdbaa"
    }
    
    for db_name, source_dir in protein_dirs.items():
        if source_dir.exists():
            dest_dir = blast_dir / "protein" / db_name
            try:
                shutil.move(str(source_dir), str(dest_dir))
                print(f"Moved: {source_dir} -> {dest_dir}")
            except Exception as e:
                print(f"Error moving {source_dir}: {e}")
    
    # Move nucleotide databases
    nucleotide_dirs = {
        "refseq_select_rna": blast_dir / "refseq_select_rna",
        "taxonomy": blast_dir / "taxonomy4blast.sqlite3"
    }
    
    for db_name, source_path in nucleotide_dirs.items():
        if source_path.exists():
            dest_dir = blast_dir / "nucleotide" / db_name
            if source_path.is_file():
                dest_dir.parent.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.move(str(source_path), str(dest_dir))
                    print(f"Moved: {source_path} -> {dest_dir}")
                except Exception as e:
                    print(f"Error moving {source_path}: {e}")
            else:
                try:
                    shutil.move(str(source_path), str(dest_dir))
                    print(f"Moved: {source_path} -> {dest_dir}")
                except Exception as e:
                    print(f"Error moving {source_path}: {e}")

def main():
    """Main reorganization function."""
    parser = argparse.ArgumentParser(description="Reorganize IgBLAST and BLAST databases")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--no-backup", action="store_true", help="Skip creating backup of old structure")
    args = parser.parse_args()
    
    base_dir = Path.cwd()
    print(f"Working in: {base_dir}")
    
    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")
    
    # Step 1: Create new directory structure
    print("\n=== Step 1: Creating new directory structure ===")
    if not args.dry_run:
        create_new_directory_structure(base_dir)
    else:
        print("Would create new directory structure")
    
    # Step 2: Get essential databases
    print("\n=== Step 2: Identifying essential databases ===")
    essential_dbs = get_essential_databases()
    
    # Step 3: Copy essential database files
    print("\n=== Step 3: Copying essential database files ===")
    if not args.dry_run:
        copied_files = copy_database_files(base_dir, essential_dbs)
        print(f"Copied {len(copied_files)} database files")
    else:
        print("Would copy essential database files")
    
    # Step 4: Create database metadata
    print("\n=== Step 4: Creating database metadata ===")
    if not args.dry_run:
        metadata = create_database_metadata(base_dir, essential_dbs)
    else:
        print("Would create database metadata file")
    
    # Step 5: Reorganize BLAST databases
    print("\n=== Step 5: Reorganizing BLAST databases ===")
    if not args.dry_run:
        reorganize_blast_databases(base_dir)
    else:
        print("Would reorganize BLAST databases")
    
    # Step 6: Backup old structure
    if not args.no_backup and not args.dry_run:
        print("\n=== Step 6: Creating backup ===")
        backup_old_structure(base_dir)
    elif args.dry_run:
        print("\n=== Step 6: Would create backup ===")
    
    # Step 7: Clean up old structure
    print("\n=== Step 7: Cleaning up old structure ===")
    cleanup_old_structure(base_dir, dry_run=args.dry_run)
    
    print("\n=== Reorganization Complete ===")
    if not args.dry_run:
        print("Database reorganization completed successfully!")
        print("New structure created in: data/igblast/databases/")
        print("Database metadata: data/igblast/database_metadata.json")
        print("Backup created in: data/igblast/internal_data_backup/")
    else:
        print("Dry run completed. Review the planned changes above.")

if __name__ == "__main__":
    main()
