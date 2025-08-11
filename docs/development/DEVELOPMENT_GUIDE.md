# Development Guide

## Overview

This guide covers the development workflow, coding standards, and best practices for contributing to AbSequenceAlign.

## Development Environment Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- Conda (for Python environment management)
- Git

### Initial Setup
```bash
# Clone the repository
git clone https://github.com/maquino1985/AbSequenceAlign.git
cd AbSequenceAlign

# Setup Python environment
cd app/backend
conda env create -f environment.yml
conda activate AbSequenceAlign

# Setup Node.js environment
cd ../frontend
npm install

# Install pre-commit hooks
pre-commit install
```

## Project Structure

```
AbSequenceAlign/
├── app/
│   ├── backend/                 # FastAPI backend
│   │   ├── api/                # API endpoints
│   │   ├── application/        # Application layer
│   │   │   ├── commands/       # Command pattern implementation
│   │   │   ├── handlers/       # Command handlers
│   │   │   ├── services/       # Application services
│   │   │   └── strategies/     # Strategy pattern implementations
│   │   ├── domain/             # Domain layer
│   │   │   ├── entities.py     # Domain entities
│   │   │   ├── models.py       # Domain models and enums
│   │   │   └── value_objects.py # Value objects
│   │   ├── infrastructure/     # Infrastructure layer
│   │   │   ├── adapters/       # External service adapters
│   │   │   └── repositories/   # Data access layer
│   │   └── core/               # Core interfaces and base classes
│   └── frontend/               # React frontend
│       ├── src/
│       │   ├── components/     # Reusable components
│       │   ├── modules/        # Feature modules
│       │   ├── services/       # API services
│       │   └── types/          # TypeScript type definitions
│       └── public/             # Static assets
├── data/                       # Data files and models
├── docs/                       # Documentation
├── scripts/                    # Build and utility scripts
└── tests/                      # End-to-end tests
```

## Coding Standards

### Python (Backend)

#### Code Style
- **Formatter**: Black (line length: 88)
- **Linter**: Flake8
- **Type Checker**: MyPy
- **Import Sorter**: isort

#### Naming Conventions
```python
# Classes: PascalCase
class BiologicEntity:
    pass

# Functions and variables: snake_case
def validate_sequence(sequence_data: str) -> bool:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_SEQUENCE_LENGTH = 10000

# Private methods: _leading_underscore
def _internal_helper(self) -> None:
    pass
```

#### Type Annotations
```python
from typing import List, Optional, Dict, Any

def process_sequences(
    sequences: List[str],
    options: Optional[Dict[str, Any]] = None
) -> List[BiologicEntity]:
    pass
```

#### Documentation
```python
def annotate_sequence(sequence: str, scheme: NumberingScheme) -> AnnotationResult:
    """
    Annotate an antibody sequence using the specified numbering scheme.
    
    Args:
        sequence: The amino acid sequence to annotate
        scheme: The numbering scheme to use (IMGT, Kabat, etc.)
        
    Returns:
        AnnotationResult containing the annotated sequence data
        
    Raises:
        ValidationError: If the sequence is invalid
        AnnotationError: If annotation fails
    """
    pass
```

### TypeScript (Frontend)

#### Code Style
- **Formatter**: Prettier
- **Linter**: ESLint
- **Type Checker**: TypeScript strict mode

#### Naming Conventions
```typescript
// Interfaces: PascalCase
interface SequenceData {
  name: string;
  sequence: string;
}

// Functions and variables: camelCase
const processSequence = (data: SequenceData): ProcessedResult => {
  return {};
};

// Constants: UPPER_SNAKE_CASE
const MAX_SEQUENCE_LENGTH = 10000;

// Private methods: _leadingUnderscore
private _internalHelper(): void {
  // ...
}
```

#### Type Definitions
```typescript
// Define types for API responses
interface ApiResponse<T> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
}

// Use enums for constants
enum NumberingScheme {
  IMGT = 'imgt',
  KABAT = 'kabat',
  CHOTHIA = 'chothia'
}
```

## Architecture Patterns

### Domain-Driven Design (DDD)

The backend follows DDD principles with clear separation of concerns:

#### Domain Layer
```python
# Rich domain entities with business logic
@dataclass
class BiologicEntity(DomainEntity):
    name: str
    biologic_type: BiologicType
    chains: List[BiologicChain]
    
    def is_antibody(self) -> bool:
        return self.biologic_type == BiologicType.ANTIBODY
    
    def add_chain(self, chain: BiologicChain) -> None:
        self.chains.append(chain)
```

