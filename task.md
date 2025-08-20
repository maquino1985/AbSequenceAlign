# AbSequenceAlign Task List

## Current Issues

### Frontend Issues
- **blastn database not found errors**: Frontend still using wrong database names for nucleotide databases
  - Error: `No alias or index file found for nucleotide database [/blast/blastdb/nucleotide/human_genome]`
  - Issue: Database path resolution in blast_adapter.py needs fixing for nucleotide databases
  - Status: ✅ **RESOLVED** - Fixed with configuration-based database name mapping

### Backend Test Issues

#### Tests using requests instead of FastAPI TestClient (need conversion)
- `test_get_databases` ✅ **RESOLVED** - Fixed field name expectations
- `test_igblast_nucleotide_no_c_gene` ✅ **RESOLVED** - Fixed field name expectations
- `test_igblast_nucleotide_with_c_gene` ✅ **RESOLVED** - Fixed field name expectations
- `test_igblast_airr_format` ✅ **RESOLVED** - Fixed field name expectations

#### Tests with real logic errors (need investigation)
- `TestAPIIntegration::test_annotation_endpoint_error_handling` ✅ **RESOLVED** - Fixed to expect HTTP 422 instead of exception
- `test_blast_search_antibody_endpoint_nucleotide_real` ✅ **RESOLVED** - Fixed field name expectations
- `test_blast_search_antibody_endpoint_protein_real` ✅ **RESOLVED** - Fixed field name expectations and optional field checks
- `test_job_status_not_found_real` ✅ **RESOLVED** - Fixed to expect HTTP 404 instead of exception

### Data and Database Issues

