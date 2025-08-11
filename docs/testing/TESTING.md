# AbSequenceAlign Testing Guide

This document describes the comprehensive testing setup for AbSequenceAlign, including local testing, Docker testing, and CI/CD pipeline testing.

## 🧪 Testing Overview

AbSequenceAlign has multiple testing layers:

1. **Backend Tests** - Python unit and integration tests
2. **Frontend Tests** - React component and utility tests
3. **E2E Tests** - Cypress end-to-end tests
4. **Docker Tests** - Containerized testing environments
5. **CI/CD Tests** - Automated GitHub Actions testing

## 🚀 Quick Start

### Run All Tests Locally
```bash
# Run all tests (backend, frontend, E2E, Docker)
make test

# Or use the unified test script
./scripts/test.sh
```

### Run Tests in Docker
```bash
# Run all tests in isolated Docker containers
make test-docker

# Or use the Docker test script
./scripts/test-docker.sh
```

## 📋 Test Commands

### Local Testing

| Command | Description |
|---------|-------------|
| `make test` | Run all tests locally |
| `make test-backend` | Run only backend tests |
| `make test-frontend` | Run only frontend tests |
| `make test-e2e` | Run only E2E tests |
| `make test-quick` | Run quick UI tests |
| `make test-parallel` | Run E2E tests in parallel |
| `make test-coverage` | Run all tests with coverage |

### Docker Testing

| Command | Description |
|---------|-------------|
| `make test-docker` | Run all tests in Docker |
| `make test-docker-backend` | Run backend tests in Docker |
| `make test-docker-frontend` | Run frontend tests in Docker |
| `make test-docker-e2e` | Run E2E tests in Docker |
| `make test-docker-cleanup` | Clean up Docker test resources |

### Development

| Command | Description |
|---------|-------------|
| `make dev` | Start development environment |
| `make dev-backend` | Start backend only |
| `make dev-frontend` | Start frontend only |

## 🔧 Test Scripts

### Unified Test Script (`./scripts/test.sh`)

The main test script that handles all types of testing:

```bash
# Run all tests
./scripts/test.sh

# Run specific test types
./scripts/test.sh --backend
./scripts/test.sh --frontend
./scripts/test.sh --e2e
./scripts/test.sh --quick
./scripts/test.sh --parallel
./scripts/test.sh --docker

# Run with coverage
./scripts/test.sh --coverage

# Show help
./scripts/test.sh --help
```

### Docker Test Script (`./scripts/test-docker.sh`)

Runs tests in isolated Docker containers:

```bash
# Run all tests in Docker
./scripts/test-docker.sh

# Run specific test types in Docker
./scripts/test-docker.sh --backend
./scripts/test-docker.sh --frontend
./scripts/test-docker.sh --e2e
./scripts/test-docker.sh --integration

# Clean up Docker resources
./scripts/test-docker.sh --cleanup
```

### E2E Test Script (`./app/frontend/scripts/run-e2e.sh`)

Runs Cypress E2E tests with proper server setup:

```bash
cd app/frontend
./scripts/run-e2e.sh
```

### Quick Test Script (`./app/frontend/scripts/quick-test.sh`)

Runs quick UI smoke tests:

```bash
cd app/frontend
./scripts/quick-test.sh
```

## 🐳 Docker Testing

### Test Containers

The project includes several Docker containers for testing:

1. **Backend Test Container** - Runs Python tests with conda environment
2. **Frontend Test Container** - Runs React tests with Node.js
3. **E2E Test Container** - Runs Cypress tests with browser
4. **Integration Test Container** - Runs integration tests

### Docker Compose Test Setup

```yaml
# docker-compose.test.yml
services:
  backend-test:     # Python backend tests
  frontend-test:    # React frontend tests
  e2e-test:         # Cypress E2E tests
  integration-test: # Integration tests
```

### Running Docker Tests

