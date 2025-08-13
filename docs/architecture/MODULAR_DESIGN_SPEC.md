# AbSequenceAlign - Modular Application Design Specification

## 1. Overview

### 1.1 Purpose
Transform the current single-module antibody sequence annotation tool into a modular platform that supports multiple analysis modules, starting with:
- **Antibody Sequence Annotation** (existing)
- **Multiple Sequence Alignment (MSA) Viewer** (new)

### 1.2 Architecture Goals
- **Modular Design**: Easy addition of new modules
- **Consistent UX**: Unified interface across all modules
- **Scalable Backend**: Extensible API structure
- **Shared Components**: Reusable UI components and services

## 2. Frontend Architecture

### 2.1 Module Structure
```
src/
├── modules/
│   ├── antibody-annotation/
│   │   ├── components/
│   │   │   ├── AntibodyAnnotationTool.tsx
│   │   │   ├── SequenceCards/
│   │   │   ├── SequenceInput/
│   │   │   └── Visualization/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── types/
│   ├── msa-viewer/
│   │   ├── components/
│   │   │   ├── MSAViewerTool.tsx
│   │   │   ├── MSAInput/
│   │   │   ├── MSAVisualization/
│   │   │   └── RegionOverlay/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── types/
│   └── shared/
│       ├── components/
│       │   ├── ModuleSelector.tsx
│       │   ├── NavigationBar.tsx
│       │   ├── FileUpload.tsx
│       │   └── LoadingStates.tsx
│       ├── hooks/
│       ├── services/
│       └── types/
```

### 2.2 Module Registration System
```typescript
interface ModuleDefinition {
  id: string;
  name: string;
  description: string;
  icon: React.ComponentType;
  component: React.ComponentType;
  route: string;
  enabled: boolean;
}

const MODULES: ModuleDefinition[] = [
  {
    id: 'antibody-annotation',
    name: 'Antibody Sequence Annotation',
    description: 'Analyze and annotate individual antibody sequences',
    icon: Biotech,
    component: AntibodyAnnotationTool,
    route: '/antibody-annotation',
    enabled: true
  },
  {
    id: 'msa-viewer',
    name: 'Multiple Sequence Alignment',
    description: 'Create and visualize MSA with region annotations',
    icon: ViewColumn,
    component: MSAViewerTool,
    route: '/msa-viewer',
    enabled: true
  }
];
```

### 2.3 Navigation Structure
- **Top Navigation Bar**: Module selector + global controls
- **Module-Specific Navigation**: Contextual controls within each module
- **Breadcrumb Navigation**: Show current module and sub-pages

## 3. Backend Architecture

### 3.1 API Structure
```
/api/v1/
├── modules/
│   ├── antibody-annotation/
│   │   ├── upload
│   │   ├── annotate
│   │   ├── align
│   │   └── datasets
│   └── msa-viewer/
│       ├── upload
│       ├── create-msa
│       ├── annotate-msa
│       ├── get-msa
│       └── datasets
├── shared/
│   ├── health
│   ├── modules
│   └── datasets
```

### 3.2 New MSA Module Endpoints

#### 3.2.1 Upload Sequences for MSA
```python
@router.post("/msa-viewer/upload")
async def upload_sequences_for_msa(
    file: Optional[UploadFile] = File(None),
    sequences: Optional[str] = Form(None)
):
    """
    Upload sequences for MSA creation
    Returns: dataset_id, sequence_count, validation_errors
    """
```

#### 3.2.2 Create MSA
```python
@router.post("/msa-viewer/create-msa")
async def create_msa(request: MSACreationRequest):
    """
    Create MSA from uploaded sequences
    Parameters: dataset_id, alignment_algorithm, parameters
    Returns: msa_id, alignment_data, statistics
    """
```

#### 3.2.3 Annotate MSA
```python
@router.post("/msa-viewer/annotate-msa")
async def annotate_msa(request: MSAAnnotationRequest):
    """
    Annotate regions in MSA sequences
    Parameters: msa_id, numbering_scheme
    Returns: annotation_data, region_mappings
    """
```

#### 3.2.4 Get MSA Data
```python
@router.get("/msa-viewer/msa/{msa_id}")
async def get_msa_data(msa_id: str):
    """
    Retrieve MSA data with annotations
    Returns: alignment_matrix, annotations, regions, metadata
    """
```