#### Application Layer
```python
# Application services orchestrate domain logic
class AnnotationService:
    def __init__(self, repository: BiologicRepository):
        self.repository = repository
    
    async def annotate_sequence(self, command: AnnotateSequenceCommand) -> AnnotationResult:
        # Orchestrate domain logic
        pass
```

#### Infrastructure Layer
```python
# Infrastructure adapts external services
class AnarciAdapter(ExternalToolAdapter):
    async def annotate(self, sequence: str) -> AnnotationResult:
        # Adapt external ANARCI tool
        pass
```

### Command Pattern

Commands encapsulate requests and handlers process them:

```python
# Command
class AnnotateSequenceCommand:
    def __init__(self, sequence: str, name: str):
        self.sequence = sequence
        self.name = name

# Handler
class AnnotationHandler:
    def __init__(self, annotation_service: AnnotationService):
        self.annotation_service = annotation_service
    
    async def handle(self, command: AnnotateSequenceCommand) -> AnnotationResult:
        return await self.annotation_service.annotate_sequence(command)
```

### Strategy Pattern

Strategies provide pluggable implementations:

```python
# Strategy interface
class AnnotationStrategy(ABC):
    @abstractmethod
    async def annotate(self, sequence: str) -> AnnotationResult:
        pass

# Concrete strategies
class ImgtAnnotationStrategy(AnnotationStrategy):
    async def annotate(self, sequence: str) -> AnnotationResult:
        # IMGT-specific annotation logic
        pass

class KabatAnnotationStrategy(AnnotationStrategy):
    async def annotate(self, sequence: str) -> AnnotationResult:
        # Kabat-specific annotation logic
        pass
```

## Testing

### Backend Testing

#### Unit Tests
```python
# Test domain entities
def test_biologic_entity_creation():
    entity = BiologicEntity(
        name="test_antibody",
        biologic_type=BiologicType.ANTIBODY
    )
    assert entity.name == "test_antibody"
    assert entity.is_antibody() is True

# Test application services
def test_annotation_service():
    mock_repo = Mock(spec=BiologicRepository)
    service = AnnotationService(mock_repo)
    
    result = service.annotate_sequence("QVQLVQSGAEVKKPGASVKVSCKASGYTFTNYWMQWVKQRPGQGLEWIGYINPYNDGTKYNEKFKGKATLTADKSSSTAYMQLSSLTSEDSAVYYCARYYDDHYCLDYWGQGTTLTVSS")
    assert result.success is True
```

#### Integration Tests
```python
# Test API endpoints
async def test_annotate_endpoint(client):
    response = await client.post("/api/v2/annotate", json={
        "sequence": "QVQLVQSGAEVKKPGASVKVSCKASGYTFTNYWMQWVKQRPGQGLEWIGYINPYNDGTKYNEKFKGKATLTADKSSSTAYMQLSSLTSEDSAVYYCARYYDDHYCLDYWGQGTTLTVSS",
        "name": "test_antibody"
    })
    assert response.status_code == 200
    assert response.json()["success"] is True
```

### Frontend Testing

#### Unit Tests
```typescript
// Test components
describe('SequenceInput', () => {
  it('should validate sequence input', () => {
    render(<SequenceInput onSequenceChange={mockFn} />);
    const input = screen.getByLabelText(/sequence/i);
    fireEvent.change(input, { target: { value: 'INVALID123' } });
    expect(screen.getByText(/invalid sequence/i)).toBeInTheDocument();
  });
});

// Test services
describe('ApiService', () => {
  it('should annotate sequence', async () => {
    const result = await apiService.annotateSequence('QVQLVQSGAEVKKPGASVKVSCKASGYTFTNYWMQWVKQRPGQGLEWIGYINPYNDGTKYNEKFKGKATLTADKSSSTAYMQLSSLTSEDSAVYYCARYYDDHYCLDYWGQGTTLTVSS');
    expect(result.success).toBe(true);
  });
});
```

#### E2E Tests
```typescript
// Test user workflows
describe('Sequence Annotation Workflow', () => {
  it('should annotate sequence end-to-end', () => {
    cy.visit('/');
    cy.get('[data-testid="sequence-input"]').type('QVQLVQSGAEVKKPGASVKVSCKASGYTFTNYWMQWVKQRPGQGLEWIGYINPYNDGTKYNEKFKGKATLTADKSSSTAYMQLSSLTSEDSAVYYCARYYDDHYCLDYWGQGTTLTVSS');
    cy.get('[data-testid="annotate-button"]').click();
    cy.get('[data-testid="annotation-result"]').should('be.visible');
  });
});
```