```bash
# Run all Docker tests
docker-compose -f docker-compose.test.yml up --build

# Run specific test service
docker-compose -f docker-compose.test.yml up --build backend-test

# Clean up
docker-compose -f docker-compose.test.yml down -v
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

The CI/CD pipeline includes:

1. **Backend Tests** - Python tests with coverage
2. **Frontend Tests** - React tests, linting, type checking
3. **Docker Tests** - Container build verification
4. **E2E Tests** - Parallel Cypress tests
5. **Security Scan** - Vulnerability scanning
6. **Build & Push** - Docker image building and pushing
7. **Deploy** - Production deployment (on release)

### Parallel E2E Testing

Cypress tests run in parallel across 4 jobs:

- `0-health-check.cy.ts`
- `1-scfv-annotation.cy.ts`
- `2-igG-dvdi-tcr.cy.ts`
- `quick-ui-test.cy.ts`

### Test Artifacts

On test failure, the pipeline uploads:
- Screenshots from failed tests
- Video recordings of test runs
- Coverage reports

## 📊 Test Coverage

### Backend Coverage

Backend tests generate coverage reports:
- XML format for CI/CD integration
- Terminal output for local development
- Coverage includes all backend modules

### Frontend Coverage

Frontend tests include:
- Unit test coverage
- Type checking with TypeScript
- Linting with ESLint
- Component testing with Vitest

## 🛠️ Test Environment Setup

### Prerequisites

1. **Conda Environment** - Python dependencies
2. **Node.js** - Frontend dependencies
3. **Docker** - Containerized testing
4. **ANARCI** - Antibody numbering tool

### Environment Variables

```bash
# Development
VITE_PORT=5679
BACKEND_PORT=8000
PYTHONPATH=/path/to/app

# Testing
CI=true
NODE_ENV=test
CYPRESS_baseUrl=http://localhost:5679
CYPRESS_backendPort=8000
```

## 🐛 Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Kill processes on ports
   lsof -ti:5679 | xargs kill -9
   lsof -ti:8000 | xargs kill -9
   ```

2. **Docker Cleanup**
   ```bash
   # Clean up Docker resources
   ./scripts/test-docker.sh --cleanup
   ```

3. **Environment Issues**
   ```bash
   # Reinstall dependencies
   make install
   ```

4. **Cypress Issues**
   ```bash
   # Clear Cypress cache
   npx cypress cache clear
   ```

### Test Debugging

1. **Backend Tests**
   ```bash
   cd app/backend
   PYTHONPATH="$(pwd)/.." conda run -n AbSequenceAlign python -m pytest tests/ -v -s
   ```

2. **Frontend Tests**
   ```bash
   cd app/frontend
   npm run test -- --reporter=verbose
   ```

3. **E2E Tests**
   ```bash
   cd app/frontend
   npx cypress open
   ```

## 📈 Performance

### Test Execution Times

- **Backend Tests**: ~30 seconds
- **Frontend Tests**: ~15 seconds
- **E2E Tests**: ~2-3 minutes (parallel)
- **Docker Tests**: ~5-10 minutes

### Optimization Tips

1. **Use Quick Tests** for rapid feedback
2. **Run Tests in Parallel** for faster execution
3. **Use Docker** for isolated testing
4. **Cache Dependencies** in CI/CD

## 🔍 Test Types

### Backend Tests

- **Unit Tests** - Individual function testing
- **Integration Tests** - API endpoint testing
- **Annotation Tests** - Antibody annotation logic
- **Alignment Tests** - Sequence alignment algorithms

### Frontend Tests

- **Component Tests** - React component testing
- **Hook Tests** - Custom React hooks
- **Utility Tests** - Helper function testing
- **Type Tests** - TypeScript type checking

### E2E Tests

- **Health Check** - Basic connectivity
- **ScFv Annotation** - Single-chain antibody testing
- **IgG/DVD-Ig/TCR** - Multi-domain antibody testing
- **Quick UI** - User interface smoke tests

## 📝 Adding New Tests

### Backend Tests

```python
# tests/test_new_feature.py
import pytest
from backend.module import function

def test_new_function():
    result = function()
    assert result == expected_value
```

### Frontend Tests

```typescript
// src/components/__tests__/NewComponent.test.tsx
import { render, screen } from '@testing-library/react'
import { NewComponent } from '../NewComponent'

test('renders component', () => {
  render(<NewComponent />)
  expect(screen.getByText('Hello')).toBeInTheDocument()
})
```

### E2E Tests

```typescript
// cypress/e2e/new-feature.cy.ts
describe('New Feature', () => {
  it('should work correctly', () => {
    cy.visit('/')
    cy.get('[data-testid="button"]').click()
    cy.contains('Success').should('be.visible')
  })
})
```

## 🎯 Best Practices

1. **Write Tests First** - TDD approach
2. **Keep Tests Fast** - Avoid slow operations
3. **Test Edge Cases** - Cover error scenarios
4. **Use Descriptive Names** - Clear test names
5. **Maintain Test Data** - Keep test data clean
6. **Run Tests Regularly** - Integrate into workflow
7. **Monitor Coverage** - Track test coverage
8. **Document Tests** - Explain complex test logic