### 3.3 Data Models

#### 3.3.1 MSA Request Models
```python
class MSACreationRequest(BaseModel):
    dataset_id: str
    algorithm: str = "muscle"  # muscle, clustalo, mafft
    parameters: Dict[str, Any] = {}
    
class MSAAnnotationRequest(BaseModel):
    msa_id: str
    numbering_scheme: str = "imgt"
    annotate_regions: bool = True
```

#### 3.3.2 MSA Response Models
```python
class MSAResult(BaseModel):
    msa_id: str
    alignment_matrix: List[List[str]]
    sequence_names: List[str]
    alignment_length: int
    statistics: Dict[str, Any]
    
class MSAAnnotationResult(BaseModel):
    msa_id: str
    annotations: List[SequenceAnnotation]
    region_mappings: Dict[str, List[Region]]
    numbering_data: Dict[str, Dict[int, str]]
```

## 4. MSA Viewer Module Specification

### 4.1 Core Features
1. **Sequence Upload**: FASTA file or text input
2. **MSA Creation**: Multiple alignment algorithms
3. **Region Annotation**: Antibody region detection
4. **Interactive Visualization**: Zoom, pan, region highlighting
5. **Export Options**: FASTA, image, statistics

### 4.2 Visualization Components

#### 4.2.1 MSA Matrix Display
- **Alignment View**: Amino acid matrix with color coding
- **Conservation View**: Conservation scores and consensus
- **Region Overlay**: Highlight antibody regions across sequences
- **Numbering Display**: Show position numbers for selected scheme

#### 4.2.2 Interactive Features
- **Zoom Controls**: Adjustable zoom levels
- **Region Selection**: Click to highlight regions across all sequences
- **Sequence Selection**: Select individual sequences for detailed view
- **Position Navigation**: Jump to specific positions

#### 4.2.3 Information Panels
- **Statistics Panel**: MSA quality metrics, conservation scores
- **Region Legend**: Color-coded region types
- **Sequence Info**: Individual sequence details and annotations

### 4.3 MSA Algorithms Support
- **MUSCLE**: Fast and accurate for large datasets
- **Clustal Omega**: High accuracy, slower for large datasets
- **MAFFT**: Good balance of speed and accuracy

## 5. Implementation Plan

### 5.1 Phase 1: Modular Frontend Structure
1. **Create Module System**: Set up module registration and routing
2. **Refactor Existing Code**: Move antibody annotation to module structure
3. **Add Navigation**: Implement module selector in top navigation
4. **Shared Components**: Extract reusable components

### 5.2 Phase 2: MSA Backend Services
1. **MSA API Endpoints**: Implement upload, create, annotate, retrieve
2. **MSA Engine**: Integrate alignment algorithms (MUSCLE, ClustalO, MAFFT)
3. **Annotation Integration**: Extend existing annotation engine for MSA
4. **Data Storage**: Design MSA data storage schema

### 5.3 Phase 3: MSA Frontend Module
1. **MSA Input Components**: File upload and sequence input
2. **MSA Visualization**: Interactive alignment matrix display
3. **Region Overlay**: Highlight regions across sequences
4. **Export Features**: Download aligned sequences and images

### 5.4 Phase 4: Integration and Testing
1. **End-to-End Testing**: Full MSA workflow testing
2. **Performance Optimization**: Large dataset handling
3. **User Experience**: Polish UI/UX for both modules
4. **Documentation**: User guides and API documentation

## 6. Technical Requirements

### 6.1 Frontend Requirements
- **React 18+**: Latest React features and hooks
- **TypeScript**: Full type safety
- **Material-UI**: Consistent design system
- **State Management**: React Context or Zustand for module state
- **File Handling**: Support for FASTA file uploads
- **Visualization**: Canvas-based or SVG-based MSA display

### 6.2 Backend Requirements
- **FastAPI**: RESTful API framework
- **BioPython**: Sequence manipulation and MSA algorithms
- **NumPy/SciPy**: Scientific computing for MSA analysis
- **Redis/Cache**: Caching for large MSA computations
- **PostgreSQL**: Data storage for MSA results
- **Celery**: Background task processing for long-running alignments