#### GitHub LFS File Issues
- **Broken/moved GitHub LFS files in data/**: Some large files in the data/ directory may be broken or moved due to Git LFS issues. Need to identify and fix these files to ensure proper functionality.

#### Symbolic Link Cleanup
- **Remove symbolic links in data directory**: The data directory contains symbolic links (e.g., `data/blast/16S_ribosomal_RNA -> nucleotide/16S_ribosomal_RNA`) that can interfere with Docker commands and are unnecessary. Need to remove these symbolic links and update any code that references the old paths to use the new organized directory structure directly.

#### BLAST Database Issues
- **Download/replace existing blastn databases**: Current blastn databases for human and mouse may be corrupted or outdated. Need to download fresh, working blastn databases for both organisms to ensure reliable BLAST searches.

### IgBLAST Protein Framework/CDR Detection Issues

#### IgBLAST Protein Analysis Enhancement
- **Task 1: Investigate IgBLAST protein output parsing** ✅ **COMPLETED** - Found that IgBLAST protein output (outfmt 7) includes detailed framework and CDR annotations in the "Alignment summary" section, but the current TabularParser only extracts hit table data and ignores the framework/CDR information. The output shows FR1, CDR1, FR2, CDR2, FR3 regions with coordinates, lengths, matches, mismatches, gaps, and percent identity for each region.

- **Task 2: Research IgBLAST numbering systems** ✅ **COMPLETED** - Found that IgBLAST protein supports `-domain_system` parameter with options `imgt` (default) and `kabat`. The numbering system affects how framework and CDR regions are defined and their coordinates. IMGT and Kabat have different CDR definitions, which is reflected in the alignment summary output.

- **Task 3: Update IgBLAST adapter for protein analysis** ✅ **COMPLETED** - Modified the TabularParser to extract framework and CDR annotations from the "Alignment summary" section of IgBLAST protein output. The parser now extracts detailed metrics for FR1, CDR1, FR2, CDR2, FR3 regions including start/end positions, length, matches/mismatches/gaps, and percent identity. Also added support for the `domain_system` parameter in the IgBLAST adapter to specify numbering systems (IMGT/Kabat).

- **Task 4: Add numbering system selection to API** ✅ **COMPLETED** - Extended the `IgBlastSearchRequest` model to include an optional `domain_system` parameter (defaults to "imgt"). Updated the `IgBlastService.analyze_antibody_sequence` method to accept and validate the `domain_system` parameter, passing it through to the IgBLAST adapter for protein analysis. The API now supports both IMGT and Kabat numbering systems for protein IgBLAST.

- **Task 5: Update response models** ✅ **COMPLETED** - Added comprehensive framework and CDR models (`FrameworkCDRRegion`, `IgBlastAnalysisSummary`) to `igblast_models.py` for better API documentation. The existing flexible response structure already properly returns framework and CDR data through the `analysis_summary` field, including all region metrics (start/end positions, length, matches/mismatches/gaps, percent identity) for FR1, CDR1, FR2, CDR2, FR3 regions.

- **Task 6: Update frontend to display framework/CDR data**: Modify the frontend to display the framework and CDR annotations when available, including the ability to select different numbering systems.

- **Task 7: Add numbering system selection UI**: Create user interface components to allow users to select their preferred numbering system (IMGT, Kabat, etc.) when performing IgBLAST protein analysis.

- **Task 8: Update tests for framework/CDR detection** ✅ **COMPLETED** - Added comprehensive unit tests for framework and CDR detection functionality. Created new test file `test_tabular_parser.py` with 6 tests covering IMGT/Kabat numbering systems, malformed data handling, and edge cases. Updated `test_blast_service.py` with 4 new tests for domain system validation and parameter passing. Updated `test_igblast_adapter_v3.py` with 5 new tests for domain system command building. Updated `test_api_integration.py` with 4 new integration tests for API endpoints with domain system parameters. All tests pass and verify proper error handling, validation, and data extraction.

## Previous TODOs

### IgBLAST Database Issues
- **Mouse IgBLAST nucleotide database error**: 
  - Error: `No alias or index file found for nucleotide database [/blast/internal_data/ncbi_mouse_c_genes]`
  - TODO: Review `data/igblast/internal-data` contents and correct organism error for mouse
  - TODO: Rearrange files if needed and add missing organisms
  - Note: Mouse protein and nucleotide sequence data exists but failing

### C Gene Detection
- **C gene detection tests skipped**: Will be revisited later
- **C gene databases corrupted**: May be due to mixing IgBLAST and BLAST databases
- TODO: Revisit C gene detection implementation

### IgBLAST Protein Functionality
- **Missing CDR/Framework information**: IgBLAST protein detects these features but not showing in results
- TODO: Revisit IgBLAST protein functionality to display CDR/Framework information

### Database Organization
- **BLAST data disorganized**: `data/blast` needs consistent and logical paths
- **Mixed database types**: Some IgBLAST databases in BLAST directory (mouse_c_genes, ncbi_human_c_genes)
- TODO: Clean up database organization and remove unnecessary databases

### UI/UX Improvements
- **Enhanced view links not obvious**: Links in enhanced view pages don't appear clickable
- **Sequence alignment display**: Needs better formatting (split onto multiple lines, smaller size)
- **Productive status display**: Shows "0.0% productive" instead of "unknown" for unproductive sequences

## Completed Tasks ✅
- Fixed IgBLAST adapter parsing issues
- Implemented AIRR format parsing
- Created new IgBLAST adapter (V3) with simplified database handling
- Fixed integration tests for blast_api_comprehensive.py
- Reorganized database structure with metadata file
- Updated frontend to use new database selection approach
- Fixed protein IgBLAST functionality (V domain only)
- Disabled AIRR format for protein IgBLAST
- Fixed standard BLAST database integration
- **Fixed blastn database path resolution with configuration-based approach**
  - Added `BLAST_DB_NAME_MAPPINGS` to config.py
  - Created `get_blast_db_name()` function for database name resolution
  - Updated blast_adapter.py to use configuration instead of hardcoded names
  - Updated database metadata to include actual database names
  - Downloaded Git LFS database files for human and mouse genomes

## Feature Roadmap (Advanced Features)

### 🔴 **HIGH PRIORITY** - Core Advanced Features
- **Enhanced Gene Assignments**: Implement comprehensive V/D/J/C gene detection with confidence scores
- **Paired Heavy/Light Chain Analysis**: Support for analyzing paired antibody chains together
- **Advanced AIRR Visualization**: Complete AIRR format parsing and visualization components
- **Somatic Mutation Analysis**: Implement mutation analysis with replacement/silent ratios
- **Productivity Analysis**: Enhanced productivity determination with detailed reasoning

### 🟡 **MEDIUM PRIORITY** - Advanced Analysis Features
- **Multi-sequence Analysis**: Batch processing of multiple antibody sequences
- **Comparative Analysis**: Compare multiple antibodies for similarity/differences
- **Germline Analysis**: Compare sequences against germline databases
- **CDR3 Analysis**: Advanced CDR3 region analysis with length distributions
- **Framework Region Analysis**: Detailed framework region annotation and analysis
- **Isotype Prediction**: Predict antibody isotypes from sequence data
- **Affinity Maturation Analysis**: Track somatic hypermutation patterns

### 🟢 **LOW PRIORITY** - Advanced UI/UX Features
- **Interactive Sequence Viewer**: Advanced sequence visualization with region highlighting
- **Export Functionality**: Export results in various formats (CSV, JSON, FASTA)
- **Batch Processing UI**: User interface for processing multiple sequences
- **Advanced Filtering**: Filter results by various criteria (identity, length, etc.)
- **Custom Database Support**: Allow users to upload custom databases

## Priority Order
1. ✅ **COMPLETED**: Fix blastn database path resolution
2. 🔴 **URGENT**: Convert failing tests to use FastAPI TestClient
3. 🟡 **HIGH**: Investigate real logic errors in failing tests
4. 🟡 **HIGH**: Fix IgBLAST mouse database issues
5. 🟡 **HIGH**: Implement Enhanced Gene Assignments (from roadmap)
6. 🟡 **HIGH**: Implement Paired Heavy/Light Chain Analysis (from roadmap)
7. 🟢 **MEDIUM**: Revisit C gene detection
8. 🟢 **MEDIUM**: Improve IgBLAST protein CDR/Framework display
9. 🟢 **MEDIUM**: Clean up database organization
10. 🟢 **MEDIUM**: UI/UX improvements
11. 🟢 **MEDIUM**: Advanced AIRR Visualization (from roadmap)
12. 🟢 **MEDIUM**: Somatic Mutation Analysis (from roadmap)
