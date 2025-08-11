# AbSequenceAlign

A comprehensive antibody sequence analysis and annotation platform with a modern React frontend and FastAPI backend. This platform provides advanced tools for analyzing, annotating, and visualizing antibody sequences with support for multiple numbering schemes and annotation methods.

## 🎯 Overview

AbSequenceAlign is designed for bioinformatics researchers, immunologists, and pharmaceutical companies who need to analyze antibody sequences. The platform provides:

- **Sequence Annotation**: Automated annotation of antibody sequences using ANARCI and HMMER
- **Multiple Numbering Schemes**: Support for IMGT, Kabat, Chothia, and other numbering schemes
- **Sequence Alignment**: Multiple sequence alignment with visualization
- **Domain Analysis**: Identification and analysis of variable and constant domains
- **Feature Extraction**: CDR and FR region identification
- **Modern Web Interface**: React-based frontend with real-time visualization

## 🏗️ Architecture

The application follows a clean architecture pattern with clear separation of concerns:

- **Frontend**: React + TypeScript + Vite + Material-UI
- **Backend**: FastAPI + Python + ANARCI + HMMER
- **Domain Model**: Rich domain entities with enum-based type safety
- **Database**: PostgreSQL with SQLAlchemy 2.0 async support
- **Testing**: Comprehensive test suite with unit, integration, and E2E tests
- **CI/CD**: GitHub Actions with Docker containerization

## 📚 Documentation

### Architecture & Design
- [Architecture Patterns](./docs/architecture/ARCHITECTURE_PATTERNS.md) - Design patterns and architectural decisions
- [Modular Design Specification](./docs/architecture/MODULAR_DESIGN_SPEC.md) - Detailed modular architecture
- [Design Specification](./docs/architecture/Design_spec.md) - Original design specification
- [Architecture Simplification Plan](./docs/architecture/ARCHITECTURE_SIMPLIFICATION_PLAN.md) - Architecture evolution roadmap

### Database
- [Database Design Decisions](./docs/database/DATABASE_DESIGN_DECISIONS.md) - Database design rationale and trade-offs
- [Database Implementation Plan](./docs/database/DATABASE_IMPLEMENTATION_PLAN.md) - Database implementation roadmap

### Development
- [Command Pattern Implementation](./docs/development/COMMAND_PATTERN_IMPLEMENTATION.md) - Command pattern usage in the application
- [Cleanup Summary](./docs/development/CLEANUP_SUMMARY.md) - Code cleanup and refactoring history
- [Cleanup Completion Summary](./docs/development/CLEANUP_COMPLETION_SUMMARY.md) - Latest cleanup status

### Testing
- [Testing Guide](./docs/testing/TESTING.md) - Comprehensive testing strategy and guidelines

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- Conda (for Python environment management)

### Development Setup

```bash
# Clone the repository
git clone https://github.com/maquino1985/AbSequenceAlign.git
cd AbSequenceAlign

# Start development environment
make dev
# or
docker-compose up
```

### Production Setup

```bash
# Build and run production containers
docker-compose -f docker-compose.prod.yml up -d

# Or build and run individual services
docker-compose up backend frontend
```

## 🧪 Testing

### Unit Tests
```bash
# Frontend unit tests
cd app/frontend && npm run test

# Backend unit tests
cd app/backend && python -m pytest
```

### E2E Tests
```bash
# Development E2E (Vite dev server)
cd app/frontend && npm run test:e2e

# Production-like E2E (Nginx + built assets)
cd app/frontend && npm run test:e2e:prod
```

### Docker Testing
```bash
# Test Docker builds
make test-docker

# Run production-like E2E tests
docker-compose -f docker-compose.e2e-prod.yml up --abort-on-container-exit
```

## 🔧 Development Workflow

### Local Development
1. **Frontend**: `cd app/frontend && npm run dev`
2. **Backend**: `cd app/backend && python -m uvicorn backend.main:app --reload`
3. **Database**: PostgreSQL with Docker or local installation

### Code Quality
- **Python**: Black formatting, Flake8 linting, MyPy type checking
- **TypeScript**: ESLint, TypeScript strict mode
- **Pre-commit**: Automated checks before commits

### Docker Development
```bash
# Build base images (first time only)
make build-base-images

# Start development environment
make dev

# Run tests
make test
```

## 🚀 Deployment

### Docker Deployment
```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# With monitoring
docker-compose -f docker-compose.prod.yml up -d
```

### Cloud Deployment
The application is containerized and ready for deployment on:
- **AWS ECS/Fargate**
- **Google Cloud Run**
- **Azure Container Instances**
- **Kubernetes**

### Environment Variables
See `env.example` for required environment variables.

## 📊 Monitoring

### Production Monitoring
- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboard
- **Health Checks**: Built-in endpoints

### Logging
- **Structured Logging**: JSON format
- **Log Levels**: Configurable per environment
- **Centralized**: Ready for ELK stack integration

## 🔒 Security

### Production Security
- **HTTPS**: Nginx SSL termination
- **Security Headers**: XSS protection, CSP, etc.
- **CORS**: Properly configured for API access
- **Input Validation**: Pydantic models with strict validation

### Container Security
- **Base Images**: Alpine Linux for minimal attack surface
- **Non-root**: Containers run as non-root users
- **Vulnerability Scanning**: Trivy integration in CI/CD

## 📈 Performance

### Frontend Optimization
- **Code Splitting**: Automatic with Vite
- **Tree Shaking**: Unused code elimination
- **Asset Optimization**: Compressed static assets
- **Caching**: Long-term caching for static assets

### Backend Optimization
- **Async Processing**: Background job processing
- **Caching**: Redis integration ready
- **Database**: Optimized queries and indexing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test`
5. Submit a pull request

### Development Guidelines
- Follow TypeScript strict mode
- Write unit tests for new features
- Update documentation
- Use conventional commits

## 📄 License

[Add your license here]

## 🆘 Support

For issues and questions:
- Create a GitHub issue
- Check the documentation in the `docs/` directory
- Review existing issues

---

**Note**: This application is designed for production use with proper security, monitoring, and scalability considerations built-in.