### 6.3 Performance Requirements
- **Upload**: Support up to 1000 sequences per upload
- **MSA Creation**: Handle up to 500 sequences in reasonable time (<5 minutes)
- **Visualization**: Smooth scrolling and zooming for large alignments
- **Memory**: Efficient memory usage for large datasets

## 7. User Experience Design

### 7.1 Module Selection
- **Clear Navigation**: Prominent module selector in top bar
- **Module Cards**: Visual cards showing module capabilities
- **Quick Access**: Recent modules and favorites

### 7.2 MSA Workflow
1. **Upload Sequences**: Drag-and-drop or text input
2. **Configure Alignment**: Select algorithm and parameters
3. **Create MSA**: Progress indicator during alignment
4. **View Results**: Interactive visualization with annotations
5. **Export/Share**: Download results or share links

### 7.3 Consistent Design Language
- **Color Scheme**: Consistent across all modules
- **Component Library**: Shared UI components
- **Typography**: Unified font hierarchy
- **Spacing**: Consistent layout grid

## 8. Future Module Considerations

### 8.1 Potential Additional Modules
- **Phylogenetic Analysis**: Tree construction and visualization
- **Structure Prediction**: 3D structure modeling
- **Epitope Analysis**: B-cell epitope prediction
- **Diversity Analysis**: Sequence diversity metrics
- **Batch Processing**: High-throughput sequence analysis

### 8.2 Extensibility Features
- **Plugin System**: Third-party module support
- **API Extensions**: Custom endpoint registration
- **Custom Visualizations**: User-defined plot types
- **Workflow Automation**: Sequence analysis pipelines

## 9. Success Metrics

### 9.1 Technical Metrics
- **Performance**: MSA creation time <5 minutes for 500 sequences
- **Reliability**: 99.9% uptime for core services
- **Scalability**: Support for 1000+ sequences
- **Accuracy**: MSA quality scores comparable to industry standards

### 9.2 User Experience Metrics
- **Usability**: Task completion rate >90%
- **Performance**: Page load time <3 seconds
- **Adoption**: User engagement with new MSA module
- **Satisfaction**: User feedback scores >4.0/5.0

## 10. Detailed Requirements for MSA Module

### 10.1 Backend MSA Service Requirements

#### 10.1.1 MSA Engine Integration
- **BioPython Integration**: Use Bio.Align.Applications for external tools
- **Algorithm Support**: MUSCLE, Clustal Omega, MAFFT
- **Parameter Configuration**: Algorithm-specific parameters
- **Progress Tracking**: Real-time progress updates for long alignments

#### 10.1.2 Data Processing Pipeline
1. **Sequence Validation**: Validate input sequences
2. **Preprocessing**: Clean and standardize sequences
3. **Alignment Execution**: Run selected algorithm
4. **Post-processing**: Calculate statistics and quality metrics
5. **Annotation Integration**: Apply antibody region detection

#### 10.1.3 Storage and Caching
- **MSA Storage**: Efficient storage of alignment matrices
- **Annotation Storage**: Region mappings and numbering data
- **Result Caching**: Cache alignment results for reuse
- **Metadata Storage**: Alignment parameters and statistics

### 10.2 Frontend MSA Visualization Requirements

#### 10.2.1 Interactive MSA Display
- **Canvas Rendering**: High-performance rendering for large alignments
- **Zoom and Pan**: Smooth navigation through large alignments
- **Region Highlighting**: Visual overlay of antibody regions
- **Conservation Display**: Color-coded conservation scores

#### 10.2.2 User Interface Components
- **Sequence Upload**: Drag-and-drop FASTA file support
- **Algorithm Selection**: Dropdown for MSA algorithm choice
- **Parameter Configuration**: Advanced options for each algorithm
- **Progress Tracking**: Real-time progress indicators
- **Result Export**: Download aligned sequences and images

#### 10.2.3 Information Display
- **Alignment Statistics**: Quality metrics and conservation scores
- **Region Legend**: Color-coded region type display
- **Sequence Information**: Individual sequence details
- **Position Navigation**: Jump to specific alignment positions

This design specification provides a comprehensive roadmap for transforming the current single-module application into a robust, modular platform that can support multiple analysis workflows while maintaining consistency and extensibility.