## Development Workflow

### Git Workflow

#### Branch Naming
- `feature/feature-name` - New features
- `bugfix/bug-description` - Bug fixes
- `hotfix/urgent-fix` - Critical fixes
- `refactor/refactor-description` - Code refactoring

#### Commit Messages
Use conventional commits:
```
feat: add new annotation strategy
fix: resolve sequence validation issue
docs: update API documentation
refactor: simplify domain entity structure
test: add unit tests for annotation service
```

#### Pull Request Process
1. Create feature branch from `main`
2. Make changes with proper tests
3. Run all tests locally
4. Create pull request with description
5. Address review comments
6. Merge after approval

### Code Review Guidelines

#### What to Review
- **Functionality**: Does the code work as intended?
- **Architecture**: Does it follow established patterns?
- **Testing**: Are there adequate tests?
- **Documentation**: Is the code well-documented?
- **Performance**: Are there performance implications?
- **Security**: Are there security concerns?

#### Review Comments
- Be constructive and specific
- Suggest alternatives when possible
- Focus on the code, not the person
- Use questions to understand intent

## Performance Considerations

### Backend Performance
```python
# Use async/await for I/O operations
async def annotate_sequences(sequences: List[str]) -> List[AnnotationResult]:
    tasks = [annotate_single_sequence(seq) for seq in sequences]
    return await asyncio.gather(*tasks)

# Implement caching
@lru_cache(maxsize=1000)
def expensive_calculation(sequence: str) -> Result:
    # Cache expensive calculations
    pass
```

### Frontend Performance
```typescript
// Use React.memo for expensive components
const ExpensiveComponent = React.memo(({ data }) => {
  return <div>{expensiveCalculation(data)}</div>;
});

// Implement virtual scrolling for large lists
import { FixedSizeList as List } from 'react-window';

const VirtualizedList = ({ items }) => (
  <List
    height={400}
    itemCount={items.length}
    itemSize={50}
    itemData={items}
  >
    {({ index, style, data }) => (
      <div style={style}>
        {data[index]}
      </div>
    )}
  </List>
);
```

## Security Best Practices

### Backend Security
```python
# Validate all inputs
from pydantic import BaseModel, validator

class SequenceRequest(BaseModel):
    sequence: str
    
    @validator('sequence')
    def validate_sequence(cls, v):
        if not re.match(r'^[ACDEFGHIKLMNPQRSTVWYX]+$', v.upper()):
            raise ValueError('Invalid amino acid sequence')
        return v.upper()

# Use dependency injection for authentication
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Validate JWT token
    pass
```

### Frontend Security
```typescript
// Sanitize user inputs
import DOMPurify from 'dompurify';

const sanitizedInput = DOMPurify.sanitize(userInput);

// Use HTTPS in production
const apiUrl = process.env.NODE_ENV === 'production' 
  ? 'https://api.example.com' 
  : 'http://localhost:8000';
```

## Debugging

### Backend Debugging
```python
# Use structured logging
import logging

logger = logging.getLogger(__name__)
logger.info("Processing sequence", extra={
    "sequence_length": len(sequence),
    "annotation_method": method
})

# Use debugger
import pdb; pdb.set_trace()

# Use async debugger
import asyncio
asyncio.run(debug_function())
```

### Frontend Debugging
```typescript
// Use React DevTools
// Use browser dev tools
console.log('Debug info:', { data, state });

// Use error boundaries
class ErrorBoundary extends React.Component {
  componentDidCatch(error, errorInfo) {
    console.error('Error caught:', error, errorInfo);
  }
}
```

## Continuous Integration

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
```

### GitHub Actions
```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: make test
      - name: Run linting
        run: make lint
```

## Documentation

### Code Documentation
- Document all public APIs
- Include examples in docstrings
- Keep documentation up to date
- Use type hints for better documentation

### Architecture Documentation
- Document design decisions
- Keep architecture diagrams current
- Document trade-offs and alternatives
- Update when patterns change

## Resources

### Learning Resources
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)

### Tools
- [Black Formatter](https://black.readthedocs.io/)
- [MyPy Type Checker](https://mypy.readthedocs.io/)
- [ESLint](https://eslint.org/)
- [Prettier](https://prettier.io/)
